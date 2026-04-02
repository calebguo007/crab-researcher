#!/usr/bin/env node

/**
 * CrabRes CLI — AI Growth Agent in your terminal
 * 
 * Usage:
 *   crabres chat "I built an AI resume tool, help me grow"
 *   crabres status
 *   crabres plan
 *   crabres simulate "What if I launch on Product Hunt?"
 *   crabres login
 *   crabres config
 */

const API = process.env.CRABRES_API || 'https://crab-researcher.onrender.com/api'
let TOKEN = process.env.CRABRES_TOKEN || ''

const args = process.argv.slice(2)
const command = args[0]
const rest = args.slice(1).join(' ')

// ANSI 颜色
const c = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  blue: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  orange: '\x1b[38;5;208m',
}

async function main() {
  if (!command || command === 'help' || command === '--help') {
    printHelp()
    return
  }

  if (command === 'login') {
    await login()
    return
  }

  if (!TOKEN) {
    // 尝试从文件读取
    try {
      const fs = await import('fs')
      const os = await import('os')
      const path = await import('path')
      const tokenFile = path.join(os.default.homedir(), '.crabres-token')
      TOKEN = fs.default.readFileSync(tokenFile, 'utf-8').trim()
    } catch {}
  }

  if (!TOKEN && command !== 'login') {
    console.log(`${c.yellow}Not logged in.${c.reset} Run: ${c.bold}crabres login${c.reset}`)
    return
  }

  switch (command) {
    case 'chat': await chat(rest); break
    case 'status': await status(); break
    case 'plan': await plan(); break
    case 'simulate': await simulate(rest); break
    case 'discoveries': await discoveries(); break
    case 'cost': await cost(); break
    case 'config': printConfig(); break
    default:
      // 没有命令直接当 chat
      await chat(args.join(' '))
  }
}

function printHelp() {
  console.log(`
${c.orange}🦀 CrabRes${c.reset} — AI Growth Agent

${c.bold}Usage:${c.reset}
  crabres chat <message>      Talk to CrabRes
  crabres status              Growth dashboard
  crabres plan                View growth plan
  crabres simulate <what-if>  Strategy simulator
  crabres discoveries         Latest findings
  crabres login               Authenticate
  crabres config              Show configuration

${c.bold}Examples:${c.reset}
  ${c.dim}crabres chat "I built an AI resume tool for job seekers"${c.reset}
  ${c.dim}crabres simulate "What if I launch on Product Hunt next week?"${c.reset}
  ${c.dim}crabres "help me find competitors for my SaaS"${c.reset}

${c.bold}Environment:${c.reset}
  CRABRES_TOKEN    Auth token (or run 'crabres login')
  CRABRES_API      API base URL (default: production)
`)
}

async function apiFetch(path, opts = {}) {
  const url = `${API}${path}`
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${TOKEN}`,
    ...opts.headers,
  }
  const res = await fetch(url, { ...opts, headers })
  if (res.status === 401) {
    console.log(`${c.red}Session expired.${c.reset} Run: crabres login`)
    process.exit(1)
  }
  return res.json()
}

async function login() {
  const readline = await import('readline')
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
  const ask = (q) => new Promise(r => rl.question(q, r))

  console.log(`${c.orange}🦀 CrabRes Login${c.reset}\n`)

  const email = await ask('Email: ')
  const password = await ask('Password: ')
  rl.close()

  try {
    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    const data = await res.json()

    if (data.access_token) {
      TOKEN = data.access_token
      // 保存 token
      const fs = await import('fs')
      const os = await import('os')
      const path = await import('path')
      fs.default.writeFileSync(path.join(os.default.homedir(), '.crabres-token'), TOKEN)
      console.log(`\n${c.green}✓ Logged in!${c.reset} Token saved to ~/.crabres-token`)
    } else {
      console.log(`\n${c.red}Login failed:${c.reset} ${data.detail || 'Unknown error'}`)
    }
  } catch (e) {
    console.log(`${c.red}Connection failed:${c.reset} ${e.message}`)
  }
}

async function chat(message) {
  if (!message) {
    console.log(`${c.yellow}Usage:${c.reset} crabres chat "your message"`)
    return
  }

  console.log(`${c.dim}🔍 Researching...${c.reset}`)

  try {
    const data = await apiFetch('/agent/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    })

    for (const item of data) {
      if (item.type === 'status') {
        console.log(`  ${c.dim}⏳ ${item.content}${c.reset}`)
      } else if (item.type === 'expert_thinking') {
        console.log(`  ${c.blue}🧠 [${item.expert_id}]${c.reset} ${item.content.slice(0, 120)}...`)
      } else if (item.type === 'message') {
        console.log(`\n${c.orange}🦀 CrabRes:${c.reset}`)
        console.log(item.content)
      }
    }
  } catch (e) {
    console.log(`${c.red}Error:${c.reset} ${e.message}`)
  }
}

async function status() {
  try {
    const [stats, creature] = await Promise.all([
      apiFetch('/growth/stats'),
      apiFetch('/creature/state'),
    ])

    console.log(`\n${c.orange}🦀 CrabRes Growth Dashboard${c.reset}`)
    console.log(`${c.dim}${'─'.repeat(40)}${c.reset}`)

    const mood = creature.mood || 'idle'
    const attrs = creature.attributes || {}

    console.log(`  Mood: ${mood}  Level: ${creature.level}  Size: ${creature.size}`)
    console.log(`  Growth: ${bar(attrs.growth)}  Reach: ${bar(attrs.reach)}`)
    console.log(`  Consistency: ${bar(attrs.consistency)}  Momentum: ${bar(attrs.momentum)}`)
    console.log()
    console.log(`  Users: ${c.bold}${stats.total_users}${c.reset}  Growth: ${c.green}+${stats.growth_rate}%${c.reset}  Streak: ${c.orange}${stats.streak_days}d${c.reset}`)
  } catch (e) {
    console.log(`${c.red}Error:${c.reset} ${e.message}`)
  }
}

async function plan() {
  try {
    const data = await apiFetch('/growth/plan')
    const planContent = data.plan?.content
    if (planContent) {
      console.log(`\n${c.orange}📋 Growth Plan${c.reset}\n`)
      console.log(planContent)
    } else {
      console.log(`${c.yellow}No growth plan yet.${c.reset} Run: crabres chat "Help me create a growth plan"`)
    }
  } catch (e) {
    console.log(`${c.red}Error:${c.reset} ${e.message}`)
  }
}

async function simulate(hypothesis) {
  if (!hypothesis) {
    console.log(`${c.yellow}Usage:${c.reset} crabres simulate "What if I launch on Product Hunt?"`)
    return
  }

  console.log(`${c.dim}🎯 Simulating...${c.reset}`)
  try {
    const data = await apiFetch('/simulate', {
      method: 'POST',
      body: JSON.stringify({ hypothesis }),
    })
    console.log(`\n${c.orange}🎯 Strategy Simulation${c.reset}\n`)
    console.log(data.simulation || data.error || 'No result')
    if (data.cost_usd) console.log(`\n${c.dim}Cost: $${data.cost_usd.toFixed(4)}${c.reset}`)
  } catch (e) {
    console.log(`${c.red}Error:${c.reset} ${e.message}`)
  }
}

async function discoveries() {
  try {
    const data = await apiFetch('/growth/discoveries')
    const items = data.discoveries || []
    if (items.length === 0) {
      console.log(`${c.dim}No new discoveries. Daemon is scanning...${c.reset}`)
      return
    }
    console.log(`\n${c.orange}💡 Recent Discoveries${c.reset}\n`)
    for (const d of items) {
      console.log(`  ${c.blue}${d.type}:${c.reset} ${d.title || d.change || d.competitor || ''}`)
      if (d.analysis) console.log(`  ${c.green}→ ${d.analysis}${c.reset}`)
      console.log()
    }
  } catch (e) {
    console.log(`${c.red}Error:${c.reset} ${e.message}`)
  }
}

async function cost() {
  try {
    const sessions = await apiFetch('/agent/sessions')
    for (const s of sessions.sessions || []) {
      const costData = await apiFetch(`/agent/session/${s.session_id}/cost`)
      console.log(`Session ${s.session_id.slice(0, 8)}: $${costData.total_cost_usd} (${costData.total_tokens} tokens)`)
    }
  } catch (e) {
    console.log(`${c.red}Error:${c.reset} ${e.message}`)
  }
}

function printConfig() {
  console.log(`\n${c.orange}⚙️ CrabRes Config${c.reset}\n`)
  console.log(`  API: ${API}`)
  console.log(`  Token: ${TOKEN ? TOKEN.slice(0, 15) + '...' : 'not set'}`)
  console.log(`  Token file: ~/.crabres-token`)
}

function bar(value = 0) {
  const filled = Math.round(value / 10)
  return `${'█'.repeat(filled)}${'░'.repeat(10 - filled)} ${value}`
}

main().catch(e => {
  console.error(`${c.red}Fatal:${c.reset} ${e.message}`)
  process.exit(1)
})
