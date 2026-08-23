import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import {
  Zap,
  Radio,
  Search,
  FileText,
  ShieldCheck,
  Clock,
  CheckCircle2,
  Lock
} from 'lucide-react';

import PipelineVisualizer from './components/PipelineVisualizer.jsx';
import TrendCard from './components/TrendCard.jsx';
import RAGInspector from './components/RAGInspector.jsx';
import GeneratedPost from './components/GeneratedPost.jsx';
import SwytchcodeLog from './components/SwytchcodeLog.jsx';
import SchedulerPanel from './components/SchedulerPanel.jsx';

const API_BASE = '/api';

function App() {
  const [pipelineSteps, setPipelineSteps] = useState({
    fetch: 'waiting',
    ingest: 'waiting',
    retrieve: 'waiting',
    generate: 'waiting',
    post: 'waiting',
  });
  const [trends, setTrends] = useState([]);
  const [passages, setPassages] = useState([]);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [postResult, setPostResult] = useState(null);
  const [swytchcodeLog, setSwytchcodeLog] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    axios.get(`${API_BASE}/scheduler/status`).then(res => setSchedulerStatus(res.data)).catch(() => {});
    axios.get(`${API_BASE}/swytchcode/log`).then(res => setSwytchcodeLog(res.data.log || [])).catch(() => {});
    axios.get(`${API_BASE}/trends`).then(res => {
      if (res.data.trends?.length) setTrends(res.data.trends);
    }).catch(() => {});
    axios.get(`${API_BASE}/posts`).then(res => {
      if (res.data.posts?.length) {
        const latest = res.data.posts[res.data.posts.length - 1];
        setGeneratedContent(latest.generated_content);
        setPostResult(latest.post_result);
      }
    }).catch(() => {});
  }, []);

  const connectSSE = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const es = new EventSource(`${API_BASE}/pipeline/stream`);
    eventSourceRef.current = es;

    es.addEventListener('pipeline_step', (e) => {
      const data = JSON.parse(e.data);
      const { step, status } = data;

      setPipelineSteps(prev => ({ ...prev, [step]: status }));

      if (step === 'retrieve' && status === 'done' && data.data?.passages) {
        setPassages(data.data.passages);
      }
      if (step === 'generate' && status === 'done' && data.data) {
        setGeneratedContent(data.data);
      }
      if (step === 'post' && status === 'done' && data.data) {
        setPostResult(data.data);
      }
    });

    es.addEventListener('pipeline_complete', (e) => {
      const data = JSON.parse(e.data);
      setTrends(data.trends || []);
      if (data.swytchcode_log) {
        setSwytchcodeLog(prev => [...prev, ...data.swytchcode_log]);
      }
      setIsRunning(false);
    });

    es.onerror = () => {
      setTimeout(connectSSE, 3000);
    };

    return es;
  }, []);

  useEffect(() => {
    const es = connectSSE();
    return () => es.close();
  }, [connectSSE]);

  const handleRunPipeline = async () => {
    setIsRunning(true);
    setTrends([]);
    setPassages([]);
    setGeneratedContent(null);
    setPostResult(null);
    setPipelineSteps({
      fetch: 'waiting',
      ingest: 'waiting',
      retrieve: 'waiting',
      generate: 'waiting',
      post: 'waiting',
    });

    try {
      const res = await axios.post(`${API_BASE}/pipeline/run`);
      const result = res.data;
      setTrends(result.trends || []);
      if (result.generated_content) setGeneratedContent(result.generated_content);
      if (result.post_result) setPostResult(result.post_result);
      if (result.swytchcode_log) {
        setSwytchcodeLog(prev => [...prev, ...result.swytchcode_log]);
      }

      setPipelineSteps({
        fetch: 'done',
        ingest: 'done',
        retrieve: 'done',
        generate: 'done',
        post: result.post_result?.success ? 'done' : 'error',
      });
    } catch (err) {
      console.error('Pipeline error:', err);
      setPipelineSteps(prev => {
        const next = { ...prev };
        Object.keys(next).forEach(k => {
          if (next[k] === 'waiting' || next[k] === 'running') next[k] = 'error';
        });
        return next;
      });
    } finally {
      setIsRunning(false);
      axios.get(`${API_BASE}/scheduler/status`).then(res => setSchedulerStatus(res.data)).catch(() => {});
    }
  };

  return (
    <div className="app-container">
      {/* ── Header ────────────────────────────────────────────── */}
      <header className="header">
        <div className="header-brand">
          <div className="header-logo-badge">
            <Zap size={24} />
          </div>
          <div>
            <h1 className="header-title">TrendPulse</h1>
            <p className="header-subtitle">RAG-Powered Trend Automation Engine</p>
          </div>
        </div>
        <div className="header-status">
          <span className="status-dot"></span>
          <span className="status-text">
            <ShieldCheck size={16} style={{ color: 'var(--accent-emerald)' }} />
            Swytchcode Engine Active
          </span>
        </div>
      </header>

      {/* ── Dashboard Grid ────────────────────────────────────── */}
      <div className="dashboard-grid">
        {/* Pipeline Visualizer — Full Width */}
        <div className="grid-pipeline">
          <PipelineVisualizer
            steps={pipelineSteps}
            isRunning={isRunning}
            onRun={handleRunPipeline}
          />
        </div>

        {/* Main Grid: Trends & RAG Inspector */}
        <div className="grid-main">
          <div className="glass-card">
            <div className="card-header">
              <h2 className="card-title">
                <span className="card-title-icon">
                  <Radio size={18} />
                </span>
                Live Trends Feed
              </h2>
              <span className="card-badge badge-sky">{trends.length} Fetched</span>
            </div>
            <div className="trends-grid">
              {trends.length > 0 ? (
                trends.map((trend, i) => (
                  <TrendCard key={i} trend={trend} index={i} />
                ))
              ) : (
                <div className="empty-state">
                  <Radio className="empty-state-icon" />
                  <p className="message">No active trends. Click "Run Now" to aggregate live trends from NewsAPI, Reddit, HackerNews, Dev.to, and Google News RSS.</p>
                </div>
              )}
            </div>
          </div>

          <div className="glass-card">
            <div className="card-header">
              <h2 className="card-title">
                <span className="card-title-icon" style={{ background: 'rgba(139, 92, 246, 0.12)', color: 'var(--accent-violet)' }}>
                  <Search size={18} />
                </span>
                Vector RAG Inspector
              </h2>
              <span className="card-badge badge-violet">ChromaDB</span>
            </div>
            <RAGInspector passages={passages} />
          </div>
        </div>

        {/* Generated Post — Full Width */}
        <div className="glass-card">
          <div className="card-header">
            <h2 className="card-title">
              <span className="card-title-icon" style={{ background: 'rgba(16, 185, 129, 0.12)', color: 'var(--accent-emerald)' }}>
                <FileText size={18} />
              </span>
              Generated Content Preview
            </h2>
            {postResult?.success && (
              <span className="card-badge badge-emerald" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <CheckCircle2 size={12} /> Posted to Reddit
              </span>
            )}
          </div>
          <GeneratedPost content={generatedContent} postResult={postResult} />
        </div>

        {/* Bottom Row: Swytchcode Log & Scheduler */}
        <div className="grid-bottom">
          <div className="glass-card">
            <div className="card-header">
              <h2 className="card-title">
                <span className="card-title-icon" style={{ background: 'rgba(245, 158, 11, 0.12)', color: 'var(--accent-amber)' }}>
                  <Lock size={18} />
                </span>
                Swytchcode Audit Log
              </h2>
              <span className="card-badge badge-amber">{swytchcodeLog.length} Executions</span>
            </div>
            <SwytchcodeLog log={swytchcodeLog} />
          </div>

          <div className="glass-card">
            <div className="card-header">
              <h2 className="card-title">
                <span className="card-title-icon" style={{ background: 'rgba(14, 165, 233, 0.12)', color: 'var(--accent-sky)' }}>
                  <Clock size={18} />
                </span>
                Automation Scheduler
              </h2>
              <span className="card-badge badge-emerald">Active Schedule</span>
            </div>
            <SchedulerPanel
              status={schedulerStatus}
              isRunning={isRunning}
              onRun={handleRunPipeline}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
