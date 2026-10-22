import { useState } from 'react'
import {
  ArrowDown, ArrowDownRight, ArrowRight, ArrowUpRight, Award, Bot, Braces,
  BriefcaseBusiness, Check, ChevronRight, Code2, ExternalLink, Github,
  Layers3, Linkedin, Mail, MapPin, Menu, Radio, Sparkles, X,
} from 'lucide-react'

const links = {
  linkedin: 'https://www.linkedin.com/in/ramagiri-pavan-4210341bb/',
  github: 'https://github.com/pavan9753',
  leetcode: 'https://leetcode.com/u/pavan9753/',
  gfg: 'https://www.geeksforgeeks.org/profile/ramagiripavan9753?tab=activity',
  hackerrank: 'https://www.hackerrank.com/profile/pavan9753',
  interviewbit: 'https://www.interviewbit.com/profile/pavan9753/',
}

const skills = ['Java', 'Spring Boot', 'Distributed systems', 'Apache Kafka', 'Google ADK', 'LangGraph', 'Python', 'React + TypeScript', 'MongoDB', 'Redis', 'AWS', 'Observability']

const experiences = [
  {
    date: 'MAY 2025 — PRESENT',
    title: 'Software Development Engineer II · Full Stack AI',
    company: "Lowe’s India",
    location: 'Bengaluru, India',
    points: [
      'Built conversational agent workflows for inventory replenishment and demand forecasting with Google ADK, LangGraph, FastAPI, and LLM tool calling.',
      'Designed event-driven demand forecast scheduling with Kafka, MongoDB, and Kubernetes CronJobs.',
      'Reduced agent response time by 2–3 seconds per call through prompt and payload optimization.',
      'Created product search across 7+ searchable dimensions with bounded pagination and sub-second response targets.',
    ],
    tags: ['Agentic AI', 'Google ADK', 'Kafka', 'MongoDB', 'Kubernetes'],
  },
  {
    date: 'JUN 2023 — APR 2025',
    title: 'Associate Software Engineer · Backend',
    company: "Lowe’s India",
    location: 'Bengaluru, India',
    points: [
      'Integrated checkout services with Spring Cloud OpenFeign, improving reliability and keeping p95 latency below 200 ms.',
      'Built OIDC / OAuth 2.0 SSO with JWT authentication and shared React + TypeScript product features end to end.',
      'Delivered centralized logs and monitoring dashboards that helped reduce issue resolution time by 30%.',
      'Contributed to exchange and eligibility workflows supporting 1,800+ stores and 99.9% uptime.',
    ],
    tags: ['Java', 'Spring Boot', 'Microservices', 'React', 'Grafana'],
  },
]

const profiles = [
  { label: 'LeetCode', detail: 'Algorithms & problem solving', href: links.leetcode, mark: 'LC' },
  { label: 'GeeksforGeeks', detail: 'Coding practice & articles', href: links.gfg, mark: 'Gf' },
  { label: 'HackerRank', detail: 'Skills & challenges', href: links.hackerrank, mark: 'Hr' },
  { label: 'InterviewBit', detail: 'Interview preparation', href: links.interviewbit, mark: 'Ib' },
]

function Eyebrow({ children }) { return <p className="eyebrow">{children}</p> }

function App() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  const email = 'ramagiripavan045@gmail.com'

  async function copyEmail() {
    try {
      await navigator.clipboard.writeText(email)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1800)
    } catch { window.location.href = `mailto:${email}` }
  }

  function closeMenu() { setMenuOpen(false) }

  return (
    <div className="site-shell">
      <div className="page-grain" aria-hidden="true" />
      <header className="topbar">
        <a className="wordmark" href="#top" onClick={closeMenu} aria-label="Pavan Ramagiri home">PR<span>.</span></a>
        <button className="menu-toggle" aria-label={menuOpen ? 'Close navigation' : 'Open navigation'} onClick={() => setMenuOpen(!menuOpen)}>{menuOpen ? <X /> : <Menu />}</button>
        <nav className={`nav-links ${menuOpen ? 'nav-open' : ''}`} aria-label="Main navigation">
          <a href="#work" onClick={closeMenu}>Work</a><a href="#about" onClick={closeMenu}>About</a><a href="#proof" onClick={closeMenu}>Recognition</a>
          <a href="#contact" onClick={closeMenu} className="nav-contact">Let’s talk <ArrowUpRight size={14} /></a>
        </nav>
      </header>

      <main id="top">
        <section className="hero section-wrap">
          <div className="hero-copy">
            <div className="availability"><span className="pulse-dot" /> SOFTWARE ENGINEER II <span className="availability-divider">/</span> BENGALURU, INDIA</div>
            <h1>I build things<br />that <span className="serif-accent">move</span> work<br className="mobile-break" /> forward<span className="hero-period">.</span></h1>
            <p className="hero-intro">Full-stack engineer shaping reliable systems and useful AI experiences — from the first API to the last pixel.</p>
            <div className="hero-actions">
              <a className="button button-dark" href="#work">Explore my work <ArrowDownRight size={17} /></a>
              <a className="text-link" href="./Pavan_R_SWE2.pdf" target="_blank" rel="noreferrer">View résumé <ArrowUpRight size={15} /></a>
            </div>
            <div className="hero-socials" aria-label="Social links">
              <a href={links.linkedin} target="_blank" rel="noreferrer" aria-label="LinkedIn"><Linkedin size={17} /></a>
              <a href={links.github} target="_blank" rel="noreferrer" aria-label="GitHub"><Github size={17} /></a>
              <span className="social-line" /><span>OPEN TO GREAT PROBLEMS</span>
            </div>
          </div>
          <div className="hero-art" aria-label="Abstract software engineering illustration">
            <div className="art-orbit orbit-one" /><div className="art-orbit orbit-two" />
            <div className="art-sun"><span>PR</span></div>
            <div className="art-label label-top"><span className="tiny-square" /> SYSTEMS THINKER</div>
            <div className="art-label label-bottom"><span className="tiny-square orange" /> PRODUCT BUILDER</div>
            <div className="art-float float-one"><Braces size={20} /><span>build<br />with intent</span></div>
            <div className="art-float float-two"><Radio size={17} /><span>always<br />observing</span></div>
            <div className="art-coordinate">17°23' N<br />78°29' E</div>
            <div className="art-vertical">ENGINEERING · CURIOSITY · IMPACT</div>
          </div>
          <a href="#intro" className="scroll-cue"><span>SCROLL TO EXPLORE</span><ArrowDown size={14} /></a>
        </section>

        <section className="intro-strip" id="intro">
          <div className="section-wrap intro-inner"><Eyebrow>A LITTLE CONTEXT</Eyebrow><p>Software engineer by craft.<br /><span>Problem solver by instinct.</span></p><div className="intro-note">I work across backend, frontend, and AI to turn complex workflows into dependable products people can actually use.</div></div>
        </section>

        <section className="section-wrap work-section" id="work">
          <div className="section-heading"><div><Eyebrow>SELECTED WORK</Eyebrow><h2>Proof in the<br /><span className="serif-accent">building.</span></h2></div><p className="section-aside">A few things I’ve helped make better, faster, and more useful.</p></div>
          <article className="feature-project">
            <div className="feature-visual">
              <div className="feature-visual-top"><span>01 / PERSONAL PROJECT</span><Bot size={19} /></div>
              <div className="terminal-card"><div className="terminal-chrome"><i /><i /><i /><span>atm-agent / session</span></div><div className="terminal-content"><div className="terminal-muted">GOOGLE ADK · TOOL-CALLING AGENT</div><p><b className="term-green">›</b> Show my recent transactions</p><div className="terminal-response"><span className="response-check"><Check size={13} /></span><span>Here are your last 3 transactions.<br /><em>Balance: ₹2,500.00</em></span></div><div className="terminal-rule" /><div className="terminal-foot"><span><span className="live-dot" /> SESSION SECURE</span><span>SQLITE · PYTHON</span></div></div></div>
              <div className="feature-caption"><span>AN EXPERIMENT IN RESPONSIBLE AI</span><span>GOOGLE ADK / PYTHON</span></div>
            </div>
            <div className="feature-content"><Eyebrow>01 — AGENTIC AI</Eyebrow><h3>A conversational ATM agent, built with guardrails.</h3><p>A small but complete banking simulator where an AI assistant can help with everyday tasks while safety stays in the service layer.</p><ul className="feature-points"><li><Check size={15} /> Confirmation before money-moving actions</li><li><Check size={15} /> SQLite ledger with atomic transactions</li><li><Check size={15} /> Input validation, PIN hashing, and lockout</li><li><Check size={15} /> Read-only currency reference via MCP</li></ul><div className="tag-list"><span>Google ADK</span><span>Python</span><span>SQLite</span><span>MCP</span></div><a className="project-link" href="./ATM_AI_AGENT/atm_agent/README.md" target="_blank" rel="noreferrer">Explore the project <ArrowRight size={16} /></a></div>
          </article>

          <div className="work-cards">
            <article className="work-card work-card-light"><div className="card-meta"><span>02 / PLATFORM ENGINEERING</span><Layers3 size={18} /></div><div className="mini-flow"><div className="flow-node">FORECAST<br />SIGNAL</div><ArrowRight size={17} /><div className="flow-node active-node">KAFKA<br />EVENT</div><ArrowRight size={17} /><div className="flow-node">SCHEDULED<br />ACTION</div></div><h3>Event-driven demand forecasting</h3><p>Automated purchase order scheduling and cancellation windows, orchestrated with Kafka, MongoDB, and Kubernetes.</p><div className="tag-list"><span>Kafka</span><span>MongoDB</span><span>Kubernetes</span></div></article>
            <article className="work-card work-card-dark"><div className="card-meta"><span>03 / DEVELOPER JOURNEY</span><Code2 size={18} /></div><div className="rank-mark"><span>#</span>349<small>GLOBAL RANK<br />CODEVITA · SEASON IX</small></div><h3>Built for the hard problems.</h3><p>Competitive programming taught me to find the simplest path through a complicated problem.</p><a href="https://drive.google.com/file/d/1un7rFIeg463vb5LJ-xa-1w78LIfV99-g/view" target="_blank" rel="noreferrer" className="light-link">See CodeVita proof <ExternalLink size={14} /></a></article>
          </div>
        </section>

        <section className="experience-section" id="about">
          <div className="section-wrap experience-inner"><div className="experience-heading"><Eyebrow>THE THROUGH LINE</Eyebrow><h2>Make complex<br /><span className="serif-accent">feel simple.</span></h2><p>Three years of building for real users, real scale, and the systems in between.</p><div className="experience-stat"><span>3<span>+</span></span><small>YEARS BUILDING<br />SOFTWARE</small></div></div>
            <div className="timeline">{experiences.map((item) => <article className="timeline-item" key={item.date}><div className="timeline-marker"><BriefcaseBusiness size={15} /></div><div className="timeline-date">{item.date}</div><h3>{item.title}</h3><div className="timeline-company">{item.company}<span>·</span><MapPin size={13} /> {item.location}</div><ul>{item.points.map((point) => <li key={point}>{point}</li>)}</ul><div className="tag-list">{item.tags.map((tag) => <span key={tag}>{tag}</span>)}</div></article>)}</div>
          </div>
        </section>

        <section className="section-wrap toolkit-section">
          <div className="toolkit-copy"><Eyebrow>MY TOOLKIT</Eyebrow><h2>Curious across<br /><span className="serif-accent">the stack.</span></h2><p>I like understanding the whole system: how the UI feels, how the service behaves, and how it holds up when things get busy.</p></div>
          <div className="toolkit-grid">{skills.map((skill, index) => <div className="toolkit-chip" key={skill}><span>{String(index + 1).padStart(2, '0')}</span>{skill}<ChevronRight size={14} /></div>)}</div>
        </section>

        <section className="recognition-section" id="proof"><div className="section-wrap recognition-inner"><div className="section-heading recognition-heading"><div><Eyebrow>RECOGNITION & CREDENTIALS</Eyebrow><h2>Good work<br /><span className="serif-accent">gets noticed.</span></h2></div><p className="section-aside">A few milestones I’m proud of. Click a certificate to view it full size.</p></div>
          <div className="recognition-grid"><a className="certificate-card" href="./Certificates/induvidual_excellence_award.png" target="_blank" rel="noreferrer"><div className="certificate-image"><img src="./Certificates/induvidual_excellence_award.png" alt="Lowe's Spot Award certificate awarded to Pavan Ramagiri" /><span className="image-open"><ArrowUpRight size={16} /></span></div><div className="certificate-info"><span>LOWE’S INDIA · SPOT AWARD</span><h3>Individual Excellence</h3><p>Recognized for taking action at the right time and getting the job done.</p></div></a>
            <a className="certificate-card" href="./Certificates/team_excellence.png" target="_blank" rel="noreferrer"><div className="certificate-image"><img src="./Certificates/team_excellence.png" alt="Lowe's Team Excellence Award certificate awarded to Pavan Ramagiri" /><span className="image-open"><ArrowUpRight size={16} /></span></div><div className="certificate-info"><span>LOWE’S INDIA · TEAM AWARD</span><h3>Team Excellence</h3><p>Recognized for outstanding project contributions and shared results.</p></div></a>
            <div className="achievement-list"><div className="achievement"><span className="achievement-icon"><Award size={18} /></span><div><span>COMPETITIVE PROGRAMMING</span><h3>Global Rank 349 · TCS CodeVita</h3><a href="https://drive.google.com/file/d/1un7rFIeg463vb5LJ-xa-1w78LIfV99-g/view" target="_blank" rel="noreferrer">View certificate <ArrowUpRight size={13} /></a></div></div><div className="achievement"><span className="achievement-icon"><Sparkles size={18} /></span><div><span>HACKATHON · LOWE’S INDIA</span><h3>Top 15 finish · secured PPO</h3><a href="https://drive.google.com/file/d/1jL_3-_li5p_4-KOFg2sp5egObBiAVOPO/view" target="_blank" rel="noreferrer">View proof of work <ArrowUpRight size={13} /></a></div></div><div className="achievement"><span className="achievement-icon"><Code2 size={18} /></span><div><span>PROBLEM SOLVING</span><h3>GeeksforGeeks certificate</h3><a href="https://media.geeksforgeeks.org/courses/certificates/e665e2c2e3676ef521343f8124ab2ffd.pdf" target="_blank" rel="noreferrer">View certificate <ArrowUpRight size={13} /></a></div></div></div>
          </div>
        </div></section>

        <section className="section-wrap profiles-section"><div className="profiles-heading"><div><Eyebrow>OUTSIDE THE DAY JOB</Eyebrow><h2>Find me<br /><span className="serif-accent">around the web.</span></h2></div><a href={links.github} target="_blank" rel="noreferrer" className="button button-outline"><Github size={16} /> More on GitHub <ArrowUpRight size={15} /></a></div><div className="profiles-list">{profiles.map((profile) => <a href={profile.href} target="_blank" rel="noreferrer" className="profile-row" key={profile.label}><span className="profile-mark">{profile.mark}</span><span className="profile-name">{profile.label}</span><span className="profile-detail">{profile.detail}</span><ArrowUpRight size={16} /></a>)}</div></section>

        <section className="contact-section" id="contact"><div className="section-wrap contact-inner"><div className="contact-topline"><span><span className="pulse-dot" /> OPEN TO WHAT’S NEXT</span><span>01 — LET’S CONNECT</span></div><h2>Have a good<br />problem to <span className="serif-accent">solve?</span></h2><p>I’m always glad to meet thoughtful people building useful things.</p><div className="contact-actions"><a className="button button-cream" href={`mailto:${email}`}><Mail size={16} /> Say hello <ArrowUpRight size={15} /></a><button className="contact-email" onClick={copyEmail}>{copied ? <Check size={14} /> : <span>{email}</span>} {copied ? 'Copied' : <span className="copy-hint">COPY</span>}</button></div><div className="contact-socials"><a href={links.linkedin} target="_blank" rel="noreferrer"><Linkedin size={15} /> LinkedIn <ArrowUpRight size={13} /></a><a href={links.github} target="_blank" rel="noreferrer"><Github size={15} /> GitHub <ArrowUpRight size={13} /></a></div><div className="contact-spark" aria-hidden="true">✳</div></div></section>
      </main>
      <footer className="footer section-wrap"><a className="wordmark" href="#top">PR<span>.</span></a><span>DESIGNED & BUILT WITH CARE · © {new Date().getFullYear()} PAVAN RAMAGIRI</span><a href="#top" className="back-top">BACK TO TOP <ArrowUpRight size={13} /></a></footer>
    </div>
  )
}

export default App
