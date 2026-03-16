---
name: ai-newsletters
description: Curate AI newsletter content with smart deduplication and ranking. Use when user invokes /ai-newsletters or when /start-my-day needs newsletter content.
---

# AI Newsletter Curation

Fetch, deduplicate, and rank AI newsletter content into a daily digest.

## RSS Sources

- **TLDR AI**: `https://bullrich.dev/tldr-rss/ai.rss`
- **The Rundown AI**: `https://rss.beehiiv.com/feeds/2R3C6Bt5wj.xml`

## Workflow

1. **Check cache**: Look for `50_资源/Newsletters/YYYY-MM/YYYY-MM-DD-摘要.md`. If exists with today's date, return cached content.

2. **Fetch feeds**: Use WebFetch on both RSS URLs. Extract title, link, pubDate, description for each item.

3. **Deduplicate**: Merge items with similar titles (80%+ word overlap). Keep longer description, track both sources.

4. **Rank items** by:
   - AI relevance (LLM, GPT, Claude, agents, ML keywords)
   - Productivity relevance (workflow, automation, tools, PKM)
   - Recency (newer = higher)
   - Novelty (check recent archives, penalize repeats)

5. **Generate digest**: See [TEMPLATE.md](TEMPLATE.md) for format. Include:
   - 精选推荐 (3-5 highest scoring) with content creation angles
   - AI动态 section
   - 生产力工具 section
   - Stats footer

6. **Save files**:
   - `50_资源/Newsletters/YYYY-MM/YYYY-MM-DD-摘要.md` (curated)
   - `50_资源/Newsletters/YYYY-MM/原始数据/YYYY-MM-DD_TLDR-AI-Raw.md`
   - `50_资源/Newsletters/YYYY-MM/原始数据/YYYY-MM-DD_Rundown-AI-Raw.md`

## Output Format

**Manual invocation**: Display full digest with all sections.

**From /start-my-day**: Return condensed list:

```
**内容机会 (5):**
- [标题] - [角度]
...
完整摘要: [[YYYY-MM-DD-摘要]]
```

## Error Handling

- One feed down: Continue with other, note in digest
- Both down: Use yesterday's archive with warning
- Empty feeds: Create minimal digest noting "今日无新内容"

## Robust Fetch Strategy

**Retry Logic:**

1. First attempt: Direct WebFetch on RSS URLs
2. If fails: Try alternative user-agent headers
3. If still fails: Check if cached raw data exists from yesterday, use as fallback
4. Never give up immediately - always try multiple approaches

**Common Issues & Fixes:**

- RSS timeout: Increase timeout to 60s, retry once
- Rate limiting: Wait 5s, retry with different approach
- XML parsing errors: Extract items manually via regex on raw text
- Empty items: Check if feed structure changed, adapt parsing

**Success Criteria:**

- At least one feed must return valid items
- Items must have title and link at minimum
- Description can be empty (not critical)

## Implementation Notes

When fetching RSS:

1. Use `webfetch` tool with `format: "text"` to get raw XML
2. Parse XML to extract `<item>` elements
3. For each item, extract: `<title>`, `<link>`, `<pubDate>`, `<description>`
4. Handle CDATA sections in descriptions
5. Skip sponsor items (contain "Sponsor" in title)
