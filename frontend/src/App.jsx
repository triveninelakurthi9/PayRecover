import React, { useEffect, useState } from 'react';
import StatsOverview from './components/StatsOverview';
import ControlPanel from './components/ControlPanel';
import CasesTable from './components/CasesTable';
import AuditModal from './components/AuditModal';
import FailureDemoBanner from './components/FailureDemoBanner';
import { ShieldCheck, RefreshCw, Layers } from 'lucide-react';

export default function App() {
  const [stats, setStats] = useState(null);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [failureData, setFailureData] = useState(null);

  // Filter States
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/stats');
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error("Failed to fetch stats", err);
    }
  };

  const fetchCases = async () => {
    try {
      let url = '/api/cases?';
      if (search) url += `search=${encodeURIComponent(search)}&`;
      if (categoryFilter) url += `category=${encodeURIComponent(categoryFilter)}&`;
      if (statusFilter) url += `status=${encodeURIComponent(statusFilter)}&`;

      const res = await fetch(url);
      const data = await res.json();
      setCases(data);
    } catch (err) {
      console.error("Failed to fetch cases", err);
    }
  };

  useEffect(() => {
    fetchStats();
    fetchCases();
  }, [search, categoryFilter, statusFilter]);

  const handleRunBatch = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/run-batch', { method: 'POST' });
      const data = await res.json();
      console.log("Batch run complete", data);
      await fetchStats();
      await fetchCases();
    } catch (err) {
      console.error("Batch run failed", err);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerFailureDemo = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/trigger-failure-demo?case_id=PAY-0042', { method: 'POST' });
      const data = await res.json();
      setFailureData(data);
      await fetchStats();
      await fetchCases();
    } catch (err) {
      console.error("Trigger failure demo failed", err);
    } finally {
      setLoading(false);
    }
  };

  const handleResetSeed = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/reset-seed', { method: 'POST' });
      setFailureData(null);
      await fetchStats();
      await fetchCases();
    } catch (err) {
      console.error("Reset seed failed", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '32px 24px' }}>
      {/* Header */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '32px',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            padding: '12px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%)',
            border: '1px solid rgba(56, 189, 248, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <ShieldCheck size={32} color="#38bdf8" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.8rem', fontWeight: '800', letterSpacing: '-0.5px' }} className="gradient-text">
              PayRecover Agent
            </h1>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Autonomous Revenue Recovery System • Razorpay AI Buildathon (Track 03)
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            padding: '6px 14px',
            borderRadius: '20px',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            color: '#34d399',
            fontSize: '0.8rem',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#34d399', boxShadow: '0 0 8px #34d399' }}></span>
            Razorpay Test Mode Active
          </div>
        </div>
      </header>

      {/* Graceful Failure Banner */}
      <FailureDemoBanner failureData={failureData} onClose={() => setFailureData(null)} />

      {/* Stats Cards */}
      <StatsOverview stats={stats} />

      {/* Control Panel */}
      <ControlPanel
        onRunBatch={handleRunBatch}
        onTriggerFailureDemo={handleTriggerFailureDemo}
        onResetSeed={handleResetSeed}
        loading={loading}
        search={search}
        setSearch={setSearch}
        categoryFilter={categoryFilter}
        setCategoryFilter={setCategoryFilter}
        statusFilter={statusFilter}
        setStatusFilter={setStatusFilter}
      />

      {/* Data Table */}
      <CasesTable cases={cases} onSelectCase={(id) => setSelectedCaseId(id)} />

      {/* Audit Log Modal */}
      {selectedCaseId && (
        <AuditModal caseId={selectedCaseId} onClose={() => setSelectedCaseId(null)} />
      )}
    </div>
  );
}
