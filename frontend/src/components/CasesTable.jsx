import React from 'react';
import { Eye, ExternalLink, ShieldCheck, Zap } from 'lucide-react';

export default function CasesTable({ cases, onSelectCase }) {
  if (!cases || cases.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <Zap size={32} style={{ marginBottom: '12px', opacity: 0.5 }} />
        <p>No matching recovery cases found. Try clearing search or filters.</p>
      </div>
    );
  }

  const formatCategory = (cat) => {
    switch (cat) {
      case 'payment_degradation': return 'Payment Degradation';
      case 'checkout_abandonment': return 'Checkout Abandonment';
      case 'subscription_failure': return 'Subscription Failure';
      default: return cat;
    }
  };

  return (
    <div className="glass-panel" style={{ overflow: 'hidden' }}>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
          <thead>
            <tr style={{
              background: 'rgba(0, 0, 0, 0.4)',
              borderBottom: '1px solid var(--border-color)',
              color: 'var(--text-muted)',
              fontSize: '0.78rem',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              <th style={{ padding: '14px 16px' }}>Case ID</th>
              <th style={{ padding: '14px 16px' }}>Customer</th>
              <th style={{ padding: '14px 16px' }}>Category</th>
              <th style={{ padding: '14px 16px' }}>Amount</th>
              <th style={{ padding: '14px 16px' }}>Root Cause</th>
              <th style={{ padding: '14px 16px' }}>Rule / Intervention</th>
              <th style={{ padding: '14px 16px' }}>Status</th>
              <th style={{ padding: '14px 16px', textAlign: 'right' }}>Audit Trail</th>
            </tr>
          </thead>
          <tbody>
            {cases.map((c) => (
              <tr 
                key={c.id}
                style={{
                  borderBottom: '1px solid var(--border-color)',
                  transition: 'background 0.15s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                {/* Case ID */}
                <td style={{ padding: '14px 16px', fontFamily: 'monospace', fontWeight: '600', color: 'var(--primary-cyan)' }}>
                  {c.id}
                </td>

                {/* Customer */}
                <td style={{ padding: '14px 16px' }}>
                  <div style={{ fontWeight: '600' }}>{c.customer_name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>{c.customer_email}</div>
                </td>

                {/* Category */}
                <td style={{ padding: '14px 16px', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                  {formatCategory(c.category)}
                </td>

                {/* Amount */}
                <td style={{ padding: '14px 16px', fontWeight: '700', color: '#f9fafb' }}>
                  ₹{c.amount.toLocaleString('en-IN')}
                </td>

                {/* Root Cause */}
                <td style={{ padding: '14px 16px' }}>
                  {c.root_cause ? (
                    <span className="taxonomy-badge">{c.root_cause}</span>
                  ) : (
                    <span style={{ color: 'var(--text-dim)', fontSize: '0.78rem' }}>Unprocessed</span>
                  )}
                </td>

                {/* Intervention */}
                <td style={{ padding: '14px 16px', fontSize: '0.82rem' }}>
                  {c.last_action ? (
                    <div>
                      <div style={{ fontWeight: '500', color: '#e5e7eb' }}>{c.last_action}</div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>{c.rule_fired}</div>
                    </div>
                  ) : (
                    <span style={{ color: 'var(--text-dim)' }}>—</span>
                  )}
                </td>

                {/* Status */}
                <td style={{ padding: '14px 16px' }}>
                  <span className={`status-pill status-${c.status}`}>
                    {c.status}
                  </span>
                </td>

                {/* Actions */}
                <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                  <button
                    className="btn btn-secondary"
                    style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                    onClick={() => onSelectCase(c.id)}
                  >
                    <Eye size={14} />
                    Audit Log
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
