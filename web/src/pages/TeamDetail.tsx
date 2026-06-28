import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getSnapshotCurrent, getTournamentMatches, getTournamentGroups, getTournamentBracket, getMatchPrediction, getDeltas } from '../api/client';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend, PieChart, Pie, Cell } from 'recharts';
import { ArrowLeft, TrendingUp, Activity, ShieldAlert, Target, GitMerge } from 'lucide-react';

const COLORS = ['#10b981', '#6b7280', '#ef4444']; // Win, Draw, Loss

const TeamDetail = () => {
  const { teamId } = useParams<{ teamId: string }>();
  const navigate = useNavigate();
  const [selectedModel, setSelectedModel] = useState<string>('ALL');
  const [deltaMetric, setDeltaMetric] = useState<string>('champion');

  const { data: snapshot, isLoading } = useQuery({ queryKey: ['snapshot'], queryFn: getSnapshotCurrent });
  const { data: matches } = useQuery({ queryKey: ['matches'], queryFn: getTournamentMatches });
  const { data: groups } = useQuery({ queryKey: ['groups'], queryFn: getTournamentGroups });
  const { data: bracket } = useQuery({ queryKey: ['bracket'], queryFn: getTournamentBracket });
  const { data: deltasData } = useQuery({ 
    queryKey: ['deltas', teamId, deltaMetric], 
    queryFn: () => getDeltas('COMPARE', deltaMetric, teamId),
    enabled: !!teamId 
  });

  const [predictions, setPredictions] = useState<any>({});

  useEffect(() => {
    if (matches && teamId) {
      const teamMatches = matches.filter((m: any) => m.type === 'group' && (m.homeTeamId === teamId || m.awayTeamId === teamId) && !m.played);
      teamMatches.forEach(async (m: any) => {
        if (!predictions[m.id]) {
          const pred = await getMatchPrediction(m.homeTeamId, m.awayTeamId);
          setPredictions((prev: any) => ({ ...prev, [m.id]: pred }));
        }
      });
    }
  }, [matches, teamId]);

  if (isLoading) return <div style={{ padding: '2rem' }}>Loading team details...</div>;
  if (!snapshot || !teamId || !snapshot.results[teamId]) {
    return <div style={{ padding: '2rem' }}>Team not found or snapshot missing.</div>;
  }

  const hasComparisons = !!snapshot.comparisons;
  const activeResults = (hasComparisons && selectedModel !== 'ALL') ? snapshot.comparisons[selectedModel] : snapshot.results;
  const team = activeResults[teamId] || snapshot.results[teamId];
  
  // Data for the Radar Chart
  let radarData = [];
  if (hasComparisons && selectedModel === 'ALL') {
    radarData = [
      { stage: '1/16', V1: snapshot.comparisons['V1'][teamId]?.roundOf32 * 100 || 0, V2: snapshot.comparisons['V2'][teamId]?.roundOf32 * 100 || 0, V3: snapshot.comparisons['V3'][teamId]?.roundOf32 * 100 || 0, V4: snapshot.comparisons['V4']?.[teamId]?.roundOf32 * 100 || 0, V5: snapshot.comparisons['V5']?.[teamId]?.roundOf32 * 100 || 0 },
      { stage: '1/8', V1: snapshot.comparisons['V1'][teamId]?.roundOf16 * 100 || 0, V2: snapshot.comparisons['V2'][teamId]?.roundOf16 * 100 || 0, V3: snapshot.comparisons['V3'][teamId]?.roundOf16 * 100 || 0, V4: snapshot.comparisons['V4']?.[teamId]?.roundOf16 * 100 || 0, V5: snapshot.comparisons['V5']?.[teamId]?.roundOf16 * 100 || 0 },
      { stage: '1/4', V1: snapshot.comparisons['V1'][teamId]?.quarterFinal * 100 || 0, V2: snapshot.comparisons['V2'][teamId]?.quarterFinal * 100 || 0, V3: snapshot.comparisons['V3'][teamId]?.quarterFinal * 100 || 0, V4: snapshot.comparisons['V4']?.[teamId]?.quarterFinal * 100 || 0, V5: snapshot.comparisons['V5']?.[teamId]?.quarterFinal * 100 || 0 },
      { stage: '1/2', V1: snapshot.comparisons['V1'][teamId]?.semiFinal * 100 || 0, V2: snapshot.comparisons['V2'][teamId]?.semiFinal * 100 || 0, V3: snapshot.comparisons['V3'][teamId]?.semiFinal * 100 || 0, V4: snapshot.comparisons['V4']?.[teamId]?.semiFinal * 100 || 0, V5: snapshot.comparisons['V5']?.[teamId]?.semiFinal * 100 || 0 },
      { stage: 'Finale', V1: snapshot.comparisons['V1'][teamId]?.final * 100 || 0, V2: snapshot.comparisons['V2'][teamId]?.final * 100 || 0, V3: snapshot.comparisons['V3'][teamId]?.final * 100 || 0, V4: snapshot.comparisons['V4']?.[teamId]?.final * 100 || 0, V5: snapshot.comparisons['V5']?.[teamId]?.final * 100 || 0 },
      { stage: 'Titre', V1: snapshot.comparisons['V1'][teamId]?.champion * 100 || 0, V2: snapshot.comparisons['V2'][teamId]?.champion * 100 || 0, V3: snapshot.comparisons['V3'][teamId]?.champion * 100 || 0, V4: snapshot.comparisons['V4']?.[teamId]?.champion * 100 || 0, V5: snapshot.comparisons['V5']?.[teamId]?.champion * 100 || 0 },
    ];
  } else {
    radarData = [
      { stage: '1/16', prob: team.roundOf32 * 100 },
      { stage: '1/8', prob: team.roundOf16 * 100 },
      { stage: '1/4', prob: team.quarterFinal * 100 },
      { stage: '1/2', prob: team.semiFinal * 100 },
      { stage: 'Finale', prob: team.final * 100 },
      { stage: 'Titre', prob: team.champion * 100 },
    ];
  }

  // Find Team's Group
  let teamGroup = '';
  if (groups) {
    for (const [groupName, groupTeams] of Object.entries(groups)) {
      if ((groupTeams as any[]).some(t => t.id === teamId)) {
        teamGroup = groupName;
        break;
      }
    }
  }

  // Knockout Crossings Logic
  let firstPlaceOpponent = 'Inconnu';
  let secondPlaceOpponent = 'Inconnu';
  if (teamGroup && bracket && bracket.roundOf32) {
    // Look for matches where 1[teamGroup] or 2[teamGroup] is playing
    const firstMatch = bracket.roundOf32.find((m: any) => m.homeSlot === `1${teamGroup}` || m.awaySlot === `1${teamGroup}`);
    const secondMatch = bracket.roundOf32.find((m: any) => m.homeSlot === `2${teamGroup}` || m.awaySlot === `2${teamGroup}`);
    
    if (firstMatch) {
      const oppSlot = firstMatch.homeSlot === `1${teamGroup}` ? firstMatch.awaySlot : firstMatch.homeSlot;
      // oppSlot is like 2B. We can find who is currently 2nd in group B
      const oppRank = parseInt(oppSlot[0]);
      const oppGroup = oppSlot.substring(1);
      if (groups && groups[oppGroup] && groups[oppGroup].length >= oppRank) {
         firstPlaceOpponent = groups[oppGroup][oppRank - 1].name;
      } else {
         firstPlaceOpponent = `Le ${oppRank}e du Groupe ${oppGroup}`;
      }
    }
    if (secondMatch) {
      const oppSlot = secondMatch.homeSlot === `2${teamGroup}` ? secondMatch.awaySlot : secondMatch.homeSlot;
      const oppRank = parseInt(oppSlot[0]);
      const oppGroup = oppSlot.substring(1);
      if (groups && groups[oppGroup] && groups[oppGroup].length >= oppRank) {
         secondPlaceOpponent = groups[oppGroup][oppRank - 1].name;
      } else {
         secondPlaceOpponent = `Le ${oppRank}e du Groupe ${oppGroup}`;
      }
    }
  }

  const teamMatches = matches?.filter((m: any) => m.type === 'group' && (m.homeTeamId === teamId || m.awayTeamId === teamId)) || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button onClick={() => navigate('/')} style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: 0, width: 'fit-content' }}>
          <ArrowLeft size={20} /> Retour au Dashboard
        </button>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--surface-sunken)', padding: '8px 12px', borderRadius: 'var(--radius-sm)' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Sélectionner une équipe :</span>
          <select 
            value={teamId}
            onChange={e => navigate(`/team/${e.target.value}`)}
            style={{ background: 'transparent', color: 'var(--brand-primary)', border: 'none', outline: 'none', cursor: 'pointer', fontSize: '1.1rem', fontWeight: 'bold' }}
          >
            {Object.keys(snapshot.results)
              .sort((a, b) => snapshot.results[a].name.localeCompare(snapshot.results[b].name))
              .map(id => (
              <option key={id} value={id} style={{ background: '#0f172a', color: 'white' }}>{snapshot.results[id].name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: 'var(--space-6)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '2.5rem', marginBottom: 'var(--space-2)' }}>{team.name}</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Hub d'Analyse Avancée & Probabilités</p>
        </div>
        
        {hasComparisons && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--surface-sunken)', padding: '8px 12px', borderRadius: 'var(--radius-sm)' }}>
            <Activity size={18} color="var(--brand-primary)" />
            <select 
              value={selectedModel} 
              onChange={e => setSelectedModel(e.target.value)}
              style={{ background: 'transparent', color: 'var(--text-primary)', border: 'none', outline: 'none', cursor: 'pointer', fontSize: '1.1rem', fontWeight: 'bold' }}
            >
              <option value="ALL" style={{ background: '#0f172a', color: 'white' }}>Comparaison (V1, V2, V3)</option>
              <option value="V1" style={{ background: '#0f172a', color: 'white' }}>Modèle V1 (Classique)</option>
              <option value="V2" style={{ background: '#0f172a', color: 'white' }}>Modèle V2 (Calibré)</option>
              <option value="V3" style={{ background: '#0f172a', color: 'white' }}>Modèle V3 (Dixon-Coles)</option>
              <option value="V4" style={{ background: '#0f172a', color: 'white' }}>Modèle V4 (Bayésien)</option>
              <option value="V5" style={{ background: '#0f172a', color: 'white' }}>Modèle V5 (Bivarié)</option>
            </select>
          </div>
        )}
      </div>

      {/* OPTION B : Incertitude (CI95) */}
      <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
          <ShieldAlert color="var(--brand-primary)" /> Intervalle de Confiance (Titre de Champion)
        </h2>
        <div style={{ display: 'flex', gap: 'var(--space-6)', flexWrap: 'wrap' }}>
          {(selectedModel === 'ALL' ? ['V1', 'V2', 'V3', 'V4', 'V5'] : [selectedModel]).map(model => {
            const mTeam = snapshot.comparisons ? snapshot.comparisons[model][teamId] : snapshot.results[teamId];
            if (!mTeam) return null;
            const prob = mTeam.champion * 100;
            const low = mTeam.champion_ci95_low * 100;
            const high = mTeam.champion_ci95_high * 100;
            const margin = (high - low) / 2;
            
            return (
              <div key={model} style={{ flex: 1, minWidth: '250px', background: 'rgba(255,255,255,0.02)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', marginBottom: 'var(--space-2)', color: model === 'V1' ? '#3b82f6' : model === 'V2' ? '#10b981' : model === 'V3' ? '#f59e0b' : model === 'V4' ? '#8b5cf6' : model === 'V5' ? '#ec4899' : 'var(--text-primary)' }}>
                  {model} <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>±{margin.toFixed(1)}%</span>
                </div>
                <div style={{ position: 'relative', height: '24px', background: 'rgba(0,0,0,0.5)', borderRadius: '12px', marginTop: 'var(--space-4)' }}>
                  {/* CI Range Bar */}
                  <div style={{ position: 'absolute', left: `${low}%`, width: `${high - low}%`, height: '100%', background: 'rgba(255,255,255,0.2)', borderRadius: '12px' }}></div>
                  {/* Exact Prob Marker */}
                  <div style={{ position: 'absolute', left: `${prob}%`, width: '4px', height: '32px', top: '-4px', background: 'white', borderRadius: '2px', boxShadow: '0 0 8px rgba(255,255,255,0.8)' }}></div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  <span>Pessimiste: {low.toFixed(1)}%</span>
                  <span style={{ fontWeight: 'bold', color: 'white' }}>{prob.toFixed(1)}%</span>
                  <span>Optimiste: {high.toFixed(1)}%</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }}>
        {/* Radar Probabilities */}
        <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
          <h2 style={{ marginBottom: 'var(--space-6)' }}>Radar de Progression</h2>
          <div style={{ height: '300px', width: '100%' }}>
            <ResponsiveContainer>
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="var(--border-color)" />
                <PolarAngleAxis dataKey="stage" stroke="var(--text-secondary)" />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="var(--border-color)" />
                <Tooltip 
                  formatter={(value: number) => [`${value.toFixed(1)}%`, 'Probabilité']}
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid var(--border-color)' }}
                />
                
                {hasComparisons && selectedModel === 'ALL' ? (
                  <>
                    <Legend />
                    <Radar name="V1" dataKey="V1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
                    <Radar name="V2" dataKey="V2" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
                    <Radar name="V3" dataKey="V3" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.2} />
                    <Radar name="V4" dataKey="V4" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.2} />
                    <Radar name="V5" dataKey="V5" stroke="#ec4899" fill="#ec4899" fillOpacity={0.2} />
                  </>
                ) : (
                  <Radar name={team.name} dataKey="prob" stroke="var(--brand-primary)" fill="var(--brand-primary)" fillOpacity={0.6} />
                )}
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* OPTION C: Croisements Théoriques */}
        <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
          <h2 style={{ marginBottom: 'var(--space-6)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <GitMerge color="var(--success-color)" /> Croisements en 16èmes (Si Groupe {teamGroup})
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', marginTop: 'var(--space-6)' }}>
            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)', borderLeft: '4px solid #10b981' }}>
              <h3 style={{ margin: 0, color: '#10b981', fontSize: '1.1rem' }}>Si {team.name} finit 1er du groupe</h3>
              <p style={{ marginTop: '8px', color: 'var(--text-secondary)' }}>Affrontera potentiellement :</p>
              <div style={{ fontSize: '1.4rem', fontWeight: 'bold', marginTop: '4px' }}>{firstPlaceOpponent}</div>
            </div>
            
            <div style={{ background: 'rgba(0, 0, 0, 0.3)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)', borderLeft: '4px solid #f59e0b' }}>
              <h3 style={{ margin: 0, color: '#f59e0b', fontSize: '1.1rem' }}>Si {team.name} finit 2ème du groupe</h3>
              <p style={{ marginTop: '8px', color: 'var(--text-secondary)' }}>Affrontera potentiellement :</p>
              <div style={{ fontSize: '1.4rem', fontWeight: 'bold', marginTop: '4px' }}>{secondPlaceOpponent}</div>
            </div>
            
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: 'var(--space-2)', fontStyle: 'italic' }}>
              * Ces adversaires sont calculés dynamiquement en fonction du classement live des autres groupes (Bracket de la CDM 2026).
            </p>
          </div>
        </div>
      </div>
      
      {/* OPTION E: Historical Evolution */}
      {deltasData && deltasData.history && deltasData.history.length > 0 && (
        <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
          <div style={{ marginBottom: 'var(--space-6)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', margin: 0 }}>
              <TrendingUp color="#3b82f6" /> Évolution des Probabilités
            </h2>
            <select 
              value={deltaMetric} 
              onChange={e => setDeltaMetric(e.target.value)}
              style={{ background: 'var(--surface-sunken)', color: 'var(--text-primary)', border: '1px solid rgba(255,255,255,0.1)', padding: '8px 12px', borderRadius: 'var(--radius-sm)', outline: 'none', cursor: 'pointer', fontSize: '1rem', fontWeight: 'bold' }}
            >
              <option value="roundOf32" style={{ background: '#0f172a' }}>Atteindre 1/16</option>
              <option value="roundOf16" style={{ background: '#0f172a' }}>Atteindre 1/8</option>
              <option value="quarterFinal" style={{ background: '#0f172a' }}>Atteindre 1/4</option>
              <option value="semiFinal" style={{ background: '#0f172a' }}>Atteindre 1/2</option>
              <option value="final" style={{ background: '#0f172a' }}>Atteindre Finale</option>
              <option value="champion" style={{ background: '#0f172a' }}>Gagner le Titre</option>
            </select>
          </div>
          <div style={{ height: '300px', width: '100%' }}>
            <ResponsiveContainer>
              <LineChart data={deltasData.history} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis dataKey="time" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" domain={[0, 'auto']} tickFormatter={(value) => `${value}%`} />
                <Tooltip 
                  formatter={(value: number) => [`${value.toFixed(1)}%`, 'Probabilité']}
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
                />
                <Legend />
                <Line type="monotone" name="V1 (Classique)" dataKey="V1" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                <Line type="monotone" name="V2 (Calibré)" dataKey="V2" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                <Line type="monotone" name="V3 (Dixon-Coles)" dataKey="V3" stroke="#f59e0b" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                <Line type="monotone" name="V4 (Bayésien)" dataKey="V4" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                <Line type="monotone" name="V5 (Bivarié)" dataKey="V5" stroke="#ec4899" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
      
      {/* OPTION D: Matrice des Adversaires Potentiels */}
      {team.potentialOpponents && Object.keys(team.potentialOpponents).length > 0 && (
        <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-4)' }}>
            <Target color="#8b5cf6" /> Adversaires Potentiels les plus probables (Knockouts)
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 'var(--space-6)' }}>
            Probabilité globale de rencontrer ces équipes lors des phases à élimination directe (calculé sur 10 000 univers parallèles).
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)' }}>
            {Object.entries(team.potentialOpponents)
              .sort((a: [string, any], b: [string, any]) => b[1] - a[1])
              .slice(0, 8)
              .map(([oppId, prob]: [string, any]) => {
                const oppName = snapshot.results[oppId]?.name || oppId;
                return (
                  <div key={oppId} style={{ background: 'var(--surface-sunken)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 'bold' }}>{oppName}</span>
                    <span style={{ color: '#8b5cf6', fontSize: '1.2rem', fontWeight: 'bold' }}>{(prob * 100).toFixed(1)}%</span>
                  </div>
                );
              })
            }
          </div>
        </div>
      )}

      {/* OPTION A: Analyse H2H Groupes */}
      <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-6)' }}>
          <Target color="#ec4899" /> Analyse des Matchs de Poule (H2H)
        </h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-4)' }}>
          {teamMatches.map((m: any) => {
            const isHome = m.homeTeamId === teamId;
            const opponentName = isHome ? m.awayTeamName : m.homeTeamName;
            
            if (m.played) {
               return (
                 <div key={m.id} style={{ background: 'rgba(16, 185, 129, 0.1)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                   <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '8px' }}>
                     <span>Match Joué</span> <span>{m.date}</span>
                   </div>
                   <div style={{ fontSize: '1.2rem', fontWeight: 'bold', textAlign: 'center', marginTop: '16px' }}>
                     {m.homeTeamName} {m.homeScore} - {m.awayScore} {m.awayTeamName}
                   </div>
                 </div>
               );
            }
            
            const predData = predictions[m.id];
            if (!predData) return <div key={m.id} style={{ padding: 'var(--space-4)', background: 'var(--surface-sunken)', borderRadius: 'var(--radius-md)' }}>Chargement des probabilités...</div>;
            
            // By default use V3 if ALL, otherwise use selectedModel
            const mToUse = selectedModel === 'ALL' ? 'V3' : selectedModel;
            const modelData = predData.models.find((mod: any) => mod.id === mToUse) || predData.models[0];
            
            const winProb = isHome ? modelData.probabilities.homeWin : modelData.probabilities.awayWin;
            const lossProb = isHome ? modelData.probabilities.awayWin : modelData.probabilities.homeWin;
            const drawProb = modelData.probabilities.draw;
            
            const pieData = [
              { name: 'Victoire', value: winProb * 100 },
              { name: 'Nul', value: drawProb * 100 },
              { name: 'Défaite', value: lossProb * 100 },
            ];

            return (
              <div key={m.id} style={{ background: 'var(--surface-sunken)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '8px' }}>
                  <span>Contre {opponentName}</span> <span>{m.date}</span>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <div style={{ width: '120px', height: '120px' }}>
                    <ResponsiveContainer>
                      <PieChart>
                        <Pie data={pieData} cx="50%" cy="50%" innerRadius={30} outerRadius={50} paddingAngle={2} dataKey="value" stroke="none">
                          {pieData.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                        </Pie>
                        <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  
                  <div style={{ flex: 1, paddingLeft: '16px' }}>
                    <div style={{ fontSize: '0.9rem', marginBottom: '8px', color: 'var(--text-secondary)' }}>Top Scores Exacts :</div>
                    {modelData.topExactScores.slice(0, 3).map((score: any, idx: number) => {
                      const hg = isHome ? score.homeGoals : score.awayGoals;
                      const ag = isHome ? score.awayGoals : score.homeGoals;
                      return (
                        <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', background: 'rgba(0,0,0,0.3)', padding: '4px 8px', borderRadius: '4px', marginBottom: '4px' }}>
                          <span style={{ fontWeight: 'bold' }}>{hg} - {ag}</span>
                          <span style={{ color: 'var(--brand-primary)' }}>{(score.probability * 100).toFixed(1)}%</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default TeamDetail;
