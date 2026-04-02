/**
 * Chat — Agent 对话页面 v2
 * 
 * 群聊形态：CrabRes + 专家都在同一个对话流中。
 * 用户看到的是一个"增长团队群聊"，不是一对一对话。
 * 专家发言以不同颜色的小头像区分。
 */

import { useState, useRef, useEffect } from 'react'
import { CreatureRenderer } from '../components/creature/CreatureRenderer'
import { RoundtableSimulation } from '../components/ui/RoundtableSimulation'
import type { CreatureState } from '../components/creature/types'
import { api } from '../lib/api'
import { EXPERTS } from '../lib/experts'

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
  const [messages, setMessages] = useState<Message[]>([{
    id: '0', role: 'assistant',
    content: "Hey! Tell me about your product and I'll start researching your market. I'll search for competitors, find your target users, and build you a growth plan — with every post and email written.",
    timestamp: Date.now(),
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [activeExpert, setActiveExpert] = useState<string | undefined>(undefined)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg: Message = { id: `u-${Date.now()}`, role: 'user', content: input.trim(), timestamp: Date.now() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await api<any[]>('/agent/chat', {
        method: 'POST',
        body: JSON.stringify({ message: userMsg.content, session_id: sessionId }),
      })
      if (res.length > 0 && res[0].session_id) setSessionId(res[0].session_id)

      // 模拟圆桌讨论过程：逐步放出专家见解
      for (let i = 0; i < res.length; i++) {
        const r = res[i];
        
        // 处理专家思考状态：同步到可视化组件
        if (r.type === 'expert_thinking') {
          setActiveExpert(r.expert_id);
          // 专家思考时的小停顿，增强真实感
          if (r.content.includes('is analyzing')) {
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        } else {
          setActiveExpert(undefined);
        }

        const newMsg: Message = {
          id: `a-${Date.now()}-${i}`,
          role: r.type === 'expert_thinking' ? 'expert' as const
            : r.type === 'status' ? 'status' as const
            : 'assistant' as const,
          content: r.content,
          expertId: r.expert_id || undefined,
          timestamp: Date.now() + i,
        };

        // 如果已经有同一个专家的最终结论，就替换掉"正在分析"的中间状态
        setMessages(prev => {
          if (r.type === 'expert_thinking' && !r.content.includes('is analyzing')) {
            const filtered = prev.filter(m => !(m.expertId === r.expert_id && m.content.includes('is analyzing')));
            return [...filtered, newMsg];
          }
          return [...prev, newMsg];
        });
        
        // 每个消息之间的呼吸感
        if (i < res.length - 1) {
          const delay = r.type === 'status' ? 200 : 400;
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
      setActiveExpert(undefined);
    } catch (e: any) {
      setMessages(prev => [...prev, {
        id: `e-${Date.now()}`, role: 'assistant',
        content: `Something went wrong: ${e.message}. Please try again.`,
        timestamp: Date.now(),
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  // 统计活跃专家
  const activeExperts = new Set(messages.filter(m => m.role === 'expert').map(m => m.expertId).filter(Boolean))

  return (
    <div className="min-h-screen bg-surface bg-grid bg-noise flex flex-col max-w-2xl mx-auto relative z-10">
      {/* 头部 */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-border bg-glass sticky top-0 z-20">
        <button onClick={onBack} className="p-2 rounded-xl hover:bg-hover transition-colors">
          <ArrowLeftIcon />
        </button>
        <div className="flex -space-x-1.5">
          <CreatureRenderer creature={{ ...creature, mood: loading ? 'thinking' : 'happy' }} size={28} animate={loading} />
          {/* 显示活跃专家的小头像 */}
          {Array.from(activeExperts).slice(0, 4).map(eid => {
            const expert = EXPERTS[eid || '']
            return expert ? (
              <div key={eid} className="w-7 h-7 rounded-full flex items-center justify-center text-xs border-2 border-white"
                style={{ background: expert.color + '20', color: expert.color }}>
                {expert.icon}
              </div>
            ) : null
          })}
          {activeExperts.size > 4 && (
            <div className="w-7 h-7 rounded-full bg-hover flex items-center justify-center text-[10px] text-muted border-2 border-white">
              +{activeExperts.size - 4}
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-heading font-semibold text-primary">Growth Team</p>
          <p className="text-xs text-muted truncate">
            {loading ? 'Researching your market...' :
              activeExperts.size > 0 ? `${activeExperts.size} experts contributed` : '13 experts ready'}
          </p>
        </div>
      </div>

      {/* 消息区 — 群聊形态 */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {/* 专家圆桌模拟可视化 */}
        {(loading || activeExpert || messages.some(m => m.role === 'expert')) && (
          <RoundtableSimulation activeExpertId={activeExpert} isSimulating={loading || !!activeExpert} />
        )}

        {messages.map(msg => {
          // 用户消息
          if (msg.role === 'user') {
            return (
              <div key={msg.id} className="flex justify-end animate-fade-in">
                <div className="max-w-[80%] px-4 py-3 rounded-2xl rounded-br-sm bg-brand text-white text-sm shadow-sm">
                  {msg.content}
                </div>
              </div>
            )
          }

          // CrabRes 主消息（Coordinator 的统一输出）
          if (msg.role === 'assistant') {
            return (
              <div key={msg.id} className="flex gap-2.5 animate-fade-in">
                <div className="w-7 h-7 shrink-0 mt-0.5">
                  <CreatureRenderer creature={creature} size={28} animate={false} />
                </div>
                <div className="max-w-[85%]">
                  <p className="text-[10px] font-heading font-medium text-brand mb-1">CrabRes</p>
                  <div className="px-4 py-3 rounded-2xl rounded-tl-sm card text-sm text-primary whitespace-pre-wrap leading-relaxed">
                    {msg.content}
                  </div>
                </div>
              </div>
            )
          }

          // 专家发言（群聊中其他成员的消息）
          if (msg.role === 'expert' && msg.expertId) {
            const expert = EXPERTS[msg.expertId]
            if (!expert) return null
            return (
              <div key={msg.id} className="flex gap-2.5 animate-fade-in">
                <div className="w-7 h-7 shrink-0 mt-0.5 rounded-full flex items-center justify-center text-xs"
                  style={{ background: expert.color + '15', color: expert.color }}>
                  {expert.icon}
                </div>
                <div className="max-w-[85%]">
                  <p className="text-[10px] font-heading font-medium mb-1" style={{ color: expert.color }}>
                    {expert.name}
                  </p>
                  <div className="px-3.5 py-2.5 rounded-2xl rounded-tl-sm text-sm text-secondary leading-relaxed"
                    style={{ background: expert.color + '08', border: `1px solid ${expert.color}15` }}>
                    {msg.content.length > 300 ? (
                      <CollapsibleText text={msg.content} maxLength={300} />
                    ) : msg.content}
                  </div>
                </div>
              </div>
            )
          }

          // 状态消息
          if (msg.role === 'status') {
            return (
              <div key={msg.id} className="flex justify-center animate-fade-in">
                <span className="text-xs text-muted bg-hover px-3 py-1.5 rounded-full flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand animate-pulse" />
                  {msg.content}
                </span>
              </div>
            )
          }

          return null
        })}

        {/* 正在思考指示器 */}
        {loading && (
          <div className="flex gap-2.5 animate-fade-in">
            <div className="w-7 h-7 shrink-0 mt-0.5">
              <CreatureRenderer creature={{ ...creature, mood: 'thinking' }} size={28} />
            </div>
            <div className="px-4 py-3 rounded-2xl rounded-tl-sm card">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-brand/50 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-1.5 h-1.5 rounded-full bg-brand/50 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-1.5 h-1.5 rounded-full bg-brand/50 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-xs text-muted">Researching...</span>
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
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
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

// 可折叠长文本
function CollapsibleText({ text, maxLength }: { text: string; maxLength: number }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <>
      {expanded ? text : text.slice(0, maxLength) + '...'}
      <button onClick={() => setExpanded(!expanded)}
        className="ml-1 text-brand text-xs hover:underline">
        {expanded ? 'Show less' : 'Read more'}
      </button>
    </>
  )
}

// 图标
import { ArrowLeftIcon } from '../components/ui/Icons'
function SendIcon() {
  return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-white"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
}
