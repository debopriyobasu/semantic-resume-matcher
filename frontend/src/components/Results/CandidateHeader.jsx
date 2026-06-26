import { User, Mail, Calendar, GraduationCap, MapPin } from 'lucide-react';

export function CandidateHeader({ profile }) {
  if (!profile) return null;

  const { name, email, skills, experience_years, education, location } = profile;

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            width: '54px',
            height: '54px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            boxShadow: '0 4px 15px rgba(99, 102, 241, 0.2)'
          }}>
            <User size={26} />
          </div>
          <div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 700 }}>{name || 'Unknown Candidate'}</h2>
            {email && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.15rem' }}>
                <Mail size={14} />
                <a href={`mailto:${email}`} style={{ color: 'inherit', textDecoration: 'none' }} className="hover:underline">{email}</a>
              </div>
            )}
          </div>
        </div>

        {/* Experience & Education Highlights */}
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
          {experience_years !== undefined && experience_years !== null && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
              <Calendar size={18} style={{ color: 'var(--color-secondary)' }} />
              <div>
                <span style={{ display: 'block', fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Experience</span>
                <span style={{ fontWeight: 600 }}>{experience_years} Years</span>
              </div>
            </div>
          )}

          {location && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
              <MapPin size={18} style={{ color: 'var(--color-primary)' }} />
              <div>
                <span style={{ display: 'block', fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Location</span>
                <span style={{ fontWeight: 600 }}>{location}</span>
              </div>
            </div>
          )}

          {education && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
              <GraduationCap size={18} style={{ color: 'var(--color-success)' }} />
              <div>
                <span style={{ display: 'block', fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Education</span>
                <span style={{ fontWeight: 600, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'inline-block' }} title={education}>{education}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Skills Chips */}
      {skills && skills.length > 0 && (
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
          <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem', fontWeight: 600 }}>Extracted Core Skills</span>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {skills.map((skill, i) => (
              <span key={i} className="chip chip-primary">{skill}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default CandidateHeader;
