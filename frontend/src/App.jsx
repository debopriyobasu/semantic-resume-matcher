import { useState, useEffect } from 'react';
import Sidebar from './components/Layout/Sidebar';
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import ResultsPage from './pages/ResultsPage';
import JobsPage from './pages/JobsPage';

// Simple Hash-based routing utility
const parseHash = () => {
  const hash = window.location.hash || '#/';
  if (hash.startsWith('#/results')) {
    const parts = hash.split('/');
    // Check format: #/results/UUID
    const candidateId = parts[2] || null;
    return { tab: 'results', candidateId };
  }
  if (hash === '#/upload') return { tab: 'upload-resume', candidateId: null };
  if (hash === '#/jobs') return { tab: 'manage-jobs', candidateId: null };
  return { tab: 'dashboard', candidateId: null };
};

const updateHash = (tab, candidateId = null) => {
  if (tab === 'results') {
    window.location.hash = candidateId ? `#/results/${candidateId}` : `#/results`;
  } else if (tab === 'upload-resume') {
    window.location.hash = `#/upload`;
  } else if (tab === 'manage-jobs') {
    window.location.hash = `#/jobs`;
  } else {
    window.location.hash = `#/`;
  }
};

export function App() {
  const [currentRoute, setCurrentRoute] = useState(parseHash());
  const [activeCandidateId, setActiveCandidateId] = useState(null);

  // Sync hash routing on popstate / hashchange
  useEffect(() => {
    const handleHashChange = () => {
      const route = parseHash();
      setCurrentRoute(route);
      if (route.candidateId) {
        setActiveCandidateId(route.candidateId);
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    // Initial check
    handleHashChange();

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleTabChange = (tabId) => {
    // If navigating to results, pass current activeCandidateId if any
    const cId = tabId === 'results' ? activeCandidateId : null;
    updateHash(tabId, cId);
  };

  const handleNavigateToResults = (candidateId) => {
    setActiveCandidateId(candidateId);
    updateHash('results', candidateId);
  };

  const handleUpdateActiveCandidateId = (candidateId) => {
    setActiveCandidateId(candidateId);
    // Update hash silently if it's already results
    if (currentRoute.tab === 'results') {
      updateHash('results', candidateId);
    }
  };

  const renderContent = () => {
    switch (currentRoute.tab) {
      case 'dashboard':
        return <DashboardPage />;
      case 'upload-resume':
        return <UploadPage onNavigateToResults={handleNavigateToResults} />;
      case 'results':
        return (
          <ResultsPage 
            activeCandidateId={activeCandidateId} 
            setActiveCandidateId={handleUpdateActiveCandidateId} 
          />
        );
      case 'manage-jobs':
        return <JobsPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar 
        currentTab={currentRoute.tab} 
        onTabChange={handleTabChange} 
      />
      <div className="main-content">
        {renderContent()}
      </div>
    </div>
  );
}

export default App;
