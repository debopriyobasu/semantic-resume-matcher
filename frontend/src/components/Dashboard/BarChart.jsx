import { useApi } from '../../hooks/useApi';
import { usePolling } from '../../hooks/usePolling';
import { APP_CONFIG } from '../../config/theme';

export function BarChart({ label, endpoint, dataKey, description }) {
  const { data, loading, execute } = useApi(endpoint);

  usePolling(execute, APP_CONFIG.dashboardRefreshIntervalMs);

  const rawValues = data && dataKey ? data[dataKey] : {};
  const entries = Object.entries(rawValues).sort((a, b) => a[0].localeCompare(b[0]));
  const maxCount = Math.max(...entries.map(e => e[1]), 1); // Avoid division by zero
  const total = entries.reduce((sum, e) => sum + e[1], 0);

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
      <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', tracking: '0.05em', color: 'var(--text-muted)' }}>
        {label}
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', flex: 1, justifyContent: 'center' }}>
        {loading && !data ? (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', py: 2 }}>Loading...</div>
        ) : total === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', py: 2 }}>No metrics computed yet. Matches are required to view distribution.</div>
        ) : (
          entries.map(([bucket, count]) => {
            const percentage = (count / maxCount) * 100;
            const absolutePercent = total > 0 ? Math.round((count / total) * 100) : 0;
            return (
              <div key={bucket} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                  <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
                    Confidence Level: {bucket}
                  </span>
                  <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>
                    {count} ({absolutePercent}%)
                  </span>
                </div>
                {/* Custom bar background and filling */}
                <div style={{
                  height: '8px',
                  width: '100%',
                  backgroundColor: 'rgba(255,255,255,0.03)',
                  borderRadius: '999px',
                  overflow: 'hidden',
                  border: '1px solid rgba(255,255,255,0.05)'
                }}>
                  <div style={{
                    height: '100%',
                    width: `${percentage}%`,
                    background: 'linear-gradient(90deg, var(--color-primary), var(--color-secondary))',
                    borderRadius: '999px',
                    transition: 'width 1s cubic-bezier(0.4, 0, 0.2, 1)'
                  }} />
                </div>
              </div>
            );
          })
        )}
      </div>

      {description && <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{description}</p>}
    </div>
  );
}

export default BarChart;
