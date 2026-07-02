#!/usr/bin/env node

import { spawn } from "node:child_process"
import { mkdir, readdir, readFile, writeFile } from "node:fs/promises"
import path from "node:path"
import { parseArgs } from "node:util"

const DEFAULT_TIMEOUT_MS = 10_000
const RETRY_TIMEOUT_MS = 15_000
const DEFAULT_LIMIT = 5
const TIME_ZONE = "Asia/Shanghai"

const RETRY_SOURCES = new Set([
  "github",
  "github-trending-today",
  "hackernews",
  "kaopu",
  "linuxdo",
  "linuxdo-hot",
  "linuxdo-latest",
  "mktnews",
  "mktnews-flash",
  "steam",
  "v2ex",
  "v2ex-share",
  "zaobao",
])

const SOURCE_LABELS = {
  "36kr": "36氪",
  "36kr-quick": "36氪快讯",
  "36kr-renqi": "36氪人气",
  baidu: "百度热搜",
  bilibili: "B站热搜",
  "bilibili-hot-search": "B站热搜",
  "bilibili-hot-video": "B站热门视频",
  "bilibili-ranking": "B站排行榜",
  cankaoxiaoxi: "参考消息",
  chongbuluo: "虫部落",
  "chongbuluo-hot": "虫部落热帖",
  "chongbuluo-latest": "虫部落最新",
  cls: "财联社",
  "cls-depth": "财联社深度",
  "cls-hot": "财联社热榜",
  "cls-telegraph": "财联社电报",
  coolapk: "酷安",
  douban: "豆瓣",
  douyin: "抖音热榜",
  fastbull: "法布财经",
  "fastbull-express": "法布财经快讯",
  "fastbull-news": "法布财经新闻",
  freebuf: "FreeBuf",
  gelonghui: "格隆汇",
  ghxi: "果核剥壳",
  github: "GitHub",
  "github-trending-today": "GitHub Trending",
  hackernews: "Hacker News",
  hupu: "虎扑",
  ifeng: "凤凰网资讯",
  "iqiyi-hot-ranklist": "爱奇艺热播",
  ithome: "IT之家",
  jin10: "金十快讯",
  juejin: "掘金",
  kaopu: "靠谱新闻",
  kuaishou: "快手热榜",
  linuxdo: "LinuxDo",
  "linuxdo-hot": "LinuxDo 热榜",
  "linuxdo-latest": "LinuxDo 最新",
  mktnews: "市场资讯",
  "mktnews-flash": "市场快讯",
  nowcoder: "牛客",
  "pcbeta-windows": "PCBeta Windows",
  "pcbeta-windows11": "PCBeta Windows 11",
  producthunt: "Product Hunt",
  "qqvideo-tv-hotsearch": "腾讯视频热搜",
  smzdm: "什么值得买",
  solidot: "Solidot",
  sputniknewscn: "俄卫星通讯社",
  sspai: "少数派",
  steam: "Steam",
  "tencent-hot": "腾讯热榜",
  thepaper: "澎湃新闻",
  tieba: "贴吧热议",
  toutiao: "今日头条",
  v2ex: "V2EX",
  "v2ex-share": "V2EX 热门",
  wallstreetcn: "华尔街见闻",
  "wallstreetcn-hot": "华尔街见闻热点",
  "wallstreetcn-news": "华尔街见闻新闻",
  "wallstreetcn-quick": "华尔街见闻快讯",
  weibo: "微博热搜",
  xueqiu: "雪球",
  "xueqiu-hotstock": "雪球热股",
  zaobao: "联合早报",
  zhihu: "知乎热榜",
}

const SOURCE_GROUPS = [
  {
    title: "综合/资讯",
    sources: [
      "baidu",
      "zhihu",
      "weibo",
      "tencent-hot",
      "toutiao",
      "thepaper",
      "ifeng",
      "cankaoxiaoxi",
      "sputniknewscn",
    ],
  },
  {
    title: "财经/产业",
    sources: [
      "36kr",
      "36kr-quick",
      "36kr-renqi",
      "cls-depth",
      "cls-hot",
      "gelonghui",
      "wallstreetcn",
      "wallstreetcn-hot",
      "wallstreetcn-news",
      "wallstreetcn-quick",
      "jin10",
      "xueqiu",
      "xueqiu-hotstock",
    ],
  },
  {
    title: "科技/开发者",
    sources: [
      "ithome",
      "juejin",
      "nowcoder",
      "solidot",
      "sspai",
      "ghxi",
      "github",
      "github-trending-today",
      "hackernews",
      "linuxdo",
      "linuxdo-hot",
      "linuxdo-latest",
      "freebuf",
      "pcbeta-windows",
      "pcbeta-windows11",
    ],
  },
  {
    title: "平台/社区热度",
    sources: [
      "bilibili",
      "bilibili-hot-search",
      "bilibili-hot-video",
      "bilibili-ranking",
      "chongbuluo",
      "chongbuluo-hot",
      "chongbuluo-latest",
      "coolapk",
      "douban",
      "douyin",
      "hupu",
      "iqiyi-hot-ranklist",
      "kuaishou",
      "qqvideo-tv-hotsearch",
      "smzdm",
      "steam",
      "tieba",
    ],
  },
]

const { values } = parseArgs({
  options: {
    date: { type: "string" },
    limit: { type: "string" },
  },
})

const targetDate = values.date ?? todayInTimeZone(TIME_ZONE)
const limit = Number(values.limit ?? DEFAULT_LIMIT)

if (!/^\d{4}-\d{2}-\d{2}$/.test(targetDate)) {
  console.error(`无效日期格式: ${targetDate}`)
  process.exit(1)
}

if (!Number.isInteger(limit) || limit <= 0) {
  console.error(`无效 limit: ${values.limit}`)
  process.exit(1)
}

const monthKey = targetDate.slice(0, 7)
const rawDir = path.join(process.cwd(), "50_资源", "Newsletters", monthKey, "原始数据")
const monthIndexPath = path.join(process.cwd(), "50_资源", "Newsletters", monthKey, `${monthKey}.md`)
const usagePath = path.join(rawDir, `${targetDate}_newsnow-usage.txt`)
const listPath = path.join(rawDir, `${targetDate}_newsnow-list.json`)
const summaryPath = path.join(rawDir, `${targetDate}_newsnow-summary.json`)
const logPath = path.join(rawDir, `${targetDate}_newsnow-log.md`)

await mkdir(rawDir, { recursive: true })

const startedAt = new Date().toISOString()
const usage = await runNewsNow([], DEFAULT_TIMEOUT_MS)
await writeFile(usagePath, normalizeLineEndings(usage.stdout || usage.stderr || ""), "utf8")

const listRun = await runNewsNow(["list", "--json", "--pretty"], DEFAULT_TIMEOUT_MS)
if (listRun.status !== "success") {
  const detail = listRun.stderr || listRun.stdout || listRun.error || "未知错误"
  console.error(`获取 source 列表失败: ${detail}`)
  process.exit(1)
}

let listJson
try {
  listJson = JSON.parse(listRun.stdout)
} catch (error) {
  console.error(`source 列表 JSON 解析失败: ${String(error)}`)
  process.exit(1)
}

await writeFile(listPath, normalizeLineEndings(listRun.stdout), "utf8")

const previousSummary = await readPreviousSummary(rawDir, targetDate)
const previousSuccessSet = new Set(
  (previousSummary?.results ?? [])
    .filter((result) => result.status === "success")
    .map((result) => result.source),
)

const summary = {
  date: targetDate,
  startedAt,
  finishedAt: "",
  usage: sanitizeRun(usage),
  sourceCount: Array.isArray(listJson.sources) ? listJson.sources.length : 0,
  counts: {
    success: 0,
    nonzero: 0,
    timeout: 0,
    empty: 0,
    badjson: 0,
  },
  retries: [],
  results: [],
  previous: previousSummary
    ? {
        date: previousSummary.date,
        counts: previousSummary.counts,
      }
    : null,
}

for (const sourceMeta of listJson.sources ?? []) {
  const result = await fetchSource(sourceMeta, targetDate, rawDir, limit)
  summary.results.push(result)
  if (result.retried) {
    summary.retries.push(result.source)
  }
  if (result.status in summary.counts) {
    summary.counts[result.status] += 1
  } else {
    summary.counts.nonzero += 1
  }
}

summary.finishedAt = new Date().toISOString()

const currentSuccessSet = new Set(
  summary.results.filter((result) => result.status === "success").map((result) => result.source),
)
const recoveredSources = [...currentSuccessSet].filter((name) => !previousSuccessSet.has(name))
const lostSources = [...previousSuccessSet].filter((name) => !currentSuccessSet.has(name))
summary.diff = previousSummary
  ? {
      previousDate: previousSummary.date,
      successDelta: summary.counts.success - (previousSummary.counts?.success ?? 0),
      recoveredSources,
      lostSources,
    }
  : null

await writeFile(summaryPath, `${JSON.stringify(summary, null, 2)}\n`, "utf8")
await writeFile(
  logPath,
  buildLogMarkdown({
    summary,
    listJson,
    logPath,
    summaryPath,
    targetDate,
    generatedAt: formatChineseDateTime(new Date()),
  }),
  "utf8",
)

console.log(
  JSON.stringify(
    {
      date: targetDate,
      sourceCount: summary.sourceCount,
      counts: summary.counts,
      retryCount: summary.retries.length,
      rawDir,
      summaryPath,
      logPath,
      monthIndexPath,
    },
    null,
    2,
  ),
)

async function fetchSource(sourceMeta, date, outputDir, itemLimit) {
  const source = sourceMeta.name
  const attempts = []

  const firstRun = await runNewsNow([source, "--limit", String(itemLimit), "--json", "--pretty"], DEFAULT_TIMEOUT_MS)
  attempts.push(sanitizeRun(firstRun))

  let finalRun = firstRun
  let retried = false

  if (shouldRetry(source, firstRun)) {
    retried = true
    const secondRun = await runNewsNow(
      [source, "--limit", String(itemLimit), "--json", "--pretty"],
      RETRY_TIMEOUT_MS,
    )
    attempts.push(sanitizeRun(secondRun))
    finalRun = secondRun
  }

  const baseResult = {
    source,
    category: sourceMeta.category ?? source,
    envVars: sourceMeta.envVars ?? [],
    retried,
    attempts,
  }

  if (finalRun.status !== "success") {
    const result = {
      ...baseResult,
      status: finalRun.status === "timeout" ? "timeout" : "nonzero",
      exitCode: finalRun.exitCode,
      signal: finalRun.signal,
      timeoutMs: finalRun.timeoutMs,
      count: 0,
      sampleTitles: [],
      error: pickErrorMessage(finalRun),
      stderr: finalRun.stderr,
      stdout: finalRun.stdout,
      startedAt: finalRun.startedAt,
      finishedAt: finalRun.finishedAt,
    }

    await writeFile(
      path.join(outputDir, `${date}_${source}.err`),
      buildErrorFileContent(source, attempts, finalRun),
      "utf8",
    )

    return result
  }

  try {
    const parsed = JSON.parse(finalRun.stdout)
    const items = Array.isArray(parsed.items) ? parsed.items : []
    const count = Number(parsed.count ?? items.length) || 0
    const status = count > 0 && items.length > 0 ? "success" : "empty"

    await writeFile(path.join(outputDir, `${date}_${source}.json`), normalizeLineEndings(finalRun.stdout), "utf8")

    return {
      ...baseResult,
      status,
      exitCode: finalRun.exitCode,
      signal: finalRun.signal,
      timeoutMs: finalRun.timeoutMs,
      count,
      sampleTitles: items.map((item) => item?.title).filter(Boolean).slice(0, 3),
      error: null,
      stderr: finalRun.stderr,
      stdout: finalRun.stdout,
      startedAt: finalRun.startedAt,
      finishedAt: finalRun.finishedAt,
    }
  } catch (error) {
    const result = {
      ...baseResult,
      status: "badjson",
      exitCode: finalRun.exitCode,
      signal: finalRun.signal,
      timeoutMs: finalRun.timeoutMs,
      count: 0,
      sampleTitles: [],
      error: `JSON 解析失败: ${String(error)}`,
      stderr: finalRun.stderr,
      stdout: finalRun.stdout,
      startedAt: finalRun.startedAt,
      finishedAt: finalRun.finishedAt,
    }

    await writeFile(
      path.join(outputDir, `${date}_${source}.err`),
      buildErrorFileContent(source, attempts, finalRun),
      "utf8",
    )

    return result
  }
}

function runNewsNow(args, timeoutMs) {
  return new Promise((resolve) => {
    const startedAt = new Date().toISOString()
    const child = spawn("npx", ["--yes", "newsnow", ...args], {
      cwd: process.cwd(),
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    })

    let stdout = ""
    let stderr = ""
    let timedOut = false
    let settled = false

    const timer = setTimeout(() => {
      timedOut = true
      child.kill("SIGTERM")
      setTimeout(() => child.kill("SIGKILL"), 1_000).unref()
    }, timeoutMs)

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString()
    })

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString()
    })

    child.on("error", (error) => {
      if (settled) {
        return
      }
      settled = true
      clearTimeout(timer)
      resolve({
        status: "nonzero",
        exitCode: null,
        signal: null,
        timeoutMs,
        error: String(error),
        stderr,
        stdout,
        startedAt,
        finishedAt: new Date().toISOString(),
      })
    })

    child.on("close", (exitCode, signal) => {
      if (settled) {
        return
      }
      settled = true
      clearTimeout(timer)
      resolve({
        status: timedOut ? "timeout" : exitCode === 0 ? "success" : "nonzero",
        exitCode,
        signal,
        timeoutMs,
        error: timedOut ? `Timed out after ${timeoutMs}ms` : null,
        stderr,
        stdout,
        startedAt,
        finishedAt: new Date().toISOString(),
      })
    })
  })
}

function shouldRetry(source, run) {
  if (!RETRY_SOURCES.has(source)) {
    return false
  }

  return run.status === "timeout" || run.status === "nonzero"
}

function sanitizeRun(run) {
  return {
    status: run.status,
    exitCode: run.exitCode,
    signal: run.signal,
    timeoutMs: run.timeoutMs,
    error: run.error,
    stderr: run.stderr,
    stdout: run.stdout,
    startedAt: run.startedAt,
    finishedAt: run.finishedAt,
  }
}

function pickErrorMessage(run) {
  return run.stderr.trim() || run.stdout.trim() || run.error || "未知错误"
}

function buildErrorFileContent(source, attempts, finalRun) {
  const lines = [
    `source: ${source}`,
    `generatedAt: ${formatChineseDateTime(new Date())}`,
    `finalStatus: ${finalRun.status}`,
    "",
  ]

  attempts.forEach((attempt, index) => {
    lines.push(`attempt ${index + 1}`)
    lines.push(`status: ${attempt.status}`)
    lines.push(`exitCode: ${attempt.exitCode ?? "null"}`)
    lines.push(`signal: ${attempt.signal ?? "null"}`)
    lines.push(`timeoutMs: ${attempt.timeoutMs}`)
    if (attempt.error) {
      lines.push(`error: ${attempt.error}`)
    }
    if (attempt.stdout) {
      lines.push("stdout:")
      lines.push(attempt.stdout.trimEnd())
    }
    if (attempt.stderr) {
      lines.push("stderr:")
      lines.push(attempt.stderr.trimEnd())
    }
    lines.push("")
  })

  return normalizeLineEndings(lines.join("\n"))
}

function buildLogMarkdown({ summary, listJson, summaryPath, targetDate, generatedAt }) {
  const successes = summary.results.filter((result) => result.status === "success")
  const empties = summary.results.filter((result) => result.status === "empty")
  const failures = summary.results.filter((result) => result.status === "nonzero" || result.status === "timeout")
  const badJson = summary.results.filter((result) => result.status === "badjson")

  const successSections = SOURCE_GROUPS.map((group) => {
    const matched = group.sources.filter((source) => successes.some((result) => result.source === source))
    return matched.length
      ? `- ${group.title}: ${matched.map((source) => `\`${source}\``).join("、")}`
      : null
  }).filter(Boolean)

  const otherSuccesses = successes
    .map((result) => result.source)
    .filter((source) => !SOURCE_GROUPS.some((group) => group.sources.includes(source)))

  if (otherSuccesses.length > 0) {
    successSections.push(`- 其他: ${otherSuccesses.map((source) => `\`${source}\``).join("、")}`)
  }

  const diffLine = buildDiffLine(summary.diff)

  const lines = [
    `# ${targetDate} 抓取说明`,
    "",
    `- 时间: ${generatedAt}`,
    "- 入口命令: `npx newsnow`",
    `- 裸命令结果: ${summary.usage.stdout.includes("Usage: newsnow") ? "返回 CLI 用法说明，不直接输出新闻。" : "返回了非预期输出，请以原始日志为准。"}`,
    `- \`npx newsnow list --json --pretty\` 结果: 共识别 ${summary.sourceCount} 个 source。`,
    `- 本轮结果: ${summary.counts.success} 个成功返回、${summary.counts.empty} 个空结果、${summary.counts.nonzero} 个非零失败、${summary.counts.timeout} 个超时、${summary.counts.badjson} 个无效 JSON。`,
  ]

  if (diffLine) {
    lines.push(`- 本轮变化: ${diffLine}`)
  }

  lines.push("")
  lines.push("## 成功返回的 source")
  lines.push("")
  lines.push(...successSections)

  if (empties.length > 0) {
    lines.push("")
    lines.push("## 返回空结果的 source")
    lines.push("")
    empties.forEach((result) => {
      lines.push(`- \`${result.source}\``)
    })
  }

  if (failures.length > 0 || badJson.length > 0) {
    lines.push("")
    lines.push("## 失败或超时的 source")
    lines.push("")

    for (const result of [...failures, ...badJson]) {
      lines.push(`- \`${result.source}\``)
      lines.push(`  - 状态: \`${result.status}\``)
      lines.push(`  - 信息: ${formatFailureMessage(result)}`)
    }
  }

  lines.push("")
  lines.push("## 重试与补救")
  lines.push("")
  lines.push(
    `- 直接按单个 source 执行 \`npx newsnow <source> --limit ${DEFAULT_LIMIT} --json --pretty\`，保持“单源失败跳过、不阻塞全量轮询”的策略。`,
  )
  if (summary.retries.length > 0) {
    lines.push(
      `- 对 ${summary.retries.map((source) => `\`${source}\``).join("、")} 做了第二轮窄重试，单源超时上调到 ${RETRY_TIMEOUT_MS / 1000} 秒。`,
    )
  }
  lines.push(
    `- 本轮继续保持“失败跳过、不阻塞成稿”的策略，没有因为个别 source 失败而收缩成少量固定来源。`,
  )
  lines.push(`- 详细结果见 \`${summaryPath}\`。`)

  return `${normalizeLineEndings(lines.join("\n"))}\n`
}

function buildDiffLine(diff) {
  if (!diff) {
    return ""
  }

  const parts = [`与 ${diff.previousDate} 相比，成功源${diff.successDelta >= 0 ? "增加" : "减少"} ${Math.abs(diff.successDelta)} 个`]

  if (diff.recoveredSources.length > 0) {
    parts.push(
      `恢复可用：${diff.recoveredSources.map((source) => `\`${source}\``).join("、")}`,
    )
  }

  if (diff.lostSources.length > 0) {
    parts.push(`转为缺失：${diff.lostSources.map((source) => `\`${source}\``).join("、")}`)
  }

  return `${parts.join("；")}。`
}

function formatFailureMessage(result) {
  const message = result.error?.trim() || "未知错误"
  const normalized = message.replace(/\s+/g, " ").trim()

  if (normalized.includes("PRODUCTHUNT_API_TOKEN")) {
    return "缺少 `PRODUCTHUNT_API_TOKEN`"
  }
  if (normalized.includes("404")) {
    return normalized
  }
  if (normalized.length > 180) {
    return `${normalized.slice(0, 177)}...`
  }

  return normalized
}

async function readPreviousSummary(dir, date) {
  const entries = await readdir(dir).catch(() => [])
  const candidates = entries
    .filter((name) => name.endsWith("_newsnow-summary.json"))
    .map((name) => name.slice(0, 10))
    .filter((candidateDate) => candidateDate < date)
    .sort()

  const previousDate = candidates.at(-1)
  if (!previousDate) {
    return null
  }

  const content = await readFile(path.join(dir, `${previousDate}_newsnow-summary.json`), "utf8")
  return JSON.parse(content)
}

function normalizeLineEndings(text) {
  return text.replace(/\r\n/g, "\n")
}

function todayInTimeZone(timeZone) {
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  })

  const parts = Object.fromEntries(
    formatter
      .formatToParts(new Date())
      .filter((part) => part.type !== "literal")
      .map((part) => [part.type, part.value]),
  )

  return `${parts.year}-${parts.month}-${parts.day}`
}

function formatChineseDateTime(date) {
  const formatter = new Intl.DateTimeFormat("zh-CN", {
    timeZone: TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23",
  })

  const parts = Object.fromEntries(
    formatter
      .formatToParts(date)
      .filter((part) => part.type !== "literal")
      .map((part) => [part.type, part.value]),
  )

  return `${parts.year}/${parts.month}/${parts.day} ${parts.hour}:${parts.minute}:${parts.second} CST`
}
