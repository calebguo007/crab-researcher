/**
 * Dashboard — Agent 控制中心
 * 
 * 集成：目标追踪、周报、通知、审批队列、SSE 实时推送
 * 风格：与 Surface 一致的暖白卡片风格
 */

import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import type { CreatureState } from '../components/creature/types'
import { api } from '../lib/api'
import { ArrowLeftIcon, BellIcon, TargetIcon, CalendarIcon, ShieldCheckIcon, ZapIcon, SearchSparkIcon, NewsIcon, ChartBarIcon, BrainIcon, GearIcon, PinIcon, LockIcon, CircleCheckIcon, AlertTriangleIcon, RocketIcon } from '../components/ui/Icons'

interface DashboardProps {
  creature: CreatureState
  onBack: () => void
}

type Tab = 'overview' | 'notifications' | 'approvals' | 'reports'

export function Dashboard({ creature, onBack }: DashboardProps) {
  const [tab, setTab] = useState<Tab>('overview')
  const [goals, setGoals] = useState<any>(null)
  const [notifications, setNotifications] = useState<any[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [pending, setPending] = useState<any[]>([])
  const [reports, setReports] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [sseConnected, setSseConnected] = useState(false)
  const sseRef = useRef<EventSource | null>(null)

  // 加载数据
  useEffect(() => {
    const load = async () => {
      try {
        const [goalRes, notifRes, unreadRes, pendingRes, reportRes] = await Promise.all([
          api<any>('/goals').catch(() => ({ has_goal: false })),
          api<any>('/notifications?limit=30').catch(() => ({ notifications: [] })),
          api<any>('/notifications/unread').catch(() => ({ count: 0, notifications: [] })),
          api<any>('/autonomous/pending').catch(() => ({ pending: [] })),
          api<any>('/reports/weekly?limit=4').catch(() => ({ reports: [] })),
        ])
        setGoals(goalRes)
        setNotifications(notifRes.notifications || [])
        setUnreadCount(unreadRes.count || 0)
        setPending(pendingRes.pending || [])
        setReports(reportRes.reports || [])
      } catch {} finally { setLoading(false) }
    }
    load()
    const interval = setInterval(load, 30_000) // 每 30 秒刷新
    return () => clearInterval(interval)
  }, [])

  // SSE 实时推送
  useEffect(() => {
    const API = (import.meta as any).env?.VITE_API_BASE || '/api'
    const es = new EventSource(`${API}/notifications/stream`)
    sseRef.current = es

    es.addEventListener('connected', () => setSseConnected(true))
    es.addEventListener('notification', (e) => {
      try {
        const notif = JSON.parse(e.data)
        setNotifications(prev => [notif, ...prev].slice(0, 50))
        setUnreadCount(prev => prev + 1)
      } catch {}
    })
    es.addEventListener('heartbeat', () => {})
    es.onerror = () => setSseConnected(false)

    return () => { es.close(); sseRef.current = null }
  }, [])

  const markRead = async (id: string) => {
    await api(`/notifications/${id}/read`, { method: 'POST' }).catch(() => {})
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n))
    setUnreadCount(prev => Math.max(0, prev - 1))
  }

  const markAllRead = async () => {
    await api('/notifications/read-all', { method: 'POST' }).catch(() => {})
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
    setUnreadCount(0)
  }

  const approveAction = async (id: string) => {
    await api(`/autonomous/${id}/approve`, { method: 'POST' }).catch(() => {})
    setPending(prev => prev.filter(a => a.id !== id))
  }

  const rejectAction = async (id: string) => {
    await api(`/autonomous/${id}/reject`, { method: 'POST' }).catch(() => {})
    setPending(prev => prev.filter(a => a.id !== id))
  }

  const tabs: { key: Tab; label: string; icon: React.ReactNode; badge?: number }[] = [
    { key: 'overview', label: 'Overview', icon: <TargetIcon /> },
    { key: 'notifications', label: 'Alerts', icon: <BellIcon />, badge: unreadCount },
    { key: 'approvals', label: 'Approve', icon: <ShieldCheckIcon />, badge: pending.length },
    { key: 'reports', label: 'Reports', icon: <CalendarIcon /> },
  ]

  return (
    <div className="min-h-screen bg-surface">
      {/* 头部 */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-border bg-glass sticky top-0 z-20 max-w-3xl mx-auto">
        <button onClick={onBack} className="p-2 rounded-xl hover:bg-hover transition-colors">
          <ArrowLeftIcon />
        </button>
        <div className="flex-1">
          <p className="text-sm font-semibold text-primary">Agent Dashboard</p>
          <p className="text-[10px] text-muted flex items-center gap-1">
            <span className={`w-1.5 h-1.5 rounded-full ${sseConnected ? 'bg-emerald-500' : 'bg-gray-300'}`} />
            {sseConnected ? 'Live connected' : 'Polling mode'}
          </p>
        </div>
      </div>

      {/* Tab 导航 */}
      <div className="max-w-3xl mx-auto px-4 pt-4">
        <div className="flex gap-1 p-1 rounded-xl bg-hover">
          {tabs.map(t => (
            <button key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 text-xs font-medium rounded-lg transition-all relative ${
                tab === t.key ? 'bg-white shadow-sm text-primary dark:bg-[var(--bg-card)]' : 'text-muted hover:text-primary'
              }`}>
              {t.icon}
              <span className="hidden sm:inline">{t.label}</span>
              {t.badge && t.badge > 0 ? (
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-brand text-white text-[9px] font-bold flex items-center justify-center">
                  {t.badge > 9 ? '9+' : t.badge}
                </span>
              ) : null}
            </button>
          ))}
        </div>
      </div>

      {/* 内容区 */}
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
        {loading ? (
          <div className="text-center py-16 text-muted text-sm">Loading dashboard...</div>
        ) : (
          <>
            {tab === 'overview' && <OverviewTab goals={goals} pending={pending} unreadCount={unreadCount} reports={reports} />}
            {tab === 'notifications' && <NotificationsTab notifications={notifications} onMarkRead={markRead} onMarkAllRead={markAllRead} />}
            {tab === 'approvals' && <ApprovalsTab pending={pending} onApprove={approveAction} onReject={rejectAction} />}
            {tab === 'reports' && <ReportsTab reports={reports} />}
          </>
        )}
      </div>
    </div>
  )
}

// === Overview Tab ===
function OverviewTab({ goals, pending, unreadCount, reports }: any) {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* 目标进度 */}
      <section>
        <h3 className="text-xs font-medium text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
          <TargetIcon className="w-3.5 h-3.5" /> Goals
        </h3>
        {goals?.has_goal ? (
          <div className="card p-5">
            <div className="flex items-baseline gap-2 mb-3">
              <span className="text-3xl font-bold text-primary">{goals.overall_progress || 0}%</span>
              <span className="text-xs text-muted">overall progress</span>
            </div>
            <div className="h-2 rounded-full bg-border overflow-hidden mb-4">
              <div className="h-full bg-brand rounded-full transition-all duration-700"
                style={{ width: `${goals.overall_progress || 0}%` }} />
            </div>
            {goals.objective && (
              <p className="text-sm font-medium text-primary mb-2">{goals.objective}</p>
            )}
            {goals.key_results?.map((kr: any, i: number) => (
              <div key={i} className="flex items-center gap-2 text-xs text-secondary py-1">
                <span className={`w-1.5 h-1.5 rounded-full ${kr.progress >= 100 ? 'bg-emerald-500' : kr.progress >= 50 ? 'bg-brand' : 'bg-gray-300'}`} />
                <span className="flex-1">{kr.description || kr.metric}</span>
                <span className="font-mono text-muted">{kr.progress || 0}%</span>
              </div>
            ))}
            {goals.at_risk?.length > 0 && (
              <div className="mt-3 p-2 rounded-lg bg-red-50 dark:bg-red-500/10 text-xs text-red-600 dark:text-red-400">
                ⚠️ At risk: {goals.at_risk.join(', ')}
              </div>
            )}
          </div>
        ) : (
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-brand/8 flex items-center justify-center">
                <RocketIcon className="w-5 h-5 text-brand" />
              </div>
              <div>
                <p className="text-sm font-medium text-primary">Getting started</p>
                <p className="text-xs text-muted">Tell CrabRes about your product to set growth goals</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-xs text-secondary p-2 rounded-lg bg-hover">
                <span className="w-5 h-5 rounded-full bg-brand/10 flex items-center justify-center text-[10px] font-bold text-brand">1</span>
                <span>Describe your product in the chat</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-secondary p-2 rounded-lg bg-hover">
                <span className="w-5 h-5 rounded-full bg-brand/10 flex items-center justify-center text-[10px] font-bold text-brand">2</span>
                <span>CrabRes researches your market & competitors</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-secondary p-2 rounded-lg bg-hover">
                <span className="w-5 h-5 rounded-full bg-brand/10 flex items-center justify-center text-[10px] font-bold text-brand">3</span>
                <span>Growth playbook & goals auto-generated here</span>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* 快速状态 */}
      <div className="grid grid-cols-3 gap-3">
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-primary">{unreadCount}</p>
          <p className="text-[10px] text-muted uppercase">Alerts</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-primary">{pending.length}</p>
          <p className="text-[10px] text-muted uppercase">Pending</p>
        </div>
        <div className="card p-4 text-center">
          <p className="text-2xl font-bold text-primary">{reports.length}</p>
          <p className="text-[10px] text-muted uppercase">Reports</p>
        </div>
      </div>

      {/* 待审批预览 */}
      {pending.length > 0 && (
        <section>
          <h3 className="text-xs font-medium text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
            <ShieldCheckIcon className="w-3.5 h-3.5" /> Needs your approval
          </h3>
          <div className="space-y-2">
            {pending.slice(0, 3).map((a: any) => (
              <div key={a.id} className="card p-3 flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${a.risk === 'high' ? 'bg-red-500' : a.risk === 'medium' ? 'bg-amber-500' : 'bg-emerald-500'}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-primary truncate">{a.description}</p>
                  <p className="text-[10px] text-muted">{a.type} · {a.risk} risk</p>
                </div>
                <span className="text-xs text-brand">Review →</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

// === Notifications Tab ===
function NotificationsTab({ notifications, onMarkRead, onMarkAllRead }: any) {
  const typeIcons: Record<string, React.ReactNode> = {
    competitor_change: <SearchSparkIcon className="w-4 h-4 text-blue-500" />,
    rss_discovery: <NewsIcon className="w-4 h-4 text-emerald-500" />,
    action_result: <ChartBarIcon className="w-4 h-4 text-brand" />,
    goal_at_risk: <AlertTriangleIcon className="w-4 h-4 text-amber-500" />,
    daily_reflection: <BrainIcon className="w-4 h-4 text-purple-500" />,
    approval_needed: <LockIcon className="w-4 h-4 text-red-500" />,
    skill_learned: <BrainIcon className="w-4 h-4 text-indigo-500" />,
    system: <GearIcon className="w-4 h-4 text-gray-500" />,
  }

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-medium text-muted uppercase tracking-wider">Notifications</h3>
        {notifications.some((n: any) => !n.read) && (
          <button onClick={onMarkAllRead} className="text-xs text-brand hover:underline">Mark all read</button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="card p-8 text-center">
          <BellIcon className="w-8 h-8 text-muted mx-auto mb-2" />
          <p className="text-sm text-muted">No notifications yet</p>
          <p className="text-xs text-muted mt-1">Agent discoveries will appear here</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n: any) => (
            <div key={n.id}
              onClick={() => !n.read && onMarkRead(n.id)}
              className={`card p-3 flex items-start gap-3 cursor-pointer transition-all ${
                !n.read ? 'border-brand/20 bg-brand/3' : 'opacity-70'
              }`}>
              <span className="mt-0.5 shrink-0">{typeIcons[n.type] || <PinIcon className="w-4 h-4 text-muted" />}</span>
              <div className="flex-1 min-w-0">
                <p className={`text-sm ${!n.read ? 'font-medium text-primary' : 'text-secondary'}`}>{n.title}</p>
                <p className="text-xs text-muted mt-0.5 line-clamp-2">{n.body}</p>
                <p className="text-[10px] text-muted mt-1">
                  {new Date(n.created_at * 1000).toLocaleString()}
                  {n.delivered_via?.length > 0 && ` · via ${n.delivered_via.join(', ')}`}
                </p>
              </div>
              {!n.read && <span className="w-2 h-2 rounded-full bg-brand shrink-0 mt-1.5" />}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// === Approvals Tab ===
function ApprovalsTab({ pending, onApprove, onReject }: any) {
  return (
    <div className="space-y-4 animate-fade-in">
      <h3 className="text-xs font-medium text-muted uppercase tracking-wider">Pending Approvals</h3>

      {pending.length === 0 ? (
        <div className="card p-8 text-center">
          <CircleCheckIcon className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <p className="text-sm text-muted">No pending approvals</p>
          <p className="text-xs text-muted mt-1">Agent will request approval for risky actions</p>
        </div>
      ) : (
        <div className="space-y-3">
          {pending.map((a: any) => (
            <div key={a.id} className="card p-4">
              <div className="flex items-start gap-3 mb-3">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${
                  a.risk === 'high' ? 'bg-red-100 text-red-600 dark:bg-red-500/20' :
                  a.risk === 'medium' ? 'bg-amber-100 text-amber-600 dark:bg-amber-500/20' :
                  'bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20'
                }`}>
                  {a.risk?.[0]?.toUpperCase() || '?'}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-primary">{a.description}</p>
                  <p className="text-xs text-muted mt-0.5">{a.type} · {a.risk} risk · {new Date(a.created_at * 1000).toLocaleString()}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button onClick={() => onApprove(a.id)}
                  className="flex-1 py-2 rounded-lg bg-brand text-white text-xs font-medium hover:bg-brand-hover transition-colors">
                  ✓ Approve
                </button>
                <button onClick={() => onReject(a.id)}
                  className="flex-1 py-2 rounded-lg border border-border text-xs font-medium text-muted hover:text-primary hover:border-red-200 transition-colors">
                  ✕ Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// === Reports Tab ===
function ReportsTab({ reports }: any) {
  const [expanded, setExpanded] = useState<string | null>(null)

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-medium text-muted uppercase tracking-wider">Weekly Reports</h3>
        <button
          onClick={async () => {
            try {
              await api('/reports/weekly/generate', { method: 'POST' })
              window.location.reload()
            } catch {}
          }}
          className="text-xs text-brand hover:underline">
          Generate now
        </button>
      </div>

      {reports.length === 0 ? (
        <div className="card p-8 text-center">
          <ChartBarIcon className="w-8 h-8 text-muted mx-auto mb-2" />
          <p className="text-sm text-muted">No reports yet</p>
          <p className="text-xs text-muted mt-1">Weekly reports auto-generate every Monday</p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((r: any, i: number) => (
            <div key={r.id || i} className="card overflow-hidden">
              <button
                onClick={() => setExpanded(expanded === (r.id || i) ? null : (r.id || i))}
                className="w-full p-4 flex items-center gap-3 text-left hover:bg-hover transition-colors">
                <CalendarIcon className="w-4 h-4 text-muted shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-primary">{r.title || `Week of ${r.week || 'Unknown'}`}</p>
                  <p className="text-xs text-muted">{r.executive_summary?.slice(0, 100) || 'Report available'}</p>
                </div>
                <span className="text-xs text-muted">{expanded === (r.id || i) ? '−' : '+'}</span>
              </button>
              {expanded === (r.id || i) && (
                <div className="px-4 pb-4 pt-0 border-t border-border animate-fade-in">
                  <div className="crabres-prose text-sm mt-3">
                    <ReactMarkdown>{r.content || r.executive_summary || 'No content available'}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
