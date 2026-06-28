import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSnapshotCurrent } from '../api/client';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const PowerRankings = () => {
  const { data: snapshot, isLoading, error } = useQuery({
    queryKey: ['snapshot'],
    queryFn: getSnapshotCurrent
  });

  if (isLoading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Power Rankings...</div>;
  if (error || !snapshot) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--danger-color)' }}>No data available.</div>;

  const results = snapshot.results || {};
  let teams = Object.keys(results).map(teamId => {
    const liveElo = results[teamId].liveElo || 1500;
    const baseElo = results[teamId].baseElo || 1500;
    return {
      teamId,
      name: results[teamId].name || teamId,
      liveElo,
      baseElo,
      delta: liveElo - baseElo
    };
  });

  // Sort by delta (highest first)
  teams.sort((a, b) => b.delta - a.delta);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <TrendingUp color="var(--brand-primary)" />
          La Bourse de l'Elo (Power Rankings)
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
          Découvrez les équipes qui ont accumulé le plus de "momentum" depuis le début du tournoi.
        </p>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: '40px 180px 100px 100px 120px', 
          gap: 'var(--space-4)', 
          padding: '0 var(--space-3) var(--space-2) var(--space-3)', 
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          color: 'var(--text-secondary)',
          fontSize: '0.85rem',
          fontWeight: 600,
          textTransform: 'uppercase'
        }}>
          <div>#</div>
          <div>Équipe</div>
          <div style={{ textAlign: 'center' }}>Elo Initial</div>
          <div style={{ textAlign: 'center' }}>Live Elo</div>
          <div style={{ textAlign: 'right' }}>Dynamique</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', marginTop: 'var(--space-3)' }}>
          {teams.map((team, index) => {
            const isPositive = team.delta > 0.5;
            const isNegative = team.delta < -0.5;
            const deltaColor = isPositive ? '#00e676' : isNegative ? '#ff1744' : 'var(--text-secondary)';
            
            return (
              <div 
                key={team.teamId} 
                style={{ 
                  display: 'grid', 
                  gridTemplateColumns: '40px 180px 100px 100px 120px', 
                  alignItems: 'center', gap: 'var(--space-4)', 
                  padding: 'var(--space-3)', 
                  borderBottom: '1px solid rgba(255,255,255,0.05)',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(255,255,255,0.02)'
                }}
              >
                <div style={{ fontWeight: 'bold', color: 'var(--text-secondary)' }}>
                  {index + 1}
                </div>
                <div style={{ fontWeight: 600, fontSize: '1.05rem' }}>{team.name}</div>
                
                <div style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
                  {Math.round(team.baseElo)}
                </div>

                <div style={{ textAlign: 'center', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                  {Math.round(team.liveElo)}
                </div>

                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'flex-end',
                  gap: 'var(--space-2)',
                  color: deltaColor,
                  fontWeight: 'bold',
                  fontSize: '1.1rem'
                }}>
                  {isPositive ? '+' : ''}{team.delta.toFixed(1)}
                  {isPositive ? <TrendingUp size={18} /> : isNegative ? <TrendingDown size={18} /> : <Minus size={18} />}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default PowerRankings;
