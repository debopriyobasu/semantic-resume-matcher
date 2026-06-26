import { useState, useEffect } from 'react';
import PageShell from '../components/Layout/PageShell';
import CandidateHeader from '../components/Results/CandidateHeader';
import MatchCard from '../components/Results/MatchCard';
import { ENDPOINTS } from '../config/endpoints';
import { Search, Loader2, Sparkles, Filter, ArrowUpDown } from 'lucide-react';

export function ResultsPage({ activeCandidateId, setActiveCandidateId }) {
  const [searchId, setSearchId] = useState(activeCandidateId || '');
  const [candidateProfile, setCandidateProfile] = useState(null);
  const [matches, setMatches] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Filter & Sort state
  const [filterCategory, setFilterCategory] = useState('ALL'); // 'ALL' | 'STRONG_MATCH' | 'POTENTIAL_MATCH' | 'WEAK_MATCH' | 'REJECTED'
  const [sortBy, setSortBy] = useState('confidence'); // 'confidence' | 'score'

  const fetchCandidateAndMatches = async (id) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch Candidate status/profile
      const candidateRes = await fetch(ENDPOINTS.candidateStatus(id));
      if (!candidateRes.ok) {
        throw new Error('Candidate records not found. Ensure the ID is valid.');
      }
      const candidateData = await candidateRes.json();
      setCandidateProfile(candidateData.profile);

      // 2. Fetch matches
      const matchesRes = await fetch(ENDPOINTS.candidateMatches(id));
      if (!matchesRes.ok) {
        throw new Error('Failed to retrieve matches data.');
      }
      const matchesData = await matchesRes.json();
      setMatches(matchesData.matches || []);
      setSearchId(id);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Error occurred during data retrieval.');
      setCandidateProfile(null);
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  // Fetch results when activeCandidateId changes
  useEffect(() => {
    if (activeCandidateId) {
      fetchCandidateAndMatches(activeCandidateId);
    } else {
      setCandidateProfile(null);
      setMatches([]);
    }
  }, [activeCandidateId]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!searchId.trim()) return;
    setActiveCandidateId(searchId.trim());
  };

  // Perform filtering & sorting on local state
  const filteredMatches = matches
    .filter(m => filterCategory === 'ALL' || m.match_category === filterCategory)
    .sort((a, b) => {
      if (sortBy === 'confidence') {
        const confA = a.confidence !== null ? a.confidence : 0;
        const confB = b.confidence !== null ? b.confidence : 0;
        if (confA !== confB) return confB - confA;
      }
      return b.vector_score - a.vector_score;
    });

  return (
    <PageShell
      title="Candidate Match Results"
      description="Inspect extracted profiles and examine ranked job openings calculated using vector indices and LLM reasoning."
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {/* Candidate Search / Lookup ID bar */}
        <form onSubmit={handleSearchSubmit} className="glass-card" style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Paste candidate UUID to load analysis..."
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              className="form-input"
              style={{ width: '100%', paddingLeft: '2.75rem' }}
            />
          </div>
          <button type="submit" className="btn-primary" style={{ flexShrink: 0 }}>
            Load Analysis
          </button>
        </form>

        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px', flexDirection: 'column', gap: '1rem' }}>
            <Loader2 size={36} className="animate-spin" style={{ animation: 'spin 1.5s linear infinite', color: 'var(--color-primary)' }} />
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Evaluating candidate profile matching records...</span>
          </div>
        ) : error ? (
          <div className="glass-card" style={{ border: '1px solid rgba(239, 68, 68, 0.2)', backgroundColor: 'rgba(239, 68, 68, 0.02)', textAlign: 'center', padding: '2.5rem' }}>
            <span style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--color-error)' }}>Lookup Failed</span>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.5rem' }}>{error}</p>
          </div>
        ) : !candidateProfile ? (
          <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-muted)' }}>
            <Sparkles size={40} style={{ margin: '0 auto 1.5rem', color: 'var(--color-secondary)' }} />
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>No Candidate Loaded</h3>
            <p style={{ maxWidth: '400px', margin: '0 auto', fontSize: '0.9rem' }}>
              Upload a resume PDF or enter a previously parsed candidate UUID to view ranked match results.
            </p>
          </div>
        ) : (
          <div className="animate-fade" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            {/* Extracted Profile Details Card */}
            <CandidateHeader profile={candidateProfile} />

            {/* Results Filter & Sort bar */}
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              flexWrap: 'wrap', 
              gap: '1rem',
              borderBottom: '1px solid var(--border-color)',
              paddingBottom: '0.75rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Filter size={16} style={{ color: 'var(--text-muted)' }} />
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginRight: '0.5rem' }}>Filter Category:</span>
                <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                  {['ALL', 'STRONG_MATCH', 'POTENTIAL_MATCH', 'WEAK_MATCH', 'REJECTED'].map((cat) => (
                    <button
                      key={cat}
                      onClick={() => setFilterCategory(cat)}
                      style={{
                        padding: '0.3rem 0.7rem',
                        borderRadius: '6px',
                        border: '1px solid var(--border-color)',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        backgroundColor: filterCategory === cat ? 'var(--color-primary)' : 'rgba(255, 255, 255, 0.02)',
                        color: filterCategory === cat ? 'white' : 'var(--text-secondary)',
                        transition: 'all var(--transition-fast)'
                      }}
                    >
                      {cat === 'ALL' ? 'All Matches' : cat.replace('_', ' ')}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ArrowUpDown size={16} style={{ color: 'var(--text-muted)' }} />
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginRight: '0.5rem' }}>Sort By:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  style={{
                    backgroundColor: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                    padding: '0.35rem 1rem',
                    borderRadius: '6px',
                    fontSize: '0.8rem',
                    fontWeight: 500,
                    outline: 'none',
                    cursor: 'pointer'
                  }}
                >
                  <option value="confidence">AI Confidence Level</option>
                  <option value="score">Vector Similarity Score</option>
                </select>
              </div>
            </div>

            {/* List of matched cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {filteredMatches.length > 0 ? (
                filteredMatches.map((match) => (
                  <MatchCard key={match.match_id} match={match} />
                ))
              ) : (
                <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                  No match results fit the selected filter category.
                </div>
              )}
            </div>

          </div>
        )}

      </div>
    </PageShell>
  );
}

export default ResultsPage;
