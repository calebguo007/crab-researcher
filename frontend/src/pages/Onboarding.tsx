/**
 * Onboarding — 3步引导流
 * 
 * 注册后进入。收集产品信息，生成生物体，开始研究。
 * 不超过 2 分钟。每步都可跳过。
 */

import { useState } from 'react'
import { CreatureRenderer } from '../components/creature/CreatureRenderer'
import { generateCreature, SPECIES_CONFIG } from '../components/creature/types'
import type { CreatureState } from '../components/creature/types'
import { api } from '../lib/api'

interface OnboardingProps {
  userId: string
  onComplete: (creature: CreatureState, productData: any) => void
}

const PRODUCT_TYPES = [
  { value: 'saas', label: 'SaaS / Software', icon: '💻' },
  { value: 'tool', label: 'Developer Tool', icon: '🔧' },
  { value: 'ecommerce', label: 'E-commerce', icon: '🛒' },
  { value: 'community', label: 'Community / Social', icon: '👥' },
  { value: 'content', label: 'Content / Media', icon: '📝' },
  { value: 'education', label: 'Education', icon: '📚' },
  { value: 'creative', label: 'Creative / Design', icon: '🎨' },
  { value: 'finance', label: 'Finance / Fintech', icon: '💰' },
  { value: 'game', label: 'Gaming / Entertainment', icon: '🎮' },
  { value: 'other', label: 'Other', icon: '✨' },
]

const USER_GOALS = [
  { value: '100', label: '100 users' },
  { value: '500', label: '500 users' },
  { value: '1000', label: '1,000 users' },
  { value: '5000', label: '5,000 users' },
  { value: '10000', label: '10,000+' },
]

const BUDGETS = [
  { value: '0', label: '$0 (time only)' },
  { value: '100', label: '$100/mo' },
  { value: '500', label: '$500/mo' },
  { value: '1000', label: '$1,000+/mo' },
]

export function Onboarding({ userId, onComplete }: OnboardingProps) {
  const [step, setStep] = useState(1)
  const [productName, setProductName] = useState('')
  const [productUrl, setProductUrl] = useState('')
  const [productDesc, setProductDesc] = useState('')
  const [productType, setProductType] = useState('')
  const [userGoal, setUserGoal] = useState('')
  const [budget, setBudget] = useState('')
  const [loading, setLoading] = useState(false)
  const [creature, setCreature] = useState<CreatureState | null>(null)

  const handleStep1Next = () => {
    if (!productName.trim()) return
    setStep(2)
  }

  const handleStep2Next = () => {
    setStep(3)
    // 生成生物体
    const c = generateCreature(userId, productType || 'default')
    c.name = productName
    c.mood = 'waving'
    setCreature(c)
  }

  const handleFinish = async () => {
    setLoading(true)
    const productData = {
      name: productName,
      url: productUrl,
      description: productDesc,
      type: productType,
      goal_users: userGoal,
      monthly_budget: budget,
    }

    // 存入后端记忆
    try {
      await api('/agent/chat', {
        method: 'POST',
        body: JSON.stringify({
          message: `My product is called "${productName}". ${productDesc ? `It's ${productDesc}.` : ''} ${productUrl ? `URL: ${productUrl}.` : ''} Product type: ${productType || 'not specified'}. Goal: ${userGoal || 'not set'} users in 3 months. Monthly budget: $${budget || '0'}.`,
        }),
      })
    } catch (e) {
      // 即使 API 失败也继续（不阻塞 onboarding）
    }

    const c = creature || generateCreature(userId, productType || 'default')
    c.name = productName
    onComplete(c, productData)
  }

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center px-4">
      <div className="w-full max-w-md">

        {/* 进度指示 */}
        <div className="flex items-center gap-2 mb-8 justify-center">
          {[1, 2, 3].map(s => (
            <div key={s} className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                s === step ? 'bg-brand text-white' :
                s < step ? 'bg-brand/20 text-brand' :
                'bg-hover text-muted'
              }`}>
                {s < step ? '✓' : s}
              </div>
              {s < 3 && <div className={`w-8 h-px ${s < step ? 'bg-brand' : 'bg-border'}`} />}
            </div>
          ))}
        </div>

        {/* Step 1: 产品信息 */}
        {step === 1 && (
          <div className="text-center">
            <div className="text-4xl mb-3">🦀</div>
            <h2 className="text-xl font-bold text-primary mb-1">Tell me about your product</h2>
            <p className="text-sm text-muted mb-6">I'll research your market and build a growth plan.</p>

            <div className="space-y-3 text-left">
              <div>
                <label className="text-xs font-medium text-secondary mb-1 block">Product name *</label>
                <input
                  className="w-full"
                  placeholder="e.g., JobPilot"
                  value={productName}
                  onChange={e => setProductName(e.target.value)}
                  autoFocus
                />
              </div>
              <div>
                <label className="text-xs font-medium text-secondary mb-1 block">What does it do?</label>
                <input
                  className="w-full"
                  placeholder="e.g., AI resume optimizer for job seekers"
                  value={productDesc}
                  onChange={e => setProductDesc(e.target.value)}
                />
              </div>
              <div>
                <label className="text-xs font-medium text-secondary mb-1 block">Product URL (optional)</label>
                <input
                  className="w-full"
                  placeholder="https://..."
                  value={productUrl}
                  onChange={e => setProductUrl(e.target.value)}
                />
              </div>
              <div>
                <label className="text-xs font-medium text-secondary mb-1 block">Product type</label>
                <div className="grid grid-cols-2 gap-2">
                  {PRODUCT_TYPES.map(t => (
                    <button
                      key={t.value}
                      onClick={() => setProductType(t.value)}
                      className={`p-2.5 rounded-xl text-left text-sm border transition-all ${
                        productType === t.value
                          ? 'border-brand bg-brand/5 text-primary'
                          : 'border-border text-secondary hover:border-brand/30'
                      }`}
                    >
                      <span className="mr-1.5">{t.icon}</span>{t.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <button onClick={handleStep1Next} disabled={!productName.trim()}
              className="btn-primary w-full mt-6 !py-3 disabled:opacity-40">
              Next →
            </button>
          </div>
        )}

        {/* Step 2: 目标 */}
        {step === 2 && (
          <div className="text-center">
            <div className="text-4xl mb-3">🎯</div>
            <h2 className="text-xl font-bold text-primary mb-1">What's your growth goal?</h2>
            <p className="text-sm text-muted mb-6">This helps me calibrate the strategy.</p>

            <div className="space-y-4 text-left">
              <div>
                <label className="text-xs font-medium text-secondary mb-2 block">Target users in 3 months</label>
                <div className="flex flex-wrap gap-2">
                  {USER_GOALS.map(g => (
                    <button
                      key={g.value}
                      onClick={() => setUserGoal(g.value)}
                      className={`px-4 py-2 rounded-xl text-sm border transition-all ${
                        userGoal === g.value
                          ? 'border-brand bg-brand/5 text-brand font-medium'
                          : 'border-border text-secondary hover:border-brand/30'
                      }`}
                    >
                      {g.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-medium text-secondary mb-2 block">Monthly marketing budget</label>
                <div className="flex flex-wrap gap-2">
                  {BUDGETS.map(b => (
                    <button
                      key={b.value}
                      onClick={() => setBudget(b.value)}
                      className={`px-4 py-2 rounded-xl text-sm border transition-all ${
                        budget === b.value
                          ? 'border-brand bg-brand/5 text-brand font-medium'
                          : 'border-border text-secondary hover:border-brand/30'
                      }`}
                    >
                      {b.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button onClick={() => setStep(1)} className="btn-ghost flex-1 !py-3">← Back</button>
              <button onClick={handleStep2Next} className="btn-primary flex-1 !py-3">
                Next →
              </button>
            </div>

            <button onClick={handleStep2Next} className="text-xs text-muted mt-3 hover:text-secondary">
              Skip for now →
            </button>
          </div>
        )}

        {/* Step 3: 生物体揭晓 */}
        {step === 3 && creature && (
          <div className="text-center">
            <h2 className="text-xl font-bold text-primary mb-2">Meet your growth companion</h2>
            <p className="text-sm text-muted mb-6">Assembling your 13-expert growth team...</p>

            <div className="mb-4">
              <CreatureRenderer creature={creature} size={160} />
            </div>

            <div className="mb-6">
              <p className="text-lg font-bold" style={{ color: SPECIES_CONFIG[creature.species].baseColor }}>
                {SPECIES_CONFIG[creature.species].displayName}
              </p>
              <p className="text-sm text-muted mt-1">
                "{SPECIES_CONFIG[creature.species].description}"
              </p>
            </div>

            {/* 专家组装动画 */}
            <div className="space-y-1.5 text-left max-w-xs mx-auto mb-6">
              {[
                '🔍 Market Researcher', '💰 Economist', '📝 Content Strategist',
                '🎯 Social Media', '📢 Partnerships', '🤖 AI Distribution',
                '🧠 Psychologist', '📈 Product Growth', '📊 Data Analyst',
                '✍️ Copywriter', '🎨 Designer', '⚖️ Critic', '🎖️ Chief Growth Officer',
              ].map((expert, i) => (
                <div key={i} className="flex items-center gap-2 text-xs animate-fade-in"
                  style={{ animationDelay: `${i * 100}ms`, opacity: 0, animationFillMode: 'forwards' }}>
                  <span className="text-brand">✓</span>
                  <span className="text-secondary">{expert}</span>
                  <span className="text-muted">ready</span>
                </div>
              ))}
            </div>

            <button onClick={handleFinish} disabled={loading}
              className="btn-primary w-full !py-3 disabled:opacity-60">
              {loading ? 'Starting research...' : "Let's grow! →"}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
