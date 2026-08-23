import {
  Radio,
  Layers,
  Search,
  Cpu,
  Share2,
  CheckCircle2,
  Play,
  Loader2
} from 'lucide-react';

function PipelineVisualizer({ steps, isRunning, onRun }) {
  const pipelineConfig = [
    { key: 'fetch',    Icon: Radio,   label: 'Fetch Trends',     sub: 'Swytchcode' },
    { key: 'ingest',   Icon: Layers,  label: 'Chunk & Embed',    sub: 'ChromaDB' },
    { key: 'retrieve', Icon: Search,  label: 'Vector Retrieve',  sub: 'Top-5 RAG' },
    { key: 'generate', Icon: Cpu,     label: 'Groq Generate',    sub: 'Llama-3.3 70B' },
    { key: 'post',     Icon: Share2,  label: 'Post to Reddit',   sub: 'Swytchcode' },
  ];

  const getStepStatus = (key) => steps[key] || 'waiting';

  const isConnectorActive = (index) => {
    const current = getStepStatus(pipelineConfig[index].key);
    return current === 'done' || current === 'running';
  };

  return (
    <div className="glass-card">
      <div className="card-header">
        <h2 className="card-title">
          <span className="card-title-icon">
            <Cpu size={18} />
          </span>
          RAG Pipeline Execution
        </h2>
        <button
          className="run-button"
          onClick={onRun}
          disabled={isRunning}
          id="run-pipeline-button"
        >
          {isRunning ? (
            <>
              <Loader2 size={16} className="spinner-icon" style={{ animation: 'spin 1s linear infinite' }} />
              Processing Pipeline...
            </>
          ) : (
            <>
              <Play size={16} fill="currentColor" /> Run Pipeline Now
            </>
          )}
        </button>
      </div>

      <div className="pipeline-steps">
        {pipelineConfig.map((step, i) => {
          const status = getStepStatus(step.key);
          const StepIcon = step.Icon;

          return (
            <div key={step.key} style={{ display: 'contents' }}>
              <div className="pipeline-step">
                <div className={`step-circle ${status}`}>
                  {status === 'done' ? (
                    <CheckCircle2 size={22} style={{ color: 'var(--accent-emerald)' }} />
                  ) : (
                    <StepIcon size={22} />
                  )}
                </div>
                <span className="step-label">{step.label}</span>
                <span className="step-sublabel">{step.sub}</span>
              </div>
              {i < pipelineConfig.length - 1 && (
                <div className={`step-connector ${isConnectorActive(i) ? 'active' : ''}`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default PipelineVisualizer;
