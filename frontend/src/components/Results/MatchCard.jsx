import { useState } from 'react';
import { ChevronDown, ChevronUp, MapPin, DollarSign, Globe, Shield, Award, AlertCircle } from 'lucide-react';
import { ProgressRing } from '../Dashboard/ProgressRing';

const CATEGORY_STYLES = {
  'STRONG_MATCH': { className: 'chip chip-success', label: 'Strong Match' },
  'POTENTIAL_MATCH': { className: 'chip chip-warning', label: 'Potential Match' },
  'WEAK_MATCH': { className: 'chip chip-danger', label: 'Weak Match' },
  'REJECTED': { className: 'chip chip-muted', label: 'Rejected Match' }
};

export function MatchCard({ match }) {
  const [expanded, setExpanded] = useState(false);

  const { job, vector_score, confidence, match_category, reasoning, skill_gaps, standout_strengths } = match;

  const categoryStyle = CATEGORY_STYLES[match_category] || { className: 'chip chip-muted', label: match_category };
  const isRejected = match_category === 'REJECTED';

  // Format currency/salary helper
  const formatSalary = (min, max) => {
    if (!min && !max) return 'Not Specified';
    if (min && max) return `$${(min / 1000).toFixed(0)}k - $${(max / 1000).toFixed(0)}k`;
    if (min) return `From $${(min / 1000).toFixed(0)}k`;
    return `Up to $${(max / 1000).toFixed(0)}k`;
  };

  return (
    <div 
      className="glass-card glass-card-interactive" 
      style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '1rem',
        opacity: isRejected ? 0.65 : 1,
        borderLeft: isRejected ? '4px solid var(--text-muted)' : `4px solid ${match_category === 'STRONG_MATCH' ? 'var(--color-success)' : match_category === 'POTENTIAL_MATCH' ? 'var(--color-warning)' : 'var(--color-error)'}`
      }}
    >
      <div 
        onClick={() => setExpanded(!expanded)}
        style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          cursor: 'pointer',
          flexWrap: 'wrap',
          gap: '1rem'
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', flex: 1, minWidth: '250px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <h3 style={{ 
              fontSize: '1.2rem', 
              fontWeight: 600,
              textDecoration: isRejected ? 'line-through' : 'none'
            }}>
              {job.title}
            </h3>
            <span className={categoryStyle.className}>{categoryStyle.label}</span>
          </div>

          <span style={{ fontSize: '0.95rem', color: 'var(--color-secondary)', fontWeight: 500 }}>
            {job.company}
          </span>

          {/* Job Specifications Row */}
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '0.25rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {job.location && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <MapPin size={12} />
                {job.location}
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <DollarSign size={12} />
              {formatSalary(job.min_salary, job.max_salary)}
            </div>
            {job.remote_ok && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <Globe size={12} />
                Remote Friendly
              </div>
            )}
            {job.visa_sponsorship && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <Shield size={12} />
                Visa Sponsorship
              </div>
            )}
          </div>
        </div>

        {/* Scoring & Controls Column */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          {/* Circular vector score progress ring */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <ProgressRing 
              value={vector_score * 100} 
              size={65} 
              strokeWidth={5} 
              showCard={false} 
            />
            <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.15rem', textTransform: 'uppercase', fontWeight: 600 }}>Vector Match</span>
          </div>

          {/* Confidence Indicator */}
          {confidence !== undefined && confidence !== null && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div style={{
                width: '45px',
                height: '45px',
                borderRadius: '50%',
                backgroundColor: 'rgba(255,255,255,0.03)',
                border: '1.5px solid var(--border-color)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.85rem',
                fontWeight: 700,
                color: confidence >= 0.7 ? 'var(--color-success)' : confidence >= 0.4 ? 'var(--color-warning)' : 'var(--color-error)'
              }}>
                {Math.round(confidence * 100)}%
              </div>
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.35rem', textTransform: 'uppercase', fontWeight: 600 }}>AI Confidence</span>
            </div>
          )}

          {/* Collapse toggle button */}
          <div style={{ color: 'var(--text-muted)' }}>
            {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>
        </div>
      </div>

      {/* Expanded reasoning details section */}
      {expanded && (
        <div style={{ 
          borderTop: '1px solid var(--border-color)', 
          paddingTop: '1rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
          animation: 'fadeIn var(--transition-fast)'
        }}>
          {reasoning && (
            <div>
              <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.3rem', fontWeight: 600 }}>AI Match Analysis</span>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{reasoning}</p>
            </div>
          )}

          {/* Standout Strengths & Skill Gaps Grid */}
          {!isRejected && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '0.25rem' }}>
              {/* Standout Strengths */}
              {standout_strengths && standout_strengths.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.75rem', color: 'var(--color-success)', textTransform: 'uppercase', fontWeight: 600 }}>
                    <Award size={14} />
                    Standout Strengths
                  </span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {standout_strengths.map((str, i) => (
                      <span key={i} className="chip chip-success" style={{ fontSize: '0.75rem' }}>{str}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Skill Gaps */}
              {skill_gaps && skill_gaps.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.75rem', color: 'var(--color-error)', textTransform: 'uppercase', fontWeight: 600 }}>
                    <AlertCircle size={14} />
                    Identified Skill Gaps
                  </span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
                    {skill_gaps.map((str, i) => (
                      <span key={i} className="chip chip-danger" style={{ fontSize: '0.75rem' }}>{str}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default MatchCard;
