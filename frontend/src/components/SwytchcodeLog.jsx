import { CheckCircle2, XCircle, Lock } from 'lucide-react';

function SwytchcodeLog({ log }) {
  if (!log || log.length === 0) {
    return (
      <div className="empty-state">
        <Lock className="empty-state-icon" />
        <p className="message">Swytchcode execution audit log will populate as tools are called by the pipeline.</p>
      </div>
    );
  }

  const formatTime = (ts) => {
    if (!ts) return '--';
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return ts;
    }
  };

  return (
    <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
      <table className="log-table" id="swytchcode-log-table">
        <thead>
          <tr style={{ opacity: 1 }}>
            <th>Timestamp</th>
            <th>Canonical Tool ID</th>
            <th>Execution Status</th>
            <th>Latency</th>
          </tr>
        </thead>
        <tbody>
          {log.map((entry, i) => (
            <tr key={i} style={{ animationDelay: `${i * 0.05}s` }}>
              <td>{formatTime(entry.timestamp)}</td>
              <td style={{ color: 'var(--accent-sky)', fontWeight: '600' }}>{entry.tool_id}</td>
              <td>
                <span className={entry.status === 'success' ? 'log-status-success' : 'log-status-error'}>
                  {entry.status === 'success' ? <CheckCircle2 size={13} /> : <XCircle size={13} />} HTTP {entry.status_code}
                </span>
              </td>
              <td>{entry.latency_ms} ms</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SwytchcodeLog;
