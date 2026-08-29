import React from 'react';
import { Play, AlertCircle, RefreshCw, Search, Filter } from 'lucide-react';

export default function ControlPanel({ 
  onRunBatch, 
  onTriggerFailureDemo, 
  onResetSeed, 
  loading,
  search,
  setSearch,
  categoryFilter,
  setCategoryFilter,
  statusFilter,
  setStatusFilter
}) {
  return (
    <div className="glass-panel" style={{ padding: '18px 24px', marginBottom: '24px' }}>
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '16px'
      }}>
        {/* Action Controls */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
          <button 
            className="btn btn-primary"
            onClick={onRunBatch}
            disabled={loading}
          >
            <Play size={16} />
            {loading ? "Executing Batch Agent..." : "Run Batch Agent (50+ Cases)"}
          </button>

          <button 
            className="btn btn-warning"
            onClick={onTriggerFailureDemo}
            disabled={loading}
            title="Demonstrate how the agent handles an API timeout gracefully without crashing"
          >
            <AlertCircle size={16} />
            Demo Graceful Failure
          </button>

          <button 
            className="btn btn-secondary"
            onClick={onResetSeed}
            disabled={loading}
          >
            <RefreshCw size={16} />
            Reset Seed Data
          </button>
        </div>

        {/* Filters and Search */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
          {/* Search Box */}
          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search customer, email, ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                paddingLeft: '36px',
                paddingRight: '12px',
                paddingTop: '8px',
                paddingBottom: '8px',
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                color: 'var(--text-main)',
                fontSize: '0.85rem',
                outline: 'none',
                width: '210px'
              }}
            />
          </div>

          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            style={{
              padding: '8px 12px',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              color: 'var(--text-main)',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          >
            <option value="">All Categories</option>
            <option value="payment_degradation">Payment Degradation</option>
            <option value="checkout_abandonment">Checkout Abandonment</option>
            <option value="subscription_failure">Subscription Failure</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: '8px 12px',
              background: 'rgba(0, 0, 0, 0.3)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              color: 'var(--text-main)',
              fontSize: '0.85rem',
              outline: 'none'
            }}
          >
            <option value="">All Statuses</option>
            <option value="recovered">Recovered</option>
            <option value="link_sent">Link Sent</option>
            <option value="retrying">Retrying</option>
            <option value="escalated">Escalated</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>
    </div>
  );
}
