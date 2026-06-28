import React from 'react';
import { BookOpen, Activity, Cpu, Calculator, ShieldAlert, GitCommit, Binary } from 'lucide-react';

const MathFormula = ({ children }: { children: React.ReactNode }) => (
  <div style={{ 
    background: 'rgba(0,0,0,0.5)', 
    padding: 'var(--space-4)', 
    borderRadius: 'var(--radius-md)', 
    fontFamily: '"Cambria Math", "Times New Roman", serif', 
    color: '#f8fafc',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderLeft: '4px solid #a78bfa',
    margin: 'var(--space-4) 0',
    overflowX: 'auto',
    textAlign: 'center',
    fontSize: '1.3rem',
    lineHeight: '2',
    boxShadow: 'inset 0 4px 6px rgba(0,0,0,0.3)'
  }}>
    <span style={{ fontStyle: 'italic' }}>{children}</span>
  </div>
);

const Fraction = ({ num, den }: { num: React.ReactNode, den: React.ReactNode }) => (
  <span style={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'center', verticalAlign: 'middle', margin: '0 6px', fontSize: '0.9em' }}>
    <span style={{ borderBottom: '1px solid currentColor', padding: '0 4px', lineHeight: '1.4' }}>{num}</span>
    <span style={{ padding: '0 4px', lineHeight: '1.4' }}>{den}</span>
  </span>
);

const Documentation = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      <div className="glass-panel" style={{ padding: 'var(--space-6)' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-4)', color: 'var(--brand-primary)' }}>
          <BookOpen size={28} /> Whitepaper & Architecture Mathématique
        </h2>
        <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: '1.1rem', marginBottom: 'var(--space-6)' }}>
          Ce document détaille l'architecture prédictive de notre plateforme. Conçu comme un moteur de Data Science professionnelle, le système repose sur un pipeline stochastique garantissant une quantification rigoureuse de l'incertitude (UQ - Uncertainty Quantification).
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          
          {/* PHASE 1: ELO */}
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: 'var(--space-5)', borderRadius: 'var(--radius-md)', borderLeft: '4px solid #3b82f6' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginTop: 0, color: '#3b82f6' }}>
              <Calculator size={22} /> Phase 1 : Système Elo & Espérance de Buts (xG)
            </h3>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)' }}>
              Le socle du moteur est le système <strong>Elo</strong>, un processus de Markov (sans mémoire) à somme nulle. L'écart de points Elo (ΔElo) est converti en probabilité logistique de victoire attendue (P<sub>exp</sub>) :
            </p>
            <MathFormula>
              P<sub>exp</sub> = <Fraction num="1" den={<>1 + 10<sup>(Elo<sub>B</sub> - Elo<sub>A</sub>) / Scale</sup></>} />
            </MathFormula>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)' }}>
              Ce ratio conditionne l'intensité offensive via le paramètre <em>Base Goals</em>, générant les estimateurs de Poisson <strong>λ</strong> (domicile) et <strong>μ</strong> (extérieur). L'algorithme apprend dynamiquement (Machine Learning on-line) en réajustant le Elo après chaque match selon la formule :<br/>
              <span style={{ fontFamily: 'monospace', color: '#9ca3af' }}>R<sub>new</sub> = R<sub>old</sub> + K &times; (Score<sub>réel</sub> - P<sub>exp</sub>)</span>
            </p>
          </div>

          {/* PHASE 2: DIXON-COLES */}
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: 'var(--space-5)', borderRadius: 'var(--radius-md)', borderLeft: '4px solid #10b981' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginTop: 0, color: '#10b981' }}>
              <Cpu size={22} /> Phase 2 : Modélisation Stochastique (Dixon-Coles)
            </h3>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)', marginBottom: 'var(--space-4)' }}>
              Les paramètres λ et μ alimentent des modèles statistiques de distribution des buts. La comparaison de nos architectures illustre l'évolution vers l'état de l'art industriel :
            </p>
            
            <h4 style={{ color: '#fff', marginBottom: '8px' }}><GitCommit size={16} style={{display:'inline', verticalAlign:'middle'}}/> Modèle V1 (Bivariate Poisson)</h4>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              Il suppose l'indépendance stricte des variables aléatoires X et Y (buts marqués).
            </p>
            <MathFormula>
              P(X=x, Y=y) = <Fraction num={<>e<sup>-λ</sup> &lambda;<sup>x</sup></>} den={<>x!</>} /> &times; <Fraction num={<>e<sup>-μ</sup> &mu;<sup>y</sup></>} den={<>y!</>} />
            </MathFormula>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              <em>Biais identifié :</em> Ce modèle souffre d'un biais d'indépendance, écrasant artificiellement la masse de probabilité sur les diagonales de la matrice de transition (les matchs nuls).
            </p>

            <h4 style={{ color: '#fff', marginTop: 'var(--space-4)', marginBottom: '8px' }}><ShieldAlert size={16} style={{display:'inline', verticalAlign:'middle'}}/> Modèle V3 (Dixon-Coles Correction)</h4>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              La publication fondatrice de Dixon et Coles (1997) démontre que les scores de football possèdent une <strong>covariance non-nulle</strong>, particulièrement à l'approche de la fin du match où les stratégies deviennent averses au risque. Le modèle introduit le facteur de dépendance τ(x,y) régi par le coefficient ρ &approx; -0.13.
            </p>
            <MathFormula>
              P<sub>DC</sub>(X=x, Y=y) = τ<sub>ρ</sub>(x,y) &times; P<sub>Poisson</sub>(X=x, Y=y)<br/><br/>
              <span style={{fontSize: '0.85rem', color: '#9ca3af', fontStyle: 'normal', display: 'inline-block', textAlign: 'left' }}>
                Où τ(0,0) = 1 - ρλμ<br/>
                τ(1,0) = 1 + ρλ<br/>
                τ(0,1) = 1 + ρμ<br/>
                τ(1,1) = 1 - ρ
              </span>
            </MathFormula>
          </div>

          {/* PHASE 3: EVALUATION */}
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: 'var(--space-5)', borderRadius: 'var(--radius-md)', borderLeft: '4px solid #8b5cf6' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginTop: 0, color: '#8b5cf6' }}>
              <Binary size={22} /> Phase 3 : Évaluation de Performance (Loss Functions)
            </h3>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)' }}>
              Afin de mesurer mathématiquement la supériorité du modèle V3 sur la V1, nous utilisons des fonctions de perte (Loss Functions) standards en Data Science, mesurant l'écart entre nos probabilités P<sub>i</sub> et la réalité binaire O<sub>i</sub> :
            </p>
            <MathFormula>
              Brier Score = <Fraction num="1" den="N" /> &sum; ( P<sub>i</sub> - O<sub>i</sub> )<sup>2</sup> <br/><br/>
              LogLoss = - <Fraction num="1" den="N" /> &sum; [ O<sub>i</sub> log(P<sub>i</sub>) + (1 - O<sub>i</sub>) log(1 - P<sub>i</sub>) ]
            </MathFormula>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              Le modèle Dixon-Coles (V3) réduit systématiquement le Brier Score en corrigeant la sous-estimation chronique des matchs nuls (réduction de l'entropie croisée).
            </p>
          </div>

          {/* PHASE 4: MONTE CARLO (Expanded) */}
          <div style={{ background: 'rgba(255,255,255,0.02)', padding: 'var(--space-5)', borderRadius: 'var(--radius-md)', borderLeft: '4px solid #f59e0b' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginTop: 0, color: '#f59e0b' }}>
              <Activity size={22} /> Phase 4 : Approximation de Monte Carlo & Convergence
            </h3>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)' }}>
              L'arbre du tournoi représentant un espace combinatoire quasi-infini (impossible à résoudre par équation fermée), nous évaluons l'intégrale stochastique globale par la méthode d'approximation de <strong>Monte Carlo</strong>. Le système procède à <em>N = 10 000</em> marches aléatoires (random walks) le long de l'arbre.
            </p>
            <h4 style={{ color: '#fff', marginTop: 'var(--space-4)' }}>Convergence Asymptotique (Théorème Central Limite)</h4>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              D'après la loi forte des grands nombres, la fréquence empirique (p&#770;) converge vers la probabilité théorique P. La variance de cet estimateur s'écrase selon l'inverse de la racine de N, ce qui nous permet d'extraire l'<strong>Erreur Standard (SE)</strong> :
            </p>
            <MathFormula>
              SE = <Fraction num={<>&radic;[ p&#770; (1 - p&#770;) ]</>} den={<>&radic;N</>} />
            </MathFormula>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              L'intervalle de confiance bilatéral strict à 95% est alors obtenu via le quantile de la loi normale (Z = 1.96) :
            </p>
            <MathFormula>
              CI<sub>95%</sub> = p&#770; &plusmn; ( 1.96 &times; SE )
            </MathFormula>
            
            <h4 style={{ color: '#fff', marginTop: 'var(--space-4)' }}>La "Règle de 3" (Détecteur de Miracles)</h4>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              <strong>Gestion des événements extrêmes :</strong> Si un événement n'est jamais observé (p&#770; = 0) sur nos 10 000 itérations (ex: San Marino remporte le tournoi), affirmer une probabilité absolue de 0% est une erreur statistique. Nous utilisons l'approximation de Poisson, dite <strong>Règle de 3</strong>. L'intervalle de confiance supérieur d'un événement non-observé devient :
            </p>
            <MathFormula>
              P<sub>max</sub> &approx; <Fraction num="3" den="N" />
            </MathFormula>
            <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
              Ainsi, avec N = 10 000, la probabilité maximale d'un miracle non-simulé est plafonnée à <strong>0.03%</strong>. C'est ce que notre système affiche pour les événements réputés impossibles.
            </p>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Documentation;
