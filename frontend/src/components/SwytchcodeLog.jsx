/**
 * SwytchcodeLog — Live audit trail of all swy_exec() calls.
 * Shows tool IDs, status, latency, and policy enforcement.
 */
function SwytchcodeLog({ log }) {
  if (!log || log.length === 0) {
    return (
      <div className="empty-state">
        <span className="icon">🔒</span>
        <p className="message">Swytchcode audit log will populate as API calls are executed.</p>
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
            <th>Time</th>
            <th>Tool ID</th>
            <th>Status</th>
            <th>Latency</th>
          </tr>
        </thead>
        <tbody>
          {log.map((entry, i) => (
            <tr key={i} style={{ animationDelay: `${i * 0.05}s` }}>
              <td>{formatTime(entry.timestamp)}</td>
              <td style={{ color: 'var(--accent-cyan)' }}>{entry.tool_id}</td>
              <td>
                <span className={entry.status === 'success' ? 'log-status-success' : 'log-status-error'}>
                  {entry.status === 'success' ? '✅' : '❌'} {entry.status_code}
                </span>
              </td>
              <td>{entry.latency_ms}ms</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default SwytchcodeLog;
