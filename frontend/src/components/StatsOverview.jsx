import React from 'react';
import { DollarSign, ShieldAlert, CheckCircle2, TrendingUp, Clock, AlertTriangle } from 'lucide-react';

export default function StatsOverview({ stats }) {
  if (!stats) return null;

  const cards = [
    {
      title: "Amount at Risk",
      value: `₹${(stats.total_amount_at_risk || 0).toLocaleString('en-IN')}`,
      subtext: `${stats.total_cases || 0} Total Recovery Cases`,
      icon: DollarSign,
      color: "from-blue-500/20 to-cyan-500/20",
      borderColor: "border-blue-500/30",
      iconColor: "#38bdf8"
    },
    {
      title: "Amount Recovered",
      value: `₹${(stats.amount_recovered || 0).toLocaleString('en-IN')}`,
      subtext: `${stats.cases_recovered || 0} Recovered Transactions`,
      icon: CheckCircle2,
      color: "from-emerald-500/20 to-teal-500/20",
      borderColor: "border-emerald-500/30",
      iconColor: "#34d399"
    },
    {
      title: "Recovery Rate",
      value: `${stats.recovery_rate_pct || 0}%`,
      subtext: "Automated Conversion Rate",
      icon: TrendingUp,
      color: "from-indigo-500/20 to-purple-500/20",
      borderColor: "border-indigo-500/30",
      iconColor: "#818cf8"
    },
    {
      title: "Escalated (Human Queue)",
      value: stats.cases_escalated || 0,
      subtext: "Risk Blocks & Max Limits",
      icon: ShieldAlert,
      color: "from-rose-500/20 to-pink-500/20",
      borderColor: "border-rose-500/30",
      iconColor: "#fb7185"
    },
    {
      title: "Pending Interventions",
      value: stats.cases_pending || 0,
      subtext: "Active & Retrying Cases",
      icon: AlertTriangle,
      color: "from-amber-500/20 to-orange-500/20",
      borderColor: "border-amber-500/30",
      iconColor: "#fbbf24"
    },
    {
      title: "Avg Time-to-Recovery",
      value: `${stats.avg_time_to_recovery_hours || 0} hrs`,
      subtext: "Bounded Action Latency",
      icon: Clock,
      color: "from-violet-500/20 to-purple-500/20",
      borderColor: "border-violet-500/30",
      iconColor: "#c084fc"
    }
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
      gap: '16px',
      marginBottom: '24px'
    }}>
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div 
            key={idx} 
            className="glass-panel"
            style={{
              padding: '20px',
              position: 'relative',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: '500' }}>
                  {card.title}
                </span>
                <h2 style={{ fontSize: '1.6rem', marginTop: '4px', fontWeight: '700', letterSpacing: '-0.5px' }}>
                  {card.value}
                </h2>
              </div>
              <div style={{
                padding: '10px',
                borderRadius: '12px',
                background: 'rgba(255, 255, 255, 0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Icon size={22} color={card.iconColor} />
              </div>
            </div>

            <div style={{ marginTop: '12px', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
              {card.subtext}
            </div>
          </div>
        );
      })}
    </div>
  );
}
