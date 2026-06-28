import React, { useState, useEffect } from 'react';
import { submitMatchResult, triggerSimulation } from '../api/client';
import { Settings, Play, CheckCircle, Loader2 } from 'lucide-react';

interface Match {
  id: string;
  homeTeamId: string;
  awayTeamId: string;
  homeTeamName: string;
  awayTeamName: string;
  group: string;
  date: string;
  type: string;
  played: boolean;
  homeScore?: number;
  awayScore?: number;
}

const MatchCard = ({ match, onSave }: { match: Match, onSave: (matchId: string, home: number, away: number) => Promise<void> }) => {
  const [homeGoals, setHomeGoals] = useState<number | ''>(match.homeScore ?? '');
  const [awayGoals, setAwayGoals] = useState<number | ''>(match.awayScore ?? '');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [isEditing, setIsEditing] = useState(!match.played);

  // Update state if match data changes from parent
  useEffect(() => {
    setHomeGoals(match.homeScore ?? '');
    setAwayGoals(match.awayScore ?? '');
    if (match.played) {
      setIsEditing(false);
    }
  }, [match.homeScore, match.awayScore, match.played]);

  const handleSave = async () => {
    if (homeGoals === '' || awayGoals === '') return;
    setSaving(true);
    await onSave(match.id, homeGoals as number, awayGoals as number);
    setSaving(false);
    setSaved(true);
    setIsEditing(false);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleCancel = () => {
    setHomeGoals(match.homeScore ?? '');
    setAwayGoals(match.awayScore ?? '');
    setIsEditing(false);
  };

  const isPlayed = match.played;

  let buttonText = 'Sauvegarder';
  if (saving) buttonText = '...';
  else if (saved) buttonText = '✓ Enregistré';

  let buttonBg = (homeGoals !== '' && awayGoals !== '') ? 'var(--brand-primary)' : 'var(--border-color)';
  if (saved) buttonBg = 'var(--status-success)';

  return (
    <div style={{ background: (isPlayed && !isEditing) ? 'rgba(16, 185, 129, 0.05)' : 'var(--surface-sunken)', borderRadius: 'var(--radius-md)', padding: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', border: (isPlayed && !isEditing) ? '1px solid rgba(16, 185, 129, 0.2)' : '1px solid transparent' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', color: (isPlayed && !isEditing) ? 'var(--status-success)' : 'var(--text-secondary)' }}>
        <span>{match.date} {(isPlayed && !isEditing) && '✓ Terminé'}</span>
        <span>{match.id}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        <div style={{ flex: 1, textAlign: 'right', fontWeight: 'bold', color: isPlayed ? 'var(--text-primary)' : 'inherit' }}>{match.homeTeamName}</div>
        
        {!isEditing ? (
          <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '1.2rem', padding: 'var(--space-2)', minWidth: '120px' }}>
            <span>{match.homeScore}</span>
            <span style={{ color: 'var(--text-secondary)' }}>-</span>
            <span>{match.awayScore}</span>
          </div>
        ) : (
          <>
            <input 
              type="number" min="0" value={homeGoals} onChange={e => setHomeGoals(e.target.value === '' ? '' : parseInt(e.target.value))} 
              style={{ width: '50px', padding: 'var(--space-2)', textAlign: 'center', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)', color: 'white', borderRadius: 'var(--radius-sm)' }} 
            />
            <span style={{ color: 'var(--text-secondary)' }}>-</span>
            <input 
              type="number" min="0" value={awayGoals} onChange={e => setAwayGoals(e.target.value === '' ? '' : parseInt(e.target.value))} 
              style={{ width: '50px', padding: 'var(--space-2)', textAlign: 'center', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)', color: 'white', borderRadius: 'var(--radius-sm)' }} 
            />
          </>
        )}
        
        <div style={{ flex: 1, fontWeight: 'bold', color: isPlayed ? 'var(--text-primary)' : 'inherit' }}>{match.awayTeamName}</div>
      </div>
      
      {!isEditing ? (
        <button 
          onClick={() => setIsEditing(true)} 
          style={{ 
            marginTop: 'var(--space-2)', width: '100%', padding: 'var(--space-2)', 
            background: 'transparent', 
            color: 'var(--text-secondary)', 
            border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', 
            cursor: 'pointer',
            fontWeight: 'bold', transition: 'all 0.2s'
          }}
        >
          Modifier
        </button>
      ) : (
        <div style={{ display: 'flex', gap: 'var(--space-2)', marginTop: 'var(--space-2)' }}>
          {isPlayed && (
            <button 
              onClick={handleCancel}
              style={{ 
                flex: 1, padding: 'var(--space-2)', 
                background: 'transparent', color: 'var(--text-secondary)', 
                border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', 
                cursor: 'pointer', fontWeight: 'bold'
              }}
            >
              Annuler
            </button>
          )}
          <button 
            onClick={handleSave} 
            disabled={homeGoals === '' || awayGoals === '' || saving}
            style={{ 
              flex: 2, padding: 'var(--space-2)', 
              background: buttonBg, color: 'white', 
              border: 'none', borderRadius: 'var(--radius-sm)', 
              cursor: (homeGoals !== '' && awayGoals !== '') ? 'pointer' : 'default',
              fontWeight: 'bold', transition: 'all 0.2s'
            }}
          >
            {buttonText}
          </button>
        </div>
      )}
    </div>
  );
};

import { useQueryClient } from '@tanstack/react-query';

const AdminCockpit = () => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [activeGroup, setActiveGroup] = useState<string>('A');
  const [activeMatchday, setActiveMatchday] = useState<number>(0); // 0 means all matchdays
  const [status, setStatus] = useState('');
  const [isSimulating, setIsSimulating] = useState(false);
  
  const queryClient = useQueryClient();

  // God Mode & Params
  const [nSims, setNSims] = useState<number>(10000);
  const [simulationMode, setSimulationMode] = useState<string>('live');
  const [modelVersion, setModelVersion] = useState<string>('ALL');
  const [godModeTeam, setGodModeTeam] = useState<string>('fra');
  const [godModeDelta, setGodModeDelta] = useState<number>(0);
  const [eloDeltas, setEloDeltas] = useState<Record<string, number>>({});

  useEffect(() => {
    fetch('http://localhost:8000/api/tournament/matches')
      .then(res => res.json())
      .then(d => {
        if (Array.isArray(d)) setMatches(d);
      })
      .catch(console.error);
  }, []);

  const handleSaveMatch = async (matchId: string, homeGoals: number, awayGoals: number) => {
    const match = matches.find(m => m.id === matchId);
    if (!match) return;
    try {
      await submitMatchResult({
        matchId: match.id,
        homeTeamId: match.homeTeamId,
        awayTeamId: match.awayTeamId,
        homeGoals,
        awayGoals,
      });
      // Update local state so UI reacts instantly
      setMatches(prev => prev.map(m => 
        m.id === matchId 
          ? { ...m, played: true, homeScore: homeGoals, awayScore: awayGoals }
          : m
      ));
    } catch (error) {
      console.error(error);
      throw error;
    }
  };

  const handleSimulate = async () => {
    setIsSimulating(true);
    setStatus('Calcul en cours... (Patientez quelques secondes)');
    try {
      const params = {
        nSimulations: nSims,
        mode: simulationMode,
        modelVersion,
        eloDeltas: Object.keys(eloDeltas).length > 0 ? eloDeltas : undefined
      };
      const res = await triggerSimulation(params);
      
      // Force all tabs to fetch fresh data
      queryClient.invalidateQueries({ queryKey: ['snapshot'] });
      queryClient.invalidateQueries({ queryKey: ['upsets'] });
      
      setStatus(res.message || 'Simulation terminée avec succès !');
    } catch (error) {
      setStatus('Erreur lors du lancement de la simulation.');
    } finally {
      setIsSimulating(false);
    }
  };

  const handleAddDelta = () => {
    if (godModeTeam && godModeDelta !== 0) {
      setEloDeltas(prev => ({ ...prev, [godModeTeam]: godModeDelta }));
      setGodModeDelta(0);
    }
  };

  const handleRemoveDelta = (teamId: string) => {
    setEloDeltas(prev => {
      const copy = { ...prev };
      delete copy[teamId];
      return copy;
    });
  };

  // Extract unique groups
  const groups = Array.from(new Set(matches.map(m => m.group))).sort((a, b) => {
    if (a.length === 1 && b.length === 1) return a.localeCompare(b); // Sort A-L
    if (a.length === 1) return -1; // Groups before knockouts
    if (b.length === 1) return 1;
    return 0; // Don't sort knockouts for now, trust API order
  });

  const isGroupStage = activeGroup.length === 1;

  const filteredMatches = matches.filter(m => {
    if (m.group !== activeGroup) return false;
    if (isGroupStage && activeMatchday !== 0) {
      // Need to cast to any or define matchday in Match interface.
      // I'll assume matchday exists on m as I added it to the API.
      return (m as any).matchday === activeMatchday;
    }
    return true;
  });

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-6)' }}>
      <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Settings size={24} color="var(--brand-primary)" /> Saisie des Scores (Live)
        </h2>
        
        {/* Navigation Tabs */}
        <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap', marginTop: 'var(--space-6)' }}>
          {groups.map(g => (
            <button 
              key={g} 
              onClick={() => { setActiveGroup(g); setActiveMatchday(0); }}
              style={{
                padding: 'var(--space-2) var(--space-4)',
                background: activeGroup === g ? 'var(--brand-primary)' : 'rgba(0,0,0,0.3)',
                color: activeGroup === g ? 'white' : 'var(--text-secondary)',
                border: '1px solid ' + (activeGroup === g ? 'var(--brand-primary)' : 'var(--border-subtle)'),
                borderRadius: 'var(--radius-full)',
                cursor: 'pointer',
                fontWeight: activeGroup === g ? 'bold' : 'normal',
              }}
            >
              {g.length === 1 ? `Groupe ${g}` : g}
            </button>
          ))}
        </div>

        {isGroupStage && (
          <div style={{ display: 'flex', gap: 'var(--space-2)', marginTop: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
            {[0, 1, 2, 3].map(md => (
              <button 
                key={md}
                onClick={() => setActiveMatchday(md)}
                style={{
                  padding: 'var(--space-1) var(--space-3)',
                  background: activeMatchday === md ? 'var(--surface-sunken)' : 'transparent',
                  color: activeMatchday === md ? 'var(--brand-primary)' : 'var(--text-secondary)',
                  border: '1px solid ' + (activeMatchday === md ? 'var(--brand-primary)' : 'transparent'),
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  fontSize: '0.875rem'
                }}
              >
                {md === 0 ? 'Toutes les journées' : `Journée ${md}`}
              </button>
            ))}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)', marginTop: isGroupStage ? '0' : 'var(--space-4)' }}>
          {filteredMatches.map(m => (
            <MatchCard key={m.id} match={m} onSave={handleSaveMatch} />
          ))}
        </div>
      </div>

      <div className="glass-panel" style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', height: 'fit-content' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <Play size={24} color="var(--status-warning)" /> Déclencher Simulation
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-4)', lineHeight: 1.6 }}>
          Une fois les résultats saisis à gauche, cliquez ici pour figer les classements, mettre à jour le système Elo et relancer le Monte Carlo sur le reste des matchs du tournoi.
        </p>

        <div style={{ marginTop: 'var(--space-6)', background: 'var(--surface-sunken)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)' }}>
          <h3 style={{ marginTop: 0, marginBottom: 'var(--space-4)', color: 'var(--brand-primary)' }}>🛠️ Paramètres du Moteur</h3>
          
          <div style={{ marginBottom: 'var(--space-3)' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Type de Lancement</label>
            <select value={simulationMode} onChange={e => setSimulationMode(e.target.value)} style={{ width: '100%', padding: '8px', background: '#1f2937', color: 'white', border: '1px solid var(--border-color)', borderRadius: '4px' }}>
              <option value="live">Live (Prend en compte les matchs joués)</option>
              <option value="pre_tournament">Pré-Tournoi (Repartir de zéro)</option>
            </select>
          </div>

          <div style={{ marginBottom: 'var(--space-3)' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Modèle de Simulation</label>
            <select value={modelVersion} onChange={e => setModelVersion(e.target.value)} style={{ width: '100%', padding: '8px', background: '#1f2937', color: 'white', border: '1px solid var(--border-color)', borderRadius: '4px' }}>
              <option value="V1">V1 - Poisson Indépendant (Classique)</option>
              <option value="V2">V2 - Calibré (Coupe du Monde)</option>
              <option value="V3">V3 - Dixon-Coles (Réaliste)</option>
              <option value="V4">V4 - Bayésien (Ajusté)</option>
              <option value="V5">V5 - Bivarié Covariables</option>
              <option value="ALL">TOUS - Comparer V1, V2 et V3</option>
            </select>
          </div>

          <div style={{ marginBottom: 'var(--space-3)' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Itérations Monte Carlo</label>
            <input type="number" value={nSims} onChange={e => setNSims(parseInt(e.target.value))} step="1000" style={{ width: '100%', padding: '8px', background: '#1f2937', color: 'white', border: '1px solid var(--border-color)', borderRadius: '4px' }} />
          </div>
        </div>

        <div style={{ marginTop: 'var(--space-4)', background: 'var(--surface-sunken)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)' }}>
          <h3 style={{ marginTop: 0, marginBottom: 'var(--space-4)', color: '#ec4899' }}>⚡ God Mode (Chocs Elo)</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>Ajoutez ou retirez des points Elo artificiellement avant de simuler (ex: blessure d'un joueur = -50).</p>
          
          <div style={{ display: 'flex', gap: '8px', marginBottom: 'var(--space-3)' }}>
            <select value={godModeTeam} onChange={e => setGodModeTeam(e.target.value)} style={{ flex: 1, padding: '8px', background: '#1f2937', color: 'white', border: '1px solid var(--border-color)', borderRadius: '4px' }}>
              {Array.from(new Set(matches.flatMap(m => [m.homeTeamId, m.awayTeamId]))).sort().map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <input type="number" value={godModeDelta} onChange={e => setGodModeDelta(parseInt(e.target.value) || 0)} style={{ width: '80px', padding: '8px', background: '#1f2937', color: 'white', border: '1px solid var(--border-color)', borderRadius: '4px' }} />
            <button onClick={handleAddDelta} style={{ padding: '8px 16px', background: '#ec4899', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>+</button>
          </div>

          {Object.entries(eloDeltas).map(([team, delta]) => (
            <div key={team} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(236, 72, 153, 0.1)', padding: '8px', borderRadius: '4px', marginBottom: '4px', border: '1px solid rgba(236, 72, 153, 0.2)' }}>
              <span style={{ fontWeight: 'bold', color: 'var(--text-primary)' }}>{team}</span>
              <span style={{ color: delta > 0 ? 'var(--status-success)' : 'var(--status-error)' }}>{delta > 0 ? '+' : ''}{delta} Elo</span>
              <button onClick={() => handleRemoveDelta(team)} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>✕</button>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 'var(--space-6)' }}>
          <button 
            onClick={handleSimulate} 
            disabled={isSimulating}
            style={{ 
              width: '100%', padding: 'var(--space-4)', 
              background: isSimulating ? 'var(--border-color)' : 'linear-gradient(45deg, var(--status-warning), #EF4444)', 
              color: 'white', border: 'none', borderRadius: 'var(--radius-md)', 
              cursor: isSimulating ? 'wait' : 'pointer', 
              fontWeight: 'bold', fontSize: '1.1rem', 
              display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 'var(--space-2)' 
            }}
          >
            {isSimulating ? (
              <><Loader2 size={20} className="spinner" /> Calcul en cours...</>
            ) : (
              <><Play size={20} /> Lancer le Monte Carlo</>
            )}
          </button>
        </div>

        {status && (
          <div style={{ marginTop: 'var(--space-4)', padding: 'var(--space-3)', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--status-success)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <CheckCircle size={18} /> {status}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminCockpit;
