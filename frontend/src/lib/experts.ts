
export interface ExpertInfo {
  name: string;
  short: string;
  color: string;
  icon: string;
}

export const EXPERTS: Record<string, ExpertInfo> = {
  market_researcher: { name: 'Market Researcher', short: 'Research', color: '#0EA5E9', icon: '🔍' },
  economist: { name: 'Economist', short: 'Econ', color: '#10B981', icon: '💰' },
  content_strategist: { name: 'Content Strategist', short: 'Content', color: '#8B5CF6', icon: '📝' },
  social_media: { name: 'Social Media', short: 'Social', color: '#F43F5E', icon: '🎯' },
  paid_ads: { name: 'Paid Ads', short: 'Ads', color: '#F59E0B', icon: '📢' },
  partnerships: { name: 'Partnerships', short: 'Partners', color: '#EC4899', icon: '🤝' },
  ai_distribution: { name: 'AI Distribution', short: 'AI Dist', color: '#6366F1', icon: '🤖' },
  psychologist: { name: 'Psychologist', short: 'Psych', color: '#14B8A6', icon: '🧠' },
  product_growth: { name: 'Product Growth', short: 'Growth', color: '#F97316', icon: '📈' },
  data_analyst: { name: 'Data Analyst', short: 'Data', color: '#64748B', icon: '📊' },
  copywriter: { name: 'Copywriter', short: 'Copy', color: '#A855F7', icon: '✍️' },
  critic: { name: 'Strategy Critic', short: 'Critic', color: '#EF4444', icon: '⚖️' },
  designer: { name: 'Designer', short: 'Design', color: '#06B6D4', icon: '🎨' },
}
