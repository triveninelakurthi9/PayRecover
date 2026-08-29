import React from 'react';
import { ShieldAlert, CheckCircle, RefreshCw, X } from 'lucide-react';

export default function FailureDemoBanner({ failureData, onClose }) {
  if (!failureData) return null;

  return (
    <div style={{
      marginBottom: '24px',
      padding: '16px 20px',
      background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(245, 158, 11, 0.15) 100%)',
      border: '1px solid rgba(239, 68, 68, 0.4)',
      borderRadius: '14px',
      position: 'relative',
      boxShadow: '0 4px 20px rgba(239, 68, 68, 0.2)'
    }}>
      <button 
        onClick={onClose}
        style={{
          position: 'absolute',
          top: '12px',
          right: '14px',
          background: 'transparent',
          border: 'none',
          color: 'var(--text-muted)',
          cursor: 'pointer'
        }}
      >
        <X size={18} />
      </button>

      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
        <div style={{
          padding: '10px',
          borderRadius: '10px',
          background: 'rgba(239, 68, 68, 0.2)',
          color: '#f87171'
        }}>
          <ShieldAlert size={24} />
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h4 style={{ fontSize: '1rem', color: '#fca5a5', fontWeight: '700' }}>
              Deliberate Graceful Failure Demo (Target: {failureData.injected_case})
            </h4>
            <span style={{
              fontSize: '0.72rem',
              fontWeight: '700',
              padding: '2px 8px',
              borderRadius: '12px',
              background: 'rgba(16, 185, 129, 0.2)',
              color: '#34d399',
              border: '1px solid rgba(16, 185, 129, 0.3)'
            }}>
              AGENT FALLBACK SUCCESSFUL
            </span>
          </div>

          <p style={{ fontSize: '0.84rem', color: '#e5e7eb', marginTop: '6px', lineHeight: '1.4' }}>
            {failureData.result?.explanation}
          </p>

          <div style={{
            marginTop: '10px',
            fontSize: '0.78rem',
            color: 'var(--text-muted)',
            display: 'flex',
            gap: '16px',
            fontFamily: 'monospace'
          }}>
            <span>• Error Code: HTTP 504 Gateway Timeout</span>
            <span>• Rule: RULE_GRACEFUL_FAILURE_FALLBACK</span>
            <span>• System State: Uncrashed / Healthy</span>
          </div>
        </div>
      </div>
    </div>
  );
}
