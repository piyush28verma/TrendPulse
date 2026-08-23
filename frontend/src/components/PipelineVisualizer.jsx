/**
 * PipelineVisualizer — 5-step animated pipeline
 * Steps animate from grey → purple glow → green as SSE events arrive.
 */
function PipelineVisualizer({ steps, isRunning, onRun }) {
  const pipelineConfig = [
    { key: 'fetch',    icon: '📡', label: 'Fetch Trends',     sub: 'Swytchcode' },
    { key: 'ingest',   icon: '🧩', label: 'Chunk & Embed',    sub: 'ChromaDB' },
    { key: 'retrieve', icon: '🔍', label: 'Vector Retrieve',  sub: 'Top-5 RAG' },
    { key: 'generate', icon: '🧠', label: 'Groq Generate',    sub: 'llama-3.3-70b' },
    { key: 'post',     icon: '📤', label: 'Post to Reddit',   sub: 'Swytchcode' },
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
          <span className="icon">⚡</span>
          RAG Pipeline
        </h2>
        <button
          className="run-button"
          onClick={onRun}
          disabled={isRunning}
          id="run-pipeline-button"
        >
          {isRunning ? (
            <>
              <span className="spinner"></span>
              Processing...
            </>
          ) : (
            <>🚀 Run Now</>
          )}
        </button>
      </div>

      <div className="pipeline-steps">
        {pipelineConfig.map((step, i) => (
          <div key={step.key} style={{ display: 'contents' }}>
            <div className="pipeline-step">
              <div className={`step-circle ${getStepStatus(step.key)}`}>
                {getStepStatus(step.key) === 'done' ? '✅' : step.icon}
              </div>
              <span className="step-label">{step.label}</span>
              <span className="step-sublabel">{step.sub}</span>
            </div>
            {i < pipelineConfig.length - 1 && (
              <div className={`step-connector ${isConnectorActive(i) ? 'active' : ''}`} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default PipelineVisualizer;
