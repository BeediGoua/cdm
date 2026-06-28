import React, { useState } from 'react';
import { getSnapshotCurrent } from '../api/client';
import { Trophy, Activity, ArrowRight, Search } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  const [selectedView, setSelectedView] = useState('ALL');
  const [selectedCustomTeam, setSelectedCustomTeam] = useState<string>('');
  
  const { data: snapshot, isLoading, error } = useQuery({
    queryKey: ['snapshot'],
    queryFn: getSnapshotCurrent
  });

  if (isLoading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading simulator data...</div>;
  if (error || !snapshot) return <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--danger-color)' }}>No snapshot data available. Please run Monte Carlo.</div>;

  const hasComparisons = !!snapshot.comparisons;
  const showComparisons = hasComparisons && selectedView === 'ALL';
  const activeResults = (hasComparisons && selectedView !== 'ALL') ? snapshot.comparisons[selectedView] : snapshot.results;

  const results = activeResults || {};
  let allTeams = Object.keys(results).map(teamId => ({
    teamId,
    name: results[teamId].name || teamId,
    liveElo: results[teamId].liveElo || 1500,
    fifaPoints: results[teamId].fifaPoints || 0,
    champion: results[teamId].champion || 0,
    champion_display: results[teamId].champion_display || "0.0%",
    champion_ci95_low: results[teamId].champion_ci95_low || 0,
    champion_ci95_high: results[teamId].champion_ci95_high || 0,
    final: results[teamId].final || 0,
    semi: results[teamId].semiFinal || 0,
    quarter: results[teamId].quarterFinal || 0,
    round16: results[teamId].roundOf16 || 0,
    round32: results[teamId].roundOf32 || 0,
  }));

  // Sort by champion probability
  const sortedTeams = [...allTeams].sort((a, b) => b.champion - a.champion);
  const top10Teams = sortedTeams.slice(0, 10);
  
  const alphabeticallySortedTeams = [...allTeams].sort((a, b) => a.name.localeCompare(b.name));
  
  // Set default custom team if not set
  if (!selectedCustomTeam && alphabeticallySortedTeams.length > 0) {
    setSelectedCustomTeam(alphabeticallySortedTeams[0].teamId);
  }

  const customTeamData = sortedTeams.find(t => t.teamId === selectedCustomTeam);
  // Find rank of the custom team
  const customTeamRank = customTeamData ? sortedTeams.findIndex(t => t.teamId === selectedCustomTeam) + 1 : 0;

  const gridColumns = showComparisons 
    ? '40px 140px 90px 90px 1fr 1fr 1fr 30px' 
    : '40px 140px 90px 90px 1fr 60px 30px';

  const getCompDisplay = (v: string, team: any) => {
    if (!showComparisons) return null;
    const prob = snapshot.comparisons[v]?.[team.teamId]?.champion || 0;
    const display = snapshot.comparisons[v]?.[team.teamId]?.champion_display || "0%";
    return (
      <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', background: 'rgba(255,255,255,0.02)', padding: 'var(--space-2)', borderRadius: 'var(--radius-sm)' }}>
        <span style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{display}</span>
        <div style={{ width: '100%', height: '4px', background: 'rgba(0,0,0,0.4)', marginTop: '4px', borderRadius: '2px' }}>
          <div style={{ width: `${prob * 100}%`, height: '100%', background: v === 'V1' ? '#3b82f6' : v === 'V2' ? '#10b981' : '#f59e0b', borderRadius: '2px' }}></div>
        </div>
      </div>
    );
  };

  const renderTeamRow = (team: any, rank: number) => (
    <div 
      key={team.teamId} 
      onClick={() => navigate(`/team/${team.teamId}`)}
      style={{ 
        display: 'grid', 
        gridTemplateColumns: gridColumns,  
        alignItems: 'center', gap: 'var(--space-4)', 
        padding: 'var(--space-3)', 
        borderBottom: '1px solid rgba(255,255,255,0.05)',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(255,255,255,0.02)'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'rgba(255,255,255,0.08)';
        e.currentTarget.style.transform = 'translateX(4px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'rgba(255,255,255,0.02)';
        e.currentTarget.style.transform = 'translateX(0px)';
      }}
    >
      <div style={{ fontWeight: 'bold', fontSize: '1.1rem', color: rank <= 3 ? 'var(--warning-color)' : 'var(--text-secondary)' }}>
        {rank}
      </div>
      <div style={{ fontWeight: 600, fontSize: '1.05rem' }}>{team.name}</div>
      
      <div style={{ 
        textAlign: 'center', 
        background: 'rgba(0,200,83,0.15)', 
        color: '#69f0ae', 
        padding: '4px 8px', 
        borderRadius: '12px',
        fontWeight: 700,
        fontSize: '0.85rem'
      }}>
        {Math.round(team.liveElo)}
      </div>

      <div style={{ 
        textAlign: 'center', 
        background: 'rgba(255,255,255,0.1)', 
        color: 'var(--text-secondary)', 
        padding: '4px 8px', 
        borderRadius: '12px',
        fontWeight: 600,
        fontSize: '0.85rem'
      }}>
        {Math.round(team.fifaPoints)}
      </div>

      {showComparisons ? (
        <>
          {getCompDisplay("V1", team)}
          {getCompDisplay("V2", team)}
          {getCompDisplay("V3", team)}
        </>
      ) : (
        <>
          <div className="progress-container" style={{ height: '8px', background: 'rgba(0,0,0,0.4)', overflow: 'hidden' }}>
            <div 
              className="progress-bar" 
              style={{ 
                width: `${(team.champion * 100).toFixed(1)}%`,
                background: rank <= 3 ? 'linear-gradient(90deg, #ffc107, #ff9800)' : 'var(--brand-primary)',
                boxShadow: rank <= 3 ? '0 0 10px rgba(255,152,0,0.5)' : 'none'
              }}
            ></div>
          </div>
          <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', justifyContent: 'center' }}>
            <span style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>
              {team.champion_display}
            </span>
            {team.champion > 0 && (
              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                ± {(((team.champion_ci95_high - team.champion_ci95_low) / 2) * 100).toFixed(1)}%
              </span>
            )}
          </div>
        </>
      )}
      
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <ArrowRight size={18} color="var(--text-secondary)" style={{ transition: 'color 0.2s' }} />
      </div>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
        <div className="glass-panel" style={{ padding: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <Activity color="var(--brand-primary)" size={24} />
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Simulations (Cache Actif)</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>{snapshot.nSimulations || 0}</div>
          </div>
        </div>
        <div className="glass-panel" style={{ padding: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
          <Trophy color="var(--warning-color)" size={24} />
          <div style={{ width: '100%' }}>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Modèle de Simulation</div>
            {hasComparisons ? (
              <select 
                value={selectedView} 
                onChange={(e) => setSelectedView(e.target.value)}
                style={{ 
                  marginTop: '4px',
                  width: '100%', 
                  padding: '4px 8px', 
                  fontSize: '1rem', 
                  fontWeight: 600, 
                  background: 'rgba(0,0,0,0.3)', 
                  border: '1px solid rgba(255,255,255,0.1)', 
                  color: 'white', 
                  borderRadius: 'var(--radius-sm)', 
                  appearance: 'none', 
                  cursor: 'pointer' 
                }}
              >
                <option value="ALL" style={{ background: '#1f2937', color: 'white' }}>Comparaison (V1, V2, V3)</option>
                <option value="V1" style={{ background: '#1f2937', color: 'white' }}>V1 - Poisson Indépendant</option>
                <option value="V2" style={{ background: '#1f2937', color: 'white' }}>V2 - Calibré</option>
                <option value="V3" style={{ background: '#1f2937', color: 'white' }}>V3 - Dixon-Coles</option>
                <option value="V4" style={{ background: '#1f2937', color: 'white' }}>V4 - Bayésien</option>
                <option value="V5" style={{ background: '#1f2937', color: 'white' }}>V5 - Bivarié</option>
              </select>
            ) : (
              <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>{snapshot.modelVersion || "V1"}</div>
            )}
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>Top 10 Favoris</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>Classement des favoris intégrant le "Live Elo" mis à jour après chaque match réel.</p>
        
        {/* Table Header */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: gridColumns, 
          alignItems: 'center', gap: 'var(--space-4)', 
          padding: '0 var(--space-3) var(--space-2) var(--space-3)', 
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          color: 'var(--text-secondary)',
          fontSize: '0.85rem',
          fontWeight: 600,
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          <div>#</div>
          <div>Équipe</div>
          <div style={{ textAlign: 'center' }}>Live Elo</div>
          <div style={{ textAlign: 'center' }}>FIFA Pts</div>
          {showComparisons ? (
            <>
              <div style={{ textAlign: 'center', color: '#3b82f6' }}>V1 (Classique)</div>
              <div style={{ textAlign: 'center', color: '#10b981' }}>V2 (Calibré)</div>
              <div style={{ textAlign: 'center', color: '#f59e0b' }}>V3 (Dixon-Coles)</div>
            </>
          ) : (
            <>
              <div>Progression vers le titre</div>
              <div style={{ textAlign: 'right' }}>Win %</div>
            </>
          )}
          <div></div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', marginTop: 'var(--space-3)' }}>
          {top10Teams.map((team, index) => renderTeamRow(team, index + 1))}
        </div>
      </div>
      
      {/* Custom Team Selection */}
      <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
          <div>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}><Search size={24} color="var(--brand-primary)" /> Rechercher une équipe</h2>
            <p style={{ color: 'var(--text-secondary)' }}>Sélectionnez n'importe quelle équipe pour voir ses statistiques au format classement.</p>
          </div>
          
          <div style={{ minWidth: '250px' }}>
            <select 
              value={selectedCustomTeam} 
              onChange={(e) => setSelectedCustomTeam(e.target.value)}
              style={{ 
                width: '100%', 
                padding: '12px 16px', 
                fontSize: '1rem', 
                fontWeight: 600, 
                background: 'rgba(0,0,0,0.5)', 
                border: '1px solid var(--brand-primary)', 
                color: 'white', 
                borderRadius: 'var(--radius-md)', 
                outline: 'none',
                cursor: 'pointer' 
              }}
            >
              {alphabeticallySortedTeams.map(t => (
                <option key={t.teamId} value={t.teamId} style={{ background: '#1f2937', color: 'white' }}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        {customTeamData && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
            {renderTeamRow(customTeamData, customTeamRank)}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
