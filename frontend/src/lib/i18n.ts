/**
 * CrabRes i18n — 轻量国际化
 * 
 * 用法：
 *   import { t, getLang } from '../lib/i18n'
 *   <p>{t('surface.greeting.start')}</p>
 */

export type Lang = 'en' | 'zh'

export function getLang(): Lang {
  return (localStorage.getItem('crabres_language') as Lang) || 'en'
}

const dict: Record<string, Record<Lang, string>> = {
  // ===== Surface =====
  'surface.today': { en: 'Today', zh: '今日待办' },
  'surface.discoveries': { en: 'Discoveries', zh: '最新发现' },
  'surface.experiments': { en: 'Growth Experiments', zh: '增长实验' },
  'surface.campaign': { en: 'Active Growth Campaign', zh: '当前增长战役' },
  'surface.talk': { en: 'Talk to CrabRes', zh: '与 CrabRes 对话' },
  'surface.plan': { en: 'Growth Plan', zh: '增长策略' },
  'surface.share': { en: 'Share your growth', zh: '分享你的增长' },
  'surface.empty': { en: 'Your growth journey starts with a conversation.', zh: '你的增长之旅从一次对话开始。' },
  'surface.scanning': { en: 'Your growth daemon is scanning...', zh: '增长引擎正在扫描中...' },
  'surface.scanning.sub': { en: 'Discoveries will appear here.', zh: '最新发现将显示在这里。' },
  'surface.task.default': { en: 'Tell CrabRes about your product', zh: '告诉 CrabRes 你的产品细节' },
  'surface.task.default.sub': { en: 'Start a conversation to begin research', zh: '开始对话以启动深度调研' },
  'surface.viewLive': { en: 'View Live', zh: '查看实时' },
  // metrics
  'metric.growth': { en: 'growth', zh: '周增长' },
  'metric.users': { en: 'users', zh: '用户数' },
  'metric.streak': { en: 'streak', zh: '连续增长' },
  // actions
  'action.chat': { en: 'Chat', zh: '开聊' },
  'action.do': { en: 'Do it', zh: '去执行' },
  'action.view': { en: 'View', zh: '查看' },
  'action.analyze': { en: 'Analyze', zh: '分析' },

  // ===== Chat =====
  'chat.title': { en: 'Growth War Room', zh: '增长作战室' },
  'chat.placeholder': { en: 'Describe your product or ask a growth question...', zh: '描述你的产品或提问增长问题...' },
  'chat.send': { en: 'Send', zh: '发送' },

  // ===== Plan =====
  'plan.title': { en: 'Growth Playbooks', zh: '增长执行手册' },
  'plan.empty': { en: 'Tell CrabRes about your product. It will research your market and create structured growth playbooks with step-by-step instructions.', zh: '告诉 CrabRes 你的产品。它会调研市场并创建结构化的增长执行手册。' },

  // ===== Settings =====
  'settings.title': { en: 'Settings', zh: '设置' },
  'settings.appearance': { en: 'Appearance', zh: '外观' },
  'settings.darkMode': { en: 'Dark mode', zh: '深色模式' },
  'settings.darkMode.desc': { en: 'Easier on the eyes at night', zh: '夜间更护眼' },
  'settings.language': { en: 'Language', zh: '语言' },
  'settings.language.desc': { en: 'Agent responses & UI language', zh: 'Agent 回复和界面语言' },
  'settings.notifications': { en: 'Notifications', zh: '通知' },
  'settings.projects': { en: 'Projects', zh: '项目' },
  'settings.account': { en: 'Account', zh: '账户' },
  'settings.logout': { en: 'Log out', zh: '退出登录' },
  'settings.export': { en: 'Export data', zh: '导出数据' },
  'settings.api': { en: 'API keys', zh: 'API 密钥' },
  'settings.subscription': { en: 'Manage subscription', zh: '管理订阅' },

  // ===== Onboarding =====
  'onboarding.goal': { en: "What's your growth goal?", zh: '你的增长目标是？' },
  'onboarding.focus': { en: 'Choose your growth focus', zh: '选择你的增长重心' },
  'onboarding.meet': { en: 'Meet your growth companion', zh: '遇见你的增长伙伴' },

  // ===== Common =====
  'common.back': { en: 'Back', zh: '返回' },
  'common.tracked': { en: 'tracked', zh: '已追踪' },
  'common.pending': { en: 'pending', zh: '待追踪' },
}

export function t(key: string): string {
  const lang = getLang()
  const entry = dict[key]
  if (!entry) return key
  return entry[lang] || entry['en'] || key
}

// 便捷方法：根据当前语言选择
export function isZh(): boolean {
  return getLang() === 'zh'
}
