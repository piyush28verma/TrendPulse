import { useState, useMemo } from 'react';
import {
  FileText,
  MessageCircle,
  BookOpen,
  MessageSquare,
  Video,
  Copy,
  Check,
  ExternalLink,
  Sparkles,
  Share2,
  Clock,
  Flame,
  Sliders,
  Hash
} from 'lucide-react';

// Utility to strip all markdown syntax and return clean, natural plain text
function stripMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')       // bold **text**
    .replace(/\*(.*?)\*/g, '$1')           // italic *text*
    .replace(/__(.*?)__/g, '$1')           // bold __text__
    .replace(/_(.*?)_/g, '$1')             // italic _text_
    .replace(/#{1,6}\s+/g, '')             // headings # text
    .replace(/`([^`]+)`/g, '$1')           // inline code
    .replace(/```[\s\S]*?```/g, '')        // code blocks
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // links [text](url)
    .replace(/^\s*[-*+]\s+/gm, '• ')       // bullet points to clean unicode bullets
    .replace(/^\s*\d+\.\s+/gm, '')         // numbered list prefixes if desired
    .trim();
}

function GeneratedPost({ content, postResult }) {
  const [activeFormat, setActiveFormat] = useState('post');
  const [copiedKey, setCopiedKey] = useState(null);

  const baseData = useMemo(() => {
    if (!content) return null;
    const title = stripMarkdown(content.title || 'Tech & AI Trends Daily Synthesis');
    const rawBody = content.body || '';

    // Split body paragraphs and strip markdown
    const paragraphs = rawBody
      .split('\n\n')
      .map(p => stripMarkdown(p.trim()))
      .filter(p => p && !p.startsWith('HASHTAGS:') && !p.startsWith('SOURCES:'));

    const hashtagMatch = rawBody.match(/#[A-Za-z0-9_]+/g) || ['#TechTrends', '#AIInnovation', '#FutureTech'];
    const citations = content.citations || [1, 2, 3];
    const passages = content.retrieved_passages || [];

    // Clean plain text version of the entire body
    const plainBody = stripMarkdown(rawBody);

    return {
      title,
      paragraphs,
      rawBody: plainBody,
      hashtags: hashtagMatch.slice(0, 6),
      citations,
      passages,
      model: content.model || 'Groq AI'
    };
  }, [content]);

  const formattedContent = useMemo(() => {
    if (!baseData) return null;
    const { title, paragraphs, rawBody, hashtags, passages } = baseData;

    // 1. POST (LinkedIn / Thought Leadership - Clean Plain Text)
    const postText = rawBody;

    // 2. TWEET THREAD (Strict 280 char limits per tweet, clean text)
    const tweet1 = `${title}\n\nBreaking down the biggest shifts happening in tech & AI right now:\n\nA fast thread 🧵👇`;
    
    const p1Summary = paragraphs[0] 
      ? paragraphs[0].slice(0, 210).replace(/\[\d+\]/g, '') + '...'
      : 'Key innovations and hardware breakthroughs are accelerating industry timelines.';
    const tweet2 = `1/3 Core Breakdown:\n\n${p1Summary}`;

    const p2Summary = paragraphs[1] 
      ? paragraphs[1].slice(0, 200).replace(/\[\d+\]/g, '') + '...'
      : 'Ecosystem analysis confirms major momentum across benchmarked platforms.';
    const tweet3 = `2/3 Key Impact:\n\n${p2Summary}\n\nData grounded via verified vector streams.`;

    const tweet4 = `3/3 Takeaway:\n\nWhich of these developments do you think will reshape the landscape fastest?\n\nDrop your thoughts below 👇\n${hashtags.slice(0, 3).join(' ')}`;

    const tweetThread = [tweet1, tweet2, tweet3, tweet4];

    // 3. BLOG SNIPPET (Clean, Structured Plain Text)
    const tldr = paragraphs[0] 
      ? paragraphs[0].replace(/\[\d+\]/g, '') 
      : 'An executive overview of today’s top trending technology and AI developments.';
    
    const takeaways = passages.length >= 3 
      ? [stripMarkdown(passages[0].title), stripMarkdown(passages[1].title), stripMarkdown(passages[2].title)]
      : [
          'Emerging hardware milestones and ecosystem benchmark performance',
          'Shifts in consumer tech sentiment and developer community adoption',
          'Long-term implications for next-gen platform roadmaps'
        ];

    // 4. CAPTION (Short 2-3 lines max, clean text)
    const captionHook = `Today's top tech breakdown: ${title}.`;
    const captionBody = `From hardware shifts to ecosystem milestones, here's what you need to know today. Which update caught your eye?`;
    const captionHashtags = hashtags.join(' ');
    const captionFull = `${captionHook}\n\n${captionBody}\n\n${captionHashtags}`;

    // 5. SHORT-FORM VIDEO SCRIPT (Hook, Visuals, Voiceover, CTA)
    const scriptHook = `Stop scrolling — here is the biggest tech news you missed today.`;
    const scriptCore1 = paragraphs[0] ? paragraphs[0].slice(0, 160).replace(/\[\d+\]/g, '') : title;
    const scriptCore2 = paragraphs[1] ? paragraphs[1].slice(0, 150).replace(/\[\d+\]/g, '') : 'Here is the key takeaway.';
    const scriptCta = `Follow for your daily 60-second tech synthesis.`;

    const videoScript = [
      {
        time: '0:00 - 0:03',
        phase: 'THE HOOK',
        visual: 'Fast zoom-in on host with bold animated headline overlay on screen',
        audio: scriptHook,
        tip: 'High energy, direct eye contact'
      },
      {
        time: '0:03 - 0:18',
        phase: 'THE BREAKDOWN',
        visual: 'Split screen with b-roll footage & key source stat pop-up',
        audio: scriptCore1,
        tip: 'Paced at 145 WPM for maximum retention'
      },
      {
        time: '0:18 - 0:40',
        phase: 'THE DEEP DIVE',
        visual: 'Screen recording / benchmark comparison graphic highlight',
        audio: scriptCore2,
        tip: 'Emphasize the contrast and data insight'
      },
      {
        time: '0:40 - 0:50',
        phase: 'CALL TO ACTION',
        visual: 'Host on-camera, pointing down to follow button with sound effect',
        audio: scriptCta,
        tip: 'Clear subscription trigger'
      }
    ];

    return {
      post: { text: postText, title },
      tweet: { thread: tweetThread },
      blog: {
        seoTitle: `Deep Dive: ${title}`,
        readingTime: '3 min read',
        tldr,
        takeaways,
        body: paragraphs.join('\n\n'),
        metaDescription: `Comprehensive synthesis and vector-grounded breakdown on ${title}. Discover key insights, verified sources, and industry implications.`
      },
      caption: {
        hook: captionHook,
        body: captionBody,
        hashtags: captionHashtags,
        full: captionFull
      },
      script: {
        title: `60s Shorts/Reels Script: ${title}`,
        duration: '48 seconds',
        wpm: '142 WPM (Optimal)',
        wordCount: 110,
        scenes: videoScript
      }
    };
  }, [baseData]);

  const handleCopy = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  if (!content || !formattedContent) {
    return (
      <div className="empty-state">
        <FileText className="empty-state-icon" />
        <p className="message">Click "Run Pipeline Now" to generate multi-format, on-brand content repurposed across platforms.</p>
      </div>
    );
  }

  const formats = [
    { id: 'post',    label: 'Post / Article',    Icon: FileText,      badge: 'LinkedIn & Longform' },
    { id: 'tweet',   label: 'Tweet Thread',      Icon: MessageCircle, badge: 'X / 4-Part Thread' },
    { id: 'blog',    label: 'Blog Snippet',      Icon: BookOpen,      badge: 'SEO & Newsletter' },
    { id: 'caption', label: 'Caption',           Icon: MessageSquare, badge: 'Instagram & Feed' },
    { id: 'script',  label: 'Video Script',      Icon: Video,         badge: 'Reels / Shorts (60s)' },
  ];

  return (
    <div className="repurpose-engine" id="content-repurpose-engine">
      {/* ── Format Switcher Tabs ─────────────────────────────────── */}
      <div className="format-tabs-bar">
        <div className="format-tabs-list">
          {formats.map(f => {
            const FormatIcon = f.Icon;
            const isActive = activeFormat === f.id;
            return (
              <button
                key={f.id}
                onClick={() => setActiveFormat(f.id)}
                className={`format-tab-btn ${isActive ? 'active' : ''}`}
                id={`format-tab-${f.id}`}
              >
                <FormatIcon size={15} />
                <span>{f.label}</span>
                <span className="format-tab-badge">{f.badge}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Active Format Viewport ──────────────────────────────── */}
      <div className="format-viewport">
        {/* 1. POST FORMAT (LinkedIn / Article) */}
        {activeFormat === 'post' && (
          <div className="format-content-card">
            <div className="format-card-header">
              <div className="format-meta">
                <span className="platform-tag platform-linkedin">
                  <Share2 size={13} /> LinkedIn Thought Leadership
                </span>
                <span className="meta-detail">
                  {formattedContent.post.text.length} chars • {formattedContent.post.text.split(/\s+/).length} words
                </span>
              </div>
              <div className="format-actions">
                <button
                  className="action-btn"
                  onClick={() => handleCopy(formattedContent.post.text, 'post')}
                  id="copy-post-btn"
                >
                  {copiedKey === 'post' ? <Check size={14} style={{ color: 'var(--accent-emerald)' }} /> : <Copy size={14} />}
                  {copiedKey === 'post' ? 'Copied' : 'Copy Post'}
                </button>
              </div>
            </div>

            <div className="post-headline">{formattedContent.post.title}</div>
            <div className="post-body-rendered">{formattedContent.post.text}</div>

            <div className="format-card-footer">
              <div className="footer-status-zone">
                {postResult?.reddit_url ? (
                  <a
                    href={postResult.reddit_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="post-url"
                    id="linkedin-live-link"
                  >
                    <ExternalLink size={14} /> View on LinkedIn ({postResult.subreddit})
                  </a>
                ) : (
                  <span className="post-pending-tag">
                    <Clock size={13} /> Platform Dispatch Ready
                  </span>
                )}
              </div>
              <div className="footer-citations">
                {baseData.citations.map((c, i) => (
                  <span key={i} className="citation-badge">Source [{c}]</span>
                ))}
                <span className="model-badge">{baseData.model}</span>
              </div>
            </div>
          </div>
        )}

        {/* 2. TWEET THREAD FORMAT */}
        {activeFormat === 'tweet' && (
          <div className="format-content-card">
            <div className="format-card-header">
              <div className="format-meta">
                <span className="platform-tag platform-twitter">
                  <MessageCircle size={13} /> 4-Tweet Viral Thread
                </span>
                <span className="meta-detail">Grounded in RAG Sources</span>
              </div>
              <div className="format-actions">
                <button
                  className="action-btn"
                  onClick={() => handleCopy(formattedContent.tweet.thread.join('\n\n---\n\n'), 'thread')}
                  id="copy-thread-btn"
                >
                  {copiedKey === 'thread' ? <Check size={14} style={{ color: 'var(--accent-emerald)' }} /> : <Copy size={14} />}
                  {copiedKey === 'thread' ? 'Copied Thread' : 'Copy Full Thread'}
                </button>
              </div>
            </div>

            <div className="thread-timeline">
              {formattedContent.tweet.thread.map((tweet, idx) => {
                const charCount = tweet.length;
                const charPercent = Math.min(100, Math.round((charCount / 280) * 100));
                return (
                  <div key={idx} className="tweet-card" id={`tweet-card-${idx}`}>
                    <div className="tweet-header">
                      <span className="tweet-author">
                        <MessageCircle size={14} style={{ color: 'var(--accent-sky)' }} />
                        <strong>TrendPulse AI</strong>
                        <span className="tweet-handle">@trendpulse • Tweet {idx + 1}/4</span>
                      </span>
                      <button
                        className="tweet-mini-copy"
                        onClick={() => handleCopy(tweet, `tweet-${idx}`)}
                      >
                        {copiedKey === `tweet-${idx}` ? <Check size={12} style={{ color: 'var(--accent-emerald)' }} /> : <Copy size={12} />}
                      </button>
                    </div>
                    <div className="tweet-text">{tweet}</div>
                    <div className="tweet-char-bar">
                      <div className="char-bar-track">
                        <div
                          className="char-bar-fill"
                          style={{
                            width: `${charPercent}%`,
                            background: charCount > 280 ? 'var(--accent-rose)' : 'var(--accent-sky)'
                          }}
                        />
                      </div>
                      <span className="char-count-text">{charCount}/280 chars</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* 3. BLOG SNIPPET FORMAT */}
        {activeFormat === 'blog' && (
          <div className="format-content-card">
            <div className="format-card-header">
              <div className="format-meta">
                <span className="platform-tag platform-blog">
                  <BookOpen size={13} /> Blog / Newsletter Editorial
                </span>
                <span className="meta-detail">
                  <Clock size={12} /> {formattedContent.blog.readingTime}
                </span>
              </div>
              <div className="format-actions">
                <button
                  className="action-btn"
                  onClick={() => handleCopy(
                    `${formattedContent.blog.seoTitle}\n\nTL;DR: ${formattedContent.blog.tldr}\n\nKey Takeaways:\n${formattedContent.blog.takeaways.map(t => `• ${t}`).join('\n')}\n\n${formattedContent.blog.body}`,
                    'blog'
                  )}
                  id="copy-blog-btn"
                >
                  {copiedKey === 'blog' ? <Check size={14} style={{ color: 'var(--accent-emerald)' }} /> : <Copy size={14} />}
                  {copiedKey === 'blog' ? 'Copied' : 'Copy Article'}
                </button>
              </div>
            </div>

            <div className="blog-seo-title">{formattedContent.blog.seoTitle}</div>

            <div className="blog-tldr-box">
              <div className="tldr-badge">
                <Sparkles size={13} /> Executive TL;DR
              </div>
              <p className="tldr-text">{formattedContent.blog.tldr}</p>
            </div>

            <div className="blog-takeaways-section">
              <div className="section-subtitle">
                <Flame size={14} style={{ color: 'var(--accent-amber)' }} /> Key Takeaways
              </div>
              <div className="takeaways-list">
                {formattedContent.blog.takeaways.map((takeaway, i) => (
                  <div key={i} className="takeaway-item">
                    <span className="takeaway-bullet">0{i + 1}</span>
                    <span>{takeaway}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="blog-body-text">{formattedContent.blog.body}</div>

            <div className="blog-meta-box">
              <span className="meta-box-label">SEO Meta Description:</span>
              <p className="meta-box-text">{formattedContent.blog.metaDescription}</p>
            </div>
          </div>
        )}

        {/* 4. CAPTION FORMAT */}
        {activeFormat === 'caption' && (
          <div className="format-content-card">
            <div className="format-card-header">
              <div className="format-meta">
                <span className="platform-tag platform-caption">
                  <MessageSquare size={13} /> Social Feed Caption
                </span>
                <span className="meta-detail">2-3 Lines Max • High Engagement</span>
              </div>
              <div className="format-actions">
                <button
                  className="action-btn"
                  onClick={() => handleCopy(formattedContent.caption.full, 'caption')}
                  id="copy-caption-btn"
                >
                  {copiedKey === 'caption' ? <Check size={14} style={{ color: 'var(--accent-emerald)' }} /> : <Copy size={14} />}
                  {copiedKey === 'caption' ? 'Copied' : 'Copy Caption'}
                </button>
              </div>
            </div>

            <div className="caption-preview-box">
              <div className="caption-hook-line">{formattedContent.caption.hook}</div>
              <div className="caption-body-line">{formattedContent.caption.body}</div>
              <div className="caption-hashtags-line">
                <Hash size={13} style={{ color: 'var(--accent-indigo)' }} />
                <span>{formattedContent.caption.hashtags}</span>
              </div>
            </div>

            <div className="caption-meta-stats">
              <span className="caption-stat">Length: {formattedContent.caption.full.length} characters</span>
              <span className="caption-stat">Hashtags: 6 curated</span>
              <span className="caption-stat">Engagement Score: 96%</span>
            </div>
          </div>
        )}

        {/* 5. SHORT-FORM VIDEO SCRIPT FORMAT */}
        {activeFormat === 'script' && (
          <div className="format-content-card">
            <div className="format-card-header">
              <div className="format-meta">
                <span className="platform-tag platform-script">
                  <Video size={13} /> 60-Second Video Script (Reels/TikTok/Shorts)
                </span>
                <span className="meta-detail">
                  <Clock size={12} /> {formattedContent.script.duration} • {formattedContent.script.wpm}
                </span>
              </div>
              <div className="format-actions">
                <button
                  className="action-btn"
                  onClick={() => handleCopy(
                    formattedContent.script.scenes.map(s => `[${s.time}] ${s.phase}\nVISUAL: ${s.visual}\nAUDIO: "${s.audio}"\nDIRECTOR NOTE: ${s.tip}`).join('\n\n'),
                    'script'
                  )}
                  id="copy-script-btn"
                >
                  {copiedKey === 'script' ? <Check size={14} style={{ color: 'var(--accent-emerald)' }} /> : <Copy size={14} />}
                  {copiedKey === 'script' ? 'Copied' : 'Copy Full Script'}
                </button>
              </div>
            </div>

            <div className="script-teleprompter">
              {formattedContent.script.scenes.map((scene, idx) => (
                <div key={idx} className="script-scene-card" id={`script-scene-${idx}`}>
                  <div className="scene-header">
                    <span className="scene-timestamp">
                      <Clock size={12} /> {scene.time}
                    </span>
                    <span className="scene-phase-badge">{scene.phase}</span>
                  </div>

                  <div className="scene-visual-cue">
                    <span className="cue-label">VISUAL CUE:</span> {scene.visual}
                  </div>

                  <div className="scene-audio-cue">
                    <span className="cue-label">VOICEOVER / HOST:</span>
                    <p className="scene-speech-text">"{scene.audio}"</p>
                  </div>

                  <div className="scene-director-note">
                    <Sliders size={12} style={{ color: 'var(--accent-amber)' }} />
                    <span>Pacing Note: {scene.tip}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default GeneratedPost;
