/**
 * CrabRes — AI Growth Strategy Agent
 * 
 * 主应用入口。管理路由和全局状态。
 */

import { useState, useEffect } from 'react'
import { Surface } from './pages/Surface'
import { Chat } from './pages/Chat'
import { Plan } from './pages/Plan'
import { Onboarding } from './pages/Onboarding'
import { Landing } from './pages/Landing'
import { Settings } from './pages/Settings'
import { getToken, setToken, clearToken, setAuthExpiredHandler, api } from './lib/api'
import { generateCreature } from './components/creature/types'
import type { CreatureState } from './components/creature/types'

// ====== 登录页（简洁版，后续丰富）======

function AuthPage({ onLogin }: { onLogin: () => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [company, setCompany] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      if (mode === 'register') {
        const res = await api<{ access_token: string }>('/auth/register', {
          method: 'POST',
          body: JSON.stringify({ company_name: company || 'My Company', contact_email: email, password }),
        })
        setToken(res.access_token)
      } else {
        const res = await api<{ access_token: string }>('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        })
        setToken(res.access_token)
      }
      onLogin()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-3xl mb-2">🦀</div>
          <h1 className="text-xl font-bold text-primary tracking-tight">CrabRes</h1>
          <p className="text-sm text-muted mt-1">Your AI Growth Partner</p>
        </div>

        {/* 切换 */}
        <div className="flex gap-1 mb-6 p-1 rounded-xl bg-hover">
          <button onClick={() => setMode('login')}
            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${mode === 'login' ? 'bg-white shadow-sm text-primary' : 'text-muted'}`}>
            Log in
          </button>
          <button onClick={() => setMode('register')}
            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${mode === 'register' ? 'bg-white shadow-sm text-primary' : 'text-muted'}`}>
            Sign up
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-100 text-sm text-red-600">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          {mode === 'register' && (
            <input
              className="w-full"
              placeholder="Company or product name"
              value={company}
              onChange={e => setCompany(e.target.value)}
            />
          )}
          <input
            className="w-full"
            type="email"
            placeholder="Email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            required
          />
          <input
            className="w-full"
            type="password"
            placeholder="Password (6+ chars)"
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            minLength={6}
          />
          <button type="submit" disabled={loading}
            className="btn-primary w-full !py-3 disabled:opacity-60">
            {loading ? 'Loading...' : mode === 'login' ? 'Log in' : 'Create account'}
          </button>
        </form>

        <p className="text-xs text-muted text-center mt-6">
          {mode === 'login' ? "Don't have an account?" : 'Already have one?'}
          <button onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(null) }}
            className="text-brand ml-1 hover:underline">
            {mode === 'login' ? 'Sign up' : 'Log in'}
          </button>
        </p>

        {/* 背书 */}
        <div className="mt-8 text-center">
          <p className="text-xs text-muted">
            Powered by 13 AI growth experts · 18 research frameworks
          </p>
        </div>
      </div>
    </div>
  )
}

// ====== 主应用 ======

export default function App() {
  const [authed, setAuthed] = useState(!!getToken())
  const [showAuth, setShowAuth] = useState(false) // 显示登录还是 Landing
  const [onboarded, setOnboarded] = useState(!!localStorage.getItem('crabres_onboarded'))
  const [page, setPage] = useState<'surface' | 'chat' | 'plan' | 'settings'>('surface')
  const [userId, setUserId] = useState('default')
  const [creature, setCreature] = useState<CreatureState>(() =>
    generateCreature('default', 'saas')
  )

  useEffect(() => {
    setAuthExpiredHandler(() => setAuthed(false))
    // 初始化暗色模式
    const savedTheme = localStorage.getItem('crabres_theme')
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark')
    }
  }, [])

  // 登录后加载用户数据
  useEffect(() => {
    if (!authed) return
    api<any>('/auth/me').then(user => {
      setUserId(String(user.id))
      // 如果已 onboarded，直接加载生物体
      if (onboarded) {
        const savedType = localStorage.getItem('crabres_product_type') || 'saas'
        const c = generateCreature(String(user.id), savedType)
        c.name = localStorage.getItem('crabres_product_name') || user.company_name || 'My Product'
        c.mood = 'happy'
        c.totalUsers = 0
        c.growthRate = 0
        c.streakDays = 0
        setCreature(c)
      }
    }).catch(() => {})
  }, [authed, onboarded])

  if (!authed) {
    if (showAuth) {
      return <AuthPage onLogin={() => { setAuthed(true); setShowAuth(false) }} />
    }
    return <Landing onGetStarted={() => setShowAuth(true)} onLogin={() => setShowAuth(true)} />
  }

  // 未完成 onboarding
  if (!onboarded) {
    return (
      <Onboarding
        userId={userId}
        onComplete={(c, productData) => {
          setCreature(c)
          localStorage.setItem('crabres_onboarded', '1')
          localStorage.setItem('crabres_product_type', productData.type || 'saas')
          localStorage.setItem('crabres_product_name', productData.name || '')
          setOnboarded(true)
        }}
      />
    )
  }

  // TODO: 实现 Chat 和 Plan 页面
  if (page === 'chat') {
    return <Chat creature={creature} onBack={() => setPage('surface')} />
  }

  if (page === 'plan') {
    return <Plan creature={creature} onBack={() => setPage('surface')} />
  }

  if (page === 'settings') {
    return <Settings creature={creature} onBack={() => setPage('surface')} onLogout={() => { setAuthed(false); setOnboarded(false) }} />
  }

  return (
    <Surface
      creature={creature}
      onChat={() => setPage('chat')}
      onPlan={() => setPage('plan')}
      onSettings={() => setPage('settings')}
    />
  )
}
