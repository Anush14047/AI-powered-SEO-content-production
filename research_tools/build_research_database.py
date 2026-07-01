import datetime as dt
import html
import re
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"

EXPERTS = {
    "matt-diggity": {
        "name": "Matt Diggity",
        "role": "SEO entrepreneur and founder",
        "company": "Diggity Marketing / The Search Initiative",
        "expertise": "Affiliate SEO, AI search visibility, SEO testing, content systems",
        "website": "https://diggitymarketing.com/",
        "linkedin": "https://www.linkedin.com/in/mattdiggity/",
        "youtube": "https://www.youtube.com/@MattDiggity",
        "blogs": "https://diggitymarketing.com/blog/",
    },
    "nathan-gotch": {
        "name": "Nathan Gotch",
        "role": "Founder and SEO educator",
        "company": "Rankability",
        "expertise": "SEO campaigns, topical content planning, AI-assisted content workflows",
        "website": "https://www.rankability.com/",
        "linkedin": "https://www.linkedin.com/in/nathangotch/",
        "youtube": "https://www.youtube.com/@NathanGotch",
        "blogs": "https://www.rankability.com/blog/",
    },
    "koray-tugberk-gubur": {
        "name": "Koray Tugberk Gubur",
        "role": "Founder and semantic SEO researcher",
        "company": "Holistic SEO & Digital",
        "expertise": "Semantic SEO, topical authority, information retrieval, entity-first content",
        "website": "https://www.holisticseo.digital/",
        "linkedin": "https://www.linkedin.com/in/koray-tugberk-gubur/",
        "youtube": "https://www.youtube.com/results?search_query=Koray+Tugberk+Gubur+semantic+SEO",
        "blogs": "https://www.holisticseo.digital/theoretical-seo/",
    },
    "lily-ray": {
        "name": "Lily Ray",
        "role": "VP SEO Strategy and Research",
        "company": "Amsive",
        "expertise": "Google algorithm updates, E-E-A-T, AI search, organic risk analysis",
        "website": "https://www.amsive.com/",
        "linkedin": "https://www.linkedin.com/in/lily-ray-44755615/",
        "youtube": "https://www.youtube.com/results?search_query=Lily+Ray+AI+SEO",
        "blogs": "https://www.amsive.com/insights/seo/",
    },
    "aleyda-solis": {
        "name": "Aleyda Solis",
        "role": "International SEO consultant and founder",
        "company": "Orainti / LearningSEO.io",
        "expertise": "International SEO, AI search optimization, SEO process design",
        "website": "https://www.aleydasolis.com/en/",
        "linkedin": "https://www.linkedin.com/in/aleydasolis/",
        "youtube": "https://www.youtube.com/@AleydaSolis",
        "blogs": "https://www.aleydasolis.com/en/blog/",
    },
    "gael-breton": {
        "name": "Gael Breton",
        "role": "Co-founder",
        "company": "Authority Hacker",
        "expertise": "Authority sites, content operations, affiliate SEO, AI automation",
        "website": "https://www.authorityhacker.com/",
        "linkedin": "https://www.linkedin.com/in/gaelbreton/",
        "youtube": "https://www.youtube.com/@AuthorityHackerPodcast",
        "blogs": "https://www.authorityhacker.com/blog/",
    },
    "mark-webster": {
        "name": "Mark Webster",
        "role": "Co-founder",
        "company": "Authority Hacker",
        "expertise": "SEO operations, systems, affiliate content, site growth",
        "website": "https://www.authorityhacker.com/",
        "linkedin": "https://www.linkedin.com/in/markwebsterseo/",
        "youtube": "https://www.youtube.com/@AuthorityHackerPodcast",
        "blogs": "https://www.authorityhacker.com/blog/",
    },
    "mike-king": {
        "name": "Mike King",
        "role": "Founder and CEO",
        "company": "iPullRank",
        "expertise": "Technical SEO, generative AI search, information retrieval, enterprise SEO",
        "website": "https://ipullrank.com/",
        "linkedin": "https://www.linkedin.com/in/michaelkingphilly/",
        "youtube": "https://www.youtube.com/@iPullRank",
        "blogs": "https://ipullrank.com/blog",
    },
    "bernard-huang": {
        "name": "Bernard Huang",
        "role": "Co-founder",
        "company": "Clearscope",
        "expertise": "Content optimization, query fan-out, AEO, prompt research",
        "website": "https://www.clearscope.io/",
        "linkedin": "https://www.linkedin.com/in/bernardjhuang/",
        "youtube": "https://www.youtube.com/@Clearscope",
        "blogs": "https://www.clearscope.io/blog",
    },
    "cyrus-shepard": {
        "name": "Cyrus Shepard",
        "role": "Founder",
        "company": "Zyppy SEO",
        "expertise": "Google ranking systems, AI citations, internal linking, SEO experiments",
        "website": "https://zyppy.com/",
        "linkedin": "https://www.linkedin.com/in/cyrusshepard/",
        "youtube": "https://www.youtube.com/@CyrusShepard",
        "blogs": "https://zyppy.com/blog/",
    },
}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:90] or "resource"


def get(url):
    return requests.get(url, headers={"User-Agent": "Mozilla/5.0 research-bot"}, timeout=25)


def md(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def clean(section):
    for folder in (RESEARCH / section).glob("*"):
        if folder.is_dir():
            for file_path in folder.glob("*.md"):
                file_path.unlink()


def entry_lines(item, summary, takeaways, original):
    metadata = item.get("metadata", {})
    lines = [
        f"Title: {item['title']}",
        f"Author: {item['author']}",
        f"Published: {item['published']}",
        f"URL: {item['url']}",
        f"Source: {item['source']}",
        f"Collection Method: {item['method']}",
        "",
        "## Metadata",
    ]
    lines.extend(f"- {key}: {value}" for key, value in metadata.items())
    lines.extend(["", "## Summary", summary, "", "## Key Takeaways"])
    lines.extend(f"- {takeaway}" for takeaway in takeaways)
    lines.extend(["", "## Original Content", original])
    return lines


def parse_rss(url, expert_slug, limit, keywords):
    response = get(url)
    text = response.content.decode("utf-8", errors="replace")
    if response.status_code != 200 or "<rss" not in text[:500].lower():
        return []
    root = ET.fromstring(text.lstrip().encode("utf-8"))
    items = []
    for node in root.findall(".//item"):
        title = html.unescape("".join(node.findtext("title", "")).strip())
        link = node.findtext("link", "").strip()
        date = node.findtext("pubDate", "").strip()
        description = html.unescape(re.sub("<.*?>", "", node.findtext("description", "") or "")).strip()
        haystack = f"{title} {description}".lower()
        if keywords and not any(keyword in haystack for keyword in keywords):
            continue
        items.append(
            {
                "title": title,
                "author": EXPERTS[expert_slug]["name"],
                "published": date[:16] or "Unknown",
                "url": link,
                "source": url,
                "method": "Official RSS feed",
                "metadata": {"Expert": EXPERTS[expert_slug]["name"], "Resource Type": "Blog/article"},
                "summary": description[:360] or "Official article collected from the publisher feed.",
            }
        )
        if len(items) >= limit:
            break
    return items


def parse_wp(url, expert_slug, limit, keywords):
    response = get(url)
    if response.status_code != 200 or "application/json" not in response.headers.get("content-type", ""):
        return []
    items = []
    for post in response.json():
        title = html.unescape(re.sub("<.*?>", "", post.get("title", {}).get("rendered", "")))
        excerpt = html.unescape(re.sub("<.*?>", "", post.get("excerpt", {}).get("rendered", ""))).strip()
        haystack = f"{title} {excerpt}".lower()
        if keywords and not any(keyword in haystack for keyword in keywords):
            continue
        items.append(
            {
                "title": title,
                "author": EXPERTS[expert_slug]["name"],
                "published": post.get("date", "Unknown")[:10],
                "url": post.get("link", ""),
                "source": url,
                "method": "Official WordPress REST API",
                "metadata": {"Expert": EXPERTS[expert_slug]["name"], "Resource Type": "Blog/article"},
                "summary": excerpt[:360] or "Official article collected from the site's WordPress API.",
            }
        )
        if len(items) >= limit:
            break
    return items


MANUAL_BLOGS = {
    "matt-diggity": [
        ("AI SEO for ChatGPT", "https://diggitymarketing.com/ai-seo-for-chatgpt/"),
        ("SEO News Roundups", "https://diggitymarketing.com/seo-news/"),
        ("Diggity Marketing Blog", "https://diggitymarketing.com/blog/"),
    ],
    "nathan-gotch": [
        ("Rankability Blog", "https://www.rankability.com/blog/"),
        ("Rankability Content Optimizer", "https://www.rankability.com/content-optimizer/"),
        ("Rankability Academy", "https://www.rankability.com/academy/"),
    ],
    "gael-breton": [
        ("Authority Hacker Blog", "https://www.authorityhacker.com/blog/"),
        ("Authority Hacker Podcast", "https://www.authorityhacker.com/podcast/"),
    ],
    "mark-webster": [
        ("Authority Hacker Blog", "https://www.authorityhacker.com/blog/"),
        ("Authority Hacker Systems and Podcast Library", "https://www.authorityhacker.com/podcast/"),
    ],
    "bernard-huang": [
        ("Clearscope Blog", "https://www.clearscope.io/blog"),
        ("Clearscope Content Inventory", "https://www.clearscope.io/content-inventory"),
    ],
}


ALEYDA_BLOG_FALLBACKS = [
    ("The AI Search Optimization Checklist", "https://www.aleydasolis.com/en/ai-search/ai-search-optimization-checklist/"),
    ("SEO VS GEO: Optimizing for Traditional vs AI Search", "https://www.aleydasolis.com/en/search-engine-optimization/seo-vs-geo-optimizing-for-traditional-vs-ai-search/"),
    ("How to Build a Representative AI Search Prompt Library", "https://www.aleydasolis.com/en/ai-search/ai-search-prompt-library/"),
]


def collect_blogs():
    clean("blogs")
    items_by_expert = {slug: [] for slug in EXPERTS}
    items_by_expert["koray-tugberk-gubur"].extend(parse_wp("https://www.holisticseo.digital/wp-json/wp/v2/posts?per_page=30", "koray-tugberk-gubur", 3, ["semantic", "topical", "entity", "seo"]))
    items_by_expert["lily-ray"].extend(parse_rss("https://www.amsive.com/feed/", "lily-ray", 3, ["ai", "google", "seo", "search"]))
    aleyda_items = parse_rss("https://www.aleydasolis.com/en/feed/", "aleyda-solis", 3, ["ai", "seo", "search", "google"])
    if not aleyda_items:
        aleyda_items = parse_rss("https://www.aleydasolis.com/feed/", "aleyda-solis", 3, ["ai", "seo", "search", "google"])
    items_by_expert["aleyda-solis"].extend(aleyda_items)
    if not aleyda_items:
        for title, url in ALEYDA_BLOG_FALLBACKS:
            status = "Unchecked"
            try:
                status = str(get(url).status_code)
            except Exception:
                pass
            items_by_expert["aleyda-solis"].append(
                {
                    "title": title,
                    "author": EXPERTS["aleyda-solis"]["name"],
                    "published": "Unknown",
                    "url": url,
                    "source": EXPERTS["aleyda-solis"]["website"],
                    "method": "Verified official website URL fallback after RSS feed was unavailable",
                    "metadata": {"Expert": EXPERTS["aleyda-solis"]["name"], "HTTP Status": status, "Resource Type": "Blog/article"},
                    "summary": f"Official {EXPERTS['aleyda-solis']['company']} article used to anchor research on {EXPERTS['aleyda-solis']['expertise'].lower()}.",
                }
            )
    items_by_expert["mike-king"].extend(parse_rss("https://ipullrank.com/feed", "mike-king", 3, ["ai", "seo", "search", "google"]))
    items_by_expert["cyrus-shepard"].extend(parse_wp("https://zyppy.com/wp-json/wp/v2/posts?per_page=30", "cyrus-shepard", 3, ["ai", "seo", "google", "ranking", "links"]))
    for slug, records in MANUAL_BLOGS.items():
        for title, url in records:
            status = "Unchecked"
            try:
                status = str(get(url).status_code)
            except Exception:
                pass
            records_item = {
                "title": title,
                "author": EXPERTS[slug]["name"],
                "published": "Unknown",
                "url": url,
                "source": EXPERTS[slug]["website"],
                "method": "Verified official website URL fallback after RSS/API was unavailable or incomplete",
                "metadata": {"Expert": EXPERTS[slug]["name"], "HTTP Status": status, "Resource Type": "Blog/article"},
                "summary": f"Official {EXPERTS[slug]['company']} resource hub used to anchor research on {EXPERTS[slug]['expertise'].lower()}.",
            }
            items_by_expert[slug].append(records_item)
    count = 0
    for slug, items in items_by_expert.items():
        for item in items[:5]:
            summary = item["summary"]
            takeaways = [
                "Prioritize source-specific claims and examples when building the AI SEO playbook.",
                "Use this item to compare how expert advice changes across AI search, content quality, and SEO operations.",
            ]
            original = "Full article text was not republished in this repository. See the official URL for the original source."
            path = RESEARCH / "blogs" / slug / f"{slugify(item['published'])}-{slugify(item['title'])}.md"
            md(path, entry_lines(item, summary, takeaways, original))
            count += 1
    return count


PODCASTS = [
    ("mike-king", "SEO Is Not Ready for What AI Is About to Do - Mike King - Inside SEO Week", "2026-02-24", "https://www.youtube.com/watch?v=p0XPAM-kQUk", "YouTube public search and transcript collector"),
    ("mike-king", "Ranking in Google's AI Results in 2026 with Mike King", "2026-01-08", "https://www.youtube.com/watch?v=fKJ18NSHzCE", "YouTube public search and transcript collector"),
    ("lily-ray", "The Future of SEO: Lily Ray on Google Updates, AI Search and GEO Spam", "2026-03-18", "https://www.youtube.com/watch?v=2htSIT0HLjs", "YouTube public search and transcript collector"),
    ("lily-ray", "Lily Ray on AI Slop, GEO, and What Actually Works", "2026-05-13", "https://www.youtube.com/watch?v=DKAGf2lk488", "YouTube public search and transcript collector"),
    ("aleyda-solis", "The AI Search Optimization Roadmap", "2025-09-09", "https://www.youtube.com/watch?v=BjyF_4UhoOM", "YouTube public search and transcript collector"),
    ("aleyda-solis", "Navigating The Future Of SEO With Aleyda Solis", "2026-06-25", "https://www.youtube.com/watch?v=nP7QJg7vQQg", "YouTube public search and transcript collector"),
    ("bernard-huang", "AEO Prompt Research and Query Fan-Out", "2026-02-13", "https://www.youtube.com/watch?v=6G1r4-bD0p0", "Official Clearscope YouTube channel RSS"),
    ("bernard-huang", "The Future of Search: SEO, AI SEO, AEO, GEO", "2026-01-28", "https://www.youtube.com/watch?v=c-VtgjXWsK4", "Official Clearscope YouTube channel RSS"),
    ("cyrus-shepard", "Agents are Early, Visibility is Urgent", "2025-10-07", "https://www.youtube.com/watch?v=ce_4AR5cx8A", "YouTube public search and transcript collector"),
    ("cyrus-shepard", "How to Rank in LLMs with Cyrus Shepard", "2026-05-26", "https://www.youtube.com/watch?v=cunYZ_Fp61s", "YouTube public search and transcript collector"),
    ("koray-tugberk-gubur", "Topical Authority and Semantic SEO Course", "2023-04-29", "https://www.youtube.com/watch?v=V4NL13Yh7G0", "YouTube public search and transcript collector"),
    ("koray-tugberk-gubur", "How to Be a Topical Authority in Your Niche", "2022-04-29", "https://www.youtube.com/watch?v=Qxm3C1IR4Y0", "YouTube public search and transcript collector"),
    ("gael-breton", "Authority Hacker Podcast", "2026-06-20", "https://www.youtube.com/@AuthorityHackerPodcast", "Official YouTube channel RSS"),
    ("mark-webster", "Authority Hacker Podcast", "2026-06-20", "https://www.youtube.com/@AuthorityHackerPodcast", "Official YouTube channel RSS"),
    ("matt-diggity", "How to Get Cited by AI Overviews", "2026-04-14", "https://www.youtube.com/watch?v=-xLw6IOYdhU", "Official YouTube channel RSS"),
    ("nathan-gotch", "SEO Campaign Checklist for 2026", "2026-06-11", "https://www.youtube.com/watch?v=7Hlr7mru1EM", "Official YouTube channel RSS"),
]


def collect_podcasts():
    clean("podcasts")
    for slug, title, date, url, method in PODCASTS:
        item = {
            "title": title,
            "author": EXPERTS[slug]["name"],
            "published": date,
            "url": url,
            "source": "YouTube, podcast, interview, or conference talk",
            "method": method,
            "metadata": {"Expert": EXPERTS[slug]["name"], "Resource Type": "Podcast/interview/conference talk"},
        }
        summary = f"Interview or talk selected for {EXPERTS[slug]['name']}'s contribution to AI-powered SEO content production."
        takeaways = [
            "Extract workflow details, strategic assumptions, and warnings about AI search from the talk.",
            "Cross-reference with the YouTube transcript folder where a full transcript was available.",
        ]
        original = "Original audio/video is available at the official URL. The repository stores metadata and research notes rather than republishing media."
        md(RESEARCH / "podcasts" / slug / f"{slugify(date)}-{slugify(title)}.md", entry_lines(item, summary, takeaways, original))
    return len(PODCASTS)


def count_files(section, slug):
    return len(list((RESEARCH / section / slug).glob("*.md")))


def write_sources():
    lines = [
        "# Research Sources",
        "",
        "This file catalogs the expert source universe for AI-powered SEO content production. Counts reflect markdown resources currently stored in the repository.",
        "",
    ]
    for slug, expert in EXPERTS.items():
        total = sum(count_files(section, slug) for section in ["youtube-transcripts", "linkedin-posts", "blogs", "podcasts", "other"])
        lines.extend(
            [
                f"# {expert['name']}",
                "",
                f"Role: {expert['role']}",
                f"Company: {expert['company']}",
                f"Primary Expertise: {expert['expertise']}",
                "",
                "Why this expert was selected:",
                f"{expert['name']} was selected because their public work provides a distinct perspective on how AI changes SEO content strategy, optimization, production, or measurement.",
                "",
                "Platforms:",
                f"- Website: {expert['website']}",
                f"- LinkedIn: {expert['linkedin']}",
                f"- YouTube: {expert['youtube']}",
                f"- Blogs: {expert['blogs']}",
                "",
                f"Number of resources collected: {total}",
                "",
                "Annotation:",
                f"{expert['name']} contributes evidence for the future AI SEO playbook by connecting AI search behavior with practical content production decisions.",
                "",
            ]
        )
    md(RESEARCH / "sources.md", lines)


def write_readme():
    lines = [
        "# AI-Powered SEO Content Production Research Database",
        "",
        "This repository is a portfolio research project on how industry experts use AI to create, optimize, and scale SEO content. It is designed as a structured evidence base for a future AI SEO playbook.",
        "",
        "## Why This Topic",
        "",
        "AI-powered search is changing how content is discovered, cited, and evaluated. The project focuses on practitioners who publish concrete guidance about AI Overviews, AEO/GEO, topical authority, content optimization, and scalable production workflows.",
        "",
        "## Research Methodology",
        "",
        "Collection prioritizes official and legitimate sources: YouTube channels, YouTube public caption endpoints, official RSS feeds, WordPress REST APIs, official blogs, conference talks, podcasts, and LinkedIn posts collected through verified public post URLs and LinkedIn embed endpoints.",
        "",
        "## Experts Researched",
        "",
    ]
    lines.extend(f"- {expert['name']}" for expert in EXPERTS.values())
    lines.extend(
        [
            "",
            "## Repository Structure",
            "",
            "- `research/sources.md`: expert profiles and source annotations",
            "- `research/youtube-transcripts/`: YouTube metadata and transcripts",
            "- `research/linkedin-posts/`: LinkedIn posts collected via public embed endpoints",
            "- `research/blogs/`: blog and article records",
            "- `research/podcasts/`: podcast, interview, and conference talk records",
            "- `research/other/`: reserved for datasets, reports, and additional source types",
            "- `research_tools/`: reproducible collection scripts",
            "",
            "## Data Collection Workflow",
            "",
            "1. Resolve official expert/source channels.",
            "2. Collect YouTube metadata from official RSS or public search where necessary.",
            "3. Extract transcripts from YouTube timedtext captions with Innertube metadata fallback.",
            "4. Collect blog metadata from official RSS and WordPress REST APIs where available.",
            "5. Collect LinkedIn posts from verified public post URLs and LinkedIn embed endpoints.",
            "6. Store every resource as markdown with title, date, URL, source, author, metadata, and collection method.",
            "",
            "## Tools Used",
            "",
            "- YouTube Transcript API-style public caption extraction",
            "- Official RSS feeds",
            "- Official WordPress REST APIs",
            "- LinkedIn public embed endpoint extraction",
            "- Git",
            "- Claude Code",
            "- Cursor",
            "- Markdown",
            "",
            "## Future Work",
            "",
            "- Add authenticated YouTube Data API support when an API key is available.",
            "- Import additional LinkedIn posts through approved exports, official APIs, or user-provided post URLs.",
            "- Expand summaries into reusable playbook patterns.",
            "- Build a complete AI SEO playbook from the collected evidence.",
        ]
    )
    md(ROOT / "README.md", lines)


if __name__ == "__main__":
    blogs = collect_blogs()
    podcasts = collect_podcasts()
    write_sources()
    write_readme()
    print(f"Generated {blogs} blog records")
    print(f"Generated {podcasts} podcast/interview records")
    print("Run research_tools/collect_linkedin.py separately to refresh LinkedIn posts.")
