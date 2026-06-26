import { Loader2, Check, AlertCircle, FileText, Binary, Search, BrainCircuit, Sparkles } from 'lucide-react';

const STAGES = [
  { id: 'PENDING', label: 'Queued', icon: FileText },
  { id: 'PARSING', label: 'PDF Parsing', icon: FileText },
  { id: 'EMBEDDING', label: 'Generating Embeddings', icon: Binary },
  { id: 'SEARCHING', label: 'Vector Search Match', icon: Search },
  { id: 'REASONING', label: 'LLM Quality Reasoning', icon: BrainCircuit },
  { id: 'COMPLETE', label: 'Success', icon: Sparkles }
];

export function PipelineStepper({ status }) {
  const getStageIndex = (stageId) => {
    return STAGES.findIndex(s => s.id === stageId);
  };

  const currentIdx = getStageIndex(status);
  const isFailed = status === 'FAILED';

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', padding: '2.5rem' }}>
      <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 600, color: 'var(--text-main)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
          {isFailed ? (
            <>
              <AlertCircle color="var(--color-error)" size={24} />
              Pipeline Execution Failed
            </>
          ) : status === 'COMPLETE' ? (
            <>
              <Check color="var(--color-success)" size={24} style={{ border: '2px solid var(--color-success)', borderRadius: '50%', padding: '2px' }} />
              Resume Processed Successfully
            </>
          ) : (
            <>
              <Loader2 className="animate-spin" size={24} style={{ animation: 'spin 1.5s linear infinite', color: 'var(--color-primary)' }} />
              Running Local AI Pipeline
            </>
          )}
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
          {isFailed 
            ? 'An error occurred during resume text extraction or model inference. Check API logs.'
            : status === 'COMPLETE'
              ? 'Candidate profile parsed, vectorized, matched, and reasoning generated!'
              : `Current Stage: ${STAGES[currentIdx]?.label || status}. Processing entirely offline.`
          }
        </p>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>

      {/* Stepper Steps List */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1.25rem',
        maxWidth: '500px',
        margin: '0 auto',
        width: '100%',
        position: 'relative'
      }}>
        {STAGES.map((stage, idx) => {
          const isCompleted = currentIdx > idx || status === 'COMPLETE';
          const isActive = currentIdx === idx && !isFailed;
          const isStageFailed = isFailed && currentIdx === idx;
          
          const StepIcon = stage.icon;

          return (
            <div key={stage.id} style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', position: 'relative' }}>
              {/* Connector line */}
              {idx < STAGES.length - 1 && (
                <div style={{
                  position: 'absolute',
                  left: '20px',
                  top: '40px',
                  bottom: '-20px',
                  width: '2px',
                  backgroundColor: isCompleted ? 'var(--color-success)' : 'var(--border-color)',
                  zIndex: 1
                }} />
              )}

              {/* Icon Sphere */}
              <div style={{
                width: '42px',
                height: '42px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 2,
                backgroundColor: isStageFailed 
                  ? 'rgba(239, 68, 68, 0.15)' 
                  : isCompleted 
                    ? 'rgba(16, 185, 129, 0.15)' 
                    : isActive 
                      ? 'rgba(99, 102, 241, 0.2)' 
                      : 'rgba(255, 255, 255, 0.03)',
                border: isStageFailed
                  ? '1.5px solid var(--color-error)'
                  : isCompleted
                    ? '1.5px solid var(--color-success)'
                    : isActive
                      ? '1.5px solid var(--color-primary)'
                      : '1.5px solid var(--border-color)',
                color: isStageFailed
                  ? 'var(--color-error)'
                  : isCompleted
                    ? 'var(--color-success)'
                    : isActive
                      ? 'var(--color-primary)'
                      : 'var(--text-muted)',
                boxShadow: isActive 
                  ? '0 0 15px rgba(99, 102, 241, 0.25)' 
                  : isCompleted 
                    ? '0 0 15px rgba(16, 185, 129, 0.1)' 
                    : 'none',
                transition: 'all 0.5s ease'
              }}>
                {isStageFailed ? (
                  <AlertCircle size={20} />
                ) : isCompleted ? (
                  <Check size={20} />
                ) : isActive ? (
                  <Loader2 size={20} style={{ animation: 'spin 1.5s linear infinite' }} />
                ) : (
                  <StepIcon size={20} />
                )}
              </div>

              {/* Text label */}
              <div>
                <span style={{
                  fontSize: '1rem',
                  fontWeight: isActive || isCompleted ? 600 : 500,
                  color: isStageFailed
                    ? 'var(--color-error)'
                    : isCompleted
                      ? 'var(--color-success)'
                      : isActive
                        ? 'var(--color-primary)'
                        : 'var(--text-secondary)'
                }}>
                  {stage.label}
                </span>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {isActive 
                    ? 'In progress (polling local Ollama model...)' 
                    : isCompleted 
                      ? 'Stage completed' 
                      : isStageFailed 
                        ? 'Failed here' 
                        : 'Waiting'
                  }
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default PipelineStepper;
