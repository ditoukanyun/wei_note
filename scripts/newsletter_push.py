#!/usr/bin/env python3
"""每日新闻 Newsletter 生成器（无 LLM，模板化）。

流程：
1. 运行 scripts/newsnow-daily.mjs 抓取 66 个新闻源
2. 读取当天 summary 与各成功源 JSON
3. 模板化生成 Newsletter markdown 到 50_资源/Newsletters/<月份>/<日期>-Newsletter.md
4. stdout 输出适合 Telegram 阅读的摘要（由 cron no_agent 模式原样推送）

设计上完全不依赖 LLM，绕开内容过滤器，保证每天稳定产出。
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TIME_ZONE = ZoneInfo("Asia/Shanghai")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR_REL = "50_资源/Newsletters"

SOURCE_LABELS = {
    "36kr": "36氪", "36kr-quick": "36氪快讯", "36kr-renqi": "36氪人气",
    "baidu": "百度热搜", "bilibili": "B站热搜", "bilibili-hot-search": "B站热搜",
    "bilibili-hot-video": "B站热门视频", "bilibili-ranking": "B站排行榜",
    "cankaoxiaoxi": "参考消息", "chongbuluo": "虫部落", "chongbuluo-hot": "虫部落热帖",
    "chongbuluo-latest": "虫部落最新", "cls": "财联社", "cls-depth": "财联社深度",
    "cls-hot": "财联社热榜", "cls-telegraph": "财联社电报", "coolapk": "酷安",
    "douban": "豆瓣", "douyin": "抖音热榜", "fastbull": "法布财经",
    "fastbull-express": "法布财经快讯", "fastbull-news": "法布财经新闻",
    "freebuf": "FreeBuf", "gelonghui": "格隆汇", "ghxi": "果核剥壳",
    "github": "GitHub", "github-trending-today": "GitHub Trending",
    "hackernews": "Hacker News", "hupu": "虎扑", "ifeng": "凤凰网资讯",
    "iqiyi-hot-ranklist": "爱奇艺热播", "ithome": "IT之家", "jin10": "金十快讯",
    "juejin": "掘金", "kaopu": "靠谱新闻", "kuaishou": "快手热榜",
    "linuxdo": "LinuxDo", "linuxdo-hot": "LinuxDo 热榜", "linuxdo-latest": "LinuxDo 最新",
    "mktnews": "市场资讯", "mktnews-flash": "市场快讯", "nowcoder": "牛客",
    "pcbeta-windows": "PCBeta Windows", "pcbeta-windows11": "PCBeta Windows 11",
    "producthunt": "Product Hunt", "qqvideo-tv-hotsearch": "腾讯视频热搜",
    "smzdm": "什么值得买", "solidot": "Solidot", "sputniknewscn": "俄卫星通讯社",
    "sspai": "少数派", "steam": "Steam", "tencent-hot": "腾讯热榜",
    "thepaper": "澎湃新闻", "tieba": "贴吧热议", "toutiao": "今日头条",
    "v2ex": "V2EX", "v2ex-share": "V2EX 热门", "wallstreetcn": "华尔街见闻",
    "wallstreetcn-hot": "华尔街见闻热点", "wallstreetcn-news": "华尔街见闻新闻",
    "wallstreetcn-quick": "华尔街见闻快讯", "weibo": "微博热搜", "xueqiu": "雪球",
    "xueqiu-hotstock": "雪球热股", "zaobao": "联合早报", "zhihu": "知乎热榜",
}

GROUPS = [
    ("综合与时政", ["baidu", "zhihu", "weibo", "tencent-hot", "toutiao", "thepaper",
                   "ifeng", "cankaoxiaoxi", "sputniknewscn"]),
    ("财经与产业", ["36kr", "36kr-quick", "36kr-renqi", "cls-depth", "cls-hot",
                   "gelonghui", "wallstreetcn", "wallstreetcn-hot", "wallstreetcn-news",
                   "wallstreetcn-quick", "jin10", "xueqiu", "xueqiu-hotstock",
                   "fastbull", "fastbull-express", "fastbull-news", "mktnews", "mktnews-flash"]),
    ("科技与开发者", ["ithome", "juejin", "nowcoder", "solidot", "sspai", "ghxi",
                     "github", "github-trending-today", "hackernews", "linuxdo",
                     "linuxdo-hot", "linuxdo-latest", "freebuf", "producthunt",
                     "pcbeta-windows", "pcbeta-windows11"]),
    ("平台与社区热度", ["bilibili", "bilibili-hot-search", "bilibili-hot-video",
                       "bilibili-ranking", "chongbuluo", "chongbuluo-hot", "chongbuluo-latest",
                       "coolapk", "douban", "douyin", "hupu", "iqiyi-hot-ranklist",
                       "kuaishou", "qqvideo-tv-hotsearch", "smzdm", "steam", "tieba"]),
]

# 今日速览优先源（取每源第 1 条）
DIGEST_PRIORITY = ["weibo", "zhihu", "tencent-hot", "36kr", "ithome",
                   "github-trending-today", "hackernews", "thepaper"]


def label_of(source: str) -> str:
    return SOURCE_LABELS.get(source, source)


def group_of(source: str) -> str:
    for title, members in GROUPS:
        if source in members:
            return title
    return "其他"


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def run_collection() -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", str(PROJECT_ROOT / "scripts" / "newsnow-daily.mjs")],
        cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=900,
    )


def build_newsletter(date: str, raw_dir: Path, summary: dict,
                     sources_data: dict, generated_at: str) -> tuple[str, list]:
    results = summary.get("results", [])
    success = [r["source"] for r in results if r.get("status") == "success"]

    not_included = []
    reason_map = {"nonzero": "抓取失败", "timeout": "超时", "empty": "返回空结果",
                  "badjson": "无效 JSON", "skipenv": "缺环境变量", "aborted": "熔断跳过"}
    for r in results:
        if r.get("status") == "success":
            continue
        reason = reason_map.get(r.get("status"), r.get("status"))
        if r.get("error"):
            err = str(r["error"]).replace("\n", " ")[:80]
            reason = f"{reason}（{err}）"
        not_included.append(f"`{r['source']}` {reason}")

    seen_labels = set()
    unique_labels = []
    for s in success:
        lbl = label_of(s)
        if lbl not in seen_labels:
            seen_labels.add(lbl)
            unique_labels.append(lbl)

    lines = [
        "---",
        f"date: {date}",
        "type: newsletter",
        "tags: [news, daily]",
        "publish: true",
        "---",
        f"# 新闻精选 | {date}",
        f"> 生成时间: {generated_at}",
        "> 来源: " + "、".join(unique_labels),
        "> 抓取说明: 通过 `npm run news:daily` 对 66 个 source 做 6 路并发轮询抓取（同站源串行），"
        "每源默认 10 秒超时并对慢源做 15 秒窄重试，保持“单源失败跳过、不阻塞成稿”的策略；"
        "本稿由模板脚本自动生成，未经过 LLM 润色。",
    ]
    if not_included:
        lines.append("> 未纳入说明: " + "；".join(not_included) + "。")
    lines.append(f"> 抓取日志: [[原始数据/{date}_newsnow-log|{date} newsnow 日志]]")
    lines.append("")

    # 今日速览（机械提取：优先源各取第 1 条）
    lines.append("## 今日速览")
    lines.append("")
    digest_items = []
    for source in DIGEST_PRIORITY:
        if source not in sources_data:
            continue
        items = sources_data[source].get("items", [])
        if items:
            title = items[0].get("title", "").strip()
            url = items[0].get("url") or items[0].get("mobileUrl") or ""
            if title:
                lines.append(f"- **{label_of(source)}**：[{title}]({url})")
                digest_items.append((label_of(source), title, url))
    lines.append("")

    # 分组章节
    by_group: dict[str, list[str]] = {}
    for source in success:
        by_group.setdefault(group_of(source), []).append(source)

    for group_title, _ in GROUPS + [("其他", [])]:
        members = by_group.get(group_title, [])
        if not members:
            continue
        lines.append(f"## {group_title}")
        lines.append("")
        for source in members:
            data = sources_data.get(source) or {}
            items = data.get("items", [])[:5]
            if not items:
                continue
            lines.append(f"### {label_of(source)}")
            lines.append("")
            for item in items:
                title = str(item.get("title", "")).strip()
                url = item.get("url") or item.get("mobileUrl") or ""
                if not title:
                    continue
                lines.append(f"- [{title}]({url})" if url else f"- {title}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n", digest_items


def build_digest(date: str, summary: dict, digest_items: list,
                 newsletter_rel: str, generated_at: str) -> str:
    counts = summary.get("counts", {})
    stats = (f"{counts.get('success', 0)} 成功 / {counts.get('nonzero', 0)} 失败 / "
             f"{counts.get('timeout', 0)} 超时 / {counts.get('empty', 0)} 空 / "
             f"{counts.get('skipenv', 0) + counts.get('aborted', 0)} 跳过")

    lines = [f"📰 每日新闻精选 | {date}", ""]
    if digest_items:
        for label, title, url in digest_items[:6]:
            short = title if len(title) <= 60 else title[:58] + "…"
            lines.append(f"• *{label}*：[{short}]({url})" if url else f"• *{label}*：{short}")
        lines.append("")
    else:
        lines.append("（今日无可展示条目）")
        lines.append("")
    lines.append(f"📊 抓取统计：{stats}")
    lines.append(f"📁 Newsletter：{newsletter_rel}")
    lines.append(f"🕐 {generated_at}")
    return "\n".join(lines)


def main() -> int:
    now = datetime.now(TIME_ZONE)
    date = now.strftime("%Y-%m-%d")
    month_key = now.strftime("%Y-%m")
    generated_at = now.strftime("%Y/%m/%d %H:%M CST")

    raw_dir = PROJECT_ROOT / RAW_DIR_REL / month_key / "原始数据"
    summary_path = raw_dir / f"{date}_newsnow-summary.json"
    newsletter_path = PROJECT_ROOT / RAW_DIR_REL / month_key / f"{date}-Newsletter.md"

    print(f"[1/3] 运行新闻抓取（约 30-60 秒）...", file=sys.stderr)
    proc = run_collection()
    if proc.returncode != 0 and not summary_path.exists():
        print("❌ 每日新闻摘要抓取失败：", proc.stderr.strip()[:300] or proc.stdout.strip()[:300])
        return 0

    summary = load_json(summary_path)
    if not summary:
        print(f"❌ 找不到或无法解析 summary：{summary_path}")
        return 0

    print("[2/3] 读取各源数据并生成 Newsletter...", file=sys.stderr)
    sources_data = {}
    for result in summary.get("results", []):
        if result.get("status") != "success":
            continue
        data = load_json(raw_dir / f"{date}_{result['source']}.json")
        if data:
            sources_data[result["source"]] = data

    content, digest_items = build_newsletter(date, raw_dir, summary, sources_data, generated_at)
    newsletter_path.write_text(content, encoding="utf-8")

    print("[3/3] 完成", file=sys.stderr)
    newsletter_rel = str(newsletter_path.relative_to(PROJECT_ROOT))
    print(build_digest(date, summary, digest_items, newsletter_rel, generated_at))
    return 0


if __name__ == "__main__":
    sys.exit(main())
