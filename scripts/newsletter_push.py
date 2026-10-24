#!/usr/bin/env python3
"""每日新闻 Newsletter 生成 + 发布（无 LLM，模板化）。

流程：
1. 运行 scripts/newsnow-daily.mjs 抓取 66 个新闻源
2. 读取当天 summary 与各成功源 JSON，模板化生成 Newsletter markdown
3. 抢救服务器端 OpenClaw 自动提交的独有文件（如有）并入仓库
4. git 提交推送 GitHub（推送远程）
5. 服务器 git 同步到最新（防止 OpenClaw 旧构建覆盖站点）
6. Mac 构建 Quartz + rsync 到服务器 /note/ 路径（部署更新）
7. stdout 输出 Telegram 摘要，含完整版站点链接

设计上完全不依赖 LLM，绕开内容过滤器，保证每天稳定产出。
"""

import json
import shlex
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from zoneinfo import ZoneInfo

TIME_ZONE = ZoneInfo("Asia/Shanghai")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR_REL = "50_资源/Newsletters"

SSH_TARGET = "root@118.145.223.121"
SERVER_REPO = "/code/wei_note"
# 站点部署到 OpenClaw 不会触碰的目录：OpenClaw 每天 ~10:30 的自动同步会
# git clean 掉 /code/wei_note 下的 gitignore 产物（含 public/），
# 所以 nginx 服务的目录必须放在仓库之外，避免每日被清空。
DEPLOY_TARGET = "/srv/wei-note-site"
SITE_BASE = "http://118.145.223.121/note"

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


def run(cmd: list[str], timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=timeout,
    )


def ssh_run(remote_cmd: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
                SSH_TARGET, remote_cmd], timeout=timeout)


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


# ---------------------------------------------------------------------------
# 部署链路
# ---------------------------------------------------------------------------

def rescue_server_files() -> Tuple[List[str], Optional[str]]:
    """把服务器仓库独有（GitHub 没有）的文件抢救回本地仓库，如 OpenClaw 的自动日记。

    git diff --diff-filter=A origin/main HEAD = 从 origin/main 到 HEAD 新增的文件，
    即只存在于服务器 HEAD、GitHub 没有的文件。
    """
    proc = ssh_run(
        f"cd {shlex.quote(SERVER_REPO)} && git fetch -q origin && "
        "git diff --name-only --diff-filter=A origin/main HEAD"
    )
    if proc.returncode != 0:
        return [], f"列出服务器独有文件失败: {proc.stderr.strip()[:120]}"

    rescued = []
    for rel in proc.stdout.splitlines():
        rel = rel.strip()
        if not rel:
            continue
        # git 会把非 ASCII 路径转成八进制转义，用 git 自身做路径解码最稳
        show = ssh_run(
            f"cd {shlex.quote(SERVER_REPO)} && "
            f"git show \"HEAD:$(python3 -c 'import sys;print(sys.argv[1].encode().decode(\"unicode_escape\").encode(\"latin-1\").decode())' {shlex.quote(rel)})\""
        )
        if show.returncode != 0 or not show.stdout:
            continue
        try:
            rel_decoded = (rel.encode("utf-8").decode("unicode_escape")
                           .encode("latin-1").decode("utf-8"))
        except Exception:
            rel_decoded = rel
        dest = PROJECT_ROOT / rel_decoded
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(show.stdout, encoding="utf-8")
        rescued.append(rel_decoded)
    return rescued, None


def git_publish(date: str) -> Optional[str]:
    run(["git", "add", "-A"])
    commit = run(["git", "commit", "-m", f"docs: {date} 每日新闻 Newsletter 自动发布", "-q"])
    if commit.returncode != 0 and "nothing to commit" not in (commit.stdout + commit.stderr):
        return f"git commit 失败: {commit.stderr.strip()[:120]}"
    push = run(["git", "push", "origin", "main"], timeout=180)
    if push.returncode != 0:
        return f"git push 失败: {(push.stderr or push.stdout).strip()[:120]}"
    return None


def server_sync() -> Optional[str]:
    proc = ssh_run(
        f"cd {shlex.quote(SERVER_REPO)} && git fetch -q origin && "
        "git reset --hard origin/main -q"
    )
    if proc.returncode != 0:
        return f"服务器 git 同步失败: {proc.stderr.strip()[:120]}"
    return None


def build_and_ship() -> Optional[str]:
    build = run(["npm", "run", "build"], timeout=600)
    if build.returncode != 0:
        return f"Quartz 构建失败: {(build.stderr or build.stdout).strip()[-200:]}"
    sync = run(["rsync", "-a", "--delete", "-e", "ssh -o BatchMode=yes",
                "public/", f"{SSH_TARGET}:{DEPLOY_TARGET}/"], timeout=600)
    if sync.returncode != 0:
        return f"rsync 部署失败: {sync.stderr.strip()[:120]}"
    return None


# ---------------------------------------------------------------------------
# Newsletter 生成
# ---------------------------------------------------------------------------

def run_collection() -> subprocess.CompletedProcess:
    return run(["node", str(PROJECT_ROOT / "scripts" / "newsnow-daily.mjs")], timeout=900)


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
                 newsletter_rel: str, generated_at: str,
                 deploy_status: list[str], newsletter_url: str) -> str:
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
    lines.append(f"🔗 完整版：{newsletter_url}")
    lines.extend(deploy_status)
    lines.append(f"📁 本地文件：{newsletter_rel}")
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

    log("[1/5] 运行新闻抓取（约 30-60 秒）...")
    proc = run_collection()
    if proc.returncode != 0 and not summary_path.exists():
        print("❌ 每日新闻摘要抓取失败：", proc.stderr.strip()[:300] or proc.stdout.strip()[:300])
        return 0

    summary = load_json(summary_path)
    if not summary:
        print(f"❌ 找不到或无法解析 summary：{summary_path}")
        return 0

    log("[2/5] 生成 Newsletter...")
    sources_data = {}
    for result in summary.get("results", []):
        if result.get("status") != "success":
            continue
        data = load_json(raw_dir / f"{date}_{result['source']}.json")
        if data:
            sources_data[result["source"]] = data

    content, digest_items = build_newsletter(date, raw_dir, summary, sources_data, generated_at)
    newsletter_path.write_text(content, encoding="utf-8")

    newsletter_rel = str(newsletter_path.relative_to(PROJECT_ROOT))
    newsletter_url = SITE_BASE + "/" + "/".join(
        urllib.parse.quote(seg) for seg in newsletter_rel.removesuffix(".md").split("/")
    ) + ".html"

    # 部署链路：每步独立容错，失败记入摘要但不中断后续步骤
    deploy_status: list[str] = []

    log("[3/5] 抢救服务器独有文件 + git 推送远程...")
    rescued, rescue_err = rescue_server_files()
    if rescue_err:
        deploy_status.append(f"⚠️ 服务器文件抢救: {rescue_err}")
    elif rescued:
        deploy_status.append(f"📥 抢救服务器独有文件 {len(rescued)} 个（如 OpenClaw 自动日记）")

    err = git_publish(date)
    if err:
        deploy_status.append(f"⚠️ {err}")
    else:
        deploy_status.append("📤 已推送 GitHub")

    log("[4/5] Quartz 构建部署（目标 /srv/wei-note-site，不经过服务器 git 仓库）...")
    err = build_and_ship()
    if err:
        deploy_status.append(f"⚠️ {err}")
    else:
        deploy_status.append(f"🚀 已部署：{SITE_BASE}/")

    log("[5/5] 完成")
    print(build_digest(date, summary, digest_items, newsletter_rel, generated_at,
                       deploy_status, newsletter_url))
    return 0


if __name__ == "__main__":
    sys.exit(main())
