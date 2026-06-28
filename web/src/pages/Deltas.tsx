import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Clock, Settings, Filter, Activity, Users } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = [
  '#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', 
  '#14b8a6', '#f43f5e', '#84cc16', '#06b6d4', '#6366f1', '#d946ef'
];

const METRICS = [
  { id: 'roundOf32', label: 'Sortie de poule (16es)' },
  { id: 'roundOf16', label: 'Atteindre les 8es' },
  { id: 'quarterFinal', label: 'Atteindre les Quarts' },
  { id: 'semiFinal', label: 'Atteindre les Demies' },
  { id: 'final', label: 'Atteindre la Finale' },
  { id: 'champion', label: 'Gagner la Coupe' },
];

const Deltas: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [mode, setMode] = useState<'recent' | 'global'>('recent');
  const [metric, setMetric] = useState<string>('champion');
  const [model, setModel] = useState<string>('V3');
  const [compareTeam, setCompareTeam] = useState<string>('fra');
  const [selectedTeams, setSelectedTeams] = useState<string[]>([]);
  const [showSelector, setShowSelector] = useState(false);

  useEffect(() => {
    setData(null);
    fetch(`http://localhost:8000/api/snapshots/deltas?metric=${metric}&model=${model}&team=${compareTeam}`)
      .then(res => res.json())
      .then(d => {
        setData(d);
        if (d.topTeams) {
          setSelectedTeams(d.topTeams);
        }
      })
      .catch(console.error);
  }, [metric, model, compareTeam]);

  const toggleTeam = (team: string) => {
    setSelectedTeams(prev => 
      prev.includes(team) ? prev.filter(t => t !== team) : [...prev, team]
    );
  };

  if (!data) return <div style={{ padding: '2rem' }}>Chargement des deltas...</div>;
  if (data.message) return <div style={{ padding: '2rem' }}>{data.message}</div>;

  const currentData = data[mode];
  const topWinner = currentData ? currentData.topWinner : null;
  const topLoser = currentData ? currentData.topLoser : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <h2>Évolution & Deltas</h2>
        
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--surface-sunken)', padding: '4px 8px', borderRadius: 'var(--radius-sm)' }}>
            <Activity size={16} color="var(--brand-primary)" />
            <select 
              value={model} 
              onChange={e => setModel(e.target.value)}
              style={{ background: 'transparent', color: 'var(--text-primary)', border: 'none', outline: 'none', cursor: 'pointer', fontSize: '1rem', fontWeight: 'bold' }}
            >
              <option value="V1" style={{ background: '#0f172a', color: 'white' }}>Modèle V1 (Classique)</option>
              <option value="V2" style={{ background: '#0f172a', color: 'white' }}>Modèle V2 (Calibré)</option>
              <option value="V3" style={{ background: '#0f172a', color: 'white' }}>Modèle V3 (Dixon-Coles)</option>
              <option value="V4" style={{ background: '#0f172a', color: 'white' }}>Modèle V4 (Bayésien)</option>
              <option value="V5" style={{ background: '#0f172a', color: 'white' }}>Modèle V5 (Bivarié)</option>
              <option value="COMPARE" style={{ background: '#0f172a', color: 'white' }}>Comparaison (1 Équipe)</option>
            </select>
          </div>

          {model === 'COMPARE' && data.availableTeams && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--surface-sunken)', padding: '4px 8px', borderRadius: 'var(--radius-sm)' }}>
              <Users size={16} color="var(--warning-color)" />
              <select 
                value={compareTeam} 
                onChange={e => setCompareTeam(e.target.value)}
                style={{ background: 'transparent', color: 'var(--text-primary)', border: 'none', outline: 'none', cursor: 'pointer', fontSize: '1rem', fontWeight: 'bold' }}
              >
                {data.availableTeams.map((t: any) => (
                  <option key={t.id} value={t.id} style={{ background: '#0f172a', color: 'white' }}>{t.name}</option>
                ))}
              </select>
            </div>
          )}

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--surface-sunken)', padding: '4px 8px', borderRadius: 'var(--radius-sm)' }}>
            <Filter size={16} color="var(--text-secondary)" />
            <select 
              value={metric} 
              onChange={e => setMetric(e.target.value)}
              style={{ background: 'transparent', color: 'var(--text-primary)', border: 'none', outline: 'none', cursor: 'pointer', fontSize: '1rem', fontWeight: 'bold' }}
            >
              {METRICS.map(m => <option key={m.id} value={m.id} style={{ background: '#0f172a', color: 'white' }}>{m.label}</option>)}
            </select>
          </div>

          {model !== 'COMPARE' && (
            <div style={{ display: 'flex', background: 'var(--surface-sunken)', borderRadius: 'var(--radius-sm)', padding: '4px' }}>
              <button 
                onClick={() => setMode('recent')}
                style={{ padding: '6px 12px', background: mode === 'recent' ? 'var(--brand-primary)' : 'transparent', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: mode === 'recent' ? 'bold' : 'normal' }}
              >
                Dernier Match
              </button>
              <button 
                onClick={() => setMode('global')}
                style={{ padding: '6px 12px', background: mode === 'global' ? 'var(--brand-primary)' : 'transparent', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: mode === 'global' ? 'bold' : 'normal' }}
              >
                Depuis le Début
              </button>
            </div>
          )}
        </div>
      </div>

      {model !== 'COMPARE' && (
        <div style={{ display: 'grid', gap: 'var(--space-4)', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
          <div className="card" style={{ padding: 'var(--space-6)', background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--status-success)', marginBottom: 'var(--space-2)' }}>
              <TrendingUp size={24} />
              <h3 style={{ margin: 0 }}>Top Gagnant</h3>
            </div>
            {topWinner ? (
              <>
                <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{topWinner.name}</div>
                <div style={{ fontSize: '1.25rem', color: 'var(--status-success)', fontWeight: 600 }}>+{(topWinner.delta * 100).toFixed(1)}%</div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Passe de {(topWinner.old * 100).toFixed(1)}% à {(topWinner.new * 100).toFixed(1)}%</div>
              </>
            ) : <p>Aucun changement</p>}
          </div>

          <div className="card" style={{ padding: 'var(--space-6)', background: 'rgba(239, 68, 68, 0.05)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'var(--status-danger)', marginBottom: 'var(--space-2)' }}>
              <TrendingDown size={24} />
              <h3 style={{ margin: 0 }}>Top Perdant</h3>
            </div>
            {topLoser ? (
              <>
                <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{topLoser.name}</div>
                <div style={{ fontSize: '1.25rem', color: 'var(--status-danger)', fontWeight: 600 }}>{(topLoser.delta * 100).toFixed(1)}%</div>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Passe de {(topLoser.old * 100).toFixed(1)}% à {(topLoser.new * 100).toFixed(1)}%</div>
              </>
            ) : <p>Aucun changement</p>}
          </div>
        </div>
      )}

      <div className="card" style={{ padding: 'var(--space-6)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-6)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <Clock size={20} color="var(--brand-primary)" />
            <h3 style={{ margin: 0 }}>
              {model === 'COMPARE' ? `Comparaison des Modèles pour ${data.availableTeams.find((t:any) => t.id === compareTeam)?.name || compareTeam}` : 'Évolution des Favoris'}
            </h3>
          </div>
          {model !== 'COMPARE' && (
            <button 
              onClick={() => setShowSelector(!showSelector)}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--surface-sunken)', border: '1px solid var(--border-color)', color: 'var(--text-primary)', padding: '6px 12px', borderRadius: 'var(--radius-sm)', cursor: 'pointer' }}
            >
              <Settings size={16} /> Personnaliser les équipes
            </button>
          )}
        </div>

        {showSelector && model !== 'COMPARE' && (
          <div style={{ background: 'var(--surface-sunken)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-6)', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {data.allTeams.map((team: string) => {
              const isSelected = selectedTeams.includes(team);
              return (
                <div 
                  key={team}
                  onClick={() => toggleTeam(team)}
                  style={{ 
                    padding: '4px 10px', fontSize: '0.875rem', borderRadius: '20px', 
                    cursor: 'pointer', userSelect: 'none', transition: 'all 0.2s',
                    background: isSelected ? 'var(--brand-primary)' : 'rgba(255,255,255,0.05)',
                    color: isSelected ? 'white' : 'var(--text-secondary)',
                    border: isSelected ? '1px solid var(--brand-primary)' : '1px solid var(--border-color)'
                  }}
                >
                  {team}
                </div>
              );
            })}
          </div>
        )}
        
        <div style={{ width: '100%', height: 400 }}>
          <ResponsiveContainer>
            <LineChart data={data.history} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="time" stroke="var(--text-secondary)" />
              <YAxis unit="%" stroke="var(--text-secondary)" />
              <Tooltip 
                contentStyle={{ background: 'var(--surface-raised)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}
                itemStyle={{ fontWeight: 'bold' }}
              />
              <Legend />
              {selectedTeams.map((teamName: string, i: number) => (
                <Line 
                  key={teamName} 
                  type="monotone" 
                  dataKey={teamName} 
                  stroke={model === 'COMPARE' && teamName === 'V1' ? '#3b82f6' : model === 'COMPARE' && teamName === 'V2' ? '#10b981' : model === 'COMPARE' && teamName === 'V3' ? '#f59e0b' : COLORS[i % COLORS.length]} 
                  strokeWidth={3}
                  activeDot={{ r: 8 }} 
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
};

export default Deltas;
