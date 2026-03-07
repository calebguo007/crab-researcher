import { useState, useEffect, useRef, useCallback } from 'react'
import {
  BarChart3, Shield, Users, FileText, ChevronRight, ChevronLeft,
  TrendingUp, TrendingDown, AlertTriangle, Bell, DollarSign, Activity,
  Plus, Trash2, Edit3, Send, Bot, User, Lock, Sparkles, ArrowRight,
  Package, ExternalLink, Search, Check, X, Loader2,
  Cog, Wifi, WifiOff, RefreshCw, Eye, Zap, Target, Briefcase,
  Globe, ShoppingCart, MessageSquare, Radio, ChevronDown,
  LogOut, Mail, Building2, Play, Pause, Clock, Hash, Save,
  ListChecks, BookOpen,
} from 'lucide-react'

/* ================================================================
   小蟹研究员 — Dashboard (Light Mode · Full API-Connected)
   ================================================================ */

// ==================== Auth / Token 管理 ====================

function getToken(): string | null { return localStorage.getItem('crab_token') }
function setToken(token: string) { localStorage.setItem('crab_token', token) }
function clearToken() { localStorage.removeItem('crab_token') }

// ==================== API 层 ====================

const API = import.meta.env.VITE_API_BASE || '/api'

// 全局登出回调，由 App 组件设置，避免 401 时 reload 死循环
let _onAuthExpired: (() => void) | null = null
function setAuthExpiredHandler(fn: () => void) { _onAuthExpired = fn }

async function api<T = any>(path: string, opts?: RequestInit): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(opts?.headers as Record<string, string> || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API}${path}`, { ...opts, headers })
  if (res.status === 401) {
    clearToken()
    _onAuthExpired?.()
    throw new Error('登录已过期，请重新登录')
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `API Error ${res.status}`)
  }
  const text = await res.text()
  return text ? JSON.parse(text) : ({} as T)
}

// ==================== 类型 ====================

type TabId = 'overview' | 'competitors' | 'personas' | 'proposal'

interface TabDef {
  id: TabId
  label: string
  icon: React.ReactNode
  price: string
  priceClass: string
}

interface AlertItem {
  id: number
  severity: string
  brand: string
  platform: string
  task_type: string
  change_type: string | null
  change_summary: string | null
  created_at: string
}

interface SystemStats {
  tasks: { total: number; active: number }
  monitoring: { total_results: number; alerts: number }
  reports: { total: number }
  cost: { total_cny: number }
}

interface BudgetInfo {
  used: number
  budget: number
  ratio: number
  remaining: number
  is_over_budget: boolean
  is_warning: boolean
}

interface PriceTrendPoint {
  date: string
  brand: string
  avg_price: number
  samples: number
}

interface UserProductItem {
  id: number
  product_name: string
  industry: string
  category: string
  keywords: string[]
  price_range: Record<string, number>
  platforms: string[]
  created_at: string
}

interface CompetitorItem {
  id: number
  user_product_id: number
  brand: string
  product_name: string
  platform: string | null
  price: number | null
  promo_price: number | null
  specs: Record<string, any>
  features: string[]
  product_url: string | null
  created_at: string
}

interface Persona {
  id: string
  name: string
  age: string
  gender: string
  income: string
  interests: string[]
  color: string
  description: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

interface TaskItem {
  id: number; brand_name: string; platform: string; task_type: string
  frequency: string; status: string; keywords: string[]
  product_url: string | null; created_at: string
}

interface ReportItem {
  id: number; report_type: string; title: string; content: string
  model_used: string | null; token_cost: number; generated_at: string
}

interface PaginatedResp<T> { items: T[]; total: number; page: number; page_size: number }

interface DiscoveryCandidate {
  id: number; brand: string; product_name: string; platform: string | null
  price: number | null; discovery_reason: string | null
  relevance_score: number; status: string
}

interface UserInfo {
  id: number; company_name: string; contact_email: string
  subscription_plan: string; monthly_budget: number
  monthly_token_used: number; is_active: boolean
  created_at: string; updated_at?: string
}

// ==================== Hooks ====================

function useApi<T>(path: string | null, deps: any[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    if (!path) return
    setLoading(true)
    setError(null)
    try {
      const result = await api<T>(path)
      setData(result)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [path, ...deps])

  useEffect(() => { fetchData() }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}

// ==================== 工具组件 ====================

function SeverityDot({ severity }: { severity: string }) {
  return <div className={`severity-dot ${severity}`} />
}

function StatCard({ icon, label, value, sub, loading: isLoading }: {
  icon: React.ReactNode; label: string; value: string; sub: string; loading?: boolean
}) {
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-2">
        <span className="text-[var(--text-muted)]">{icon}</span>
        <span className="text-xs text-[var(--text-muted)]">{label}</span>
      </div>
      {isLoading ? (
        <div className="skeleton h-8 w-20 mb-1" />
      ) : (
        <div className="text-2xl font-bold tracking-tight">{value}</div>
      )}
      <div className="mt-1 text-xs text-[var(--text-muted)]">{sub}</div>
    </div>
  )
}

function LineChart({ points, brands }: { points: PriceTrendPoint[]; brands: string[] }) {
  const COLORS = ['#f97316', '#2563eb', '#16a34a', '#7c3aed', '#dc2626', '#ca8a04']

  if (!points.length) return <div className="text-center text-xs text-[var(--text-muted)] py-12">暂无价格趋势数据</div>

  const dates = [...new Set(points.map(p => p.date))].sort()
  const brandList = brands.length ? brands : [...new Set(points.map(p => p.brand))]
  const brandColorMap: Record<string, string> = {}
  brandList.forEach((b, i) => { brandColorMap[b] = COLORS[i % COLORS.length] })

  const allPrices = points.map(p => p.avg_price).filter(v => v > 0)
  if (!allPrices.length) return <div className="text-center text-xs text-[var(--text-muted)] py-12">暂无数据</div>

  const minP = Math.min(...allPrices) * 0.92
  const maxP = Math.max(...allPrices) * 1.06
  const w = 480, h = 160, pL = 50, pR = 15, pT = 15, pB = 28
  const cW = w - pL - pR, cH = h - pT - pB
  const xStep = dates.length > 1 ? cW / (dates.length - 1) : cW
  const yFn = (v: number) => pT + cH - ((v - minP) / (maxP - minP || 1)) * cH

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-auto">
      {[0, 0.25, 0.5, 0.75, 1].map(r => {
        const yy = pT + r * cH
        return <line key={r} x1={pL} y1={yy} x2={w - pR} y2={yy} stroke="rgba(0,0,0,0.04)" strokeWidth="0.5" />
      })}
      {brandList.map(brand => {
        const bpts = dates.map((d, i) => {
          const p = points.find(pp => pp.date === d && pp.brand === brand)
          return p ? { x: pL + i * xStep, y: yFn(p.avg_price), v: p.avg_price } : null
        }).filter(Boolean) as { x: number; y: number; v: number }[]

        if (!bpts.length) return null
        const line = bpts.map(p => `${p.x},${p.y}`).join(' ')
        const area = `${bpts.map(p => `${p.x},${p.y}`).join(' ')} ${bpts[bpts.length - 1].x},${pT + cH} ${bpts[0].x},${pT + cH}`
        const col = brandColorMap[brand] || '#999'
        return (
          <g key={brand}>
            <defs>
              <linearGradient id={`g-${brand}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={col} stopOpacity="0.12" />
                <stop offset="100%" stopColor={col} stopOpacity="0" />
              </linearGradient>
            </defs>
            <polygon points={area} fill={`url(#g-${brand})`} />
            <polyline points={line} fill="none" stroke={col} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
            {bpts.map((p, i) => (
              <circle key={i} cx={p.x} cy={p.y} r="2.5" fill={col} stroke="white" strokeWidth="1.5" />
            ))}
          </g>
        )
      })}
      {dates.map((d, i) => (
        <text key={i} x={pL + i * xStep} y={h - 4} textAnchor="middle" fill="var(--text-muted)" fontSize="9" fontFamily="var(--font-mono)">{d.slice(5)}</text>
      ))}
      {[0, 0.5, 1].map(r => {
        const val = minP + r * (maxP - minP)
        return <text key={r} x={pL - 6} y={yFn(val) + 3} textAnchor="end" fill="var(--text-muted)" fontSize="9" fontFamily="var(--font-mono)">¥{Math.round(val)}</text>
      })}
    </svg>
  )
}

function BudgetGauge({ used, budget }: { used: number; budget: number }) {
  const pct = Math.min(used / budget, 1)
  const r = 50, cx = 60, cy = 58
  const circ = Math.PI * r
  const offset = circ * (1 - pct)
  const color = pct > 0.8 ? 'var(--red)' : pct > 0.5 ? 'var(--yellow)' : 'var(--green)'
  return (
    <svg viewBox="0 0 120 72" className="w-36">
      <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`} fill="none" stroke="rgba(0,0,0,0.06)" strokeWidth="7" strokeLinecap="round" />
      <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`} fill="none" stroke={color} strokeWidth="7" strokeLinecap="round"
        strokeDasharray={`${circ}`} strokeDashoffset={offset} style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)' }} />
      <text x={cx} y={cy - 12} textAnchor="middle" fill={color} fontSize="18" fontWeight="700" fontFamily="var(--font-mono)">{(pct * 100).toFixed(0)}%</text>
      <text x={cx} y={cy + 4} textAnchor="middle" fill="var(--text-muted)" fontSize="9">¥{used.toFixed(1)} / ¥{budget}</text>
    </svg>
  )
}

function PersonaBlob({ persona, isActive }: { persona: Persona; isActive: boolean }) {
  return (
    <div className="relative w-full aspect-square flex items-center justify-center">
      <div className="absolute inset-0 rounded-full opacity-15 animate-breathe" style={{ background: `radial-gradient(circle, ${persona.color} 0%, transparent 70%)` }} />
      <div className={`w-3/5 aspect-square animate-persona-morph transition-all duration-1000 ${isActive ? 'scale-100 opacity-100' : 'scale-75 opacity-40'}`}
        style={{
          background: `linear-gradient(135deg, ${persona.color}20 0%, ${persona.color}08 100%)`,
          border: `2px solid ${persona.color}30`,
          boxShadow: isActive ? `0 0 40px ${persona.color}15` : 'none',
        }} />
      {isActive && persona.interests.slice(0, 3).map((_, i) => (
        <div key={i} className="absolute w-2 h-2 rounded-full" style={{
          background: persona.color, animation: `orbit ${4 + i * 1.5}s linear infinite`,
          animationDelay: `${i * 0.8}s`, top: '50%', left: '50%', marginTop: -4, marginLeft: -4, opacity: 0.5,
        }} />
      ))}
      <div className="absolute">
        <Target size={20} style={{ color: persona.color }} />
      </div>
    </div>
  )
}

function LoadingSpinner() {
  return <Loader2 size={16} className="animate-spin text-[var(--accent)]" />
}

function ErrorBanner({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex items-center gap-2 p-3 rounded-xl bg-red-50 border border-red-100 text-xs">
      <AlertTriangle size={14} className="text-[var(--red)] shrink-0" />
      <span className="text-[var(--red)] flex-1">{message}</span>
      {onRetry && <button onClick={onRetry} className="btn-ghost !py-1 !px-2 !text-[10px] flex items-center gap-1"><RefreshCw size={10} /> 重试</button>}
    </div>
  )
}

// ==================== 登录/注册页面 ====================

function AuthPage({ onLogin }: { onLogin: () => void }) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [company, setCompany] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setLoading(true); setError(null)
    try {
      if (mode === 'register') {
        const res = await api<{ access_token: string }>('/auth/register', {
          method: 'POST', body: JSON.stringify({ company_name: company, contact_email: email, password }),
        })
        setToken(res.access_token)
      } else {
        const res = await api<{ access_token: string }>('/auth/login', {
          method: 'POST', body: JSON.stringify({ email, password }),
        })
        setToken(res.access_token)
      }
      onLogin()
    } catch (e: any) { setError(e.message) } finally { setLoading(false) }
  }

  return (
    <div className="h-screen flex items-center justify-center relative">
      <div className="frosted-backdrop" style={{ background: 'linear-gradient(135deg, #f8f9fb 0%, #eef1f5 40%, #f0f2f6 100%)' }} />
      <div className="liquid-glass p-8 w-[400px] relative z-10 glass-float-in">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[#ea580c] flex items-center justify-center">
            <BarChart3 size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gradient">小蟹研究员</h1>
            <p className="text-[10px] text-[var(--text-muted)] font-[var(--font-mono)]">AI Market Research Assistant</p>
          </div>
        </div>
        <div className="flex gap-1 mb-6 p-1 rounded-xl bg-black/[0.03]">
          <button onClick={() => setMode('login')} className={`flex-1 py-2 text-xs font-medium rounded-lg transition-all ${mode === 'login' ? 'bg-white shadow-sm text-[var(--text-primary)]' : 'text-[var(--text-muted)]'}`}>登录</button>
          <button onClick={() => setMode('register')} className={`flex-1 py-2 text-xs font-medium rounded-lg transition-all ${mode === 'register' ? 'bg-white shadow-sm text-[var(--text-primary)]' : 'text-[var(--text-muted)]'}`}>注册</button>
        </div>
        {error && <ErrorBanner message={error} />}
        <form onSubmit={handleSubmit} className="space-y-3 mt-4">
          {mode === 'register' && (
            <div className="relative">
              <Building2 size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
              <input className="input-glass !pl-10 !text-xs" placeholder="企业名称" value={company} onChange={e => setCompany(e.target.value)} required />
            </div>
          )}
          <div className="relative">
            <Mail size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
            <input className="input-glass !pl-10 !text-xs" placeholder="邮箱" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="relative">
            <Lock size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
            <input className="input-glass !pl-10 !text-xs" placeholder="密码（至少6位）" type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} />
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full !py-3 flex items-center justify-center gap-2 disabled:opacity-60">
            {loading && <Loader2 size={14} className="animate-spin" />} {mode === 'login' ? '登录' : '注册'}
          </button>
        </form>
        <p className="text-[10px] text-[var(--text-muted)] text-center mt-6">
          {mode === 'login' ? '还没有账号？' : '已有账号？'}
          <button onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(null) }} className="text-[var(--accent)] ml-1 hover:underline">
            {mode === 'login' ? '去注册' : '去登录'}
          </button>
        </p>
      </div>
    </div>
  )
}

// ==================== Tab 1: 基础信息 ====================

function OverviewTab() {
  const { data: stats, loading: statsLoading, error: statsErr, refetch: refetchStats } = useApi<SystemStats>('/system/stats')
  const { data: budget, loading: budgetLoading, error: budgetErr, refetch: refetchBudget } = useApi<BudgetInfo>('/system/budget')
  const { data: alerts, loading: alertsLoading, error: alertsErr, refetch: refetchAlerts } = useApi<AlertItem[]>('/system/dashboard/alerts?limit=10')
  const { data: trends, loading: trendsLoading, error: trendsErr, refetch: refetchTrends } = useApi<{ days: number; points: PriceTrendPoint[] }>('/system/dashboard/price-trends?days=7')
  const { data: tasksData, loading: tasksLoading, refetch: refetchTasks } = useApi<PaginatedResp<TaskItem>>('/tasks/list?page=1&page_size=5')
  const { data: reportsData, loading: reportsLoading, refetch: refetchReports } = useApi<PaginatedResp<ReportItem>>('/reports/list?page=1&page_size=5')

  const [showTaskForm, setShowTaskForm] = useState(false)
  const [taskForm, setTaskForm] = useState({ brand_name: '', platform: 'jd', task_type: 'price', frequency: 'daily', keywords: '', product_url: '' })
  const [taskSubmitting, setTaskSubmitting] = useState(false)

  const handleCreateTask = async () => {
    if (!taskForm.brand_name) return
    setTaskSubmitting(true)
    try {
      const body: any = { brand_name: taskForm.brand_name, platform: taskForm.platform, task_type: taskForm.task_type, frequency: taskForm.frequency }
      if (taskForm.keywords) body.keywords = taskForm.keywords.split(/[,，\s]+/).filter(Boolean)
      if (taskForm.product_url) body.product_url = taskForm.product_url
      await api('/tasks/create', { method: 'POST', body: JSON.stringify(body) })
      setShowTaskForm(false)
      setTaskForm({ brand_name: '', platform: 'jd', task_type: 'price', frequency: 'daily', keywords: '', product_url: '' })
      refetchTasks(); refetchStats()
    } catch (e: any) { alert(e.message) } finally { setTaskSubmitting(false) }
  }

  const handleDeleteTask = async (id: number) => {
    if (!confirm('确定删除此任务？')) return
    try { await api(`/tasks/${id}`, { method: 'DELETE' }); refetchTasks(); refetchStats() } catch (e: any) { alert(e.message) }
  }

  const handleToggleTask = async (task: TaskItem) => {
    const newStatus = task.status === 'active' ? 'paused' : 'active'
    try { await api(`/tasks/${task.id}/update`, { method: 'PUT', body: JSON.stringify({ status: newStatus }) }); refetchTasks() } catch (e: any) { alert(e.message) }
  }

  const TASK_TYPE_LABELS: Record<string, string> = { price: '价格', promotion: '促销', sentiment: '舆情', new_product: '新品' }
  const PLATFORM_LABELS: Record<string, string> = { jd: '京东', tmall: '天猫', taobao: '淘宝', pdd: '拼多多', xiaohongshu: '小红书', douyin: '抖音', weibo: '微博' }

  const trendBrands = trends ? [...new Set(trends.points.map(p => p.brand))] : []

  return (
    <div className="grid grid-cols-2 gap-5 p-6">
      {/* 卡片1: 运营概览 */}
      <div className="liquid-glass p-6 glass-float-in glass-float-in-delay-1">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <Activity size={16} className="text-[var(--accent)]" />
            <span className="text-sm font-semibold tracking-wide">运营概览</span>
          </div>
          <button onClick={refetchStats} className="p-1.5 rounded-lg hover:bg-black/[0.04] transition-colors"><RefreshCw size={13} className="text-[var(--text-muted)]" /></button>
        </div>
        {statsErr && <ErrorBanner message={statsErr} onRetry={refetchStats} />}
        <div className="grid grid-cols-3 gap-6">
          <StatCard icon={<Zap size={12} />} label="监测任务" value={stats ? `${stats.tasks.total}` : '--'} sub={stats ? `${stats.tasks.active} 活跃` : ''} loading={statsLoading} />
          <StatCard icon={<Bell size={12} />} label="告警总数" value={stats ? `${stats.monitoring.alerts}` : '--'} sub="触发通知" loading={statsLoading} />
          <StatCard icon={<FileText size={12} />} label="累计报告" value={stats ? `${stats.reports.total}` : '--'} sub="篇" loading={statsLoading} />
        </div>
      </div>

      {/* 卡片2: 成本控制 */}
      <div className="liquid-glass p-6 glass-float-in glass-float-in-delay-2">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <DollarSign size={16} className="text-[var(--green)]" />
            <span className="text-sm font-semibold tracking-wide">成本控制</span>
          </div>
          <button onClick={refetchBudget} className="p-1.5 rounded-lg hover:bg-black/[0.04] transition-colors"><RefreshCw size={13} className="text-[var(--text-muted)]" /></button>
        </div>
        {budgetErr && <ErrorBanner message={budgetErr} onRetry={refetchBudget} />}
        {!budgetErr && (
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-[var(--text-muted)] mb-1">本月已用</div>
              {budgetLoading ? <div className="skeleton h-9 w-24" /> : (
                <div className="text-3xl font-bold tracking-tight font-[var(--font-mono)]" style={{ color: budget && budget.is_warning ? 'var(--yellow)' : 'var(--green)' }}>
                  ¥{budget?.used.toFixed(1) || '0.0'}
                </div>
              )}
              <div className="mt-2 text-xs text-[var(--text-muted)]">
                剩余 <span className="text-[var(--green)] font-semibold">¥{budget?.remaining.toFixed(1) || '--'}</span>
              </div>
              <div className="progress-track mt-3 w-40">
                <div className="progress-fill" style={{ width: `${(budget?.ratio || 0) * 100}%`, background: budget?.is_warning ? 'var(--yellow)' : 'var(--green)' }} />
              </div>
            </div>
            <BudgetGauge used={budget?.used || 0} budget={budget?.budget || 100} />
          </div>
        )}
      </div>

      {/* 卡片3: 告警列表 */}
      <div className="liquid-glass p-6 glass-float-in glass-float-in-delay-3">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-[var(--yellow)]" />
            <span className="text-sm font-semibold tracking-wide">告警中心</span>
          </div>
          <button onClick={refetchAlerts} className="p-1.5 rounded-lg hover:bg-black/[0.04] transition-colors"><RefreshCw size={13} className="text-[var(--text-muted)]" /></button>
        </div>
        {alertsErr && <ErrorBanner message={alertsErr} onRetry={refetchAlerts} />}
        <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
          {alertsLoading && [1,2,3].map(i => <div key={i} className="skeleton h-14 w-full" />)}
          {!alertsLoading && alerts && alerts.length === 0 && (
            <div className="text-center text-xs text-[var(--text-muted)] py-8 flex flex-col items-center gap-2">
              <Bell size={20} className="opacity-30" />
              暂无告警
            </div>
          )}
          {alerts?.map(alert => (
            <div key={alert.id} className="flex items-start gap-3 p-3 rounded-xl hover:bg-black/[0.02] transition-colors cursor-pointer">
              <SeverityDot severity={alert.severity} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-xs font-semibold">{alert.brand}</span>
                  <span className="text-[10px] text-[var(--text-muted)] px-1.5 py-0.5 rounded bg-black/[0.03]">{alert.platform}</span>
                  {alert.change_type && <span className="text-[10px] text-[var(--accent)]">{alert.change_type}</span>}
                </div>
                <p className="text-xs text-[var(--text-secondary)] leading-relaxed truncate">{alert.change_summary || `${alert.task_type} 监测变动`}</p>
              </div>
              <span className="text-[10px] text-[var(--text-muted)] shrink-0 font-[var(--font-mono)]">
                {new Date(alert.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* 卡片4: 价格趋势 */}
      <div className="liquid-glass p-6 glass-float-in glass-float-in-delay-4">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <TrendingUp size={16} className="text-[var(--blue)]" />
            <span className="text-sm font-semibold tracking-wide">价格趋势</span>
          </div>
          <span className="text-[10px] text-[var(--text-muted)] font-[var(--font-mono)]">近 7 天</span>
        </div>
        {trendsErr && <ErrorBanner message={trendsErr} onRetry={refetchTrends} />}
        {trendBrands.length > 0 && (
          <div className="flex items-center gap-4 mb-3">
            {trendBrands.map((brand, i) => {
              const COLORS = ['#f97316', '#2563eb', '#16a34a', '#7c3aed', '#dc2626']
              return (
                <div key={brand} className="flex items-center gap-1.5 text-[11px]">
                  <span className="w-2.5 h-[2px] rounded" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <span className="text-[var(--text-muted)]">{brand}</span>
                </div>
              )
            })}
          </div>
        )}
        <div className="chart-area">
          {trendsLoading ? <div className="skeleton h-32 w-full" /> : (
            <LineChart points={trends?.points || []} brands={trendBrands} />
          )}
        </div>
      </div>

      {/* 卡片5: 监测任务 */}
      <div className="liquid-glass p-6 glass-float-in col-span-2" style={{ animationDelay: '0.5s', opacity: 0 }}>
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <ListChecks size={16} className="text-[var(--blue)]" />
            <span className="text-sm font-semibold tracking-wide">监测任务</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/[0.04] text-[var(--text-muted)]">{tasksData?.total || 0}</span>
          </div>
          <button onClick={() => setShowTaskForm(!showTaskForm)} className="btn-primary !py-1.5 !px-3 !text-xs flex items-center gap-1"><Plus size={12} /> 新建</button>
        </div>
        {showTaskForm && (
          <div className="mb-4 p-4 rounded-2xl bg-black/[0.02] border border-[var(--accent)]/15 space-y-3 animate-[slide-up_0.3s_ease]">
            <div className="grid grid-cols-4 gap-2">
              <input className="input-glass !text-xs" placeholder="品牌名称 *" value={taskForm.brand_name} onChange={e => setTaskForm({ ...taskForm, brand_name: e.target.value })} />
              <select className="input-glass !text-xs" value={taskForm.platform} onChange={e => setTaskForm({ ...taskForm, platform: e.target.value })}>
                <option value="jd">京东</option><option value="tmall">天猫</option><option value="taobao">淘宝</option>
                <option value="pdd">拼多多</option><option value="xiaohongshu">小红书</option><option value="douyin">抖音</option>
              </select>
              <select className="input-glass !text-xs" value={taskForm.task_type} onChange={e => setTaskForm({ ...taskForm, task_type: e.target.value })}>
                <option value="price">价格监测</option><option value="promotion">促销监测</option>
                <option value="sentiment">舆情监测</option><option value="new_product">新品监测</option>
              </select>
              <select className="input-glass !text-xs" value={taskForm.frequency} onChange={e => setTaskForm({ ...taskForm, frequency: e.target.value })}>
                <option value="hourly">每小时</option><option value="daily">每天</option><option value="weekly">每周</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input className="input-glass !text-xs" placeholder="关键词（逗号分隔，可选）" value={taskForm.keywords} onChange={e => setTaskForm({ ...taskForm, keywords: e.target.value })} />
              <input className="input-glass !text-xs" placeholder="商品链接（可选）" value={taskForm.product_url} onChange={e => setTaskForm({ ...taskForm, product_url: e.target.value })} />
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowTaskForm(false)} className="btn-ghost !text-xs !py-1.5">取消</button>
              <button onClick={handleCreateTask} disabled={taskSubmitting || !taskForm.brand_name} className="btn-primary !text-xs !py-1.5 flex items-center gap-1 disabled:opacity-50">
                {taskSubmitting && <Loader2 size={12} className="animate-spin" />} 创建任务
              </button>
            </div>
          </div>
        )}
        <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
          {tasksLoading && [1, 2].map(i => <div key={i} className="skeleton h-12 w-full" />)}
          {!tasksLoading && (!tasksData || tasksData.items.length === 0) && (
            <div className="text-center text-xs text-[var(--text-muted)] py-6"><ListChecks size={20} className="opacity-30 mx-auto mb-2" />暂无监测任务</div>
          )}
          {tasksData?.items.map(task => (
            <div key={task.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-black/[0.02] transition-colors group">
              <div className={`w-2 h-2 rounded-full shrink-0 ${task.status === 'active' ? 'bg-[var(--green)]' : 'bg-[var(--text-muted)]'}`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 text-xs">
                  <span className="font-semibold">{task.brand_name}</span>
                  <span className="px-1.5 py-0.5 rounded bg-black/[0.03] text-[10px] text-[var(--text-muted)]">{PLATFORM_LABELS[task.platform] || task.platform}</span>
                  <span className="px-1.5 py-0.5 rounded bg-[var(--accent)]/8 text-[10px] text-[var(--accent)]">{TASK_TYPE_LABELS[task.task_type] || task.task_type}</span>
                  <span className="text-[10px] text-[var(--text-muted)] flex items-center gap-0.5"><Clock size={9} />{task.frequency}</span>
                </div>
              </div>
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button onClick={() => handleToggleTask(task)} className="p-1.5 rounded-lg hover:bg-black/[0.04] text-[var(--text-muted)]">
                  {task.status === 'active' ? <Pause size={13} /> : <Play size={13} />}
                </button>
                <button onClick={() => handleDeleteTask(task.id)} className="p-1.5 rounded-lg hover:bg-red-50 text-[var(--text-muted)] hover:text-[var(--red)]"><Trash2 size={13} /></button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 卡片6: 最近报告 */}
      <div className="liquid-glass p-6 glass-float-in col-span-2" style={{ animationDelay: '0.6s', opacity: 0 }}>
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <BookOpen size={16} className="text-[var(--purple)]" />
            <span className="text-sm font-semibold tracking-wide">最近报告</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/[0.04] text-[var(--text-muted)]">{reportsData?.total || 0}</span>
          </div>
          <button onClick={refetchReports} className="p-1.5 rounded-lg hover:bg-black/[0.04] transition-colors"><RefreshCw size={13} className="text-[var(--text-muted)]" /></button>
        </div>
        <div className="space-y-2">
          {reportsLoading && [1, 2].map(i => <div key={i} className="skeleton h-14 w-full" />)}
          {!reportsLoading && (!reportsData || reportsData.items.length === 0) && (
            <div className="text-center text-xs text-[var(--text-muted)] py-6"><BookOpen size={20} className="opacity-30 mx-auto mb-2" />暂无报告</div>
          )}
          {reportsData?.items.map(report => (
            <div key={report.id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-black/[0.02] transition-colors">
              <div className="w-9 h-9 rounded-xl bg-[var(--purple)]/8 flex items-center justify-center"><FileText size={14} className="text-[var(--purple)]" /></div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 text-xs">
                  <span className="font-semibold truncate">{report.title}</span>
                  <span className="px-1.5 py-0.5 rounded bg-[var(--purple)]/8 text-[10px] text-[var(--purple)] shrink-0">{report.report_type}</span>
                </div>
                <div className="text-[10px] text-[var(--text-muted)] mt-1 flex items-center gap-3">
                  {report.model_used && <span>{report.model_used}</span>}
                  <span>¥{report.token_cost.toFixed(3)}</span>
                  <span>{new Date(report.generated_at).toLocaleDateString('zh-CN')}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ==================== Tab 2: 竞品 ====================

function CompetitorsTab() {
  const { data: products, loading: productsLoading, refetch: refetchProducts } = useApi<UserProductItem[]>('/competitors/products')
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null)
  const [competitors, setCompetitors] = useState<CompetitorItem[]>([])
  const [compLoading, setCompLoading] = useState(false)
  const [showAdd, setShowAdd] = useState(false)
  const [addForm, setAddForm] = useState({ brand: '', product_name: '', platform: '', price: '', promo_price: '', product_url: '' })
  const [submitting, setSubmitting] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editForm, setEditForm] = useState({ brand: '', product_name: '', platform: '', price: '', promo_price: '', product_url: '' })
  const [editSubmitting, setEditSubmitting] = useState(false)
  const [discovering, setDiscovering] = useState(false)
  const [candidates, setCandidates] = useState<DiscoveryCandidate[]>([])
  const [showCandidates, setShowCandidates] = useState(false)

  // 选中第一个产品
  useEffect(() => {
    if (products?.length && !selectedProduct) {
      setSelectedProduct(products[0].id)
    }
  }, [products])

  // 加载竞品列表
  useEffect(() => {
    if (!selectedProduct) return
    setCompLoading(true)
    api<CompetitorItem[]>(`/competitors/products/${selectedProduct}/competitors`)
      .then(setCompetitors)
      .catch(() => setCompetitors([]))
      .finally(() => setCompLoading(false))
  }, [selectedProduct])

  const refreshCompetitors = () => {
    if (!selectedProduct) return
    api<CompetitorItem[]>(`/competitors/products/${selectedProduct}/competitors`)
      .then(setCompetitors).catch(() => {})
  }

  const handleAddCompetitor = async () => {
    if (!selectedProduct || !addForm.brand || !addForm.product_name) return
    setSubmitting(true)
    try {
      const body: any = { brand: addForm.brand, product_name: addForm.product_name }
      if (addForm.platform) body.platform = addForm.platform
      if (addForm.price) body.price = parseFloat(addForm.price)
      if (addForm.promo_price) body.promo_price = parseFloat(addForm.promo_price)
      if (addForm.product_url) body.product_url = addForm.product_url
      const newComp = await api<CompetitorItem>(`/competitors/products/${selectedProduct}/competitors`, {
        method: 'POST', body: JSON.stringify(body),
      })
      setCompetitors(prev => [newComp, ...prev])
      setAddForm({ brand: '', product_name: '', platform: '', price: '', promo_price: '', product_url: '' })
      setShowAdd(false)
    } catch (e: any) {
      alert(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定删除此竞品？')) return
    try {
      await api(`/competitors/competitors/${id}`, { method: 'DELETE' })
      setCompetitors(prev => prev.filter(c => c.id !== id))
    } catch (e: any) { alert(e.message) }
  }

  const startEdit = (comp: CompetitorItem) => {
    setEditingId(comp.id)
    setEditForm({
      brand: comp.brand, product_name: comp.product_name, platform: comp.platform || '',
      price: comp.price != null ? String(comp.price) : '', promo_price: comp.promo_price != null ? String(comp.promo_price) : '',
      product_url: comp.product_url || '',
    })
  }

  const handleEditSave = async () => {
    if (!editingId) return
    setEditSubmitting(true)
    try {
      const body: any = {}
      if (editForm.brand) body.brand = editForm.brand
      if (editForm.product_name) body.product_name = editForm.product_name
      if (editForm.platform) body.platform = editForm.platform
      if (editForm.price) body.price = parseFloat(editForm.price)
      if (editForm.promo_price) body.promo_price = parseFloat(editForm.promo_price)
      if (editForm.product_url) body.product_url = editForm.product_url
      const updated = await api<CompetitorItem>(`/competitors/competitors/${editingId}`, {
        method: 'PUT', body: JSON.stringify(body),
      })
      setCompetitors(prev => prev.map(c => c.id === editingId ? updated : c))
      setEditingId(null)
    } catch (e: any) { alert(e.message) } finally { setEditSubmitting(false) }
  }

  const handleDiscover = async () => {
    if (!selectedProduct) return
    setDiscovering(true)
    try {
      const res = await api<{ message: string; candidates: DiscoveryCandidate[] }>(`/competitors/products/${selectedProduct}/discover`, { method: 'POST' })
      setCandidates(res.candidates || [])
      setShowCandidates(true)
    } catch (e: any) { alert(e.message) } finally { setDiscovering(false) }
  }

  const handleConfirmCandidate = async (candidateId: number) => {
    try {
      await api(`/competitors/candidates/${candidateId}`, { method: 'PUT', body: JSON.stringify({ action: 'confirm' }) })
      setCandidates(prev => prev.filter(c => c.id !== candidateId))
      refreshCompetitors()
    } catch (e: any) { alert(e.message) }
  }

  const handleRejectCandidate = async (candidateId: number) => {
    try {
      await api(`/competitors/candidates/${candidateId}`, { method: 'PUT', body: JSON.stringify({ action: 'reject' }) })
      setCandidates(prev => prev.filter(c => c.id !== candidateId))
    } catch (e: any) { alert(e.message) }
  }

  const product = products?.find(p => p.id === selectedProduct)
  const COMP_COLORS = ['#f97316', '#2563eb', '#16a34a', '#7c3aed', '#dc2626', '#ca8a04']

  return (
    <div className="grid grid-cols-2 gap-5 p-6">
      {/* 左: 本产品 */}
      <div className="liquid-glass p-6 glass-float-in glass-float-in-delay-1">
        <div className="flex items-center gap-2 mb-5">
          <Package size={16} className="text-[var(--accent)]" />
          <span className="text-sm font-semibold">我的产品</span>
        </div>
        {productsLoading ? (
          <div className="space-y-3"><div className="skeleton h-32 w-full" /><div className="skeleton h-12 w-full" /></div>
        ) : product ? (
          <div className="space-y-4">
            <div className="p-4 rounded-2xl bg-black/[0.02] border border-[var(--glass-border)]">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-base font-bold">{product.product_name}</h3>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-[var(--accent)]/8 text-[var(--accent)]">{product.category}</span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <span className="text-[var(--text-muted)] flex items-center gap-1"><Briefcase size={10} /> 行业</span>
                  <p className="font-medium mt-0.5">{product.industry}</p>
                </div>
                <div>
                  <span className="text-[var(--text-muted)] flex items-center gap-1"><Target size={10} /> 品类</span>
                  <p className="font-medium mt-0.5">{product.category}</p>
                </div>
                <div>
                  <span className="text-[var(--text-muted)] flex items-center gap-1"><DollarSign size={10} /> 价格带</span>
                  <p className="font-medium mt-0.5">¥{product.price_range?.min || 0} - ¥{product.price_range?.max || 0}</p>
                </div>
                <div>
                  <span className="text-[var(--text-muted)] flex items-center gap-1"><Globe size={10} /> 平台</span>
                  <p className="font-medium mt-0.5">{product.platforms?.join(' · ') || '--'}</p>
                </div>
              </div>
              {product.keywords?.length > 0 && (
                <div className="mt-3">
                  <span className="text-[var(--text-muted)] text-xs flex items-center gap-1"><Search size={10} /> 关键词</span>
                  <div className="flex flex-wrap gap-1.5 mt-1.5">
                    {product.keywords.map(kw => (
                      <span key={kw} className="text-[10px] px-2 py-0.5 rounded-full bg-black/[0.04] text-[var(--text-secondary)]">{kw}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-[var(--accent)]/5 border border-[var(--accent)]/8">
              <Radio size={16} className="text-[var(--accent)] animate-pulse shrink-0" />
              <div className="text-xs">
                <p className="font-semibold text-[var(--accent)]">持续监测中</p>
                <p className="text-[var(--text-muted)] mt-0.5">{competitors.length} 个竞品 · 每日更新</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center text-xs text-[var(--text-muted)] py-12 flex flex-col items-center gap-2">
            <Package size={24} className="opacity-30" />
            暂无产品，请先通过 API 创建
          </div>
        )}
      </div>

      {/* 右: 竞品列表 */}
      <div className="liquid-glass p-6 glass-float-in glass-float-in-delay-2">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <Shield size={16} className="text-[var(--blue)]" />
            <span className="text-sm font-semibold">竞品列表</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/[0.04] text-[var(--text-muted)]">{competitors.length}</span>
          </div>
          {selectedProduct && (
            <button onClick={() => setShowAdd(!showAdd)} className="btn-primary flex items-center gap-1 !py-1.5 !px-3 !text-xs">
              <Plus size={12} /> 添加竞品
            </button>
          )}
        </div>

        {showAdd && (
          <div className="mb-4 p-4 rounded-2xl bg-black/[0.02] border border-[var(--accent)]/15 space-y-3 animate-[slide-up_0.3s_ease]">
            <div className="grid grid-cols-2 gap-2">
              <input className="input-glass !text-xs" placeholder="品牌名称 *" value={addForm.brand} onChange={e => setAddForm({ ...addForm, brand: e.target.value })} />
              <input className="input-glass !text-xs" placeholder="产品名称 *" value={addForm.product_name} onChange={e => setAddForm({ ...addForm, product_name: e.target.value })} />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <input className="input-glass !text-xs" placeholder="平台 (jd/tmall/...)" value={addForm.platform} onChange={e => setAddForm({ ...addForm, platform: e.target.value })} />
              <input className="input-glass !text-xs" placeholder="价格" type="number" value={addForm.price} onChange={e => setAddForm({ ...addForm, price: e.target.value })} />
              <input className="input-glass !text-xs" placeholder="促销价" type="number" value={addForm.promo_price} onChange={e => setAddForm({ ...addForm, promo_price: e.target.value })} />
            </div>
            <input className="input-glass !text-xs" placeholder="商品链接 (可选)" value={addForm.product_url} onChange={e => setAddForm({ ...addForm, product_url: e.target.value })} />
            <div className="flex justify-end gap-2">
              <button onClick={() => setShowAdd(false)} className="btn-ghost !text-xs !py-1.5">取消</button>
              <button onClick={handleAddCompetitor} disabled={submitting || !addForm.brand || !addForm.product_name} className="btn-primary !text-xs !py-1.5 flex items-center gap-1 disabled:opacity-50">
                {submitting && <Loader2 size={12} className="animate-spin" />} 确认添加
              </button>
            </div>
          </div>
        )}

        <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
          {compLoading && [1,2,3].map(i => <div key={i} className="skeleton h-16 w-full" />)}
          {!compLoading && competitors.length === 0 && (
            <div className="text-center text-xs text-[var(--text-muted)] py-12 flex flex-col items-center gap-2">
              <Shield size={24} className="opacity-30" />
              暂无竞品，点击上方添加
            </div>
          )}
          {competitors.map((comp, ci) => (
            editingId === comp.id ? (
              <div key={comp.id} className="p-3 rounded-xl bg-black/[0.02] border border-[var(--accent)]/15 space-y-2 animate-[slide-up_0.2s_ease]">
                <div className="grid grid-cols-2 gap-2">
                  <input className="input-glass !text-xs !py-1.5" placeholder="品牌" value={editForm.brand} onChange={e => setEditForm({ ...editForm, brand: e.target.value })} />
                  <input className="input-glass !text-xs !py-1.5" placeholder="产品名" value={editForm.product_name} onChange={e => setEditForm({ ...editForm, product_name: e.target.value })} />
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <input className="input-glass !text-xs !py-1.5" placeholder="平台" value={editForm.platform} onChange={e => setEditForm({ ...editForm, platform: e.target.value })} />
                  <input className="input-glass !text-xs !py-1.5" placeholder="价格" type="number" value={editForm.price} onChange={e => setEditForm({ ...editForm, price: e.target.value })} />
                  <input className="input-glass !text-xs !py-1.5" placeholder="促销价" type="number" value={editForm.promo_price} onChange={e => setEditForm({ ...editForm, promo_price: e.target.value })} />
                </div>
                <input className="input-glass !text-xs !py-1.5" placeholder="商品链接" value={editForm.product_url} onChange={e => setEditForm({ ...editForm, product_url: e.target.value })} />
                <div className="flex justify-end gap-2">
                  <button onClick={() => setEditingId(null)} className="btn-ghost !text-[10px] !py-1">取消</button>
                  <button onClick={handleEditSave} disabled={editSubmitting} className="btn-primary !text-[10px] !py-1 flex items-center gap-1">
                    {editSubmitting ? <Loader2 size={10} className="animate-spin" /> : <Save size={10} />} 保存
                  </button>
                </div>
              </div>
            ) : (
            <div key={comp.id} className="flex items-center gap-4 p-3.5 rounded-xl hover:bg-black/[0.02] transition-all group border border-transparent hover:border-[var(--glass-border)]">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center text-xs font-bold shrink-0"
                style={{ background: `${COMP_COLORS[ci % COMP_COLORS.length]}10`, color: COMP_COLORS[ci % COMP_COLORS.length] }}>
                {comp.brand.slice(0, 2)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold">{comp.brand}</span>
                  <span className="text-xs text-[var(--text-muted)]">{comp.product_name}</span>
                </div>
                <div className="flex items-center gap-3 mt-1 text-[11px]">
                  {comp.platform && <span className="text-[var(--text-muted)] flex items-center gap-1"><Globe size={10} />{comp.platform}</span>}
                  {comp.price != null && <span className="font-semibold font-[var(--font-mono)]">¥{comp.price}</span>}
                  {comp.promo_price != null && <span className="text-[var(--red)] font-semibold font-[var(--font-mono)]">促 ¥{comp.promo_price}</span>}
                </div>
              </div>
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                {comp.product_url && (
                  <a href={comp.product_url} target="_blank" rel="noreferrer" className="p-1.5 rounded-lg hover:bg-black/[0.04] text-[var(--text-muted)]"><ExternalLink size={13} /></a>
                )}
                <button onClick={() => startEdit(comp)} className="p-1.5 rounded-lg hover:bg-black/[0.04] text-[var(--text-muted)] hover:text-[var(--blue)] transition-colors"><Edit3 size={13} /></button>
                <button onClick={() => handleDelete(comp.id)} className="p-1.5 rounded-lg hover:bg-red-50 text-[var(--text-muted)] hover:text-[var(--red)] transition-colors"><Trash2 size={13} /></button>
              </div>
            </div>
            )
          ))}
        </div>

        {selectedProduct && (
          <div className="mt-4 space-y-3">
            <div onClick={handleDiscover} className="p-3 rounded-xl bg-[var(--purple)]/5 border border-[var(--purple)]/8 flex items-center gap-3 cursor-pointer hover:bg-[var(--purple)]/8 transition-colors">
              {discovering ? <Loader2 size={14} className="text-[var(--purple)] animate-spin shrink-0" /> : <Sparkles size={14} className="text-[var(--purple)] shrink-0" />}
              <div className="text-xs">
                <span className="text-[var(--purple)] font-medium">{discovering ? 'AI 正在分析行业竞品...' : 'AI 辅助发现'}</span>
                {!discovering && <span className="text-[var(--text-muted)] ml-1">让 AI 基于行业分析自动推荐竞品</span>}
              </div>
              {!discovering && <ArrowRight size={12} className="text-[var(--purple)] ml-auto shrink-0" />}
            </div>
            {showCandidates && candidates.length > 0 && (
              <div className="p-4 rounded-2xl bg-[var(--purple)]/3 border border-[var(--purple)]/10 space-y-2">
                <div className="text-xs font-semibold text-[var(--purple)] mb-2">AI 发现 {candidates.length} 个候选竞品</div>
                {candidates.map(c => (
                  <div key={c.id} className="flex items-center gap-3 p-2.5 rounded-xl bg-white/60 border border-[var(--glass-border)]">
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-semibold">{c.brand} <span className="text-[var(--text-muted)] font-normal">{c.product_name}</span></div>
                      {c.discovery_reason && <p className="text-[10px] text-[var(--text-muted)] mt-0.5 truncate">{c.discovery_reason}</p>}
                      <div className="flex items-center gap-2 mt-1 text-[10px]">
                        {c.platform && <span className="text-[var(--text-muted)]">{c.platform}</span>}
                        {c.price != null && <span className="font-semibold">¥{c.price}</span>}
                        <span className="text-[var(--purple)]">相关度 {(c.relevance_score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <button onClick={() => handleConfirmCandidate(c.id)} className="p-1.5 rounded-lg hover:bg-[var(--green)]/10 text-[var(--green)]" title="确认添加"><Check size={14} /></button>
                      <button onClick={() => handleRejectCandidate(c.id)} className="p-1.5 rounded-lg hover:bg-[var(--red)]/10 text-[var(--red)]" title="排除"><X size={14} /></button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// ==================== Tab 3: 用户画像 ====================

const STATIC_PERSONAS: Persona[] = [
  { id: 'young-music', name: '潮流音乐党', age: '18-25', gender: '男性为主 (65%)', income: '¥5k-10k',
    interests: ['电子音乐', '户外露营', '潮牌穿搭', '短视频创作'], color: '#f97316',
    description: '热爱音乐、追求个性表达的年轻群体。经常参加户外活动和音乐节，对产品外观和便携性要求高。' },
  { id: 'outdoor-dad', name: '家庭户外派', age: '30-40', gender: '男性 (72%)', income: '¥15k-25k',
    interests: ['自驾游', '家庭露营', '烧烤聚会', '数码装备'], color: '#2563eb',
    description: '有家庭的中产男性，周末喜欢带家人户外活动。对音质和续航有较高要求，价格敏感度中等。' },
  { id: 'fitness-girl', name: '运动健身族', age: '22-32', gender: '女性 (68%)', income: '¥8k-15k',
    interests: ['瑜伽', '跑步', '健身房', '健康饮食'], color: '#16a34a',
    description: '注重健康生活方式的年轻女性。运动场景使用频率高，偏好轻便防水的产品。' },
  { id: 'tech-geek', name: '科技发烧友', age: '25-35', gender: '男性 (80%)', income: '¥20k+',
    interests: ['数码评测', '智能家居', 'Hi-Fi音频', '极客社区'], color: '#7c3aed',
    description: '对技术参数极为敏感，追求音质和功能的极致。是社区中的意见领袖，影响周围人的购买决策。' },
]

function PersonasTab() {
  const [selectedPersonas, setSelectedPersonas] = useState<string[]>(['young-music'])
  const [activePersona, setActivePersona] = useState<Persona>(STATIC_PERSONAS[0])
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: '你好！我现在正在模拟「潮流音乐党」的心理和行为模式。你可以问我关于购买决策、品牌偏好、使用场景等任何问题。' },
  ])
  const [inputValue, setInputValue] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  const togglePersona = (id: string) => setSelectedPersonas(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id])

  const selectActive = (persona: Persona) => {
    setActivePersona(persona)
    if (!selectedPersonas.includes(persona.id)) setSelectedPersonas(prev => [...prev, persona.id])
  }

  const sendMessage = async () => {
    if (!inputValue.trim() || aiLoading) return
    const userMsg: ChatMessage = { role: 'user', content: inputValue }
    setMessages(prev => [...prev, userMsg])
    const question = inputValue
    setInputValue('')
    setAiLoading(true)

    const names = selectedPersonas.map(id => STATIC_PERSONAS.find(p => p.id === id)?.name).filter(Boolean).join('、')
    const personaDesc = selectedPersonas.map(id => {
      const p = STATIC_PERSONAS.find(pp => pp.id === id)
      return p ? `${p.name}(${p.age},${p.gender},${p.income},兴趣:${p.interests.join('/')},${p.description})` : ''
    }).filter(Boolean).join('\n')

    try {
      const report = await api<ReportItem>('/reports/generate', {
        method: 'POST',
        body: JSON.stringify({
          report_type: 'custom',
          title: `用户画像对话-${names}`,
          brands: selectedPersonas.map(id => STATIC_PERSONAS.find(p => p.id === id)?.name).filter(Boolean) as string[],
          custom_prompt: `你正在模拟以下目标用户群体的心理和行为模式，请以第一人称回答：\n${personaDesc}\n\n用户问题：${question}\n\n请以这些人群的视角回答，真实具体有洞察力，200字以内。`,
        }),
      })
      setMessages(prev => [...prev, { role: 'assistant', content: report.content }])
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: `[请求失败] ${e.message}` }])
    } finally { setAiLoading(false) }
  }

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  return (
    <div className="grid grid-cols-2 gap-5 p-6 h-full">
      {/* 左: 人群 */}
      <div className="liquid-glass p-6 glass-float-in glass-float-in-delay-1 flex flex-col">
        <div className="flex items-center gap-2 mb-4">
          <Users size={16} className="text-[var(--green)]" />
          <span className="text-sm font-semibold">目标人群</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-black/[0.04] text-[var(--text-muted)]">可多选</span>
        </div>
        <div className="grid grid-cols-2 gap-2 mb-4">
          {STATIC_PERSONAS.map(persona => (
            <div key={persona.id} onClick={() => selectActive(persona)}
              className={`persona-card p-3 ${selectedPersonas.includes(persona.id) ? 'selected' : ''} ${activePersona.id === persona.id ? '!border-[var(--accent)]' : ''}`}>
              <div className="flex items-center gap-2 mb-1.5">
                <div className="w-2 h-2 rounded-full" style={{ background: persona.color }} />
                <span className="text-xs font-semibold">{persona.name}</span>
                <button onClick={(e) => { e.stopPropagation(); togglePersona(persona.id) }}
                  className={`ml-auto w-4 h-4 rounded border flex items-center justify-center transition-all ${selectedPersonas.includes(persona.id) ? 'bg-[var(--accent)] border-[var(--accent)]' : 'border-[var(--glass-border)]'}`}>
                  {selectedPersonas.includes(persona.id) && <Check size={10} className="text-white" />}
                </button>
              </div>
              <div className="text-[10px] text-[var(--text-muted)] space-y-0.5">
                <p>{persona.age} · {persona.gender}</p>
                <p>{persona.income}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="flex-1 rounded-2xl bg-black/[0.02] p-4 flex flex-col items-center justify-center min-h-[180px]">
          <PersonaBlob persona={activePersona} isActive={true} />
          <div className="text-center mt-3">
            <div className="text-sm font-bold" style={{ color: activePersona.color }}>{activePersona.name}</div>
            <p className="text-[10px] text-[var(--text-muted)] mt-1 max-w-[240px] leading-relaxed">{activePersona.description}</p>
            <div className="flex flex-wrap gap-1 justify-center mt-2">
              {activePersona.interests.map(tag => (
                <span key={tag} className="text-[9px] px-1.5 py-0.5 rounded-full" style={{ background: `${activePersona.color}10`, color: activePersona.color }}>{tag}</span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 右: 对话 */}
      <div className="liquid-glass p-6 glass-float-in glass-float-in-delay-2 flex flex-col">
        <div className="flex items-center gap-2 mb-4">
          <MessageSquare size={16} className="text-[var(--purple)]" />
          <span className="text-sm font-semibold">用户对话模拟</span>
          <span className="text-[10px] text-[var(--text-muted)] ml-auto">已选 {selectedPersonas.length} 个人群</span>
        </div>
        <div className="flex flex-wrap gap-1.5 mb-3">
          {selectedPersonas.map(id => {
            const p = STATIC_PERSONAS.find(pp => pp.id === id)!
            return (
              <span key={id} className="text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1" style={{ background: `${p.color}10`, color: p.color }}>
                {p.name}
                <button onClick={() => togglePersona(id)} className="hover:opacity-70"><X size={10} /></button>
              </span>
            )
          })}
        </div>
        <div className="flex-1 overflow-y-auto space-y-3 mb-4 pr-1">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-[var(--accent)]/10' : 'bg-[var(--purple)]/10'}`}>
                {msg.role === 'user' ? <User size={13} className="text-[var(--accent)]" /> : <Bot size={13} className="text-[var(--purple)]" />}
              </div>
              <div className={`max-w-[80%] px-3.5 py-2.5 ${msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'}`}>
                <p className="text-xs leading-relaxed">{msg.content}</p>
              </div>
            </div>
          ))}
          {aiLoading && (
            <div className="flex gap-2.5">
              <div className="w-7 h-7 rounded-full flex items-center justify-center bg-[var(--purple)]/10"><Bot size={13} className="text-[var(--purple)]" /></div>
              <div className="chat-bubble-ai px-3.5 py-2.5"><Loader2 size={14} className="animate-spin text-[var(--purple)]" /></div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        <div className="flex gap-2">
          <input value={inputValue} onChange={e => setInputValue(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()} className="input-glass flex-1 !text-xs"
            placeholder="作为目标用户，你最看重什么？" />
          <button onClick={sendMessage} disabled={aiLoading} className="btn-primary !p-2.5 !rounded-xl disabled:opacity-50">
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}

// ==================== Tab 4: 完整方案 ====================

const PROPOSAL_SLIDES = [
  { title: '市场概览', subtitle: '户外蓝牙音箱行业分析', type: 'cover' as const },
  { title: '行业规模', subtitle: '2025年市场规模达228.8亿元，CAGR 12.3%', type: 'data' as const },
  { title: '竞品格局', subtitle: '核心竞品深度对比分析', type: 'comparison' as const },
  { title: '目标人群', subtitle: '核心用户画像解析', type: 'persona' as const },
  { title: 'SWOT分析', subtitle: '优势 · 劣势 · 机会 · 威胁', type: 'swot' as const },
  { title: '传播策略', subtitle: '全域营销渠道组合推荐', type: 'strategy' as const },
  { title: '执行排期', subtitle: 'Q2-Q3 关键节点里程碑', type: 'timeline' as const },
  { title: '预算分配', subtitle: '预算最优分配方案', type: 'budget' as const },
]

function ProposalTab() {
  const [currentSlide, setCurrentSlide] = useState(0)
  const slide = PROPOSAL_SLIDES[currentSlide]
  const [generating, setGenerating] = useState(false)
  const [generated, setGenerated] = useState<Record<string, string>>({})

  const handleGenerate = async (type: string) => {
    setGenerating(true)
    const prompts: Record<string, string> = {
      comparison: '基于竞品监测数据生成竞品对比分析。包括价格、功能、市场定位对比。简洁专业，300字以内。',
      persona: '分析核心用户画像：年龄、消费习惯、购买动机、使用场景。简洁200字以内。',
      strategy: '推荐全域营销传播策略：渠道选择、内容策略、KOL合作、投放节奏。300字以内。',
      timeline: '制定Q2-Q3营销执行排期，列出关键节点和里程碑。200字以内。',
      budget: '制定预算分配方案，列出渠道占比和ROI预期。200字以内。',
    }
    try {
      const report = await api<ReportItem>('/reports/generate', {
        method: 'POST',
        body: JSON.stringify({
          report_type: 'custom', title: `方案-${slide.title}`, brands: [],
          custom_prompt: prompts[type] || `生成「${slide.title}」的市场分析内容，简洁专业。`,
        }),
      })
      setGenerated(prev => ({ ...prev, [type]: report.content }))
    } catch (e: any) { alert(`生成失败: ${e.message}`) } finally { setGenerating(false) }
  }

  const renderContent = () => {
    const content = generated[slide.type]
    if (content) {
      return (
        <div className="flex flex-col h-full relative z-10 p-10">
          <h2 className="text-xl font-bold mb-2 flex items-center gap-2"><Sparkles size={18} className="text-[var(--accent)]" /> {slide.title}</h2>
          <p className="text-xs text-[var(--text-muted)] mb-4">{slide.subtitle}</p>
          <div className="flex-1 overflow-y-auto text-sm text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap">{content}</div>
        </div>
      )
    }

    switch (slide.type) {
      case 'cover':
        return (
          <div className="flex flex-col items-center justify-center h-full relative z-10">
            <BarChart3 size={48} className="text-[var(--accent)] mb-6" strokeWidth={1.5} />
            <h1 className="text-3xl font-bold tracking-tight">{slide.title}</h1>
            <p className="text-base text-[var(--text-secondary)] mt-3">{slide.subtitle}</p>
            <div className="mt-8 flex items-center gap-3">
              <div className="w-12 h-[1px] bg-[var(--accent)]/30" />
              <span className="text-xs text-[var(--accent)] font-medium flex items-center gap-1.5"><Cog size={11} /> 小蟹研究员 · AI 市场调研</span>
              <div className="w-12 h-[1px] bg-[var(--accent)]/30" />
            </div>
            <p className="text-xs text-[var(--text-muted)] mt-4">2026年3月 · 纯麦科技</p>
          </div>
        )
      case 'data':
        return (
          <div className="flex flex-col justify-center h-full px-12 relative z-10">
            <h2 className="text-xl font-bold mb-8 flex items-center gap-2"><TrendingUp size={20} className="text-[var(--accent)]" /> {slide.title}</h2>
            <div className="grid grid-cols-3 gap-6">
              {[
                { label: '市场规模', value: '228.8亿', unit: '元', trend: '+12.3%', icon: <DollarSign size={14} /> },
                { label: '年复合增长率', value: '12.3', unit: '%', trend: '稳健增长', icon: <TrendingUp size={14} /> },
                { label: '在线渗透率', value: '67.2', unit: '%', trend: '+5.1%', icon: <Globe size={14} /> },
              ].map(item => (
                <div key={item.label} className="p-5 rounded-2xl bg-black/[0.02] border border-[var(--glass-border)]">
                  <div className="text-xs text-[var(--text-muted)] mb-2 flex items-center gap-1.5">{item.icon} {item.label}</div>
                  <div className="text-2xl font-bold text-[var(--accent)]">{item.value}<span className="text-sm text-[var(--text-muted)] ml-1">{item.unit}</span></div>
                  <div className="text-xs text-[var(--green)] mt-2 flex items-center gap-1"><TrendingUp size={10} /> {item.trend}</div>
                </div>
              ))}
            </div>
          </div>
        )
      case 'swot':
        return (
          <div className="flex flex-col justify-center h-full px-10 relative z-10">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2"><Target size={20} className="text-[var(--accent)]" /> {slide.title}</h2>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'S 优势', items: ['品牌口碑好', '性价比高', '本土化设计'], color: 'var(--green)', bg: 'rgba(22,163,74,0.05)' },
                { label: 'W 劣势', items: ['海外知名度低', '高端线缺失', '渠道覆盖有限'], color: 'var(--yellow)', bg: 'rgba(202,138,4,0.05)' },
                { label: 'O 机会', items: ['露营经济爆发', '直播电商增长', 'Z世代消费升级'], color: 'var(--blue)', bg: 'rgba(37,99,235,0.05)' },
                { label: 'T 威胁', items: ['国际品牌降价', '同质化竞争加剧', '原材料成本上升'], color: 'var(--red)', bg: 'rgba(220,38,38,0.05)' },
              ].map(q => (
                <div key={q.label} className="p-4 rounded-2xl border border-[var(--glass-border)]" style={{ background: q.bg }}>
                  <div className="text-sm font-bold mb-2" style={{ color: q.color }}>{q.label}</div>
                  {q.items.map(item => (
                    <div key={item} className="text-xs text-[var(--text-secondary)] flex items-center gap-1.5 mb-1">
                      <span className="w-1 h-1 rounded-full shrink-0" style={{ background: q.color }} /> {item}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )
      default:
        return (
          <div className="flex flex-col items-center justify-center h-full relative z-10">
            <Sparkles size={32} className="text-[var(--accent)] mb-4 opacity-50" />
            <h2 className="text-xl font-bold mb-3">{slide.title}</h2>
            <p className="text-sm text-[var(--text-secondary)]">{slide.subtitle}</p>
            <button onClick={() => handleGenerate(slide.type)} disabled={generating}
              className="mt-6 btn-primary !text-xs flex items-center gap-2 disabled:opacity-50">
              {generating ? <Loader2 size={12} className="animate-spin" /> : <Sparkles size={12} />}
              {generating ? 'AI 正在生成...' : 'AI 生成此页'}
            </button>
          </div>
        )
    }
  }

  return (
    <div className="p-6 flex flex-col gap-5">
      <div className="liquid-glass glass-float-in glass-float-in-delay-1 overflow-hidden">
        <div className="ppt-slide">{renderContent()}</div>
      </div>
      <div className="liquid-glass p-4 glass-float-in glass-float-in-delay-2">
        <div className="flex items-center justify-between">
          <button onClick={() => setCurrentSlide(Math.max(0, currentSlide - 1))} disabled={currentSlide === 0}
            className="btn-ghost !py-1.5 !px-3 !text-xs flex items-center gap-1 disabled:opacity-30">
            <ChevronLeft size={14} /> 上一页
          </button>
          <div className="flex items-center gap-2">
            {PROPOSAL_SLIDES.map((s, i) => (
              <button key={i} onClick={() => setCurrentSlide(i)}
                className={`w-16 h-9 rounded-lg border text-[8px] font-medium transition-all flex items-center justify-center ${i === currentSlide ? 'border-[var(--accent)] bg-[var(--accent)]/8 text-[var(--accent)]' : 'border-[var(--glass-border)] bg-black/[0.02] text-[var(--text-muted)] hover:border-black/10'}`}>
                {s.title}
              </button>
            ))}
          </div>
          <button onClick={() => setCurrentSlide(Math.min(PROPOSAL_SLIDES.length - 1, currentSlide + 1))} disabled={currentSlide === PROPOSAL_SLIDES.length - 1}
            className="btn-ghost !py-1.5 !px-3 !text-xs flex items-center gap-1 disabled:opacity-30">
            下一页 <ChevronRight size={14} />
          </button>
        </div>
        <div className="text-center mt-2">
          <span className="text-[10px] text-[var(--text-muted)] font-[var(--font-mono)]">{currentSlide + 1} / {PROPOSAL_SLIDES.length}</span>
        </div>
      </div>
    </div>
  )
}

// ==================== 主应用 ====================

const TABS: TabDef[] = [
  { id: 'overview', label: '基础信息', icon: <BarChart3 size={16} />, price: '免费', priceClass: 'free' },
  { id: 'competitors', label: '竞品分析', icon: <Shield size={16} />, price: '¥99', priceClass: 'paid' },
  { id: 'personas', label: '用户洞察', icon: <Users size={16} />, price: '¥299', priceClass: 'premium' },
  { id: 'proposal', label: '完整方案', icon: <FileText size={16} />, price: '¥599', priceClass: 'enterprise' },
]

export default function App() {
  const [authed, setAuthed] = useState(!!getToken())
  const [activeTab, setActiveTab] = useState<TabId>('overview')
  const [currentTime, setCurrentTime] = useState(new Date())
  const [showUserPanel, setShowUserPanel] = useState(false)
  const userPanelRef = useRef<HTMLDivElement>(null)
  const { data: health } = useApi<{ status: string }>('/system/health')
  const { data: userInfo, refetch: refetchUser } = useApi<UserInfo>(authed ? '/auth/me' : null, [authed])

  // 注册 401 回调：token 过期时回到登录页，不 reload
  useEffect(() => {
    setAuthExpiredHandler(() => setAuthed(false))
    return () => { _onAuthExpired = null }
  }, [])

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (userPanelRef.current && !userPanelRef.current.contains(e.target as Node)) {
        setShowUserPanel(false)
      }
    }
    if (showUserPanel) document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showUserPanel])

  const isOnline = health?.status === 'ok'

  const handleLogin = () => { setAuthed(true); refetchUser() }
  const handleLogout = () => { clearToken(); setAuthed(false); setShowUserPanel(false) }

  if (!authed) return <AuthPage onLogin={handleLogin} />

  return (
    <div className="h-screen flex overflow-hidden relative">
      <div className="frosted-backdrop" style={{
        background: 'linear-gradient(135deg, #f8f9fb 0%, #eef1f5 40%, #f0f2f6 100%)',
      }} />

      {/* 侧边栏 */}
      <aside className="sidebar-glass w-44 flex flex-col shrink-0 relative z-10">
        <div className="p-5 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[#ea580c] flex items-center justify-center">
              <BarChart3 size={16} className="text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-gradient tracking-wide">小蟹研究员</h1>
              <p className="text-[10px] text-[var(--text-muted)] mt-0.5 font-[var(--font-mono)]">Crab Researcher</p>
            </div>
          </div>
        </div>
        <div className="mx-4 h-[1px] bg-[var(--glass-border)]" />
        <nav className="flex-1 p-3 space-y-1 mt-1">
          {TABS.map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)}
              className={`tab-item w-full ${activeTab === tab.id ? 'active' : ''}`}>
              <span className={activeTab === tab.id ? 'text-[var(--accent)]' : ''}>{tab.icon}</span>
              <span>{tab.label}</span>
              <span className={`tab-price ${tab.priceClass}`}>{tab.price}</span>
            </button>
          ))}
        </nav>
        <div className="relative p-4 border-t border-[var(--glass-border)]" ref={userPanelRef}>
          {/* 用户信息弹窗 */}
          {showUserPanel && (
            <div className="absolute bottom-full left-3 right-3 mb-2 rounded-2xl bg-white/95 backdrop-blur-xl border border-[var(--glass-border)] shadow-lg overflow-hidden animate-[slide-up_0.2s_ease]" style={{ zIndex: 50 }}>
              <div className="p-4 bg-gradient-to-br from-[var(--accent)]/5 to-[var(--accent)]/[0.02]">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-[var(--accent)]/10 flex items-center justify-center">
                    <User size={18} className="text-[var(--accent)]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">{userInfo?.company_name || '--'}</p>
                    <p className="text-[10px] text-[var(--text-muted)] truncate">{userInfo?.contact_email || '--'}</p>
                  </div>
                </div>
              </div>
              {userInfo && (
                <div className="px-4 py-3 space-y-2.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[var(--text-muted)] flex items-center gap-1.5"><Mail size={11} /> 邮箱</span>
                    <span className="font-medium truncate ml-2">{userInfo.contact_email}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[var(--text-muted)] flex items-center gap-1.5"><Briefcase size={11} /> 套餐</span>
                    <span className="font-medium px-1.5 py-0.5 rounded bg-[var(--accent)]/8 text-[var(--accent)] text-[10px]">{userInfo.subscription_plan}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[var(--text-muted)] flex items-center gap-1.5"><DollarSign size={11} /> 预算</span>
                    <span className="font-medium font-[var(--font-mono)]">¥{userInfo.monthly_token_used.toFixed(1)} / ¥{userInfo.monthly_budget}</span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-[var(--text-muted)] flex items-center gap-1.5"><Clock size={11} /> 注册时间</span>
                    <span className="font-medium font-[var(--font-mono)] text-[10px]">{new Date(userInfo.created_at).toLocaleDateString('zh-CN')}</span>
                  </div>
                </div>
              )}
              <div className="px-4 pb-4 pt-1">
                <button onClick={() => { setShowUserPanel(false); handleLogout() }}
                  className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-medium text-[var(--red)] bg-red-50 hover:bg-red-100 transition-colors">
                  <LogOut size={13} /> 退出登录
                </button>
              </div>
            </div>
          )}
          {/* 底部用户头像按钮 */}
          <div onClick={() => setShowUserPanel(!showUserPanel)} className="flex items-center gap-2.5 cursor-pointer rounded-xl p-1.5 -m-1.5 hover:bg-black/[0.03] transition-colors">
            <div className="w-8 h-8 rounded-full bg-[var(--accent)]/8 flex items-center justify-center">
              <User size={14} className="text-[var(--accent)]" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium truncate">{userInfo?.company_name || '加载中...'}</p>
              <p className="text-[10px] text-[var(--text-muted)]">{userInfo?.subscription_plan || 'free'}</p>
            </div>
            <ChevronDown size={12} className={`text-[var(--text-muted)] transition-transform ${showUserPanel ? 'rotate-180' : ''}`} />
          </div>
        </div>
      </aside>

      {/* 主内容 */}
      <main className="flex-1 flex flex-col overflow-hidden relative z-10">
        <header className="flex items-center justify-between px-6 py-3.5 border-b border-[var(--glass-border)] bg-white/40 backdrop-blur-xl">
          <h2 className="text-base font-bold tracking-wide">{TABS.find(t => t.id === activeTab)?.label}</h2>
          <div className="flex items-center gap-4 text-xs text-[var(--text-muted)]">
            <span className="font-[var(--font-mono)]">{currentTime.toLocaleString('zh-CN', { hour12: false })}</span>
            <div className="flex items-center gap-1.5">
              {isOnline ? <Wifi size={12} className="text-[var(--green)]" /> : <WifiOff size={12} className="text-[var(--red)]" />}
              <span>{isOnline ? '已连接' : '离线'}</span>
            </div>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'overview' && <OverviewTab />}
          {activeTab === 'competitors' && <CompetitorsTab />}
          {activeTab === 'personas' && <PersonasTab />}
          {activeTab === 'proposal' && <ProposalTab />}
        </div>
      </main>
    </div>
  )
}
