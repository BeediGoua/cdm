import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import AdminCockpit from './pages/AdminCockpit';
import TeamDetail from './pages/TeamDetail';
import MatchPrediction from './pages/MatchPrediction';
import Deltas from './pages/Deltas';
import History from './pages/History';
import Scores from './pages/Scores';
import PowerRankings from './pages/PowerRankings';
import Bracket from './pages/Bracket';
import Upsets from './pages/Upsets';
import Documentation from './pages/Documentation';
import { Home, Settings, Activity, Swords, TrendingUp, History as HistoryIcon, Trophy, BarChart3, Zap, Map, BookOpen, Target } from 'lucide-react';

function App() {
  return (
    <Router>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <header className="navbar">
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
            <Activity color="var(--brand-primary)" />
            <h1 style={{ margin: 0, fontSize: '1.25rem', letterSpacing: '1px' }}>CDM 2026 Simulator</h1>
          </div>
          <nav style={{ display: 'flex', gap: 'var(--space-6)' }}>
            <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <Home size={18} /> Dashboard
            </Link>
            <Link to="/team/fra" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <Target size={18} /> Fiche Équipe
            </Link>
            <Link to="/prediction" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <Swords size={18} /> Labo H2H
            </Link>
            <Link to="/powerrankings" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <BarChart3 size={18} /> Bourse Elo
            </Link>
            <Link to="/bracket" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <Map size={18} /> Arbre
            </Link>
            <Link to="/upsets" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <Zap size={18} /> Miracles
            </Link>
            <Link to="/scores" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <Trophy size={18} /> Scores Live
            </Link>
            <Link to="/deltas" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <TrendingUp size={18} /> Deltas
            </Link>
            <Link to="/history" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <HistoryIcon size={18} /> Historique
            </Link>
            <Link to="/docs" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <BookOpen size={18} /> Docs
            </Link>
            <Link to="/admin" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', color: 'white', textDecoration: 'none', fontWeight: 500 }}>
              <Settings size={18} /> Admin Live
            </Link>
          </nav>
        </header>

        <main style={{ flex: 1, padding: 'var(--space-8) max(var(--space-4), 10%)', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/admin" element={<AdminCockpit />} />
            <Route path="/team/:teamId" element={<TeamDetail />} />
            <Route path="/prediction" element={<MatchPrediction />} />
            <Route path="/powerrankings" element={<PowerRankings />} />
            <Route path="/bracket" element={<Bracket />} />
            <Route path="/upsets" element={<Upsets />} />
            <Route path="/deltas" element={<Deltas />} />
            <Route path="/history" element={<History />} />
            <Route path="/scores" element={<Scores />} />
            <Route path="/docs" element={<Documentation />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
