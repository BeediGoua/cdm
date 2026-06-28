import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getMatchPrediction, getSnapshotCurrent } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts';
import WhatIfSimulator from '../components/WhatIfSimulator';
import { Swords, Activity } from 'lucide-react';

const MatchPrediction = () => {
  const [homeTeam, setHomeTeam] = useState('fra');
  const [awayTeam, setAwayTeam] = useState('ned');
  const [selectedModelId, setSelectedModelId] = useState('V2');
  const [isCompareMode, setIsCompareMode] = useState(false);

  const { data: snapshot } = useQuery({
    queryKey: ['snapshot'],
    queryFn: getSnapshotCurrent
  });

  const { data: prediction, isLoading, refetch } = useQuery({
    queryKey: ['prediction', homeTeam, awayTeam],
    queryFn: () => getMatchPrediction(homeTeam, awayTeam),
    enabled: !!homeTeam && !!awayTeam
  });

  const handlePredict = (e: React.FormEvent) => {
    e.preventDefault();
    refetch();
  };

  const teams = snapshot?.results ? Object.keys(snapshot.results).map(id => ({
    id,
    name: snapshot.results[id].name || id
  })).sort((a, b) => a.name.localeCompare(b.name)) : [];

  const models = prediction?.models || [];
  const currentModel = models.find((m: any) => m.id === selectedModelId) || models[1]; // default to V2

  // Data for comparison chart
  const comparisonData = models.map((m: any) => ({
    name: m.name.split(' ')[0], // V1, V2, V3
    'Victoire Domicile': m.probabilities.homeWin * 100,
    'Nul': m.probabilities.draw * 100,
    'Victoire Extérieur': m.probabilities.awayWin * 100,
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div className="glass-panel" style={{ padding: 'var(--space-6)', position: 'relative', overflow: 'hidden' }}>
        {/* Effet lumineux de fond pour l'arène */}
        <div style={{ position: 'absolute', top: '-50%', left: '-20%', width: '140%', height: '140%', background: 'radial-gradient(circle, rgba(255,152,0,0.05) 0%, rgba(0,0,0,0) 70%)', zIndex: 0, pointerEvents: 'none' }}></div>
        
        <h2 style={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-6)', textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>
          <Swords color="var(--warning-color)" size={28} /> Le Laboratoire (Choc des Titans)
        </h2>

        {/* Formulaire de sélection d'équipes (L'Arène) */}
        <form onSubmit={handlePredict} style={{ position: 'relative', zIndex: 1, display: 'flex', gap: 'var(--space-4)', alignItems: 'center', marginBottom: 'var(--space-8)', padding: 'var(--space-4)', background: 'rgba(0,0,0,0.3)', borderRadius: 'var(--radius-lg)', border: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ flex: 1, textAlign: 'center' }}>
            <label style={{ display: 'block', marginBottom: 'var(--space-3)', color: 'var(--brand-primary)', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '2px' }}>Domicile</label>
            <select value={homeTeam} onChange={e => setHomeTeam(e.target.value)} style={{ width: '100%', padding: 'var(--space-4)', fontSize: '1.2rem', textAlign: 'center', fontWeight: 'bold', background: 'linear-gradient(to bottom, rgba(0, 230, 118, 0.1), rgba(0,0,0,0.5))', border: '1px solid var(--brand-primary)', color: 'white', borderRadius: 'var(--radius-md)', appearance: 'none', cursor: 'pointer' }}>
              {teams.map(t => <option key={`home-${t.id}`} value={t.id} style={{ background: '#1f2937', color: 'white' }}>{t.name}</option>)}
            </select>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-2)' }}>
            <div style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--warning-color)', textShadow: '0 0 15px rgba(255,152,0,0.8)' }}>VS</div>
            <button type="submit" style={{ padding: '8px 24px', background: 'var(--warning-color)', color: 'black', border: 'none', borderRadius: '20px', cursor: 'pointer', fontWeight: 900, textTransform: 'uppercase', letterSpacing: '1px', boxShadow: '0 4px 15px rgba(255,152,0,0.4)' }}>
              Combat
            </button>
          </div>

          <div style={{ flex: 1, textAlign: 'center' }}>
            <label style={{ display: 'block', marginBottom: 'var(--space-3)', color: 'var(--danger-color)', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '2px' }}>Extérieur</label>
            <select value={awayTeam} onChange={e => setAwayTeam(e.target.value)} style={{ width: '100%', padding: 'var(--space-4)', fontSize: '1.2rem', textAlign: 'center', fontWeight: 'bold', background: 'linear-gradient(to bottom, rgba(255, 23, 68, 0.1), rgba(0,0,0,0.5))', border: '1px solid var(--danger-color)', color: 'white', borderRadius: 'var(--radius-md)', appearance: 'none', cursor: 'pointer' }}>
              {teams.map(t => <option key={`away-${t.id}`} value={t.id} style={{ background: '#1f2937', color: 'white' }}>{t.name}</option>)}
            </select>
          </div>
        </form>

        {isLoading && <div>Calcul des prédictions en cours...</div>}

        {prediction && currentModel && (
          <>
            {/* Contrôles Modèle */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-6)', padding: 'var(--space-3)', background: 'rgba(0,0,0,0.3)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                {models.map((m: any) => (
                  <button 
                    key={m.id}
                    onClick={() => { setSelectedModelId(m.id); setIsCompareMode(false); }}
                    style={{ 
                      padding: 'var(--space-2) var(--space-4)', 
                      background: selectedModelId === m.id && !isCompareMode ? 'var(--brand-primary)' : 'transparent', 
                      color: 'white', 
                      border: '1px solid var(--brand-primary)', 
                      borderRadius: 'var(--radius-sm)', 
                      cursor: 'pointer' 
                    }}
                  >
                    {m.name}
                  </button>
                ))}
              </div>
              <button 
                onClick={() => setIsCompareMode(true)}
                style={{ 
                  display: 'flex', alignItems: 'center', gap: 'var(--space-2)',
                  padding: 'var(--space-2) var(--space-4)', 
                  background: isCompareMode ? 'var(--warning-color)' : 'transparent', 
                  color: isCompareMode ? 'black' : 'var(--warning-color)', 
                  border: '1px solid var(--warning-color)', 
                  borderRadius: 'var(--radius-sm)', 
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                <Activity size={18} /> Comparer les Modèles
              </button>
            </div>

            {/* Statistiques Pré-Match (Expected Goals) */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-8)', marginBottom: 'var(--space-6)' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', textTransform: 'uppercase' }}>xG {prediction.home.name}</div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--brand-primary)' }}>{currentModel.xgHome}</div>
              </div>
              <div style={{ textAlign: 'center', alignSelf: 'center', color: 'var(--text-secondary)' }}>
                Buts Attendus
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', textTransform: 'uppercase' }}>xG {prediction.away.name}</div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--danger-color)' }}>{currentModel.xgAway}</div>
              </div>
            </div>

            {isCompareMode ? (
              /* Vue Comparaison */
              <div>
                <h3 style={{ marginBottom: 'var(--space-4)', textAlign: 'center' }}>Sensibilité des Modèles (Victoire / Nul / Défaite)</h3>
                <div style={{ height: '350px', width: '100%' }}>
                  <ResponsiveContainer>
                    <BarChart data={comparisonData}>
                      <XAxis dataKey="name" stroke="var(--text-secondary)" />
                      <YAxis stroke="var(--text-secondary)" />
                      <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid var(--border-color)' }} />
                      <Legend />
                      <Bar dataKey="Victoire Domicile" fill="var(--brand-primary)" />
                      <Bar dataKey="Nul" fill="var(--text-accent)" />
                      <Bar dataKey="Victoire Extérieur" fill="var(--danger-color)" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : (
              /* Vue Modèle Unique (Probabilités & Scores Exacts) */
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 'var(--space-6)' }}>
                {/* Win/Draw/Loss Summary */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', justifyContent: 'center' }}>
                  <div style={{ textAlign: 'center', padding: 'var(--space-4)', background: 'rgba(0,0,0,0.3)', borderRadius: 'var(--radius-md)', border: '1px solid var(--brand-primary)' }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>VICTOIRE</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}>{prediction.home.name}</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--brand-primary)' }}>{(currentModel.probabilities.homeWin * 100).toFixed(1)}%</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: 'var(--space-4)', background: 'rgba(0,0,0,0.3)', borderRadius: 'var(--radius-md)', border: '1px solid var(--text-accent)' }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>MATCH NUL</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--text-accent)' }}>{(currentModel.probabilities.draw * 100).toFixed(1)}%</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: 'var(--space-4)', background: 'rgba(0,0,0,0.3)', borderRadius: 'var(--radius-md)', border: '1px solid var(--danger-color)' }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>VICTOIRE</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: 'var(--space-2)' }}>{prediction.away.name}</div>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--danger-color)' }}>{(currentModel.probabilities.awayWin * 100).toFixed(1)}%</div>
                  </div>
                </div>

                {/* Exact Scores Chart */}
                <div>
                  <h3 style={{ marginBottom: 'var(--space-4)', textAlign: 'center' }}>Scores Exacts les plus probables ({currentModel.name})</h3>
                  <div style={{ height: '350px', width: '100%' }}>
                    <ResponsiveContainer>
                      <BarChart data={currentModel.topExactScores.map((s: any) => ({
                        name: `${s.homeGoals} - ${s.awayGoals}`,
                        prob: s.probability * 100,
                        isHomeWin: s.homeGoals > s.awayGoals,
                        isDraw: s.homeGoals === s.awayGoals
                      }))}>
                        <XAxis dataKey="name" stroke="var(--text-secondary)" />
                        <YAxis stroke="var(--text-secondary)" />
                        <Tooltip 
                          formatter={(value: number) => [`${value.toFixed(1)}%`, 'Probabilité']}
                          contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid var(--border-color)' }}
                          cursor={{fill: 'rgba(255,255,255,0.05)'}}
                        />
                        <Bar dataKey="prob" radius={[4, 4, 0, 0]}>
                          {currentModel.topExactScores.map((s: any, index: number) => (
                            <Cell key={`cell-${index}`} fill={s.homeGoals > s.awayGoals ? 'var(--brand-primary)' : s.homeGoals === s.awayGoals ? 'var(--text-accent)' : 'var(--danger-color)'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <WhatIfSimulator defaultHome={homeTeam} defaultAway={awayTeam} />
    </div>
  );
};

export default MatchPrediction;
