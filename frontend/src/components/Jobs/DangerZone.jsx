import { useState } from 'react';
import { Trash2, AlertTriangle, Loader2 } from 'lucide-react';
import { ENDPOINTS } from '../../config/endpoints';

export function DangerZone({ onDeleteComplete }) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleDelete = async () => {
    if (confirmText.toLowerCase() !== 'delete') return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(ENDPOINTS.deleteJobs, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Failed to delete database: ${response.statusText}`);
      }

      const json = await response.json();
      onDeleteComplete(json);
      setShowConfirm(false);
      setConfirmText('');
    } catch (err) {
      console.error(err);
      setError(err.message || 'Error deleting dataset');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card" style={{ border: '1px solid rgba(239, 68, 68, 0.2)', backgroundColor: 'rgba(239, 68, 68, 0.02)' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '10px',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--color-error)'
        }}>
          <AlertTriangle size={22} />
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>Danger Zone</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Delete all job postings and associated vector embeddings from the database. Due to cascade delete rules, this will also purge candidate matches.
          </p>

          {!showConfirm ? (
            <button
              onClick={() => setShowConfirm(true)}
              className="btn-secondary"
              style={{
                marginTop: '1.25rem',
                borderColor: 'rgba(239, 68, 68, 0.3)',
                color: 'var(--color-error)',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <Trash2 size={16} />
              Reset Jobs Catalog Database
            </button>
          ) : (
            <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', maxWidth: '350px' }}>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Type <strong style={{ color: 'var(--text-main)' }}>DELETE</strong> to confirm:
              </label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="text"
                  placeholder="Type delete"
                  value={confirmText}
                  onChange={(e) => setConfirmText(e.target.value)}
                  disabled={loading}
                  className="form-input"
                  style={{ flex: 1, borderColor: confirmText.toLowerCase() === 'delete' ? 'var(--color-error)' : 'var(--border-color)' }}
                />
                <button
                  onClick={handleDelete}
                  disabled={confirmText.toLowerCase() !== 'delete' || loading}
                  className="btn-primary"
                  style={{
                    background: 'linear-gradient(135deg, var(--color-error), #ef4444)',
                    padding: '0.75rem 1.25rem'
                  }}
                >
                  {loading ? (
                    <Loader2 size={16} style={{ animation: 'spin 1.5s linear infinite' }} />
                  ) : (
                    'Confirm'
                  )}
                </button>
                <button
                  onClick={() => { setShowConfirm(false); setConfirmText(''); setError(null); }}
                  disabled={loading}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>

              {error && (
                <span style={{ fontSize: '0.8rem', color: 'var(--color-error)' }}>{error}</span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DangerZone;
