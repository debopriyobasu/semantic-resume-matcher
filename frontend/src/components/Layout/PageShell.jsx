export function PageShell({ title, description, children, action }) {
  return (
    <div className="animate-fade" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'flex-start',
        borderBottom: '1px solid var(--border-color)',
        paddingBottom: '1.5rem'
      }}>
        <div>
          <h1>{title}</h1>
          {description && <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>{description}</p>}
        </div>
        {action && <div>{action}</div>}
      </header>
      
      <main style={{ minHeight: '400px' }}>
        {children}
      </main>
    </div>
  );
}

export default PageShell;
