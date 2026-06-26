import { useState } from 'react';
import PageShell from '../components/Layout/PageShell';
import CsvUpload from '../components/Jobs/CsvUpload';
import UploadResults from '../components/Jobs/UploadResults';
import ProgressRing from '../components/Dashboard/ProgressRing';
import DangerZone from '../components/Jobs/DangerZone';
import { Copy, Check } from 'lucide-react';
import { ENDPOINTS } from '../config/endpoints';

const CSV_TEMPLATE_HEADERS = "title,company,location,remote_ok,visa_sponsorship,min_salary,max_salary,required_skills,description\nAssociate Backend Engineer,Northstar Labs,\"San Francisco, CA\",true,true,120000,160000,Python;FastAPI;SQLAlchemy;PostgreSQL,\"We are looking for a backend engineer...\"";

export function JobsPage() {
  const [uploadResult, setUploadResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [deleteMsg, setDeleteMsg] = useState(null);
  const [error, setError] = useState(null);

  const handleCopyTemplate = () => {
    navigator.clipboard.writeText(CSV_TEMPLATE_HEADERS);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleUploadComplete = (data) => {
    setUploadResult(data);
    setDeleteMsg(null);
  };

  const handleDeleteComplete = (data) => {
    setUploadResult(null);
    setDeleteMsg(`Database reset: purged ${data.deleted_count} job postings and vector representations successfully.`);
  };

  return (
    <PageShell
      title="Manage Jobs Catalog"
      description="Upload or reset the global job listings dataset using CSV files. The database will automatically compute vector representations in the background."
    >
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', alignItems: 'start' }}>
        
        {/* Left Column: Upload Catalog */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          <CsvUpload 
            onUploadComplete={handleUploadComplete} 
            onError={setError} 
          />

          {uploadResult && (
            <UploadResults result={uploadResult} />
          )}

          {deleteMsg && (
            <div className="glass-card animate-fade" style={{ border: '1px solid var(--color-success)', color: 'var(--color-success)', fontSize: '0.9rem', padding: '1rem', textAlign: 'center' }}>
              {deleteMsg}
            </div>
          )}

          {error && (
            <div className="glass-card animate-fade" style={{ border: '1px solid var(--color-error)', color: 'var(--color-error)', fontSize: '0.9rem', padding: '1rem', textAlign: 'center' }}>
              {error}
            </div>
          )}

        </div>

        {/* Right Column: Schema Instructions & Tools */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Embedding progress monitor */}
          <ProgressRing
            label="Job Embedding Generation Status"
            endpoint={ENDPOINTS.jobsEmbeddingStatus}
            description="Background vector progress for active job descriptions."
          />

          {/* Template Schema Help */}
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>CSV Schema Requirements</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              To ensure parsing accuracy, the uploaded CSV catalog file must adhere to the following schema format:
            </p>

            <div style={{ 
              backgroundColor: 'rgba(0,0,0,0.3)', 
              borderRadius: '8px', 
              padding: '0.75rem', 
              fontSize: '0.75rem', 
              fontFamily: 'monospace', 
              border: '1px solid var(--border-color)',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all',
              position: 'relative'
            }}>
              {CSV_TEMPLATE_HEADERS}
            </div>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={handleCopyTemplate}
                className="btn-secondary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  fontSize: '0.8rem',
                  padding: '0.5rem 1rem',
                  flex: 1,
                  justifyContent: 'center'
                }}
              >
                {copied ? <Check size={14} color="var(--color-success)" /> : <Copy size={14} />}
                {copied ? 'Copied Template!' : 'Copy CSV Format'}
              </button>
            </div>
          </div>

          {/* Danger Zone Component */}
          <DangerZone onDeleteComplete={handleDeleteComplete} />

        </div>

      </div>
    </PageShell>
  );
}

export default JobsPage;
