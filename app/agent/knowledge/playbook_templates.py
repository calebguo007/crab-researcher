"""
CrabRes Playbook 骨架模板

这些不是写死的内容——是 Agent 生成 Playbook 时的"结构参考"。
Agent 会基于真实研究数据填充具体的博主名字、价格、子版块名等。

每个模板定义了"这条增长路径应该有哪些 Phase 和 Step"，
Agent 负责填充每个 Step 的具体细节。
"""

# 模板 1: KOL/博主种草（适合有实物产品或可视化内容的产品）
KOL_OUTREACH_TEMPLATE = {
    "name": "KOL/Influencer Seeding",
    "suitable_for": "Products with visual appeal, physical goods, lifestyle/tech products. Budget $300-5000.",
    "phases": [
        {
            "name": "Preparation",
            "duration": "Day 1-3",
            "steps": [
                {
                    "order": 1,
                    "title": "Define ideal influencer profile",
                    "detail": "Specify: platform (Instagram/TikTok/YouTube), follower range (1K-50K for best ROI), niche, engagement rate threshold (>3%), content style. Use the product research data to match.",
                    "tools": ["Modash.io", "Social Blade", "Manual search"],
                    "budget": "$0",
                    "duration": "2 hours",
                    "output": "Written ICP for influencers (1 paragraph)",
                    "success_criteria": "Can describe the ideal influencer in 3 sentences",
                    "common_mistakes": ["Only targeting big influencers (>100K) — expensive and low reply rate", "Not checking engagement rate — fake followers are common"]
                },
                {
                    "order": 2,
                    "title": "Build prospect list of 30+ candidates",
                    "detail": "Search platform-specific hashtags, competitor mentions, niche keywords. Record: name, handle, follower count, engagement rate, email, recent post quality, audience overlap with your target.",
                    "tools": ["Instagram search", "TikTok Creator Marketplace", "YouTube search", "Modash.io"],
                    "budget": "$0-50 (tool subscription optional)",
                    "duration": "4 hours",
                    "output": "Spreadsheet with 30+ influencer candidates",
                    "success_criteria": "30+ candidates with all fields filled. At least 10 with email addresses.",
                    "common_mistakes": ["Stopping at 10 candidates — you need 30+ because reply rate is ~10-20%", "Not recording email (DM only is slower)"]
                },
                {
                    "order": 3,
                    "title": "Prepare outreach assets",
                    "detail": "Create: (1) personalized email template with 3 variants, (2) DM template, (3) product one-pager/media kit, (4) high-quality product photos for reference. Every template MUST reference the influencer's specific recent content.",
                    "tools": ["Canva (media kit)", "Google Docs (templates)"],
                    "templates": ["cold_email_influencer_v1", "dm_template_influencer", "media_kit_template"],
                    "budget": "$0",
                    "duration": "3 hours",
                    "output": "3 email variants + 1 DM template + media kit PDF",
                    "success_criteria": "Templates feel personal, not mass-produced. Each references specific content.",
                    "common_mistakes": ["Generic 'Dear Creator' emails — instant delete", "Not including product photos in first email", "Writing too much — keep under 150 words"]
                },
            ]
        },
        {
            "name": "Outreach Execution",
            "duration": "Day 4-14",
            "steps": [
                {
                    "order": 4,
                    "title": "Tier-based outreach campaign",
                    "detail": "Split list into 3 tiers: Tier 1 (1K-5K) = free product only, Tier 2 (5K-20K) = product + $50-200, Tier 3 (20K+) = product + $500-1000 + contract. Send 5-10 emails/DMs per day. Personalize each one.",
                    "budget": "$0-500 for products/shipping",
                    "duration": "30 min/day for 10 days",
                    "output": "All 30+ outreach messages sent",
                    "success_criteria": "Reply rate > 15%. At least 5 confirmed collaborations.",
                    "common_mistakes": ["Sending all at once instead of batching", "Not following up (3-5 day gap, then one follow-up)", "Offering money to micro-influencers who'd do it for free product"]
                },
                {
                    "order": 5,
                    "title": "Follow-up sequence",
                    "detail": "Day 3-5 after initial outreach: send a brief follow-up (different angle, not 'just checking in'). If no reply after follow-up, move on. If replied positively, negotiate terms and send product.",
                    "duration": "15 min/day for 7 days",
                    "output": "All follow-ups sent. Final confirmed list.",
                    "success_criteria": "5-10 confirmed collaborations",
                },
                {
                    "order": 6,
                    "title": "Ship products + create content brief",
                    "detail": "For each confirmed influencer: (1) ship product with branded packaging + handwritten note, (2) send content brief (key messages, hashtags, link/code, deadline, content format preference), (3) set up tracking link/UTM/promo code.",
                    "tools": ["Shipping service", "Bitly/UTM builder"],
                    "budget": "$50-500 (products + shipping)",
                    "duration": "2-4 hours total",
                    "output": "All products shipped. Tracking spreadsheet updated.",
                    "success_criteria": "All influencers received product within 5 business days",
                    "common_mistakes": ["No content brief — influencer doesn't know what to say", "No tracking link — can't measure ROI", "Cheap packaging — first impression matters"]
                },
            ]
        },
        {
            "name": "Tracking & Iteration",
            "duration": "Day 15-30",
            "steps": [
                {
                    "order": 7,
                    "title": "Content tracking + engagement monitoring",
                    "detail": "Track each influencer's posted content: date, format, views, likes, comments, saves, clicks (via UTM), conversions. Record in spreadsheet.",
                    "duration": "15 min/day",
                    "output": "Completed tracking spreadsheet",
                    "success_criteria": "All content tracked within 48 hours of posting",
                },
                {
                    "order": 8,
                    "title": "Calculate ROI per influencer",
                    "detail": "For each: total cost (product + fee + shipping) / total conversions = CPA. Compare across tiers and platforms. Identify top 3 performers.",
                    "output": "ROI report with tier-level and platform-level analysis",
                    "success_criteria": "Clear ranking of which tier/platform has best ROI",
                },
                {
                    "order": 9,
                    "title": "Plan round 2 with learnings",
                    "detail": "Based on data: (1) double down on best-performing tier/platform, (2) refine outreach template based on reply rates, (3) expand list to 50+ candidates, (4) test new content formats that worked.",
                    "output": "Round 2 plan with specific adjustments",
                    "success_criteria": "At least 3 specific data-driven changes from Round 1",
                },
            ]
        }
    ]
}


# 模板 2: Reddit/社区深耕（适合所有类型）
COMMUNITY_GROWTH_TEMPLATE = {
    "name": "Reddit/Community Deep Engagement",
    "suitable_for": "Any product type. Best for: SaaS, dev tools, niche products. Budget $0. Requires 30 min/day.",
    "phases": [
        {
            "name": "Research & Setup",
            "duration": "Day 1-3",
            "steps": [
                {
                    "order": 1,
                    "title": "Identify 5-8 target subreddits/communities",
                    "detail": "Search for subreddits where your target users discuss their problems. Prioritize by: (1) member count, (2) post frequency, (3) commercial friendliness, (4) existing competitor presence. Include 2-3 non-obvious communities.",
                    "tools": ["Reddit search", "CrabRes social_search", "Google 'site:reddit.com [keyword]'"],
                    "output": "Ranked list of 5-8 subreddits with member count, rules summary, and top posts analysis",
                    "success_criteria": "Each subreddit has >10K members and >5 posts/day",
                    "common_mistakes": ["Only targeting the obvious subreddit", "Not reading subreddit rules (instant ban)", "Picking too many — focus on 3 primary"]
                },
                {
                    "order": 2,
                    "title": "Audit top-performing posts in each subreddit",
                    "detail": "Find the top 10 posts of all time and last month in each target subreddit. Analyze: what format works (question/story/tutorial/show-off), what titles get upvotes, when are peak hours, what gets downvoted.",
                    "output": "Content playbook per subreddit (format, tone, timing, dos and don'ts)",
                    "success_criteria": "Can describe the 'winning formula' for each subreddit in 2 sentences",
                },
                {
                    "order": 3,
                    "title": "Build Reddit credibility (if new account)",
                    "detail": "Spend 3 days genuinely helping people in your target subreddits. Answer questions, give advice, share experiences. Zero mention of your product. Build karma and post history.",
                    "duration": "30 min/day for 3 days",
                    "output": "Account with >50 karma and 10+ helpful comments",
                    "success_criteria": "At least 3 comments with >5 upvotes",
                    "common_mistakes": ["Skipping this step and posting about your product immediately = shadowban", "Being helpful but too short ('great question!' doesn't build karma)"]
                },
            ]
        },
        {
            "name": "Content Execution",
            "duration": "Day 4-21",
            "steps": [
                {
                    "order": 4,
                    "title": "Publish 2 value-first posts per week",
                    "detail": "Write posts that provide genuine value first. Format based on subreddit audit. Product mention only at the end, naturally. Use the winning formula identified in step 2.",
                    "duration": "1 hour per post, 2 posts/week",
                    "output": "6 published posts over 3 weeks",
                    "success_criteria": "Average >20 upvotes per post. At least 1 post >100 upvotes.",
                    "common_mistakes": ["Leading with the product instead of the value", "Same content format every time", "Posting at wrong time (check subreddit peak hours)"]
                },
                {
                    "order": 5,
                    "title": "Reply to 5 high-intent comments/posts daily",
                    "detail": "Search for posts where people are actively asking for solutions. Write genuinely helpful replies (3-5 sentences of value). Mention your product ONLY when directly relevant. Prioritize posts that rank on Google (long-term traffic).",
                    "duration": "20 min/day",
                    "output": "75+ helpful replies over 3 weeks",
                    "success_criteria": "Reply-to-click ratio >5%. At least 3 replies that drove measurable traffic.",
                },
                {
                    "order": 6,
                    "title": "DM high-intent users (carefully)",
                    "detail": "When someone's post/comment shows clear pain that your product solves, send a brief DM: 'Saw your post about [specific problem]. I built [product] that might help — happy to give you free access, no strings.' Never mass DM.",
                    "duration": "10 min/day",
                    "output": "15-20 targeted DMs over 3 weeks",
                    "success_criteria": "Reply rate >30%. At least 3 converted to users.",
                    "common_mistakes": ["Mass DMing = account ban", "Not referencing their specific post", "Asking for something instead of offering"]
                },
            ]
        },
        {
            "name": "Measure & Scale",
            "duration": "Day 22-30",
            "steps": [
                {
                    "order": 7,
                    "title": "Track all actions → results",
                    "detail": "For each post, reply, and DM: record engagement metrics + UTM click-throughs + signups. Build a clear picture of what content type / subreddit / timing / format drives actual conversions.",
                    "output": "Complete tracking spreadsheet with ROI per action type",
                },
                {
                    "order": 8,
                    "title": "Extract growth rules from data",
                    "detail": "Analyze: which subreddit converts best? Which post format gets most upvotes? Which time slot works? Which DM approach gets replies? Write 5 specific rules for month 2.",
                    "output": "5 data-backed growth rules",
                    "success_criteria": "Each rule has >5 data points supporting it",
                },
            ]
        }
    ]
}


# 模板 3: 精准广告投放（适合有预算的产品）
PAID_ADS_TEMPLATE = {
    "name": "Precision Ad Campaign",
    "suitable_for": "Products with clear target audience and >$500/month ad budget. Any product type.",
    "phases": [
        {
            "name": "Creative & Setup",
            "duration": "Day 1-5",
            "steps": [
                {
                    "order": 1,
                    "title": "Define target audience segments",
                    "detail": "Create 3 distinct audience segments based on research. Each segment: demographics, interests, pain points, where they spend time online. Use competitor ad library for inspiration.",
                    "tools": ["Meta Ad Library", "Google Ads Keyword Planner", "SpyFu/SEMrush"],
                    "output": "3 audience segment profiles with targeting parameters",
                    "success_criteria": "Each segment is specific enough to target on ad platforms",
                    "common_mistakes": ["Too broad targeting (all women 18-65)", "Not researching what competitors are already targeting"]
                },
                {
                    "order": 2,
                    "title": "Create 3 ad creative angles",
                    "detail": "For each segment, create 3 different creative angles: (1) Problem-focused: show the pain, (2) Solution-focused: show the result, (3) Social proof: show others using it. Each angle needs: headline, body copy, CTA, visual direction.",
                    "tools": ["Canva", "Figma", "CapCut (video)"],
                    "templates": ["ad_copy_problem", "ad_copy_solution", "ad_copy_social_proof"],
                    "output": "9 ad creative briefs (3 segments × 3 angles)",
                    "success_criteria": "Each creative is platform-native (correct sizes, format)",
                    "common_mistakes": ["Same creative for all platforms", "No clear CTA", "Too much text in image ads (Meta penalizes this)"]
                },
                {
                    "order": 3,
                    "title": "Produce visual assets",
                    "detail": "For image ads: create at correct sizes (Meta: 1080×1080, 1080×1350, 1200×628. Google: 1200×628. TikTok: 1080×1920). For video ads: 15-30 sec, hook in first 3 sec, CTA at end. Use product photos, lifestyle shots, UGC-style.",
                    "tools": ["Canva", "CapCut", "Midjourney/DALL-E (concept art)", "iPhone (UGC-style)"],
                    "budget": "$0-200",
                    "output": "9+ ad creatives ready to upload",
                    "success_criteria": "Each creative looks native to its platform. Video hooks in <3 sec.",
                },
                {
                    "order": 4,
                    "title": "Set up tracking infrastructure",
                    "detail": "Install Meta Pixel, Google Ads tag, TikTok Pixel on your website. Set up conversion events: PageView, AddToCart, Purchase. Create UTM parameters for each campaign. Test that events fire correctly.",
                    "tools": ["Google Tag Manager", "Meta Events Manager", "UTM builder"],
                    "output": "All pixels installed and conversion events verified",
                    "success_criteria": "Test purchase shows up in all ad platform dashboards",
                    "common_mistakes": ["Forgetting to install pixel before spending money = no data", "Not setting up conversion events = can't optimize"]
                },
            ]
        },
        {
            "name": "Testing Phase",
            "duration": "Day 6-12",
            "steps": [
                {
                    "order": 5,
                    "title": "Launch small-budget test campaigns",
                    "detail": "Spend $20-50 per creative, run for 72 hours. 3 segments × 3 angles = 9 ad sets. Use automatic bidding. Don't touch anything for 72 hours (let the algorithm learn).",
                    "budget": "$180-450 (test budget)",
                    "duration": "72 hours (hands off)",
                    "output": "72-hour performance data for all 9 ad sets",
                    "success_criteria": "At least 2 ad sets with CPA below target. Clear winner emerging.",
                    "common_mistakes": ["Changing ads before 72 hours", "Budget too small to get meaningful data (<$20/ad set)", "Panicking at early results"]
                },
                {
                    "order": 6,
                    "title": "Analyze and kill losers",
                    "detail": "After 72 hours: rank all ad sets by CPA. Kill bottom 50%. For winners: analyze what's working (which audience? which angle? which creative?). Don't average — look at individual ad set performance.",
                    "output": "Kill list + winner analysis with specific reasons",
                    "success_criteria": "Identified top 3 performing ad sets with clear reasons why",
                },
            ]
        },
        {
            "name": "Scale & Optimize",
            "duration": "Day 13-30",
            "steps": [
                {
                    "order": 7,
                    "title": "Scale winners gradually",
                    "detail": "Increase budget on winners by 20% every 3 days (not more — algorithm needs time). Create variations of winning creatives (same angle, different visuals/copy). Add lookalike audiences based on converters.",
                    "budget": "Remaining monthly budget",
                    "duration": "15 min/day monitoring",
                    "output": "Scaled campaigns with stable or improving CPA",
                    "success_criteria": "CPA stays within 1.5x of test phase CPA while spending 3-5x more",
                },
                {
                    "order": 8,
                    "title": "Weekly creative refresh",
                    "detail": "Ad fatigue hits after 7-14 days. Every week: create 2-3 new creatives based on the winning angle. Test new hooks, new visuals, new CTAs. Keep the same audience targeting.",
                    "output": "2-3 fresh creatives per week",
                    "success_criteria": "CTR doesn't drop below 1% (Meta) or 0.5% (Google)",
                },
                {
                    "order": 9,
                    "title": "Monthly ROI review and strategy adjustment",
                    "detail": "Calculate: total spend, total conversions, CPA, ROAS. Compare to organic channels. Decide: scale up, maintain, or shift budget to better-performing channels.",
                    "output": "Monthly ad performance report + next month plan",
                    "success_criteria": "ROAS > 2x (spending $1 generates $2+ revenue)",
                },
            ]
        }
    ]
}


# 所有模板索引——Agent 选择 Playbook 时参考
ALL_PLAYBOOK_TEMPLATES = {
    "kol_outreach": KOL_OUTREACH_TEMPLATE,
    "community_growth": COMMUNITY_GROWTH_TEMPLATE,
    "paid_ads": PAID_ADS_TEMPLATE,
}


def get_playbook_templates_prompt() -> str:
    """
    生成一段文本供 Coordinator prompt 注入，
    让 Agent 知道有哪些 Playbook 模板可以用来生成完整执行计划。
    """
    lines = [
        "\n## AVAILABLE GROWTH PLAYBOOK TEMPLATES",
        "When creating a growth plan, use these structured playbook formats instead of plain text advice.",
        "Each playbook should have Phases → Steps, with tools, templates, budgets, timelines, and success criteria.\n",
    ]
    for key, tmpl in ALL_PLAYBOOK_TEMPLATES.items():
        name = tmpl["name"]
        suitable = tmpl["suitable_for"]
        phase_names = [p["name"] for p in tmpl["phases"]]
        total_steps = sum(len(p["steps"]) for p in tmpl["phases"])
        lines.append(f"- **{name}** ({key}): {suitable}")
        lines.append(f"  Phases: {' → '.join(phase_names)} ({total_steps} steps)")

    lines.append("\nTo generate a playbook: use consult_roundtable with relevant experts,")
    lines.append("then output a structured plan following the Phase → Step format above.")
    lines.append("EVERY step must have: title, detail, tools, budget, duration, output, success_criteria, common_mistakes.")
    return "\n".join(lines)
