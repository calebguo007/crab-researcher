/**
 * 生物体渲染器
 * 
 * 用 SVG 实时渲染可爱的海洋生物。
 * 每个物种有独特的形状、表情和呼吸动画。
 * 
 * 性能：使用 requestAnimationFrame + useRef 避免 setState 驱动动画
 */

import { useRef, useEffect, useCallback } from 'react'
import type { CreatureState } from './types'

interface Props {
  creature: CreatureState
  size?: number
  animate?: boolean
  onClick?: () => void
}

export function CreatureRenderer({ creature, size = 120, animate = true, onClick }: Props) {
  const svgRef = useRef<SVGSVGElement>(null)
  const phaseRef = useRef(0)
  const rafRef = useRef<number>(0)

  const tick = useCallback(() => {
    phaseRef.current = (phaseRef.current + 2) % 360
    const phase = phaseRef.current
    const svg = svgRef.current
    if (svg) {
      const breathScale = 1 + Math.sin(phase * Math.PI / 180) * 0.03
      const wobble = Math.sin(phase * Math.PI / 90) * 2
      const glowSize = 12 + Math.sin(phase * Math.PI / 180) * 4
      svg.style.transform = `scale(${breathScale}) translateX(${wobble}px)`
      svg.style.filter = `drop-shadow(0 0 ${glowSize}px ${creature.color}40)`
    }
    rafRef.current = requestAnimationFrame(tick)
  }, [creature.color])

  useEffect(() => {
    if (!animate) return
    rafRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafRef.current)
  }, [animate, tick])

  const renderSpecies = () => {
    const { species, color, accentColor, mood } = creature
    const cx = size / 2
    const cy = size / 2
    const r = size * 0.35

    switch (species) {
      case 'crab':
        return (
          <g>
            <ellipse cx={cx} cy={cy + 4} rx={r} ry={r * 0.8} fill={color} opacity={0.9} />
            <circle cx={cx - r - 8} cy={cy - 5} r={r * 0.25} fill={accentColor} />
            <circle cx={cx + r + 8} cy={cy - 5} r={r * 0.25} fill={accentColor} />
            <line x1={cx - 10} y1={cy - r * 0.6} x2={cx - 10} y2={cy - r * 0.9} stroke={color} strokeWidth={3} strokeLinecap="round" />
            <line x1={cx + 10} y1={cy - r * 0.6} x2={cx + 10} y2={cy - r * 0.9} stroke={color} strokeWidth={3} strokeLinecap="round" />
            <circle cx={cx - 10} cy={cy - r * 0.95} r={6} fill="white" />
            <circle cx={cx + 10} cy={cy - r * 0.95} r={6} fill="white" />
            <circle cx={cx - 9} cy={cy - r * 0.95} r={3} fill="#1E293B" />
            <circle cx={cx + 11} cy={cy - r * 0.95} r={3} fill="#1E293B" />
            <circle cx={cx - 8} cy={cy - r * 0.98} r={1.5} fill="white" />
            <circle cx={cx + 12} cy={cy - r * 0.98} r={1.5} fill="white" />
            {mood === 'happy' || mood === 'waving' || mood === 'celebrating' ? (
              <path d={`M ${cx - 6} ${cy + 2} Q ${cx} ${cy + 10} ${cx + 6} ${cy + 2}`} fill="none" stroke="#1E293B" strokeWidth={1.5} strokeLinecap="round" />
            ) : mood === 'sad' ? (
              <path d={`M ${cx - 6} ${cy + 8} Q ${cx} ${cy + 2} ${cx + 6} ${cy + 8}`} fill="none" stroke="#1E293B" strokeWidth={1.5} strokeLinecap="round" />
            ) : (
              <circle cx={cx} cy={cy + 5} r={2} fill="#1E293B" />
            )}
            {[-1, 1].map(dir => [0.3, 0.6, 0.9].map((offset, i) => (
              <line key={`leg-${dir}-${i}`}
                x1={cx + dir * r * 0.5} y1={cy + r * offset * 0.5}
                x2={cx + dir * (r + 10)} y2={cy + r * offset * 0.5 + 8}
                stroke={accentColor} strokeWidth={2} strokeLinecap="round" />
            )))}
          </g>
        )

      case 'octopus':
        return (
          <g>
            <ellipse cx={cx} cy={cy - 8} rx={r * 0.85} ry={r} fill={color} opacity={0.9} />
            {Array.from({ length: 6 }).map((_, i) => {
              const angle = (i / 6) * Math.PI + 0.3
              const x1 = cx + Math.cos(angle) * r * 0.5
              const y1 = cy + 10
              const x2 = cx + Math.cos(angle) * r * 1.2
              const y2 = cy + r + 10
              return <path key={i} d={`M ${x1} ${y1} Q ${(x1 + x2) / 2} ${y2 + 10} ${x2} ${y2}`}
                fill="none" stroke={accentColor} strokeWidth={4} strokeLinecap="round" />
            })}
            <circle cx={cx - 12} cy={cy - 10} r={8} fill="white" />
            <circle cx={cx + 12} cy={cy - 10} r={8} fill="white" />
            <circle cx={cx - 10} cy={cy - 10} r={4} fill="#1E293B" />
            <circle cx={cx + 14} cy={cy - 10} r={4} fill="#1E293B" />
            <circle cx={cx - 9} cy={cy - 12} r={2} fill="white" />
            <circle cx={cx + 15} cy={cy - 12} r={2} fill="white" />
            <path d={`M ${cx - 6} ${cy + 2} Q ${cx} ${cy + 9} ${cx + 6} ${cy + 2}`}
              fill="none" stroke="#1E293B" strokeWidth={1.5} strokeLinecap="round" />
          </g>
        )

      case 'jellyfish':
        return (
          <g>
            <path d={`M ${cx - r} ${cy} Q ${cx - r} ${cy - r * 1.2} ${cx} ${cy - r * 1.2} Q ${cx + r} ${cy - r * 1.2} ${cx + r} ${cy}`}
              fill={color} opacity={0.7} />
            <path d={`M ${cx - r + 5} ${cy - 5} Q ${cx - r + 5} ${cy - r} ${cx} ${cy - r} Q ${cx + r - 5} ${cy - r} ${cx + r - 5} ${cy - 5}`}
              fill="white" opacity={0.2} />
            {Array.from({ length: 5 }).map((_, i) => {
              const x = cx - r * 0.6 + (i * r * 0.3)
              return <path key={i} d={`M ${x} ${cy} Q ${x} ${cy + r * 0.7} ${x} ${cy + r * 1.3}`}
                fill="none" stroke={accentColor} strokeWidth={2} strokeLinecap="round" opacity={0.6} />
            })}
            <circle cx={cx - 10} cy={cy - r * 0.5} r={5} fill="white" />
            <circle cx={cx + 10} cy={cy - r * 0.5} r={5} fill="white" />
            <circle cx={cx - 9} cy={cy - r * 0.5} r={2.5} fill="#1E293B" />
            <circle cx={cx + 11} cy={cy - r * 0.5} r={2.5} fill="#1E293B" />
          </g>
        )

      case 'pufferfish':
        return (
          <g>
            <circle cx={cx} cy={cy} r={r} fill={color} opacity={0.9} />
            {Array.from({ length: 12 }).map((_, i) => {
              const angle = (i / 12) * Math.PI * 2
              const x1 = cx + Math.cos(angle) * r
              const y1 = cy + Math.sin(angle) * r
              const x2 = cx + Math.cos(angle) * (r + 6)
              const y2 = cy + Math.sin(angle) * (r + 6)
              return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2}
                stroke={accentColor} strokeWidth={2} strokeLinecap="round" />
            })}
            <circle cx={cx - 12} cy={cy - 5} r={9} fill="white" />
            <circle cx={cx + 12} cy={cy - 5} r={9} fill="white" />
            <circle cx={cx - 10} cy={cy - 5} r={5} fill="#1E293B" />
            <circle cx={cx + 14} cy={cy - 5} r={5} fill="#1E293B" />
            <circle cx={cx - 9} cy={cy - 7} r={2.5} fill="white" />
            <circle cx={cx + 15} cy={cy - 7} r={2.5} fill="white" />
            <ellipse cx={cx} cy={cy + 10} rx={4} ry={5} fill="#1E293B" opacity={0.8} />
            <ellipse cx={cx - r - 3} cy={cy + 5} rx={6} ry={10} fill={accentColor} opacity={0.7}
              transform={`rotate(-20 ${cx - r - 3} ${cy + 5})`} />
            <ellipse cx={cx + r + 3} cy={cy + 5} rx={6} ry={10} fill={accentColor} opacity={0.7}
              transform={`rotate(20 ${cx + r + 3} ${cy + 5})`} />
          </g>
        )

      default:
        return (
          <g>
            <circle cx={cx} cy={cy} r={r} fill={color} opacity={0.9} />
            <circle cx={cx - 10} cy={cy - 5} r={6} fill="white" />
            <circle cx={cx + 10} cy={cy - 5} r={6} fill="white" />
            <circle cx={cx - 9} cy={cy - 5} r={3} fill="#1E293B" />
            <circle cx={cx + 11} cy={cy - 5} r={3} fill="#1E293B" />
            <path d={`M ${cx - 5} ${cy + 5} Q ${cx} ${cy + 10} ${cx + 5} ${cy + 5}`}
              fill="none" stroke="#1E293B" strokeWidth={1.5} strokeLinecap="round" />
          </g>
        )
    }
  }

  return (
    <div
      className="inline-flex items-center justify-center cursor-pointer select-none"
      style={{ width: size, height: size }}
      onClick={onClick}
    >
      <svg
        ref={svgRef}
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        style={{ transition: 'filter 0.3s ease' }}
      >
        {renderSpecies()}
      </svg>
    </div>
  )
}
