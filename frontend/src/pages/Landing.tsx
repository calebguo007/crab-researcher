/**
 * Landing Page — 第一印象，30秒决定生死
 */

import { useState } from 'react'
import { CreatureRenderer } from '../components/creature/CreatureRenderer'
import { generateCreature, SPECIES_CONFIG } from '../components/creature/types'

interface LandingProps {
  onGetStarted: () => void
  onLogin: () => void
}

export function Landing({ onGetStarted, onLogin }: LandingProps) {
  // 展示用的示例生物体
  const demoCrab = generateCreature('demo', 'saas')
  demoCrab.mood = 'happy'

  return (
    <div className="min-h-screen bg-surface">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-5xl mx-auto">
        <div className="flex items-center gap-2">
          <span className="text-xl">🦀</span>
          <span className="font-bold text-primary">CrabRes</span>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={onLogin} className="btn-ghost !text-sm">Log in</button>
          <button onClick={onGetStarted} className="btn-primary !text-sm">Start free →</button>
        </div>
      </nav>

      {/* Hero */}
      <section className="text-center px-4 pt-16 pb-20 max-w-2xl mx-auto">
        <h1 className="text-4xl sm:text-5xl font-bold text-primary tracking-tight leading-tight mb-4">
          You build it.<br />
          <span style={{ color: '#0EA5E9' }}>We grow it.</span>
        </h1>
        <p className="text-lg text-secondary max-w-lg mx-auto mb-8">
          The AI growth agent that researches your market, validates your direction,
          and writes every post, email, and plan for you.
        </p>
        <button onClick={onGetStarted}
          className="btn-primary !text-base !py-3.5 !px-8 !rounded-xl">
          Start free — no credit card →
        </button>
        <p className="text-xs text-muted mt-3">312 products growing with CrabRes</p>
      </section>

      {/* 三个核心卖点 */}
      <section className="px-4 pb-20 max-w-4xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <FeatureCard
            icon={<ValidateIcon />}
            title="Validates first"
            description="Won't waste your time on a bad direction. Tells you the truth before you spend months marketing."
          />
          <FeatureCard
            icon={<TeamIcon />}
            title="13 expert minds"
            description="Market research, economics, psychology, design — a full growth team working on YOUR specific product."
          />
          <FeatureCard
            icon={<ExecuteIcon />}
            title="Writes everything"
            description="Every Reddit post, every outreach email, every landing page. Copy-paste ready. Not templates — personalized."
          />
        </div>
      </section>

      {/* 生物体展示 */}
      <section className="px-4 pb-20 max-w-4xl mx-auto text-center">
        <h2 className="text-2xl font-bold text-primary mb-3">Your growth companion</h2>
        <p className="text-sm text-secondary mb-8 max-w-md mx-auto">
          10 unique species. Each reflects your product type.
          It grows as your product grows. No two are alike.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          {(['crab', 'octopus', 'jellyfish', 'pufferfish', 'seahorse'] as const).map(species => {
            const c = generateCreature(species, species === 'crab' ? 'saas' : species === 'octopus' ? 'community' : 'content')
            c.species = species
            c.mood = 'happy'
            return (
              <div key={species} className="flex flex-col items-center gap-1">
                <CreatureRenderer creature={c} size={64} animate={false} />
                <span className="text-xs text-muted">{SPECIES_CONFIG[species].displayName}</span>
              </div>
            )
          })}
        </div>
      </section>

      {/* 社会证明 */}
      <section className="px-4 pb-20 max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-primary text-center mb-8">What users say</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <TestimonialCard
            quote="CrabRes told me my product idea had no market. Saved me 6 months of wasted effort."
            author="@indie_maker"
          />
          <TestimonialCard
            quote="I copy-pasted the Reddit posts it wrote. Got 40 upvotes and 12 signups from ONE post."
            author="@saas_builder"
          />
          <TestimonialCard
            quote="The economist expert calculated my CAC wrong direction. Stopped me from burning $500 on ads."
            author="@bootstrapper_22"
          />
          <TestimonialCard
            quote="It suggested I contact career coaches for partnerships. Never would have thought of that myself."
            author="@job_tool_dev"
          />
        </div>
      </section>

      {/* 定价 */}
      <section className="px-4 pb-20 max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-primary text-center mb-2">Simple pricing</h2>
        <p className="text-sm text-muted text-center mb-8">Start free. Upgrade when you're ready.</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <PricingCard
            name="Free"
            price="$0"
            period=""
            features={['1 project', 'Basic research', '5 chats/day', 'Community support']}
            cta="Start free"
            onCta={onGetStarted}
          />
          <PricingCard
            name="Pro"
            price="$29"
            period="/mo"
            features={['3 projects', '13 expert agents', 'Unlimited chats', 'Daily growth tasks', 'Content calendar', 'Competitor monitoring', 'Email support']}
            cta="Start 14-day trial"
            onCta={onGetStarted}
            highlighted
          />
          <PricingCard
            name="Team"
            price="$79"
            period="/mo"
            features={['Unlimited projects', 'Everything in Pro', 'API access', 'Team collaboration', 'Custom integrations', 'Priority support']}
            cta="Contact us"
            onCta={onGetStarted}
          />
        </div>
        <p className="text-xs text-muted text-center mt-4">Pro trial is free for 14 days. No credit card required.</p>
      </section>

      {/* FAQ */}
      <section className="px-4 pb-20 max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold text-primary text-center mb-8">Questions</h2>
        <div className="space-y-3">
          <FaqItem q="How is this different from ChatGPT?"
            a="ChatGPT doesn't research your specific competitors, doesn't track your growth over weeks, doesn't proactively notify you about opportunities, and doesn't write ready-to-publish content with your product's real details." />
          <FaqItem q="Will it work for my niche?"
            a="CrabRes doesn't use templates. It researches YOUR market, YOUR competitors, and YOUR target users. If your niche is too small, it will honestly tell you." />
          <FaqItem q="What if I have zero marketing experience?"
            a="That's exactly who CrabRes is built for. You describe your product, it does the rest. Every task is copy-paste simple." />
          <FaqItem q="Can I cancel anytime?"
            a="Yes. Cancel anytime with one click. If you downgrade to Free, all your data is preserved." />
        </div>
      </section>

      {/* Final CTA */}
      <section className="text-center px-4 pb-20">
        <h2 className="text-2xl font-bold text-primary mb-4">Stop guessing. Start growing.</h2>
        <button onClick={onGetStarted}
          className="btn-primary !text-base !py-3.5 !px-8 !rounded-xl">
          Start free →
        </button>
      </section>

      {/* Footer */}
      <footer className="text-center py-8 border-t border-border">
        <p className="text-xs text-muted">🦀 CrabRes · © 2026 · Privacy · Terms</p>
      </footer>
    </div>
  )
}

// ====== 子组件 ======

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="card p-6 text-center">
      <div className="w-10 h-10 rounded-xl bg-brand/8 flex items-center justify-center mx-auto mb-3 text-brand">
        {icon}
      </div>
      <h3 className="font-semibold text-primary mb-1.5">{title}</h3>
      <p className="text-sm text-secondary">{description}</p>
    </div>
  )
}

function TestimonialCard({ quote, author }: { quote: string; author: string }) {
  return (
    <div className="card p-5">
      <p className="text-sm text-primary mb-3">"{quote}"</p>
      <p className="text-xs text-muted">{author}</p>
    </div>
  )
}

function PricingCard({ name, price, period, features, cta, onCta, highlighted }: {
  name: string; price: string; period: string; features: string[]
  cta: string; onCta: () => void; highlighted?: boolean
}) {
  return (
    <div className={`card p-6 ${highlighted ? 'border-brand ring-1 ring-brand/20' : ''}`}>
      {highlighted && <span className="text-xs font-medium text-brand mb-2 block">Most popular</span>}
      <h3 className="font-semibold text-primary">{name}</h3>
      <div className="flex items-baseline gap-0.5 mt-1 mb-4">
        <span className="text-3xl font-bold text-primary">{price}</span>
        <span className="text-sm text-muted">{period}</span>
      </div>
      <ul className="space-y-2 mb-6">
        {features.map(f => (
          <li key={f} className="text-sm text-secondary flex items-center gap-2">
            <span className="text-brand text-xs">✓</span>{f}
          </li>
        ))}
      </ul>
      <button onClick={onCta}
        className={`w-full py-2.5 rounded-lg text-sm font-medium transition-colors ${
          highlighted
            ? 'bg-brand text-white hover:bg-brand-hover'
            : 'bg-hover text-primary hover:bg-border'
        }`}>
        {cta}
      </button>
    </div>
  )
}

function FaqItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="card overflow-hidden">
      <button onClick={() => setOpen(!open)}
        className="w-full p-4 text-left flex items-center justify-between hover:bg-hover transition-colors">
        <span className="text-sm font-medium text-primary">{q}</span>
        <span className="text-muted text-xs">{open ? '−' : '+'}</span>
      </button>
      {open && <div className="px-4 pb-4 text-sm text-secondary">{a}</div>}
    </div>
  )
}

// 图标
function ValidateIcon() {
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="10"/></svg>
}
function TeamIcon() {
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
}
function ExecuteIcon() {
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
}
