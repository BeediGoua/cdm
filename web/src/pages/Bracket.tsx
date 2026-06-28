import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSnapshotCurrent } from '../api/client';
import { Map } from 'lucide-react';

const Bracket = () => {
  const [selectedModel, setSelectedModel] = React.useState<string>('V3');

  const { data: snapshot, isLoading, error } = useQuery({
    queryKey: ['snapshot'],
    queryFn: getSnapshotCurrent
  });

  if (isLoading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Bracket...</div>;
  if (error || !snapshot) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--danger-color)' }}>No data available.</div>;

  const hasComparisons = !!snapshot.comparisons;
  const activeResults = hasComparisons ? (snapshot.comparisons[selectedModel] || snapshot.results) : snapshot.results;
  const results = activeResults || {};
  
  let teams = Object.keys(results).map(teamId => ({
    teamId,
    name: results[teamId].name || teamId,
    champion: results[teamId].champion || 0,
    final: results[teamId].final || 0,
    semi: results[teamId].semiFinal || 0,
    quarter: results[teamId].quarterFinal || 0,
    round16: results[teamId].roundOf16 || 0,
  }));

  const getTop = (stageKey: keyof typeof teams[0], count: number) => {
    return [...teams].sort((a, b) => (b[stageKey] as number) - (a[stageKey] as number)).slice(0, count);
  };

  const top16 = getTop('round16', 16);
  const top8 = getTop('quarter', 8);
  const top4 = getTop('semi', 4);
  const top2 = getTop('final', 2);
  const champ = getTop('champion', 1)[0];

  const StageBox = ({ title, teamsList, count, stageKey }: { title: string, teamsList: any[], count: number, stageKey: keyof typeof teams[0] }) => (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
      <h3 style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: 'var(--space-2)' }}>{title}</h3>
      {teamsList.map((t, i) => (
        <div key={i} style={{
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid rgba(255,255,255,0.1)',
          padding: 'var(--space-3)',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontWeight: 600,
          color: t === champ && count === 1 ? 'var(--warning-color)' : 'var(--text-primary)'
        }}>
          <span>{t.name}</span>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 'normal' }}>
            {((t[stageKey] as number) * 100).toFixed(1)}%
          </span>
        </div>
      ))}
      {Array(count - teamsList.length).fill(0).map((_, i) => (
        <div key={`empty-${i}`} style={{
          background: 'rgba(255,255,255,0.01)',
          border: '1px dashed rgba(255,255,255,0.1)',
          padding: 'var(--space-3)',
          borderRadius: 'var(--radius-sm)',
          textAlign: 'center',
          color: 'var(--text-muted)'
        }}>TBD</div>
      ))}
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-6)' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', margin: 0 }}>
            <Map color="var(--brand-primary)" />
            L'Arbre du Tournoi le plus probable
          </h2>
          
          {hasComparisons && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Affichage :</span>
              <select 
                value={selectedModel} 
                onChange={e => setSelectedModel(e.target.value)}
                style={{ padding: '4px 8px', background: '#1f2937', color: 'white', border: '1px solid var(--border-color)', borderRadius: '4px' }}
              >
                <option value="V1">V1 - Poisson Classique</option>
                <option value="V2">V2 - Calibré</option>
                <option value="V3">V3 - Dixon-Coles</option>
                <option value="V4">V4 - Bayésien</option>
                <option value="V5">V5 - Bivarié</option>
              </select>
            </div>
          )}
        </div>
        
        <div style={{ display: 'flex', gap: 'var(--space-4)', overflowX: 'auto', paddingBottom: 'var(--space-4)' }}>
          <StageBox title="Huitièmes" teamsList={top16} count={16} stageKey="round16" />
          <StageBox title="Quarts" teamsList={top8} count={8} stageKey="quarter" />
          <StageBox title="Demies" teamsList={top4} count={4} stageKey="semi" />
          <StageBox title="Finale" teamsList={top2} count={2} stageKey="final" />
          <StageBox title="Vainqueur" teamsList={champ ? [champ] : []} count={1} stageKey="champion" />
        </div>
      </div>
    </div>
  );
};

export default Bracket;
