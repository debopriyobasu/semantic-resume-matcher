import * as Icons from 'lucide-react';
import { NAV_ITEMS } from '../../config/navigation';
import { APP_CONFIG } from '../../config/theme';

// Dynamic Icon Component
export function Icon({ name, className, size = 20 }) {
  const LucideIcon = Icons[name];
  if (!LucideIcon) return null;
  return <LucideIcon className={className} size={size} />;
}

export function Sidebar({ currentTab, onTabChange }) {
  return (
    <aside className="sidebar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2.5rem' }}>
        <div style={{
          background: 'linear-gradient(135deg, hsl(245, 85%, 65%), hsl(185, 80%, 55%))',
          width: '40px',
          height: '40px',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 15px rgba(99, 102, 241, 0.4)'
        }}>
          <Icons.Cpu size={22} color="white" />
        </div>
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, letterSpacing: '-0.02em', background: 'linear-gradient(135deg, #fff 40%, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            {APP_CONFIG.name}
          </h2>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 500 }}>
            v{APP_CONFIG.version} (Local)
          </span>
        </div>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
        {NAV_ITEMS.map((item) => {
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.85rem',
                width: '100%',
                padding: '0.85rem 1rem',
                border: 'none',
                borderRadius: '12px',
                background: isActive ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                color: isActive ? 'var(--text-main)' : 'var(--text-secondary)',
                borderLeft: isActive ? '3px solid var(--color-primary)' : '3px solid transparent',
                fontSize: '0.95rem',
                fontWeight: isActive ? 600 : 500,
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'background var(--transition-fast), color var(--transition-fast)'
              }}
              className={!isActive ? "glass-card-interactive" : ""}
            >
              <Icon 
                name={item.iconName} 
                className={isActive ? 'text-primary' : ''} 
                style={{ color: isActive ? 'var(--color-primary)' : 'inherit' }}
              />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div style={{ 
        borderTop: '1px solid var(--border-color)', 
        paddingTop: '1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--color-success)', boxShadow: '0 0 10px var(--color-success)' }}></div>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Offline Engine Ready</span>
      </div>
    </aside>
  );
}
export default Sidebar;
