/**
 * Chat — Agent 对话页面
 * 
 * 用户和 CrabRes 深入对话。
 * CrabRes 是一个声音，专家圆桌可选展开。
 */

import { useState, useRef, useEffect } from 'react'
import { CreatureRenderer } from '../components/creature/CreatureRenderer'
import type { CreatureState } from '../components/creature/types'
import { api } from '../lib/api'

interface ChatProps {
  creature: CreatureState
  onBack: () => void
}

interface Message {
  id: string
  role: 'user' | 'assistant' | 'status' | 'expert'
  content: string
  expertId?: string
  timestamp: number
}

export function Chat({ creature, onBack }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: "Hey! Tell me about your product and what you're trying to achieve. I'll research your market and build a growth plan.",
      timestamp: Date.now(),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [expandedExperts, setExpandedExperts] = useState<Set<string>>(new Set())
  const [showRoundtable, setShowRoundtable] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg: Message = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: Date.now(),
    }
    setMessages(prev => [...prev, userMsg])
    const text = input.trim()
    setInput('')
    setLoading(true)

    try {
      const res = await api<any[]>('/agent/chat', {
        method: 'POST',
        body: JSON.stringify({ message: text, session_id: sessionId }),
      })

      if (res.length > 0 && res[0].session_id) {
        setSessionId(res[0].session_id)
      }

      const newMsgs: Message[] = res.map((r: any, i: number) => ({
        id: `a-${Date.now()}-${i}`,
        role: r.type === 'expert_thinking' ? 'expert' as const
          : r.type === 'status' ? 'status' as const
          : 'assistant' as const,
        content: r.content,
        expertId: r.expert_id || undefined,
        timestamp: Date.now() + i,
      }))

      setMessages(prev => [...prev, ...newMsgs])
    } catch (e: any) {
      setMessages(prev => [...prev, {
        id: `e-${Date.now()}`,
        role: 'assistant',
        content: `Something went wrong: ${e.message}. Please try again.`,
        timestamp: Date.now(),
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const toggleExpert = (id: string) => {
    setExpandedExperts(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  // 收集所有专家消息
  const expertMessages = messages.filter(m => m.role === 'expert')

  // 将连续的 expert 消息分组
  const groupedMessages = groupMessages(messages)

  return (
    <div className="min-h-screen bg-surface flex flex-col max-w-2xl mx-auto">
      {/* 头部 */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-border bg-glass sticky top-0 z-10">
        <button onClick={onBack} className="p-2 rounded-xl hover:bg-hover transition-colors">
          <ArrowLeftIcon />
        </button>
        <CreatureRenderer creature={{ ...creature, mood: loading ? 'thinking' : 'happy' }} size={32} animate={loading} />
        <div className="flex-1">
          <p className="text-sm font-medium text-primary">CrabRes</p>
          <p className="text-xs text-muted">
            {loading ? 'Researching...' : '13 experts ready'}
          </p>
        </div>
        {sessionId && (
          <span className="text-xs text-muted font-mono">
            {sessionId.slice(0, 8)}
          </span>
        )}
      </div>

      {/* 圆桌状态面板 — 显示专家工作状态 */}
      {(loading || expertMessages.length > 0) && (
        <div className="px-4 py-2 border-b border-border bg-surface">
          <button
            onClick={() => setShowRoundtable(!showRoundtable)}
            className="w-full flex items-center gap-2 text-xs text-muted hover:text-secondary transition-colors"
          >
            <RoundtableIcon />
            <span className="font-heading font-medium">
              Expert Roundtable {expertMessages.length > 0 ? `(${expertMessages.length} contributions)` : ''}
            </span>
            <span className="ml-auto">{showRoundtable ? '▲' : '▼'}</span>
          </button>

          {showRoundtable && (
            <div className="mt-2 space-y-2 animate-fade-in">
              {/* 活跃专家 */}
              <div className="flex flex-wrap gap-1.5">
                {Object.keys(EXPERT_NAMES).map(eid => {
                  const isActive = expertMessages.some(m => m.expertId === eid)
                  const isWorking = loading && !isActive
                  return (
                    <span
                      key={eid}
                      className={`text-[10px] px-2 py-1 rounded-full border transition-all ${
                        isActive
                          ? 'border-brand/30 bg-brand/5 text-brand'
                          : isWorking
                          ? 'border-border bg-hover text-muted animate-pulse'
                          : 'border-transparent text-muted/50'
                      }`}
                    >
                      {EXPERT_NAMES[eid]?.split(' ')[0]} {isActive ? '✓' : ''}
                    </span>
                  )
                })}
              </div>

              {/* 专家发言摘要 */}
              {expertMessages.length > 0 && (
                <div className="space-y-1.5 pl-2 border-l-2 border-brand/15">
                  {expertMessages.slice(-5).map(m => (
                    <div key={m.id} className="text-xs">
                      <span className="font-medium text-brand">
                        {EXPERT_NAMES[m.expertId || ''] || 'Expert'}
                      </span>
                      <p className="text-secondary mt-0.5 line-clamp-2">
                        {m.content.slice(0, 150)}{m.content.length > 150 ? '...' : ''}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {loading && expertMessages.length === 0 && (
                <p className="text-xs text-muted italic">
                  Researching your market... experts will speak as they find insights.
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* 消息区 */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {groupedMessages.map((item, i) => {
          if (item.type === 'user') {
            return (
              <div key={item.msg.id} className="flex justify-end">
                <div className="max-w-[80%] px-4 py-3 rounded-2xl rounded-br-md bg-brand text-white text-sm">
                  {item.msg.content}
                </div>
              </div>
            )
          }

          if (item.type === 'assistant') {
            return (
              <div key={item.msg.id} className="flex gap-3">
                <div className="w-7 h-7 shrink-0 mt-1">
                  <CreatureRenderer creature={creature} size={28} animate={false} />
                </div>
                <div className="max-w-[85%]">
                  <div className="px-4 py-3 rounded-2xl rounded-bl-md bg-glass border border-border text-sm text-primary whitespace-pre-wrap">
                    {item.msg.content}
                  </div>
                  {/* 如果后面跟着 expert 消息，显示展开按钮 */}
                  {item.experts && item.experts.length > 0 && (
                    <button
                      onClick={() => toggleExpert(item.msg.id)}
                      className="mt-2 flex items-center gap-1.5 text-xs text-muted hover:text-secondary transition-colors"
                    >
                      <RoundtableIcon />
                      {expandedExperts.has(item.msg.id)
                        ? 'Hide expert roundtable'
                        : `See expert roundtable (${item.experts.length} experts)`}
                    </button>
                  )}
                  {/* 展开的专家讨论 */}
                  {expandedExperts.has(item.msg.id) && item.experts && (
                    <div className="mt-2 ml-2 pl-3 border-l-2 border-brand/20 space-y-2">
                      {item.experts.map(expert => (
                        <div key={expert.id} className="text-xs">
                          <span className="font-medium text-brand">
                            {EXPERT_NAMES[expert.expertId || ''] || 'Expert'}
                          </span>
                          <p className="text-secondary mt-0.5 whitespace-pre-wrap">
                            {expert.content.slice(0, 500)}
                            {expert.content.length > 500 && '...'}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )
          }

          if (item.type === 'status') {
            return (
              <div key={item.msg.id} className="flex justify-center">
                <span className="text-xs text-muted bg-hover px-3 py-1 rounded-full">
                  {item.msg.content}
                </span>
              </div>
            )
          }

          return null
        })}

        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 shrink-0 mt-1">
              <CreatureRenderer creature={{ ...creature, mood: 'thinking' }} size={28} />
            </div>
            <div className="px-4 py-3 rounded-2xl rounded-bl-md bg-glass border border-border">
              <div className="flex gap-1">
                <div className="w-2 h-2 rounded-full bg-brand/40 animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 rounded-full bg-brand/40 animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 rounded-full bg-brand/40 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入区 */}
      <div className="px-4 py-3 border-t border-border bg-glass">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            placeholder="Describe your product, ask anything..."
            className="flex-1 !rounded-xl"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="btn-primary !px-4 !rounded-xl disabled:opacity-40"
          >
            <SendIcon />
          </button>
        </div>
      </div>
    </div>
  )
}

// ====== 消息分组 ======

interface GroupedItem {
  type: 'user' | 'assistant' | 'status'
  msg: Message
  experts?: Message[]
}

function groupMessages(messages: Message[]): GroupedItem[] {
  const result: GroupedItem[] = []
  for (let i = 0; i < messages.length; i++) {
    const msg = messages[i]
    if (msg.role === 'expert') continue // expert 归入前一个 assistant

    const item: GroupedItem = {
      type: msg.role as 'user' | 'assistant' | 'status',
      msg,
    }

    // 收集紧跟的 expert 消息
    if (msg.role === 'assistant') {
      const experts: Message[] = []
      let j = i + 1
      while (j < messages.length && messages[j].role === 'expert') {
        experts.push(messages[j])
        j++
      }
      if (experts.length > 0) item.experts = experts
    }

    result.push(item)
  }
  return result
}

// ====== 专家名称映射 ======

const EXPERT_NAMES: Record<string, string> = {
  market_researcher: '🔍 Market Researcher',
  economist: '💰 Economist',
  content_strategist: '📝 Content Strategist',
  social_media: '🎯 Social Media',
  paid_ads: '📢 Paid Ads',
  partnerships: '🤝 Partnerships',
  ai_distribution: '🤖 AI Distribution',
  psychologist: '🧠 Psychologist',
  product_growth: '📈 Product Growth',
  data_analyst: '📊 Data Analyst',
  copywriter: '✍️ Copywriter',
  critic: '⚖️ Strategy Critic',
  designer: '🎨 Designer',
}

// ====== 图标 ======

function ArrowLeftIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-muted"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
}
function SendIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-white"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
}
function RoundtableIcon() {
  return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
}
