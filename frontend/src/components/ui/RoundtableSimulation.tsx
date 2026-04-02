
import { EXPERTS } from '../../lib/experts'

interface RoundtableSimulationProps {
  activeExpertId?: string;
  isSimulating?: boolean;
}

export function RoundtableSimulation({ activeExpertId, isSimulating }: RoundtableSimulationProps) {
  const expertKeys = Object.keys(EXPERTS);
  const radius = 100;
  const centerX = 150;
  const centerY = 150;

  return (
    <div className="relative w-[300px] h-[300px] mx-auto mb-8 animate-fade-in">
      {/* 背景环绕光晕 */}
      <div className="absolute inset-0 rounded-full border border-brand/10 bg-brand/5 animate-pulse" />
      <div className="absolute inset-4 rounded-full border border-brand/5" />
      
      {/* 中心：战术指挥官 (CrabRes) */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
        <div className={`w-16 h-16 rounded-full bg-surface border-2 border-brand flex items-center justify-center text-2xl shadow-lg transition-transform ${isSimulating ? 'scale-110' : ''}`}>
          🦀
        </div>
        {isSimulating && (
          <div className="absolute -inset-2 rounded-full border-2 border-brand/20 animate-ping" />
        )}
      </div>

      {/* 13 位专家环绕 */}
      {expertKeys.map((key, i) => {
        const expert = EXPERTS[key];
        const angle = (i / expertKeys.length) * 2 * Math.PI - Math.PI / 2;
        const x = centerX + radius * Math.cos(angle);
        const y = centerY + radius * Math.sin(angle);
        const isActive = activeExpertId === key;

        return (
          <div
            key={key}
            className="absolute -translate-x-1/2 -translate-y-1/2 transition-all duration-500 z-10"
            style={{ 
              left: x, 
              top: y,
              transform: `translate(-50%, -50%) scale(${isActive ? 1.4 : 1})`,
              opacity: isSimulating && !isActive ? 0.4 : 1
            }}
          >
            <div 
              className={`w-10 h-10 rounded-full flex items-center justify-center text-lg border-2 shadow-sm transition-colors ${isActive ? 'bg-surface animate-bounce' : 'bg-surface/80'}`}
              style={{ 
                borderColor: isActive ? expert.color : `${expert.color}40`,
                color: expert.color,
                boxShadow: isActive ? `0 0 15px ${expert.color}60` : 'none'
              }}
              title={expert.name}
            >
              {expert.icon}
            </div>
            
            {/* 连接线 */}
            {isActive && (
              <svg className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] pointer-events-none" style={{ left: centerX - x, top: centerY - y }}>
                <line 
                  x1={radius * Math.cos(angle)} 
                  y1={radius * Math.sin(angle)} 
                  x2={0} 
                  y2={0} 
                  stroke={expert.color} 
                  strokeWidth="2" 
                  strokeDasharray="4 2"
                  className="animate-dash"
                  style={{ transform: `translate(${centerX}px, ${centerY}px)` }}
                />
              </svg>
            )}
          </div>
        );
      })}

      {/* 战术信息流展示 */}
      {isSimulating && (
        <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 w-full text-center space-y-1">
          <p className="text-[10px] font-mono text-brand uppercase tracking-[0.2em] animate-pulse">
            {activeExpertId ? `${EXPERTS[activeExpertId]?.short} Analyzing...` : 'Roundtable Strategy Debate...'}
          </p>
          <div className="flex justify-center gap-1">
            <div className="w-1 h-1 rounded-full bg-brand animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-1 h-1 rounded-full bg-brand animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-1 h-1 rounded-full bg-brand animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      )}
    </div>
  );
}
