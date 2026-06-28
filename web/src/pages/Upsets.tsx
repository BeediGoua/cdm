import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getUpsets } from '../api/client';
import { Zap } from 'lucide-react';

const Upsets = () => {
  const { data: upsets, isLoading, error } = useQuery({
    queryKey: ['upsets'],
    queryFn: getUpsets
  });

  if (isLoading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Analyse des miracles en cours...</div>;
  if (error || !upsets) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--danger-color)' }}>Erreur lors du chargement des miracles.</div>;

  if (upsets.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
        <Zap color="var(--warning-color)" size={48} style={{ opacity: 0.5, margin: '0 auto var(--space-4)' }} />
        <h2>Aucun Miracle Détecté</h2>
        <p style={{ color: 'var(--text-secondary)' }}>La logique mathématique a été respectée sur tous les matchs jusqu'à présent.</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--warning-color)' }}>
          <Zap />
          Détecteur de Miracles
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-6)' }}>
          Classement des plus grands exploits du tournoi. Plus le score est élevé, plus la victoire était statistiquement inattendue avant le coup d'envoi.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          {upsets.map((upset: any, index: number) => (
            <div 
              key={index}
              style={{
                background: `linear-gradient(135deg, rgba(255, 152, 0, ${0.15 - (index*0.02)}), rgba(0,0,0,0))`,
                border: '1px solid rgba(255, 152, 0, 0.2)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--space-5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: 'var(--space-2)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  {upset.stage === 'group' ? 'Phase de Poules' : 'Élimination Directe'}
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', fontSize: '1.25rem', fontWeight: 700 }}>
                  <span style={{ color: 'var(--warning-color)' }}>{upset.winnerName}</span>
                  <span style={{ background: 'rgba(255,255,255,0.1)', padding: '4px 12px', borderRadius: '20px', fontSize: '1rem' }}>{upset.score}</span>
                  <span style={{ opacity: 0.5 }}>{upset.loserName}</span>
                </div>
                <div style={{ marginTop: 'var(--space-3)', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  Probabilité avant match : <strong style={{ color: 'white' }}>{(upset.expectedProb * 100).toFixed(1)}%</strong>
                </div>
              </div>
              
              <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-1)' }}>
                <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', color: 'var(--warning-color)', fontWeight: 600 }}>Upset Score</div>
                <div style={{ fontSize: '2.5rem', fontWeight: 900, color: 'var(--text-primary)', textShadow: '0 0 20px rgba(255,152,0,0.5)' }}>
                  {upset.upsetScore.toFixed(0)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Upsets;
