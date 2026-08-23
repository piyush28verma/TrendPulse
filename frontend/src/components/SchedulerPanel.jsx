import { useState, useEffect } from 'react';
import { Play, Loader2, Clock, Calendar, Activity } from 'lucide-react';

function SchedulerPanel({ status, isRunning, onRun }) {
  const [countdown, setCountdown] = useState('');

  useEffect(() => {
    if (!status?.next_run) return;

    const interval = setInterval(() => {
      const next = new Date(status.next_run);
      const now = new Date();
      const diff = next - now;

      if (diff <= 0) {
        setCountdown('Triggering imminent...');
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
        <span className="scheduler-stat-label" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <Calendar size={14} style={{ color: 'var(--accent-sky)' }} /> Daily Recurrence
        </span>
        <span className="scheduler-stat-value">
          {status?.schedule_time || '09:00 UTC'}
        </span>
      </div>

      <div className="scheduler-stat">
        <span className="scheduler-stat-label" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <Clock size={14} style={{ color: 'var(--accent-sky)' }} /> Next Trigger Countdown
        </span>
        <span className="scheduler-stat-value" style={{ color: 'var(--accent-sky)' }}>
          {countdown || 'Calculating...'}
        </span>
      </div>

      <div className="scheduler-stat">
        <span className="scheduler-stat-label" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <Activity size={14} style={{ color: 'var(--accent-secondary)' }} /> Scheduler Status
        </span>
        <span className="scheduler-stat-value" style={{ color: status?.running ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
          {status?.running ? 'Active (APScheduler)' : 'Inactive'}
        </span>
      </div>

      <button
        className="run-button"
        onClick={onRun}
        disabled={isRunning}
        style={{ width: '100%', justifyContent: 'center', marginTop: '6px' }}
        id="scheduler-run-button"
      >
        {isRunning ? (
          <>
            <Loader2 size={16} className="spinner-icon" style={{ animation: 'spin 1s linear infinite' }} />
            Pipeline Executing...
          </>
        ) : (
          <>
            <Play size={16} fill="currentColor" /> Trigger Daily Job Instantly
          </>
        )}
      </button>
    </div>
  );
}

export default SchedulerPanel;
