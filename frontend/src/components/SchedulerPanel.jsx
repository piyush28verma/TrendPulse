/**
 * SchedulerPanel — Shows scheduler status + Run Now button + countdown.
 */
import { useState, useEffect } from 'react';

function SchedulerPanel({ status, isRunning, onRun }) {
  const [countdown, setCountdown] = useState('');

  useEffect(() => {
    if (!status?.next_run) return;

    const interval = setInterval(() => {
      const next = new Date(status.next_run);
      const now = new Date();
      const diff = next - now;

      if (diff <= 0) {
        setCountdown('Imminent...');
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const secs = Math.floor((diff % (1000 * 60)) / 1000);
      setCountdown(`${hours}h ${mins}m ${secs}s`);
    }, 1000);

    return () => clearInterval(interval);
  }, [status?.next_run]);

  return (
    <div className="scheduler-info">
      <div className="scheduler-stat">
        <span className="scheduler-stat-label">Daily Schedule</span>
        <span className="scheduler-stat-value">
          {status?.schedule_time || '09:00 UTC'}
        </span>
      </div>

      <div className="scheduler-stat">
        <span className="scheduler-stat-label">Next Run</span>
        <span className="scheduler-stat-value" style={{ color: 'var(--accent-cyan)' }}>
          {countdown || 'Calculating...'}
        </span>
      </div>

      <div className="scheduler-stat">
        <span className="scheduler-stat-label">Last Run</span>
        <span className="scheduler-stat-value">
          {status?.last_run
            ? new Date(status.last_run).toLocaleTimeString('en-US', { hour12: false })
            : 'Never'
          }
        </span>
      </div>

      <div className="scheduler-stat">
        <span className="scheduler-stat-label">Status</span>
        <span className="scheduler-stat-value" style={{ color: status?.running ? 'var(--accent-green)' : 'var(--accent-red)' }}>
          {status?.running ? '● Active' : '○ Inactive'}
        </span>
      </div>

      <button
        className="run-button"
        onClick={onRun}
        disabled={isRunning}
        style={{ width: '100%', justifyContent: 'center' }}
        id="scheduler-run-button"
      >
        {isRunning ? (
          <>
            <span className="spinner"></span>
            Running Pipeline...
          </>
        ) : (
          <>🚀 Trigger Now</>
        )}
      </button>
    </div>
  );
}

export default SchedulerPanel;
