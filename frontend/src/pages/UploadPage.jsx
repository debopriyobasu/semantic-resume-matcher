import { useState } from 'react';
import PageShell from '../components/Layout/PageShell';
import DropZone from '../components/Upload/DropZone';
import DynamicForm from '../components/Upload/DynamicForm';
import PipelineStepper from '../components/Upload/PipelineStepper';
import { ENDPOINTS } from '../config/endpoints';
import { usePolling } from '../hooks/usePolling';

export function UploadPage({ onNavigateToResults }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [formData, setFormData] = useState({
    desired_salary: null,
    visa_required: false,
    preferred_location: '',
    preferred_remote: false
  });

  const [pipelineState, setPipelineState] = useState('idle'); // 'idle' | 'uploading' | 'processing' | 'done' | 'failed'
  const [candidateId, setCandidateId] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState(null); // 'PENDING', 'PARSING', etc.
  const [error, setError] = useState(null);

  // Poll pipeline status once candidateId is loaded
  usePolling(async () => {
    if (!candidateId) return;

    try {
      const response = await fetch(ENDPOINTS.candidateStatus(candidateId));
      if (!response.ok) {
        throw new Error('Failed to retrieve processing state.');
      }
      const data = await response.json();
      setPipelineStatus(data.status);

      if (data.status === 'COMPLETE') {
        setPipelineState('done');
        // Let user view results after short success message delay
        setTimeout(() => {
          onNavigateToResults(candidateId);
        }, 1500);
      } else if (data.status === 'FAILED') {
        setPipelineState('failed');
      }
    } catch (err) {
      console.error(err);
      setPipelineState('failed');
      setError('Connection to parsing background service lost.');
    }
  }, 2500, pipelineState === 'processing' && !!candidateId);

  const handleUploadSubmit = async () => {
    if (!selectedFile) return;

    setPipelineState('uploading');
    setError(null);

    const data = new FormData();
    data.append('file', selectedFile);
    
    // Add form data preferences
    if (formData.desired_salary) data.append('desired_salary', formData.desired_salary);
    data.append('visa_required', formData.visa_required);
    if (formData.preferred_location) data.append('preferred_location', formData.preferred_location);
    data.append('preferred_remote', formData.preferred_remote);

    try {
      const response = await fetch(ENDPOINTS.uploadResume, {
        method: 'POST',
        body: data
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed: ${response.statusText}`);
      }

      const json = await response.json();
      setCandidateId(json.candidate_id);
      setPipelineStatus(json.status);
      setPipelineState('processing');
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to submit resume');
      setPipelineState('idle');
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setCandidateId(null);
    setPipelineStatus(null);
    setPipelineState('idle');
    setError(null);
  };

  return (
    <PageShell
      title="Candidate Parsing Pipeline"
      description="Upload a resume PDF along with candidate preferences to extract skills and match vector embeddings against catalogs."
    >
      <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        
        {pipelineState === 'idle' || pipelineState === 'uploading' ? (
          <>
            <DropZone 
              onFileSelect={setSelectedFile} 
              selectedFile={selectedFile} 
              error={error} 
              setError={setError} 
            />

            <DynamicForm 
              formData={formData} 
              setFormData={setFormData} 
            />

            {selectedFile && (
              <button
                type="button"
                onClick={handleUploadSubmit}
                disabled={pipelineState === 'uploading'}
                className="btn-primary"
                style={{ width: '100%', padding: '0.9rem', fontSize: '1rem' }}
              >
                {pipelineState === 'uploading' 
                  ? 'Uploading resume PDF...' 
                  : 'Start Local Analysis & Semantic Match'
                }
              </button>
            )}
          </>
        ) : (
          <div className="animate-fade" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <PipelineStepper status={pipelineStatus} />

            {(pipelineState === 'done' || pipelineState === 'failed') && (
              <button
                onClick={handleReset}
                className="btn-secondary"
                style={{ width: '100%', padding: '0.9rem' }}
              >
                Upload Another Candidate Resume
              </button>
            )}
          </div>
        )}

      </div>
    </PageShell>
  );
}

export default UploadPage;
