import { useState, useRef } from 'react';
import { Upload, File, AlertTriangle } from 'lucide-react';

export function DropZone({ onFileSelect, selectedFile, error, setError }) {
  const [dragActive, setDragActive] = useState(false);
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
      validateAndProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndProcessFile(e.target.files[0]);
    }
  };

  const validateAndProcessFile = (file) => {
    setError(null);
    
    // Validate PDF mime type or extension
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith('.pdf')) {
      setError("Only PDF files are allowed.");
      return;
    }

    // Validate size (10 MB)
    if (file.size > 10 * 1024 * 1024) {
      setError("File exceeds 10MB limit.");
      return;
    }

    onFileSelect(file);
  };

  return (
    <div 
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
      onClick={() => inputRef.current.click()}
      className="glass-card"
      style={{
        border: dragActive 
          ? '2px dashed var(--color-primary)' 
          : selectedFile 
            ? '1px solid var(--color-success)' 
            : '1px dashed var(--border-color)',
        backgroundColor: dragActive 
          ? 'rgba(99, 102, 241, 0.05)' 
          : selectedFile 
            ? 'rgba(16, 185, 129, 0.03)' 
            : 'var(--bg-card)',
        padding: '3rem 2rem',
        borderRadius: '16px',
        textAlign: 'center',
        cursor: 'pointer',
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
        accept=".pdf,application/pdf"
        onChange={handleChange}
        style={{ display: 'none' }}
      />

      <div style={{
        width: '64px',
        height: '64px',
        borderRadius: '14px',
        background: selectedFile 
          ? 'rgba(16, 185, 129, 0.1)' 
          : 'rgba(255, 255, 255, 0.03)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: selectedFile ? 'var(--color-success)' : 'var(--text-secondary)',
        border: selectedFile ? '1px solid rgba(16, 185, 129, 0.2)' : '1px solid var(--border-color)',
        boxShadow: selectedFile ? '0 0 15px rgba(16, 185, 129, 0.15)' : 'none'
      }}>
        {selectedFile ? <File size={28} /> : <Upload size={28} />}
      </div>

      <div>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)' }}>
          {selectedFile ? selectedFile.name : 'Upload Candidate Resume'}
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
          {selectedFile 
            ? `${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready for processing`
            : 'Drag & drop candidate PDF file here, or click to browse files'
          }
        </p>
      </div>

      {error && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          color: 'var(--color-error)',
          fontSize: '0.85rem',
          background: 'rgba(239, 68, 68, 0.1)',
          padding: '0.5rem 1rem',
          borderRadius: '8px',
          border: '1px solid rgba(239, 68, 68, 0.2)'
        }}>
          <AlertTriangle size={16} />
          {error}
        </div>
      )}
    </div>
  );
}

export default DropZone;
