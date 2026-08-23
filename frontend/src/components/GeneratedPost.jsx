import { ExternalLink, AlertCircle, FileText, CheckCircle2 } from 'lucide-react';

function GeneratedPost({ content, postResult }) {
  if (!content) {
    return (
      <div className="empty-state">
        <FileText className="empty-state-icon" />
        <p className="message">Generated post content grounded in vector trends will be previewed here.</p>
      </div>
    );
  }

  return (
    <div className="generated-post">
      <div className="post-title">{content.title}</div>
      <div className="post-body">{content.body}</div>

      <div className="post-footer">
        <div>
          {postResult?.reddit_url ? (
            <a
              href={postResult.reddit_url}
              target="_blank"
              rel="noopener noreferrer"
              className="post-url"
              id="reddit-post-link"
            >
              <ExternalLink size={14} /> View Live Post: {postResult.reddit_url}
            </a>
          ) : postResult?.error ? (
            <span style={{ fontSize: '13px', color: 'var(--accent-rose)', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              <AlertCircle size={14} /> {postResult.error}
            </span>
          ) : (
            <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              Preparing target post...
            </span>
          )}
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          {content.citations?.map((c, i) => (
            <span key={i} className="citation-badge">Source [{c}]</span>
          ))}
          <span
            className="citation-badge"
            style={{
              background: 'rgba(14, 165, 233, 0.12)',
              color: 'var(--accent-sky)',
              borderColor: 'rgba(14, 165, 233, 0.25)',
            }}
          >
            {content.model}
          </span>
        </div>
      </div>
    </div>
  );
}

export default GeneratedPost;
