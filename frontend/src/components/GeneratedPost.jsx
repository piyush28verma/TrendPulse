/**
 * GeneratedPost — Content preview with real Reddit URL + citation badges.
 */
function GeneratedPost({ content, postResult }) {
  if (!content) {
    return (
      <div className="empty-state">
        <span className="icon">📝</span>
        <p className="message">Generated content will appear here after running the RAG pipeline.</p>
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
              🔗 {postResult.reddit_url}
            </a>
          ) : postResult?.error ? (
            <span style={{ fontSize: '12px', color: 'var(--accent-red)' }}>
              ⚠️ {postResult.error}
            </span>
          ) : (
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Waiting for post...
            </span>
          )}
        </div>

        <div className="post-citations">
          {content.citations?.map((c, i) => (
            <span key={i} className="citation-badge">[{c}]</span>
          ))}
          <span
            className="citation-badge"
            style={{
              background: 'rgba(0, 212, 255, 0.12)',
              color: 'var(--accent-cyan)',
              borderColor: 'rgba(0, 212, 255, 0.2)',
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
