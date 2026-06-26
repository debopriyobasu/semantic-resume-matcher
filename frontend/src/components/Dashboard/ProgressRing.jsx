import { useApi } from '../../hooks/useApi';
import { usePolling } from '../../hooks/usePolling';
import { APP_CONFIG } from '../../config/theme';

export function ProgressRing({ 
  value: staticValue, 
  endpoint, 
  label, 
  description, 
  size = 120, 
  strokeWidth = 10,
  showCard = true
}) {
  let percent = 0;
  let subLabel = '';
  let isLoading = false;

  const { data, execute } = useApi(endpoint, {}, !endpoint);

  usePolling(execute, APP_CONFIG.dashboardRefreshIntervalMs, !!endpoint && (!data || !data.embedding_completed));

  if (staticValue !== undefined) {
    percent = Math.round(staticValue);
    subLabel = `${percent}% Match`;
  } else if (data) {
    const total = data.total_jobs || 0;
    const missing = data.jobs_without_embeddings || 0;
    percent = total > 0 ? Math.round(((total - missing) / total) * 100) : (data.embedding_completed ? 100 : 0);
    subLabel = `${total - missing}/${total} Embedded`;
  } else if (endpoint) {
    isLoading = true;
  }

  // SVG Circle Calculations
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percent / 100) * circumference;

  const content = (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', height: '100%' }}>
      {label && (
        <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', tracking: '0.05em', color: 'var(--text-muted)' }}>
          {label}
        </h3>
      )}

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '2rem', flex: 1, padding: '0.5rem 0' }}>
        <div style={{ position: 'relative', width: size, height: size }}>
          {/* Animated SVG Ring */}
          <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
            {/* Background Ring */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="transparent"
              stroke="rgba(255, 255, 255, 0.05)"
              strokeWidth={strokeWidth}
            />
            {/* Foreground Ring */}
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="transparent"
              stroke="url(#progressGradient)"
              strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              style={{
                transition: 'stroke-dashoffset 1s ease-in-out',
              }}
            />
            {/* Gradient definition */}
            <defs>
              <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="var(--color-primary)" />
                <stop offset="100%" stopColor="var(--color-secondary)" />
              </linearGradient>
            </defs>
          </svg>
          {/* Central Percent Text */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.25rem',
            fontWeight: 700,
            color: 'var(--text-main)'
          }}>
            {isLoading ? '...' : `${percent}%`}
          </div>
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.25rem' }}>
            {isLoading ? 'Loading...' : percent === 100 ? 'Fully Processed' : 'Processing vectors...'}
          </div>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            {isLoading ? 'Fetching database status' : subLabel}
          </span>
        </div>
      </div>

      {description && <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{description}</p>}
    </div>
  );

  return showCard ? <div className="glass-card">{content}</div> : content;
}

export default ProgressRing;
