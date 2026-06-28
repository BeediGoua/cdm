import React, { useEffect, useState } from 'react';
import { History as HistoryIcon, Clock } from 'lucide-react';

interface Snapshot {
  filename: string;
  created_at: number;
}

const History: React.FC = () => {
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/snapshots/list')
      .then(res => res.json())
      .then(d => {
        if (Array.isArray(d)) setSnapshots(d);
      })
      .catch(console.error);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        <HistoryIcon size={24} color="var(--brand-primary)" />
        <h2>Historique & Snapshots</h2>
      </div>

      <div className="card" style={{ padding: 'var(--space-6)' }}>
        <p style={{ marginBottom: 'var(--space-4)', color: 'var(--text-secondary)' }}>
          Historique des simulations Monte Carlo générées.
        </p>

        {snapshots.length === 0 ? (
          <p>Aucun snapshot trouvé.</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
            {snapshots.map(s => (
              <li key={s.filename} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 'var(--space-3)', background: 'var(--surface-sunken)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                  <Clock size={16} color="var(--text-secondary)" />
                  <span style={{ fontWeight: 500 }}>{s.filename}</span>
                </div>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                  {new Date(s.created_at * 1000).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default History;
