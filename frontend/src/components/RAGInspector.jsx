import { Search, Globe, MessageSquare, Flame } from 'lucide-react';

function RAGInspector({ passages }) {
  if (!passages || passages.length === 0) {
    return (
      <div className="empty-state">
        <Search className="empty-state-icon" />
        <p className="message">Run the pipeline to inspect vector passages retrieved from ChromaDB with similarity scores.</p>
      </div>
    );
  }

  const getSourceIcon = (type) => {
    switch (type) {
      case 'news': return <Globe size={14} style={{ color: 'var(--accent-sky)' }} />;
      case 'social_chatter': return <MessageSquare size={14} style={{ color: 'var(--accent-rose)' }} />;
      case 'emerging_topic': return <Flame size={14} style={{ color: 'var(--accent-amber)' }} />;
      default: return <Search size={14} style={{ color: 'var(--accent-indigo)' }} />;
    }
  };

  return (
    <div className="rag-passages">
      {passages.map((passage, i) => (
        <div
          className="rag-passage"
          key={i}
          style={{ animationDelay: `${i * 0.1}s` }}
          id={`rag-passage-${i}`}
        >
          <div className="rag-passage-header">
            <span className="rag-passage-index">
              [{i + 1}] {getSourceIcon(passage.source_type)} {passage.source}
            </span>
            <div className="similarity-bar-container">
              <div className="similarity-bar">
                <div
                  className="similarity-bar-fill"
                  style={{ width: `${Math.round(passage.similarity_score * 100)}%` }}
                />
              </div>
              <span className="similarity-score">
                {(passage.similarity_score * 100).toFixed(1)}%
              </span>
            </div>
          </div>
          <div className="rag-passage-text">
            <strong style={{ color: 'var(--text-primary)' }}>{passage.title}</strong>
            {passage.text !== passage.title && (
              <>
                <br />
                {passage.text}
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default RAGInspector;
