import React, { useEffect, useState } from 'react';
import { Trophy } from 'lucide-react';

const Scores: React.FC = () => {
  const [groups, setGroups] = useState<any>({});

  useEffect(() => {
    // We could fetch real results or groups state here.
    // For now, let's fetch groups from tournament
    fetch('http://localhost:8000/api/tournament/groups')
      .then(res => res.json())
      .then(d => setGroups(d))
      .catch(console.error);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        <Trophy size={24} color="var(--brand-primary)" />
        <h2>Résultats Live & Classement Actuel</h2>
      </div>

      <div className="card" style={{ padding: 'var(--space-6)' }}>
        <p style={{ color: 'var(--text-secondary)' }}>
          Les résultats saisis en temps réel et le classement en direct apparaîtront ici.
        </p>

        <div style={{ marginTop: 'var(--space-6)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-4)' }}>
          {Object.entries(groups).map(([groupName, teams]: [string, any]) => (
            <div key={groupName} style={{ background: 'var(--surface-sunken)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)' }}>
              <h3 style={{ margin: '0 0 var(--space-3) 0', borderBottom: '1px solid var(--border-subtle)', paddingBottom: 'var(--space-2)' }}>{groupName}</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 'var(--space-2)', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ color: 'var(--text-secondary)', borderBottom: '1px solid var(--border-subtle)', textAlign: 'right' }}>
                    <th style={{ textAlign: 'left', padding: 'var(--space-2) 0' }}>Équipe</th>
                    <th title="Joués" style={{ padding: 'var(--space-2)' }}>J</th>
                    <th title="Victoires" style={{ padding: 'var(--space-2)' }}>V</th>
                    <th title="Nuls" style={{ padding: 'var(--space-2)' }}>N</th>
                    <th title="Défaites" style={{ padding: 'var(--space-2)' }}>D</th>
                    <th title="Différence" style={{ padding: 'var(--space-2)' }}>DB</th>
                    <th title="Points" style={{ padding: 'var(--space-2)', color: 'var(--brand-primary)' }}>Pts</th>
                  </tr>
                </thead>
                <tbody>
                  {teams.map((t: any, index: number) => (
                    <tr key={t.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: 'var(--space-2) 0', fontWeight: 500 }}>
                        <span style={{ color: 'var(--text-secondary)', marginRight: '8px' }}>{index + 1}.</span> 
                        {t.name || t.id}
                      </td>
                      <td style={{ textAlign: 'right', padding: 'var(--space-2)' }}>{t.p}</td>
                      <td style={{ textAlign: 'right', padding: 'var(--space-2)' }}>{t.w}</td>
                      <td style={{ textAlign: 'right', padding: 'var(--space-2)' }}>{t.d}</td>
                      <td style={{ textAlign: 'right', padding: 'var(--space-2)' }}>{t.l}</td>
                      <td style={{ textAlign: 'right', padding: 'var(--space-2)' }}>{t.gd > 0 ? `+${t.gd}` : t.gd}</td>
                      <td style={{ textAlign: 'right', padding: 'var(--space-2)', fontWeight: 'bold', color: 'var(--brand-primary)' }}>{t.pts}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Scores;
