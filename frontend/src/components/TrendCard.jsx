import { Globe, MessageSquare, Flame } from 'lucide-react';

function TrendCard({ trend, index }) {
  const sourceConfig = {
    news: { badge: 'source-news', label: 'News', Icon: Globe },
    social_chatter: { badge: 'source-social', label: 'Social Chatter', Icon: MessageSquare },
    emerging_topic: { badge: 'source-emerging', label: 'Emerging', Icon: Flame },
  };

  const config = sourceConfig[trend.source_type] || sourceConfig.news;
  const SourceIcon = config.Icon;

  return (
    <div
      className="trend-card"
      style={{ animationDelay: `${index * 0.05}s` }}
      id={`trend-card-${index}`}
    >
      <div className="trend-card-header">
        <span className={`trend-source-badge ${config.badge}`}>
          <SourceIcon size={12} />
          {config.label}
        </span>
        <span style={{ fontSize: '11px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
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
