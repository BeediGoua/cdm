import React, { useState } from 'react';
import { runWhatIf } from '../api/client';
import { Zap, ArrowRight } from 'lucide-react';
import { useQueryClient, useQuery } from '@tanstack/react-query';

interface Props {
  defaultHome: string;
  defaultAway: string;
}

const WhatIfSimulator: React.FC<Props> = ({ defaultHome, defaultAway }) => {
  const [homeGoals, setHomeGoals] = useState(0);
  const [awayGoals, setAwayGoals] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const queryClient = useQueryClient();
  // Get baseline from cache to compare
  const currentSnapshot = queryClient.getQueryData<any>(['snapshot']);

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      const data = await runWhatIf(defaultHome, defaultAway, homeGoals, awayGoals);
      setResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSimulating(false);
    }
  };

  const baselineHome = currentSnapshot?.results?.[defaultHome];
  const baselineAway = currentSnapshot?.results?.[defaultAway];

  return (
    <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
      <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
        <Zap color="var(--brand-primary)" /> What-If Machine (Impact en temps réel)
      </h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
        Saisissez un score hypothétique pour ce match. Une simulation express sera lancée pour estimer l'impact de ce résultat sur les chances de victoire finale des deux équipes.
      </p>

      <div style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'flex-end', marginBottom: 'var(--space-6)', background: 'rgba(0,0,0,0.3)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)' }}>
        <div style={{ flex: 1, textAlign: 'center' }}>
          <label style={{ display: 'block', marginBottom: 'var(--space-2)', color: 'var(--text-secondary)' }}>Buts {defaultHome.toUpperCase()}</label>
          <input type="number" min="0" value={homeGoals} onChange={e => setHomeGoals(parseInt(e.target.value))} style={{ width: '80px', padding: 'var(--space-3)', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)', color: 'white', borderRadius: 'var(--radius-md)', textAlign: 'center', fontSize: '1.5rem' }} />
        </div>
        <div style={{ paddingBottom: '15px', fontWeight: 'bold', color: 'var(--text-secondary)' }}>-</div>
        <div style={{ flex: 1, textAlign: 'center' }}>
          <label style={{ display: 'block', marginBottom: 'var(--space-2)', color: 'var(--text-secondary)' }}>Buts {defaultAway.toUpperCase()}</label>
          <input type="number" min="0" value={awayGoals} onChange={e => setAwayGoals(parseInt(e.target.value))} style={{ width: '80px', padding: 'var(--space-3)', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)', color: 'white', borderRadius: 'var(--radius-md)', textAlign: 'center', fontSize: '1.5rem' }} />
        </div>
        <button onClick={handleSimulate} disabled={isSimulating} style={{ padding: 'var(--space-3) var(--space-6)', background: 'linear-gradient(45deg, var(--brand-primary), #6366F1)', color: 'white', border: 'none', borderRadius: 'var(--radius-md)', cursor: 'pointer', fontWeight: 'bold', height: '60px' }}>
          {isSimulating ? 'Simulation rapide en cours...' : 'Tester le Scénario'}
        </button>
      </div>

      {result && baselineHome && baselineAway && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
          <div style={{ padding: 'var(--space-4)', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid var(--success-color)', borderRadius: 'var(--radius-md)' }}>
            <h4 style={{ marginBottom: 'var(--space-2)' }}>Impact sur {baselineHome.name}</h4>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Chance de Titre :</span>
              <span style={{ textDecoration: 'line-through' }}>{(baselineHome.champion * 100).toFixed(1)}%</span>
              <ArrowRight size={16} />
              <span style={{ fontWeight: 'bold', color: 'var(--success-color)' }}>{(result.homeTeam.champion * 100).toFixed(1)}%</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginTop: 'var(--space-1)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Chance Finale :</span>
              <span style={{ textDecoration: 'line-through' }}>{(baselineHome.final * 100).toFixed(1)}%</span>
              <ArrowRight size={16} />
              <span style={{ fontWeight: 'bold', color: 'var(--success-color)' }}>{(result.homeTeam.final * 100).toFixed(1)}%</span>
            </div>
          </div>

          <div style={{ padding: 'var(--space-4)', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--danger-color)', borderRadius: 'var(--radius-md)' }}>
            <h4 style={{ marginBottom: 'var(--space-2)' }}>Impact sur {baselineAway.name}</h4>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Chance de Titre :</span>
              <span style={{ textDecoration: 'line-through' }}>{(baselineAway.champion * 100).toFixed(1)}%</span>
              <ArrowRight size={16} />
              <span style={{ fontWeight: 'bold', color: 'var(--danger-color)' }}>{(result.awayTeam.champion * 100).toFixed(1)}%</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginTop: 'var(--space-1)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Chance Finale :</span>
              <span style={{ textDecoration: 'line-through' }}>{(baselineAway.final * 100).toFixed(1)}%</span>
              <ArrowRight size={16} />
              <span style={{ fontWeight: 'bold', color: 'var(--danger-color)' }}>{(result.awayTeam.final * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WhatIfSimulator;
