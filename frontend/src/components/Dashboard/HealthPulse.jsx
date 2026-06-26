import { useApi } from '../../hooks/useApi';
import { usePolling } from '../../hooks/usePolling';
import { ENDPOINTS } from '../../config/endpoints';

export function HealthPulse({ label, description }) {
  const { data, loading, error, execute } = useApi(ENDPOINTS.health);
  
  // Poll health every 10 seconds
  usePolling(execute, 10000);

  const isHealthy = data && data.status === 'ok';

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
      <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', tracking: '0.05em', color: 'var(--text-muted)' }}>
        {label}
      </h3>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1 }}>
        <div style={{
          width: '16px',
          height: '16px',
          borderRadius: '50%',
          backgroundColor: isHealthy ? 'var(--color-success)' : 'var(--color-error)',
          animation: 'pulseGlow 2s infinite',
          '--glow-color': isHealthy ? 'var(--color-success)' : 'var(--color-error)'
        } } />
        
        <div>
          <div style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)' }}>
            {loading && !data ? 'Checking...' : isHealthy ? 'Connected' : 'Offline'}
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {isHealthy ? 'FastAPI & Postgres Active' : error || 'Unable to connect to local backend'}
          </span>
        </div>
      </div>
      
      {description && <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{description}</p>}
    </div>
  );
}

export default HealthPulse;
