/**
 * CrabRes Hand-drawn SVG Icon System
 * 
 * 风格：手绘感线条，1.5px stroke，round caps，有机曲线
 * 不是完美的几何图形，而是有温度的手绘线条
 * 所有图标 18x18 默认，可通过 className 缩放
 */

const I = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
    className={`text-current ${className}`}>
    {children}
  </svg>
)

export function ArrowLeftIcon({ className }: { className?: string }) {
  return <I className={className}><path d="M19 12H5" /><path d="M12 19l-7-7 7-7" /></I>
}

export function SearchIcon({ className }: { className?: string }) {
  return <I className={className}><circle cx="11" cy="11" r="8" /><path d="M21 21l-4.3-4.3" /></I>
}

export function TeamIcon({ className }: { className?: string }) {
  return <I className={className}><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></I>
}

export function PenIcon({ className }: { className?: string }) {
  return <I className={className}><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" /></I>
}

export function ChatIcon({ className }: { className?: string }) {
  return <I className={className}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></I>
}

export function TrendUpIcon({ className }: { className?: string }) {
  return <I className={className}><polyline points="23 6 13.5 15.5 8.5 10.5 1 18" /><polyline points="17 6 23 6 23 12" /></I>
}

export function ShieldCheckIcon({ className }: { className?: string }) {
  return <I className={className}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /><path d="M9 12l2 2 4-4" /></I>
}

export function BellIcon({ className }: { className?: string }) {
  return <I className={className}><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" /></I>
}

export function SettingsIcon({ className }: { className?: string }) {
  return <I className={className}><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" /></I>
}

export function ZapIcon({ className }: { className?: string }) {
  return <I className={className}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></I>
}

export function ShareIcon({ className }: { className?: string }) {
  return <I className={className}><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" /><polyline points="16 6 12 2 8 6" /><line x1="12" y1="2" x2="12" y2="15" /></I>
}

export function SendIcon({ className }: { className?: string }) {
  return <I className={className}><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></I>
}

export function CalendarIcon({ className }: { className?: string }) {
  return <I className={className}><rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></I>
}

export function ClipboardIcon({ className }: { className?: string }) {
  return <I className={className}><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" /><rect x="8" y="2" width="8" height="4" rx="1" ry="1" /></I>
}

export function TargetIcon({ className }: { className?: string }) {
  return <I className={className}><circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" /></I>
}

export function GlobeIcon({ className }: { className?: string }) {
  return <I className={className}><circle cx="12" cy="12" r="10" /><line x1="2" y1="12" x2="22" y2="12" /><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" /></I>
}

export function SparklesIcon({ className }: { className?: string }) {
  return <I className={className}><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" /><path d="M19 13l.75 2.25L22 16l-2.25.75L19 19l-.75-2.25L16 16l2.25-.75L19 13z" /></I>
}

export function CheckIcon({ className }: { className?: string }) {
  return <I className={className}><polyline points="20 6 9 17 4 12" /></I>
}

// ====== 新增：替代 emoji 的手绘图标 ======

/** 📋 → 手绘剪贴板 */
export function PlaybookIcon({ className }: { className?: string }) {
  return <I className={className}>
    <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
    <rect x="9" y="3" width="6" height="4" rx="1" />
    <path d="M9 14l2 2 4-4" />
  </I>
}

/** 📊 → 手绘柱状图 */
export function ChartBarIcon({ className }: { className?: string }) {
  return <I className={className}>
    <rect x="3" y="12" width="4" height="9" rx="1" />
    <rect x="10" y="7" width="4" height="14" rx="1" />
    <rect x="17" y="3" width="4" height="18" rx="1" />
  </I>
}

/** ⚠️ → 手绘三角警告 */
export function AlertTriangleIcon({ className }: { className?: string }) {
  return <I className={className}>
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </I>
}

/** 🔔 → 手绘铃铛（已有 BellIcon，这是带徽标版本） */
export function BellDotIcon({ className }: { className?: string }) {
  return <I className={className}>
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
    <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    <circle cx="18" cy="4" r="3" fill="currentColor" stroke="none" />
  </I>
}

/** ✅ → 手绘圆形勾选 */
export function CircleCheckIcon({ className }: { className?: string }) {
  return <I className={className}>
    <circle cx="12" cy="12" r="10" />
    <path d="M9 12l2 2 4-4" />
  </I>
}

/** 🔍 → 手绘放大镜带闪光 */
export function SearchSparkIcon({ className }: { className?: string }) {
  return <I className={className}>
    <circle cx="11" cy="11" r="8" />
    <path d="M21 21l-4.3-4.3" />
    <path d="M11 8v6" /><path d="M8 11h6" />
  </I>
}

/** 📰 → 手绘报纸/新闻 */
export function NewsIcon({ className }: { className?: string }) {
  return <I className={className}>
    <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 0-2 0" />
    <path d="M2 10h4" /><path d="M2 14h4" /><path d="M2 18h4" />
    <path d="M10 6h6" /><path d="M10 10h6" /><path d="M10 14h2" />
  </I>
}

/** 🧠 → 手绘大脑/灯泡 */
export function BrainIcon({ className }: { className?: string }) {
  return <I className={className}>
    <path d="M12 2a7 7 0 0 0-5.19 11.65l.01.01A3 3 0 0 0 9 17h6a3 3 0 0 0 2.18-3.34A7 7 0 0 0 12 2z" />
    <path d="M9 17v1a3 3 0 0 0 6 0v-1" />
    <line x1="12" y1="22" x2="12" y2="21" />
    <line x1="10" y1="19" x2="14" y2="19" />
  </I>
}

/** ⚙️ → 手绘齿轮 */
export function GearIcon({ className }: { className?: string }) {
  return <I className={className}>
    <circle cx="12" cy="12" r="3" />
    <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
  </I>
}

/** 📌 → 手绘图钉 */
export function PinIcon({ className }: { className?: string }) {
  return <I className={className}>
    <path d="M12 17v5" />
    <path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.89A2 2 0 0 0 5 15.24V17h14v-1.76a2 2 0 0 0-1.11-1.79l-1.78-.89A2 2 0 0 1 15 10.76V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v4.76z" />
  </I>
}

/** 🔐 → 手绘锁 */
export function LockIcon({ className }: { className?: string }) {
  return <I className={className}>
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
  </I>
}

/** 🚀 → 手绘火箭 */
export function RocketIcon({ className }: { className?: string }) {
  return <I className={className}>
    <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
    <path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
    <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
    <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
  </I>
}
