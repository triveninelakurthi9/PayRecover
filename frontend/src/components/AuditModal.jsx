import React, { useEffect, useState } from 'react';
import { X, ShieldCheck, ExternalLink, Clock, FileText, MessageSquare, Terminal } from 'lucide-react';

export default function AuditModal({ caseId, onClose }) {
  const [caseDetail, setCaseDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!caseId) return;
    setLoading(true);
    fetch(`/api/cases/${caseId}`)
      .then((res) => res.json())
      .then((data) => {
        setCaseDetail(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load case detail", err);
        setLoading(false);
      });
  }, [caseId]);

  if (!caseId) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="glass-panel modal-content" 
        onClick={(e) => e.stopPropagation()}
        style={{ position: 'relative' }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '1.4rem', color: 'var(--text-main)' }}>Case Audit Ledger: {caseId}</h2>
              {caseDetail && (
                <span className={`status-pill status-${caseDetail.status}`}>
                  {caseDetail.status}
                </span>
              )}
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              Full decision explainability & Razorpay execution log
            </p>
          </div>

          <button 
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '6px'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading audit trail...
          </div>
        ) : caseDetail ? (
          <div>
            {/* Metadata Summary Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '14px',
              padding: '16px',
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: '12px',
              marginBottom: '20px'
            }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Customer</span>
                <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>{caseDetail.customer_name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{caseDetail.customer_email}</div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Amount at Risk</span>
                <div style={{ fontWeight: '700', fontSize: '1.1rem', color: '#f3f4f6' }}>₹{caseDetail.amount.toLocaleString('en-IN')}</div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Diagnosis Taxonomy</span>
                <div>
                  <span className="taxonomy-badge">{caseDetail.root_cause || "Unclassified"}</span>
                </div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Prior Attempts</span>
                <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>{caseDetail.prior_attempts} / 3</div>
              </div>
            </div>

            {/* Razorpay Test Payment Link (if generated) */}
            {caseDetail.razorpay_payment_link_url && (
              <div style={{
                padding: '12px 16px',
                background: 'rgba(56, 189, 248, 0.1)',
                border: '1px solid rgba(56, 189, 248, 0.25)',
                borderRadius: '10px',
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <ExternalLink size={18} color="#38bdf8" />
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: '600', color: '#38bdf8' }}>Razorpay Test Payment Link</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                      {caseDetail.razorpay_payment_link_url}
                    </div>
                  </div>
                </div>
                <a
                  href={caseDetail.razorpay_payment_link_url}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary"
                  style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                >
                  Test Link
                </a>
              </div>
            )}

            {/* Hinglish Drafted Notification Preview */}
            {caseDetail.drafted_message && (
              <div style={{
                padding: '14px 16px',
                background: 'rgba(99, 102, 241, 0.1)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                borderRadius: '10px',
                marginBottom: '24px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#a5b4fc', fontSize: '0.82rem', fontWeight: '600' }}>
                  <MessageSquare size={16} />
                  LLM Drafted Notification Stub ({caseDetail.channel_pref.toUpperCase()} - Hinglish Tone)
                </div>
                <div style={{
                  fontSize: '0.82rem',
                  fontFamily: 'sans-serif',
                  whiteSpace: 'pre-wrap',
                  color: '#e0e7ff',
                  background: 'rgba(0, 0, 0, 0.3)',
                  padding: '10px 12px',
                  borderRadius: '8px'
                }}>
                  {caseDetail.drafted_message}
                </div>
              </div>
            )}

            {/* Audit Trail Timeline */}
            <h3 style={{ fontSize: '1.05rem', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Clock size={18} color="var(--primary-cyan)" />
              Decision & Execution Audit Trail
            </h3>

            {caseDetail.audit_trail && caseDetail.audit_trail.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {caseDetail.audit_trail.map((log, idx) => (
                  <div 
                    key={idx}
                    style={{
                      padding: '14px',
                      background: 'rgba(255, 255, 255, 0.03)',
                      borderLeft: `4px solid ${log.outcome === 'recovered' ? '#10b981' : log.outcome === 'escalated' ? '#f43f5e' : '#38bdf8'}`,
                      borderRadius: '8px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: 'var(--text-dim)' }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </span>
                      <span style={{ fontSize: '0.75rem', fontWeight: '600', color: log.outcome === 'recovered' ? '#34d399' : '#a5b4fc' }}>
                        OUTCOME: {log.outcome.toUpperCase()}
                      </span>
                    </div>

                    <div style={{ fontSize: '0.85rem', fontWeight: '600', color: '#f3f4f6', marginBottom: '4px' }}>
                      Action: {log.action_taken} <span style={{ color: 'var(--text-dim)', fontWeight: 'normal' }}>(Rule: {log.rule_fired})</span>
                    </div>

                    <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                      <strong>Why chosen:</strong> {log.explanation}
                    </div>

                    {log.raw_details && (
                      <details style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                        <summary style={{ cursor: 'pointer', outline: 'none' }}>View raw execution payload</summary>
                        <pre style={{
                          background: 'rgba(0,0,0,0.5)',
                          padding: '8px',
                          borderRadius: '6px',
                          marginTop: '6px',
                          overflowX: 'auto',
                          fontFamily: 'monospace'
                        }}>
                          {log.raw_details}
                        </pre>
                      </details>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No audit events logged yet for this case.</p>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}
