import { useState, useRef } from 'react';
import { File, AlertTriangle } from 'lucide-react';

export function CsvUpload({ onUploadComplete, onError }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadMode, setUploadMode] = useState('update'); // 'update' or 'replace'
  const [loading, setLoading] = useState(false);
  const [errorLocal, setErrorLocal] = useState(null);
  
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateFile(e.target.files[0]);
    }
  };

  const validateFile = (file) => {
    setErrorLocal(null);
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setErrorLocal("Only CSV catalog files are allowed.");
      return;
    }
    setSelectedFile(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setLoading(true);
    setErrorLocal(null);
    onError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      // Build upload endpoint with mode query parameter
      const baseApi = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${baseApi}/jobs/upload?mode=${uploadMode}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed: ${response.statusText}`);
      }

      const json = await response.json();
      onUploadComplete(json);
      setSelectedFile(null);
    } catch (err) {
      console.error(err);
      setErrorLocal(err.message || "Failed to upload CSV.");
      onError(err.message || "Failed to upload CSV.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Upload Mode Selector */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>1. Choose Catalog Update Mode</h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          {/* Update Mode Card */}
          <label 
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.75rem',
              padding: '1rem',
              borderRadius: '10px',
              border: uploadMode === 'update' ? '1.5px solid var(--color-primary)' : '1px solid var(--border-color)',
              backgroundColor: uploadMode === 'update' ? 'rgba(99, 102, 241, 0.05)' : 'rgba(255,255,255,0.01)',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)'
            }}
          >
            <input 
              type="radio" 
              name="uploadMode" 
              value="update" 
              checked={uploadMode === 'update'}
              onChange={() => setUploadMode('update')}
              style={{ marginTop: '0.2rem', accentColor: 'var(--color-primary)' }}
            />
            <div>
              <span style={{ display: 'block', fontSize: '0.95rem', fontWeight: 600 }}>Incremental Update</span>
              <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                Add new postings and update modified ones (using Title & Company). Unchanged entries are left untouched.
              </span>
            </div>
          </label>

          {/* Replace Mode Card */}
          <label 
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.75rem',
              padding: '1rem',
              borderRadius: '10px',
              border: uploadMode === 'replace' ? '1.5px solid var(--color-error)' : '1px solid var(--border-color)',
              backgroundColor: uploadMode === 'replace' ? 'rgba(239, 68, 68, 0.05)' : 'rgba(255,255,255,0.01)',
              cursor: 'pointer',
              transition: 'all var(--transition-fast)'
            }}
          >
            <input 
              type="radio" 
              name="uploadMode" 
              value="replace" 
              checked={uploadMode === 'replace'}
              onChange={() => setUploadMode('replace')}
              style={{ marginTop: '0.2rem', accentColor: 'var(--color-error)' }}
            />
            <div>
              <span style={{ display: 'block', fontSize: '0.95rem', fontWeight: 600 }}>Complete Replace</span>
              <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                Deletes all current jobs in the database and imports the uploaded file from scratch.
              </span>
            </div>
          </label>
        </div>
      </div>

      {/* Drag and Drop Zone */}
      <div 
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => !loading && inputRef.current.click()}
        className="glass-card"
        style={{
          border: dragActive 
            ? '2px dashed var(--color-primary)' 
            : selectedFile 
              ? '1px solid var(--color-primary)' 
              : '1px dashed var(--border-color)',
          backgroundColor: dragActive 
            ? 'rgba(99, 102, 241, 0.05)' 
            : 'var(--bg-card)',
          padding: '2.5rem 1.5rem',
          borderRadius: '12px',
          textAlign: 'center',
          cursor: loading ? 'not-allowed' : 'pointer',
          opacity: loading ? 0.6 : 1,
          transition: 'all var(--transition-fast)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '1rem',
        }}
      >
        <input 
          ref={inputRef}
          type="file"
          accept=".csv"
          onChange={handleChange}
          disabled={loading}
          style={{ display: 'none' }}
        />

        <div style={{
          width: '54px',
          height: '54px',
          borderRadius: '12px',
          background: 'rgba(255, 255, 255, 0.03)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: selectedFile ? 'var(--color-primary)' : 'var(--text-secondary)',
          border: '1px solid var(--border-color)',
        }}>
          <File size={24} />
        </div>

        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>
            {selectedFile ? selectedFile.name : '2. Select CSV Catalog'}
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
            {selectedFile 
              ? `${(selectedFile.size / 1024).toFixed(1)} KB • Ready to submit`
              : 'Drag & drop your jobs CSV file here, or click to browse'
            }
          </p>
        </div>

        {errorLocal && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            color: 'var(--color-error)',
            fontSize: '0.8rem',
            background: 'rgba(239, 68, 68, 0.1)',
            padding: '0.4rem 0.8rem',
            borderRadius: '6px',
            border: '1px solid rgba(239, 68, 68, 0.2)'
          }}>
            <AlertTriangle size={14} />
            {errorLocal}
          </div>
        )}
      </div>

      {/* Submit Button */}
      {selectedFile && (
        <button
          type="button"
          onClick={handleSubmit}
          disabled={loading}
          className="btn-primary"
          style={{ width: '100%', padding: '0.9rem', fontSize: '1rem' }}
        >
          {loading ? 'Processing Upload & Launching Embedder...' : `Upload Database (${uploadMode === 'replace' ? 'Replace' : 'Update'})`}
        </button>
      )}
    </div>
  );
}

export default CsvUpload;
