import { RESUME_UPLOAD_FIELDS } from '../../config/forms';

export function DynamicForm({ formData, setFormData }) {
  const handleInputChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
        Deterministic Filters & Preferences
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
        {RESUME_UPLOAD_FIELDS.map((field) => {
          const value = formData[field.name] !== undefined ? formData[field.name] : field.defaultValue;

          if (field.type === 'toggle') {
            return (
              <div key={field.name} style={{ display: 'flex', flexDirection: 'column', justify: 'space-between', gap: '0.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="form-label">{field.label}</span>
                  {/* Custom Toggle Switch */}
                  <button
                    type="button"
                    onClick={() => handleInputChange(field.name, !value)}
                    style={{
                      width: '46px',
                      height: '24px',
                      borderRadius: '999px',
                      backgroundColor: value ? 'var(--color-primary)' : 'rgba(255, 255, 255, 0.1)',
                      border: 'none',
                      position: 'relative',
                      cursor: 'pointer',
                      transition: 'background-color var(--transition-fast)'
                    }}
                  >
                    <div style={{
                      width: '18px',
                      height: '18px',
                      borderRadius: '50%',
                      backgroundColor: 'white',
                      position: 'absolute',
                      top: '3px',
                      left: value ? '25px' : '3px',
                      transition: 'left var(--transition-fast)'
                    }} />
                  </button>
                </div>
                {field.helpText && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{field.helpText}</span>}
              </div>
            );
          }

          return (
            <div key={field.name} className="form-group">
              <label className="form-label" htmlFor={field.name}>{field.label}</label>
              <input
                id={field.name}
                type={field.type}
                placeholder={field.placeholder}
                value={value || ''}
                onChange={(e) => handleInputChange(field.name, field.type === 'number' ? (e.target.value ? parseInt(e.target.value, 10) : null) : e.target.value)}
                className="form-input"
              />
              {field.helpText && <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{field.helpText}</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default DynamicForm;
