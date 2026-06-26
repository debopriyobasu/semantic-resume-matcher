import { useApi } from '../../hooks/useApi';
import { usePolling } from '../../hooks/usePolling';
import { APP_CONFIG } from '../../config/theme';

const SEGMENT_COLORS = {
  // Pipeline status colors
  'COMPLETE': 'var(--color-success)',
  'PENDING': 'var(--color-warning)',
  'FAILED': 'var(--color-error)',
  
  // Match category colors
  'STRONG_MATCH': 'var(--color-success)',
  'POTENTIAL_MATCH': 'var(--color-warning)',
  'WEAK_MATCH': 'var(--color-error)',
  'REJECTED': 'rgba(255, 255, 255, 0.25)',
};

const LABEL_MAPPING = {
  'COMPLETE': 'Complete',
  'PENDING': 'Pending',
  'FAILED': 'Failed',
  'STRONG_MATCH': 'Strong Match',
  'POTENTIAL_MATCH': 'Potential Match',
  'WEAK_MATCH': 'Weak Match',
  'REJECTED': 'Rejected',
};

export function DonutChart({ label, endpoint, dataKey, description }) {
  const { data, loading, execute } = useApi(endpoint);

  usePolling(execute, APP_CONFIG.dashboardRefreshIntervalMs);

  const rawValues = data && dataKey ? data[dataKey] : {};
  
  // Filter out zero entries
  const segments = Object.entries(rawValues)
    .map(([key, value]) => ({ key, value }))
    .filter(item => item.value > 0);

  const total = segments.reduce((sum, item) => sum + item.value, 0);

  // SVG calculations
  const size = 150;
  const strokeWidth = 18;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;

  let accumulatedPercent = 0;

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
      <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', tracking: '0.05em', color: 'var(--text-muted)' }}>
        {label}
      </h3>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1.5rem', flex: 1, padding: '0.5rem 0' }}>
        {loading && !data ? (
          <div style={{ width: size, height: size, borderRadius: '50%', border: '4px dashed rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            Loading...
          </div>
        ) : total === 0 ? (
          <div style={{ width: size, height: size, borderRadius: '50%', border: '4px dashed rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            No Data
          </div>
        ) : (
          <div style={{ position: 'relative', width: size, height: size }}>
            <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
              {segments.map((segment) => {
                const percent = (segment.value / total) * 100;
                const offset = circumference - (percent / 100) * circumference;
                const rotation = (accumulatedPercent / 100) * 360;
                accumulatedPercent += percent;

                const color = SEGMENT_COLORS[segment.key] || 'var(--color-primary)';

                return (
                  <circle
                    key={segment.key}
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="transparent"
                    stroke={color}
                    strokeWidth={strokeWidth}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    transform={`rotate(${rotation} ${size / 2} ${size / 2})`}
                    style={{
                      transition: 'stroke-dashoffset 0.8s ease-in-out',
                    }}
                  />
                );
              })}
            </svg>
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
            }}>
              <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>{total}</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total</span>
            </div>
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', flex: 1 }}>
          {segments.map((segment) => {
            const color = SEGMENT_COLORS[segment.key] || 'var(--color-primary)';
            const labelText = LABEL_MAPPING[segment.key] || segment.key;
            return (
              <div key={segment.key} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '30%', backgroundColor: color }}></span>
                <span style={{ color: 'var(--text-secondary)', flex: 1 }}>{labelText}</span>
                <span style={{ fontWeight: 600 }}>{segment.value}</span>
              </div>
            );
          })}
          {segments.length === 0 && (
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Waiting for records...</div>
          )}
        </div>
      </div>

      {description && <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{description}</p>}
    </div>
  );
}

export default DonutChart;
