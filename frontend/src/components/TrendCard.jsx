/**
 * TrendCard — Individual trend item with source badge.
 * Shows source type (News/Social/Emerging) with distinct colors.
 */
function TrendCard({ trend, index }) {
  const sourceConfig = {
    news: { badge: 'source-news', label: '🗞 News' },
    social_chatter: { badge: 'source-social', label: '💬 Social' },
    emerging_topic: { badge: 'source-emerging', label: '🔥 Emerging' },
  };

  const config = sourceConfig[trend.source_type] || sourceConfig.news;

  return (
    <div
      className="trend-card"
      style={{ animationDelay: `${index * 0.05}s` }}
      id={`trend-card-${index}`}
    >
      <div className="trend-card-header">
        <span className={`trend-source-badge ${config.badge}`}>
          {config.label}
        </span>
        <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          {trend.source}
        </span>
      </div>
      <div className="trend-title">{trend.title}</div>
      {trend.description && trend.description !== trend.title && (
        <div className="trend-desc">{trend.description}</div>
      )}
    </div>
  );
}

export default TrendCard;
