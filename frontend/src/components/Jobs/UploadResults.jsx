import { Plus, RefreshCw, Trash2, Cpu } from 'lucide-react';

export function UploadResults({ result }) {
  if (!result) return null;

  const { added_count, updated_count, deleted_count, embedding_completed } = result;

  return (
    <div className="glass-card animate-fade" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Cpu size={20} color="var(--color-primary)" />
        Import Execution Complete
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '1rem' }}>
        {/* Added */}
        <div style={{
          padding: '1rem',
          borderRadius: '10px',
          background: 'rgba(16, 185, 129, 0.03)',
          border: '1px solid rgba(16, 185, 129, 0.1)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '0.25rem'
        }}>
          <Plus size={20} color="var(--color-success)" />
          <span style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-success)' }}>{added_count}</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Added</span>
        </div>

        {/* Updated */}
        <div style={{
          padding: '1rem',
          borderRadius: '10px',
          background: 'rgba(245, 158, 11, 0.03)',
          border: '1px solid rgba(245, 158, 11, 0.1)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '0.25rem'
        }}>
          <RefreshCw size={18} color="var(--color-warning)" style={{ margin: '1px 0' }} />
          <span style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-warning)' }}>{updated_count}</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Updated</span>
        </div>

        {/* Deleted */}
        <div style={{
          padding: '1rem',
          borderRadius: '10px',
          background: 'rgba(239, 68, 68, 0.03)',
          border: '1px solid rgba(239, 68, 68, 0.1)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '0.25rem'
        }}>
          <Trash2 size={18} color="var(--color-error)" style={{ margin: '1px 0' }} />
          <span style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-error)' }}>{deleted_count}</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Deleted</span>
        </div>
      </div>

      {!embedding_completed && (
        <div style={{
          fontSize: '0.85rem',
          color: 'var(--text-secondary)',
          background: 'rgba(255, 255, 255, 0.02)',
          padding: '0.75rem 1rem',
          borderRadius: '8px',
          border: '1px solid var(--border-color)',
          textAlign: 'center'
        }}>
          ⚠️ Asynchronous embedding indexing has been triggered. Ollama is generating vector representations in the background. Check the status indicator below.
        </div>
      )}
    </div>
  );
}

export default UploadResults;
