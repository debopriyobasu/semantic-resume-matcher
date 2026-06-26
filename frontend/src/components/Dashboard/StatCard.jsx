import { useApi } from '../../hooks/useApi';
import { usePolling } from '../../hooks/usePolling';
import { Icon } from '../Layout/Sidebar';
import { APP_CONFIG } from '../../config/theme';

export function StatCard({ label, endpoint, dataKey, iconName, description }) {
  const { data, loading, execute } = useApi(endpoint);

  usePolling(execute, APP_CONFIG.dashboardRefreshIntervalMs);

  const value = data && dataKey ? data[dataKey] : 0;

  return (
    <div className="glass-card glass-card-interactive" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', tracking: '0.05em', color: 'var(--text-muted)' }}>
          {label}
        </h3>
        {iconName && (
          <div style={{ color: 'var(--color-secondary)', opacity: 0.8 }}>
            <Icon name={iconName} size={22} />
          </div>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', flex: 1, justifyContent: 'center' }}>
        <div style={{ fontSize: '2.5rem', fontWeight: 700, background: 'linear-gradient(135deg, #fff 30%, var(--text-muted) 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          {loading && !data ? '...' : value.toLocaleString()}
        </div>
        {description && <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{description}</span>}
      </div>
    </div>
  );
}

export default StatCard;
