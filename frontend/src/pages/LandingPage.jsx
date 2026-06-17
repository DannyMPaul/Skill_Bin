import { useEffect, useRef } from 'react';
import './LandingPage.css';

/* ── Small reusable subcomponents ──────────────────────────────────────────── */

function NavBar() {
  return (
    <nav className="landing-nav" role="navigation" aria-label="Main navigation">
      <div className="nav-inner">
        <div className="nav-logo">
          <span className="logo-icon" aria-hidden="true">⬡</span>
          <span className="logo-text">SkillBin</span>
        </div>
        <div className="nav-actions">
          <a href="/login" className="btn-secondary" id="nav-login-btn">
            Sign In
          </a>
        </div>
      </div>
    </nav>
  );
}

function HeroBadge() {
  return (
    <div className="hero-badge" role="note">
      <span className="badge-dot" aria-hidden="true" />
      AI-Powered Task Allocation Engine
    </div>
  );
}

function FeatureCard({ icon, title, description, index }) {
  return (
    <article
      className="feature-card glass-card"
      style={{ '--card-delay': `${index * 0.1}s` }}
      aria-label={title}
    >
      <div className="feature-icon" aria-hidden="true">{icon}</div>
      <h3 className="feature-title">{title}</h3>
      <p className="feature-description">{description}</p>
    </article>
  );
}

function StatItem({ value, label }) {
  return (
    <div className="stat-item">
      <span className="stat-value gradient-text">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

/* ── Animated background grid (canvas) ─────────────────────────────────────── */
function BackgroundGrid() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animFrame;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // Floating orb particles
    const particles = Array.from({ length: 25 }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      r: Math.random() * 2 + 0.5,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.5 + 0.1,
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw connecting lines between nearby particles
      particles.forEach((p, i) => {
        particles.slice(i + 1).forEach((q) => {
          const dx = p.x - q.x;
          const dy = p.y - q.y;
          const dist = Math.hypot(dx, dy);
          if (dist < 160) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = `rgba(99, 102, 241, ${0.08 * (1 - dist / 160)})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        });

        // Draw the particle
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(129, 140, 248, ${p.opacity})`;
        ctx.fill();

        // Update position
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      });

      animFrame = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animFrame);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="bg-canvas"
      aria-hidden="true"
    />
  );
}

/* ── Main landing page ─────────────────────────────────────────────────────── */
const FEATURES = [
  {
    icon: '📄',
    title: 'Resume → Skill Ratings',
    description:
      'Paste any resume. Claude extracts structured facts — experience, certifications, project complexity. A deterministic local algorithm converts those facts into auditable, reproducible skill ratings. No LLM arithmetic, ever.',
  },
  {
    icon: '⚡',
    title: 'The Bin: Smart Matching',
    description:
      'Overloaded employees are filtered out first. Then an Elo-style expected-success probability is computed per skill per candidate. Top 3 matches are returned with a transparent per-skill breakdown and current workload.',
  },
  {
    icon: '♟️',
    title: 'Chess-Style Skill Ratings',
    description:
      'Completing one hard task moves the needle more than ten easy ones. Difficulty-weighting falls out of the Elo math by construction — no fragile hand-tuned formula to drift out of sync.',
  },
  {
    icon: '📊',
    title: 'Difficulty-Weighted Leaderboard',
    description:
      'Rankings are sorted by rating, not task count. An employee who handles three hard projects outranks someone who coasted through ten trivial ones — the leaderboard reflects genuine contribution.',
  },
  {
    icon: '🔍',
    title: 'Full Audit Trail',
    description:
      'Every match recommendation, employer override, and rating change is persisted with before/after values and a timestamp. You can trace exactly why any rating is what it is.',
  },
  {
    icon: '🔒',
    title: 'Security-First Architecture',
    description:
      'Passwords hashed with bcrypt. JWT auth on every protected route. Parameterised queries throughout — no raw SQL. API keys live only in environment variables, never in source.',
  },
];

const STATS = [
  { value: 'Elo', label: 'Rating system' },
  { value: 'v1', label: 'Single-employer focus' },
  { value: '100%', label: 'Auditable ratings' },
  { value: '0', label: 'LLM-generated numbers' },
];

export default function LandingPage() {
  return (
    <div className="landing-root">
      <BackgroundGrid />
      <NavBar />

      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <main>
        <section className="hero-section" aria-labelledby="hero-heading">
          {/* Glow orbs */}
          <div className="glow-orb glow-orb--left" aria-hidden="true" />
          <div className="glow-orb glow-orb--right" aria-hidden="true" />

          <div className="hero-content">
            <HeroBadge />

            <h1 id="hero-heading" className="hero-title">
              Assign work to{' '}
              <span className="gradient-text">who's actually best.</span>
            </h1>

            <p className="hero-subtitle">
              SkillBin reads your team's resumes into structured skill ratings,
              then recommends the right person for every incoming task — filtered
              by workload, ranked by ability, explained in plain language.
              Completing a hard task moves the needle more than ten easy ones.
            </p>

            <div className="hero-actions">
              <a href="/login" className="btn-primary" id="hero-cta-btn">
                Get Started
                <span aria-hidden="true">→</span>
              </a>
              <a
                href="https://github.com"
                className="btn-secondary"
                id="hero-docs-btn"
                rel="noopener noreferrer"
              >
                View on GitHub
              </a>
            </div>

            {/* Stats row */}
            <div className="stats-row" role="list" aria-label="Key statistics">
              {STATS.map((s) => (
                <StatItem key={s.label} {...s} />
              ))}
            </div>
          </div>

          {/* Hero visual — rating card mockup */}
          <div className="hero-visual" aria-hidden="true">
            <div className="rating-card glass-card">
              <div className="rating-card__header">
                <span className="rating-card__avatar">PS</span>
                <div>
                  <div className="rating-card__name">Priya S.</div>
                  <div className="rating-card__role">Backend Engineer</div>
                </div>
                <span className="rating-card__badge">Active</span>
              </div>

              <div className="rating-card__skills">
                {[
                  { name: 'Python', rating: 1375, rd: 262 },
                  { name: 'AWS', rating: 1250, rd: 320 },
                  { name: 'PostgreSQL', rating: 1180, rd: 350 },
                ].map((skill) => (
                  <div key={skill.name} className="skill-row">
                    <span className="skill-name">{skill.name}</span>
                    <div className="skill-bar-track">
                      <div
                        className="skill-bar-fill"
                        style={{ width: `${((skill.rating - 800) / 1200) * 100}%` }}
                      />
                    </div>
                    <span className="skill-rating">{skill.rating}</span>
                  </div>
                ))}
              </div>

              <div className="rating-card__footer">
                <span className="match-label">⚡ Best match for</span>
                <span className="match-task">"Refactor payment service"</span>
              </div>

              {/* Animated ping */}
              <div className="card-ping" />
            </div>
          </div>
        </section>

        {/* ── Features ────────────────────────────────────────────────────── */}
        <section className="features-section" aria-labelledby="features-heading">
          <div className="section-header">
            <h2 id="features-heading" className="section-title">
              How <span className="gradient-text">the Bin</span> works
            </h2>
            <p className="section-subtitle">
              Every step is transparent, auditable, and difficulty-aware —
              by design, not by configuration.
            </p>
          </div>

          <div className="features-grid" role="list">
            {FEATURES.map((f, i) => (
              <FeatureCard key={f.title} {...f} index={i} />
            ))}
          </div>
        </section>

        {/* ── CTA banner ──────────────────────────────────────────────────── */}
        <section className="cta-section" aria-labelledby="cta-heading">
          <div className="cta-card glass-card">
            <h2 id="cta-heading" className="cta-title">
              Ready to let the algorithm decide?
            </h2>
            <p className="cta-subtitle">
              Set up takes minutes. Paste a resume, create a task, and watch
              the Bin recommend the right person — with the math shown.
            </p>
            <a href="/login" className="btn-primary" id="cta-final-btn">
              Open SkillBin
              <span aria-hidden="true">→</span>
            </a>
          </div>
        </section>
      </main>

      {/* ── Footer ────────────────────────────────────────────────────────── */}
      <footer className="landing-footer">
        <p className="footer-text">
          SkillBin — portfolio project ·{' '}
          <a href="https://github.com" rel="noopener noreferrer">GitHub</a>{' '}
          · MIT License
        </p>
        <p className="footer-note">
          v1: single-employer demo. Employee self-service and multi-tenancy are
          future work — see{' '}
          <a href="https://github.com" rel="noopener noreferrer">IDEA.md</a>.
        </p>
      </footer>
    </div>
  );
}
