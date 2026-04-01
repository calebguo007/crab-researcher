/**
 * Settings — 个人管理 + 暗色切换 + 通知配置
 */

import { useState, useEffect } from 'react'
import { CreatureRenderer } from '../components/creature/CreatureRenderer'
import type { CreatureState } from '../components/creature/types'
import { SPECIES_CONFIG } from '../components/creature/types'
import { clearToken } from '../lib/api'

interface SettingsProps {
  creature: CreatureState
  onBack: () => void
  onLogout: () => void
}

export function Settings({ creature, onBack, onLogout }: SettingsProps) {
  const [dark, setDark] = useState(() => document.documentElement.classList.contains('dark'))
  const [notifications, setNotifications] = useState({
    email: true,
    discord: false,
    slack: false,
    telegram: false,
  })

  const toggleDark = () => {
    const next = !dark
    setDark(next)
    if (next) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('crabres_theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('crabres_theme', 'light')
    }
  }

  const handleLogout = () => {
    clearToken()
    localStorage.removeItem('crabres_onboarded')
    localStorage.removeItem('crabres_product_type')
    localStorage.removeItem('crabres_product_name')
    onLogout()
  }

  const specConfig = SPECIES_CONFIG[creature.species]

  return (
    <div className="min-h-screen bg-surface bg-grid bg-noise max-w-lg mx-auto">
      {/* 头部 */}
      <div className="flex items-center gap-3 px-5 py-4 sticky top-0 z-10 bg-glass border-b border-border">
        <button onClick={onBack} className="p-2 rounded-lg hover:bg-hover transition-colors">
          <ArrowIcon />
        </button>
        <h1 className="font-heading font-semibold text-primary">Settings</h1>
      </div>

      <div className="px-5 py-6 space-y-6">
        {/* 生物体 + 用户信息 */}
        <div className="card p-6 text-center card-glow animate-fade-in">
          <div className="mb-3 animate-float">
            <CreatureRenderer creature={creature} size={100} />
          </div>
          <h2 className="font-heading font-bold text-lg" style={{ color: specConfig.baseColor }}>
            {specConfig.displayName}
          </h2>
          <p className="text-sm text-muted mt-1">{creature.name || 'Your product'}</p>
          <div className="flex items-center justify-center gap-4 mt-3 text-xs text-muted">
            <span>Lv.{creature.level}</span>
            <span>·</span>
            <span>{creature.streakDays}d streak</span>
            <span>·</span>
            <span>{creature.accessories.length} items</span>
          </div>
        </div>

        {/* 外观 */}
        <section className="animate-fade-in" style={{ animationDelay: '0.1s', opacity: 0 }}>
          <h3 className="font-heading font-semibold text-sm text-muted uppercase tracking-wider mb-3">Appearance</h3>
          <div className="card overflow-hidden">
            <div className="flex items-center justify-between p-4">
              <div>
                <p className="text-sm font-medium text-primary">Dark mode</p>
                <p className="text-xs text-muted">Easier on the eyes at night</p>
              </div>
              <button onClick={toggleDark}
                className={`w-12 h-7 rounded-full transition-colors relative ${dark ? 'bg-brand' : 'bg-gray-200'}`}>
                <div className={`w-5 h-5 rounded-full bg-white shadow-md absolute top-1 transition-transform ${dark ? 'translate-x-6' : 'translate-x-1'}`} />
              </button>
            </div>
          </div>
        </section>

        {/* 通知 */}
        <section className="animate-fade-in" style={{ animationDelay: '0.2s', opacity: 0 }}>
          <h3 className="font-heading font-semibold text-sm text-muted uppercase tracking-wider mb-3">Notifications</h3>
          <div className="card overflow-hidden divide-y divide-[var(--border-default)]">
            {[
              { key: 'email', label: 'Email digest', desc: 'Daily growth summary' },
              { key: 'discord', label: 'Discord', desc: 'Real-time alerts' },
              { key: 'slack', label: 'Slack', desc: 'Team notifications' },
              { key: 'telegram', label: 'Telegram', desc: 'Mobile alerts' },
            ].map(item => (
              <div key={item.key} className="flex items-center justify-between p-4">
                <div>
                  <p className="text-sm font-medium text-primary">{item.label}</p>
                  <p className="text-xs text-muted">{item.desc}</p>
                </div>
                <button
                  onClick={() => setNotifications(n => ({ ...n, [item.key]: !n[item.key as keyof typeof n] }))}
                  className={`w-12 h-7 rounded-full transition-colors relative ${notifications[item.key as keyof typeof notifications] ? 'bg-brand' : 'bg-gray-200'}`}>
                  <div className={`w-5 h-5 rounded-full bg-white shadow-md absolute top-1 transition-transform ${notifications[item.key as keyof typeof notifications] ? 'translate-x-6' : 'translate-x-1'}`} />
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* 项目 */}
        <section className="animate-fade-in" style={{ animationDelay: '0.3s', opacity: 0 }}>
          <h3 className="font-heading font-semibold text-sm text-muted uppercase tracking-wider mb-3">Projects</h3>
          <div className="card p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                style={{ background: specConfig.baseColor + '15', color: specConfig.baseColor }}>
                {creature.name?.[0]?.toUpperCase() || '🦀'}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-primary">{creature.name || 'My Product'}</p>
                <p className="text-xs text-muted">Active · {creature.totalUsers} users</p>
              </div>
              <span className="text-xs text-brand font-mono">Pro</span>
            </div>
          </div>
          <button className="w-full mt-2 p-3 rounded-md text-sm text-brand font-medium hover:bg-brand-light transition-colors text-center">
            + Add new project
          </button>
        </section>

        {/* 账户 */}
        <section className="animate-fade-in" style={{ animationDelay: '0.4s', opacity: 0 }}>
          <h3 className="font-heading font-semibold text-sm text-muted uppercase tracking-wider mb-3">Account</h3>
          <div className="card overflow-hidden divide-y divide-[var(--border-default)]">
            <button className="w-full p-4 text-left text-sm text-primary hover:bg-hover transition-colors">
              Manage subscription
            </button>
            <button className="w-full p-4 text-left text-sm text-primary hover:bg-hover transition-colors">
              API keys
            </button>
            <button className="w-full p-4 text-left text-sm text-primary hover:bg-hover transition-colors">
              Export data
            </button>
          </div>
        </section>

        {/* 退出 */}
        <div className="pt-2 animate-fade-in" style={{ animationDelay: '0.5s', opacity: 0 }}>
          <button onClick={handleLogout}
            className="w-full p-3 rounded-md text-sm text-error font-medium hover:bg-red-50 transition-colors text-center">
            Log out
          </button>
          <p className="text-xs text-muted text-center mt-4">CrabRes v2.0 · 13 experts · Made with 🦀</p>
        </div>
      </div>
    </div>
  )
}

function ArrowIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-muted"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
}
