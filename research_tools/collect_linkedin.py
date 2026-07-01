"""Discover and collect public LinkedIn posts via search + embed endpoints."""

import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "linkedin-posts"

EXPERTS = {
    "matt-diggity": {
        "name": "Matt Diggity",
        "profile": "mattdiggity",
        "post_handles": ["mattdiggity", "mattdiggityseo"],
        "linkedin": "https://www.linkedin.com/in/mattdiggity/",
        "queries": [
            "Matt Diggity AI SEO site:linkedin.com/posts",
            "Matt Diggity AI Overviews site:linkedin.com/posts",
        ],
        "seed_urls": [
            "https://www.linkedin.com/posts/mattdiggityseo_ive-been-watching-ai-overviews-closely-since-activity-7313483298767269888-ab7l",
            "https://www.linkedin.com/posts/mattdiggityseo_ai-overviews-are-stealing-61-of-your-clicks-activity-7424849416014123008-mADm",
            "https://www.linkedin.com/posts/mattdiggityseo_googles-ai-overviews-are-swallowing-traffic-activity-7353753933086945280-oHIq",
            "https://www.linkedin.com/posts/mattdiggityseo_most-businesses-think-informational-searches-activity-7375822669688029184-wS63",
            "https://www.linkedin.com/posts/mattdiggityseo_googles-ai-overviews-are-a-trap-you-either-activity-7384102206477758464-S1iA",
        ],
    },
    "nathan-gotch": {
        "name": "Nathan Gotch",
        "profile": "nathangotch",
        "post_handles": ["nathangotch"],
        "linkedin": "https://www.linkedin.com/in/nathangotch/",
        "queries": [
            "Nathan Gotch SEO AI site:linkedin.com/posts",
            "Nathan Gotch Rankability site:linkedin.com/posts",
        ],
        "seed_urls": [
            "https://www.linkedin.com/posts/nathangotch_google-didnt-mention-organic-traffic-or-activity-7391507441814945792-Dwt-",
            "https://www.linkedin.com/posts/nathangotch_important-aeo-nuance-the-goal-is-not-to-activity-7399077974181871617-_MoR",
            "https://www.linkedin.com/posts/nathangotch_want-to-rank-in-googles-ai-mode-its-activity-7340721354142294016-WbLm",
            "https://www.linkedin.com/posts/nathangotch_stop-creating-generic-seo-content-targeting-activity-7326948799879270400-XX4n",
        ],
    },
    "koray-tugberk-gubur": {
        "name": "Koray Tugberk Gubur",
        "profile": "koray-tugberk-gubur",
        "post_handles": ["koray-tugberk-gubur"],
        "linkedin": "https://www.linkedin.com/in/koray-tugberk-gubur/",
        "queries": [
            "Koray Tugberk Gubur semantic SEO site:linkedin.com/posts",
            "Koray Gubur topical authority site:linkedin.com/posts",
        ],
        "seed_urls": [
            "https://www.linkedin.com/posts/koray-tugberk-gubur_semantic-seo-fundamentals-course-activity-7211335546634219520-MNLo",
            "https://www.linkedin.com/posts/koray-tugberk-gubur_seo-topicalauthority-algorithmicauthorship-activity-7365140458785714176-1pM7",
            "https://www.linkedin.com/posts/koray-tugberk-gubur_whoever-talks-bad-about-semantic-seo-is-doomed-activity-7234923965842903040-2C6J",
            "https://www.linkedin.com/posts/koray-tugberk-gubur_what-are-context-vectors-learn-semanticseo-activity-7206490497060659200-_kxP",
            "https://www.linkedin.com/posts/koray-tugberk-gubur_is-seo-dead-semantic-seo-guide-2025-with-activity-7332854083759816706-N-rB",
        ],
    },
    "lily-ray": {
        "name": "Lily Ray",
        "profile": "lily-ray-44755615",
        "post_handles": ["lily-ray-44755615"],
        "linkedin": "https://www.linkedin.com/in/lily-ray-44755615/",
        "queries": [
            "Lily Ray AI search SEO site:linkedin.com/posts",
            "Lily Ray Google algorithm site:linkedin.com/posts",
        ],
        "seed_urls": [
            "https://www.linkedin.com/posts/lily-ray-44755615_got-some-interesting-answers-from-john-mueller-activity-7462840529710546946-sHQL",
            "https://www.linkedin.com/posts/lily-ray-44755615_a-reflection-on-seo-geo-ai-search-in-2025-activity-7419213086412251136-etQU",
        ],
    },
    "aleyda-solis": {
        "name": "Aleyda Solis",
        "profile": "aleydasolis",
        "post_handles": ["aleyda", "aleydasolis"],
        "linkedin": "https://www.linkedin.com/in/aleydasolis/",
        "queries": [
            "Aleyda Solis AI search SEO site:linkedin.com/posts",
            "Aleyda Solis GEO site:linkedin.com/posts",
        ],
        "seed_urls": [
            "https://www.linkedin.com/posts/aleyda_ai-search-demystified-activity-7430550976257888256-l0VA",
            "https://www.linkedin.com/posts/aleyda_my-moz-guide-based-on-my-recent-webinar-activity-7463253507266052097-FXwm",
            "https://www.linkedin.com/posts/aleyda_the-ai-search-content-optimization-checklist-activity-7340439923935563776-A66c",
            "https://www.linkedin.com/posts/aleyda_the-3-layer-ai-search-diagnostic-measurement-activity-7473797353666183168-bfk2",
            "https://www.linkedin.com/posts/aleyda_how-to-build-a-representative-ai-search-activity-7469723521947131905-6DVK",
        ],
    },
    "gael-breton": {
        "name": "Gael Breton",
        "profile": "gaelbreton",
        "post_handles": ["gael-breton-78305118", "gaelbreton"],
        "linkedin": "https://www.linkedin.com/in/gaelbreton/",
        "queries": [
            "Gael Breton Authority Hacker SEO site:linkedin.com/posts",
            "Gael Breton AI content site:linkedin.com/posts",
        ],
        "seed_urls": [
            "https://www.linkedin.com/posts/gael-breton-78305118_after-10-years-of-teaching-seo-were-closing-activity-7274768322427047936-biT8",
            "https://www.linkedin.com/posts/gael-breton-78305118_this-wasnt-an-easy-one-to-film-but-it-feels-activity-7297657786153275394-J9ki",
            "https://www.linkedin.com/posts/gael-breton-78305118_last-week-i-tested-all-the-latest-ai-models-activity-7302724992994074624-3QIU",
            "https://www.linkedin.com/posts/gael-breton-78305118_meta-just-announced-theyre-adding-ai-users-activity-7280924780373889024-3Huh",
            "https://www.linkedin.com/posts/gael-breton-78305118_if-you-want-to-see-me-in-the-seat-of-the-activity-7211748774589657088-rhjo",
        ],
    },
    "mark-webster": {
        "name": "Mark Webster",
        "profile": "markwebsterseo",
        "post_handles": ["markwebster1", "markwebsterseo"],
        "linkedin": "https://www.linkedin.com/in/markwebsterseo/",
        "queries": [
            "Mark Webster Authority Hacker SEO site:linkedin.com/posts",
            "Mark Webster SEO systems site:linkedin.com/posts",
        ],
        "seed_urls": [
            "https://www.linkedin.com/posts/markwebster1_how-we-outranked-forbes-and-built-687-activity-7252029555824046080-_Ikk",
            "https://www.linkedin.com/posts/markwebster1_google-slams-forbes-with-manual-penalty-activity-7247929982948118528-gskw",
        ],
    },
    "mike-king": {
        "name": "Mike King",
        "profile": "michaelkingphilly",
        "post_handles": ["michaelkingphilly"],
        "linkedin": "https://www.linkedin.com/in/michaelkingphilly/",
        "queries": [
            "Mike King iPullRank AI SEO site:linkedin.com/posts",
            "Michael King SEO AI search site:linkedin.com/posts",
        ],
        "seed_urls": [
            "https://www.linkedin.com/posts/michaelkingphilly_how-ai-mode-and-ai-overviews-work-based-on-activity-7335330568374571008-ik6d",
            "https://www.linkedin.com/posts/michaelkingphilly_the-last-couple-years-at-ipullrank-have-been-activity-7420207312742531073-2myB",
            "https://www.linkedin.com/posts/michaelkingphilly_ive-been-thinking-about-how-valuable-an-activity-7333539956411322370-JJW3",
        ],
    },
    "bernard-huang": {
        "name": "Bernard Huang",
        "profile": "bernardjhuang",
        "post_handles": ["bernardjhuang"],
        "linkedin": "https://www.linkedin.com/in/bernardjhuang/",
        "queries": [
            "Bernard Huang Clearscope AEO site:linkedin.com/posts",
            "Bernard Huang query fan-out site:linkedin.com/posts",
        ],
        "seed_urls": [
            "https://www.linkedin.com/posts/bernardjhuang_ranch-style-seo-unoriginal-content-future-activity-7187130848553451523-9_Rv",
            "https://www.linkedin.com/posts/bernardjhuang_geo-seo-activity-7318337476614373377-mj4W",
            "https://www.linkedin.com/posts/bernardjhuang_googles-stance-that-ai-mode-will-become-activity-7338596850649731075-vlLS",
            "https://www.linkedin.com/posts/bernardjhuang_do-leads-from-ai-platforms-convert-better-activity-7394772866329690112-lG-r",
        ],
    },
    "cyrus-shepard": {
        "name": "Cyrus Shepard",
        "profile": "cyrusshepard",
        "post_handles": ["cyrusshepard"],
        "linkedin": "https://www.linkedin.com/in/cyrusshepard/",
        "queries": [
            "Cyrus Shepard AI SEO site:linkedin.com/posts",
            "Cyrus Shepard Zyppy Google site:linkedin.com/posts",
        ],
        "seed_urls": [
            "https://www.linkedin.com/posts/cyrusshepard_prompt-tracking-seo-rank-tracking-if-activity-7422718426655346688-D0GB",
            "https://www.linkedin.com/posts/cyrusshepard_rant-google-says-good-seo-is-good-geo-activity-7475283116471820288-hL6O",
            "https://www.linkedin.com/posts/cyrusshepard_are-you-tracking-visits-from-googles-ai-activity-7309996662330925057-dsOG",
            "https://www.linkedin.com/posts/cyrusshepard_good-google-is-slowly-adding-links-to-activity-7317593024807518208-wcY6",
        ],
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:80] or "linkedin-post"


def get(url, **kwargs):
    return requests.get(url, headers=HEADERS, timeout=25, **kwargs)


def normalize_post_url(url):
    url = unquote(url.split("?")[0].split("#")[0].rstrip("/"))
    if url.startswith("http://"):
        url = "https://" + url[7:]
    return url


def extract_post_urls(text):
    patterns = [
        r"https://www\.linkedin\.com/posts/[a-zA-Z0-9_-]+(?:_[a-zA-Z0-9_-]+)?-activity-\d+(?:-[a-zA-Z0-9]+)?",
        r"https://www\.linkedin\.com/feed/update/urn:li:activity:\d+",
    ]
    found = []
    for pattern in patterns:
        for match in re.findall(pattern, text):
            found.append(normalize_post_url(match))
    return list(dict.fromkeys(found))


def search_duckduckgo(query, limit=10):
    url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
    response = get(url)
    if response.status_code != 200:
        return []
    decoded = html.unescape(response.text)
    links = extract_post_urls(decoded)
    for wrapped in re.findall(r"uddg=([^&\"']+)", decoded):
        links.extend(extract_post_urls(unquote(wrapped)))
    unique = []
    for link in links:
        if link not in unique:
            unique.append(link)
        if len(unique) >= limit:
            break
    return unique


def search_bing(query, limit=10):
    url = f"https://www.bing.com/search?q={quote(query)}"
    response = get(url)
    if response.status_code != 200:
        return []
    text = html.unescape(response.text)
    links = extract_post_urls(text)
    unique = []
    for link in links:
        if link not in unique:
            unique.append(link)
        if len(unique) >= limit:
            break
    return unique


def post_belongs_to_expert(url, expert):
    lower = url.lower()
    for handle in expert.get("post_handles", [expert["profile"]]):
        if f"/posts/{handle.lower()}_" in lower or f"/posts/{handle.lower()}-" in lower:
            return True
    return False


def activity_id_from_url(url):
    match = re.search(r"activity[-:](\d+)", url)
    return match.group(1) if match else None


def fetch_embed(activity_id):
    embed_url = f"https://www.linkedin.com/embed/feed/update/urn:li:activity:{activity_id}"
    response = get(embed_url)
    if response.status_code != 200:
        return "", embed_url
    return response.text, embed_url


def fetch_post_page(url):
    response = get(url, allow_redirects=True)
    return response.status_code, response.text, response.url


def parse_embed_html(page_html):
    if not page_html:
        return {}
    text = html.unescape(page_html)
    title_match = re.search(r"<title>([^<]+)</title>", text, re.I)
    body_parts = re.findall(r"<p[^>]*>(.*?)</p>", text, re.I | re.S)
    cleaned = []
    for part in body_parts:
        plain = re.sub(r"<[^>]+>", " ", part)
        plain = re.sub(r"\s+", " ", plain).strip()
        if plain and plain.lower() not in {"linkedin", "view profile"}:
            cleaned.append(plain)
    content = "\n\n".join(cleaned).strip()
    author_match = re.search(r'"author"\s*:\s*\{[^}]*"name"\s*:\s*"([^"]+)"', text)
    date_match = re.search(r'"datePublished"\s*:\s*"([^"]+)"', text)
    return {
        "title": title_match.group(1).strip() if title_match else "",
        "author": author_match.group(1) if author_match else "",
        "published": (date_match.group(1)[:10] if date_match else "Unknown"),
        "content": content,
    }


def parse_post_page(page_html):
    if not page_html:
        return {}
    text = html.unescape(page_html)
    ld_matches = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', text, re.I | re.S
    )
    for block in ld_matches:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if item.get("@type") in {"SocialMediaPosting", "Article", "BlogPosting"}:
                article_body = item.get("articleBody") or item.get("description") or ""
                return {
                    "title": item.get("headline") or item.get("name") or "",
                    "author": (item.get("author") or {}).get("name", ""),
                    "published": (item.get("datePublished") or "Unknown")[:10],
                    "content": article_body.strip(),
                }
    og_desc = re.search(r'<meta property="og:description" content="([^"]+)"', text)
    og_title = re.search(r'<meta property="og:title" content="([^"]+)"', text)
    return {
        "title": og_title.group(1) if og_title else "",
        "author": "",
        "published": "Unknown",
        "content": og_desc.group(1) if og_desc else "",
    }


def discover_posts(expert, per_expert=5):
    seen = set()
    posts = []
    for url in expert.get("seed_urls", []):
        url = normalize_post_url(url)
        if url not in seen:
            seen.add(url)
            posts.append(url)
    for query in expert["queries"]:
        for search_fn in (search_duckduckgo, search_bing):
            for url in search_fn(query, limit=per_expert):
                if url in seen:
                    continue
                if not post_belongs_to_expert(url, expert):
                    continue
                seen.add(url)
                posts.append(url)
                if len(posts) >= per_expert:
                    return posts
    return posts[:per_expert]


def collect_post(expert_slug, expert, url):
    activity_id = activity_id_from_url(url)
    method_parts = []
    content = ""
    meta = {"title": "", "author": expert["name"], "published": "Unknown"}
    status = "blocked"

    if activity_id:
        embed_html, embed_url = fetch_embed(activity_id)
        parsed = parse_embed_html(embed_html)
        if parsed.get("content"):
            content = parsed["content"]
            meta.update(parsed)
            method_parts.append("LinkedIn public embed endpoint")
            status = "embed"

    if not content:
        code, page_html, _final_url = fetch_post_page(url)
        parsed = parse_post_page(page_html)
        if parsed.get("content"):
            content = parsed["content"]
            meta.update(parsed)
            method_parts.append(f"Public post page metadata (HTTP {code})")
            status = "page-metadata"
        elif code == 200 and len(page_html) > 1000:
            method_parts.append(f"Post page reachable but text not extractable (HTTP {code})")
            status = "blocked-content"
        else:
            method_parts.append(f"Post page blocked or login required (HTTP {code})")
            status = "blocked"

    title = meta.get("title") or f"LinkedIn post by {expert['name']}"
    if title.lower().startswith("linkedin"):
        title = f"LinkedIn post by {expert['name']}"

    return {
        "title": title,
        "author": meta.get("author") or expert["name"],
        "published": meta.get("published") or "Unknown",
        "url": url,
        "source": expert["linkedin"],
        "method": "; ".join(method_parts) or "Verified public post URL",
        "status": status,
        "content": content,
    }


def write_markdown(expert_slug, item):
    folder = OUT / expert_slug
    folder.mkdir(parents=True, exist_ok=True)
    date_part = item["published"] if item["published"] != "Unknown" else "undated"
    filename = f"{date_part}-{slugify(item['title'])}.md"
    path = folder / filename
    original = item["content"] or (
        "Full post text was not available from public LinkedIn endpoints at collection time. "
        "See the official URL for the original post."
    )
    summary = (
        f"LinkedIn post by {item['author']} on AI search, SEO strategy, or content production. "
        f"Collection status: {item['status']}."
    )
    takeaways = [
        "Review the post for short-form commentary on AI search, SEO workflows, or content strategy.",
        "Cross-reference with long-form sources (YouTube, blogs) from the same expert.",
    ]
    lines = [
        f"Title: {item['title']}",
        f"Author: {item['author']}",
        f"Published: {item['published']}",
        f"URL: {item['url']}",
        f"Source: {item['source']}",
        f"Collection Method: {item['method']}",
        "",
        "## Metadata",
        f"- Expert: {EXPERTS[expert_slug]['name']}",
        "- Platform: LinkedIn",
        f"- Collection Status: {item['status']}",
        "",
        "## Summary",
        summary,
        "",
        "## Key Takeaways",
    ]
    lines.extend(f"- {t}" for t in takeaways)
    lines.extend(["", "## Original Content", original, ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def clean_expert_folder(expert_slug):
    folder = OUT / expert_slug
    if folder.is_dir():
        for file_path in folder.glob("*.md"):
            file_path.unlink()


def main():
    per_expert = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    written = []
    for slug, expert in EXPERTS.items():
        clean_expert_folder(slug)
        urls = discover_posts(expert, per_expert=per_expert)
        print(f"{slug}: collecting {len(urls)} post URLs")
        for url in urls:
            item = collect_post(slug, expert, url)
            if item["status"] == "blocked" and not item["content"]:
                print(f"  [skip blocked] {url}")
                continue
            path = write_markdown(slug, item)
            written.append(path)
            print(f"  [{item['status']}] {path.name}")
    print(f"\nWrote {len(written)} LinkedIn post files")


if __name__ == "__main__":
    main()
