#!/usr/bin/env python3
"""
Download images from LinkedIn posts referenced in .md files.
"""

import html
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
LINKEDIN_POSTS_ROOT = ROOT / "research" / "linkedin-posts"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def get(url, **kwargs):
    # Remove default timeout to avoid conflicts
    return requests.get(url, headers=HEADERS, **kwargs)


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


def parse_images_from_html(page_html, base_url):
    """Extract image URLs from HTML."""
    if not page_html:
        return []
    text = html.unescape(page_html)
    # Find <img> tags
    img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', text, re.I)
    # Also look for og:image
    og_images = re.findall(r'<meta property="og:image" content=["\']([^"\']+)["\']', text, re.I | re.S)
    # Combine
    urls = img_tags + og_images
    # Make absolute
    absolute_urls = []
    for url in urls:
        if not url:
            continue
        absolute = urljoin(base_url, url)
        absolute_urls.append(absolute)
    return absolute_urls


def download_image(img_url, folder):
    """Download a single image, return saved path or None."""
    try:
        resp = get(img_url, stream=True, timeout=15)
        if resp.status_code != 200:
            print(f"    Failed to download {img_url}: HTTP {resp.status_code}")
            return None
        # Determine filename from URL or content-type
        parsed = urlparse(img_url)
        filename = Path(parsed.path).name
        if not filename or '.' not in filename:
            # Guess extension from content-type
            content_type = resp.headers.get('content-type', '').split(';')[0]
            ext = ''
            if content_type == 'image/jpeg':
                ext = '.jpg'
            elif content_type == 'image/png':
                ext = '.png'
            elif content_type == 'image/gif':
                ext = '.gif'
            elif content_type == 'image/webp':
                ext = '.webp'
            else:
                ext = '.jpg'  # default
            # Use activity id or hash
            filename = f"image{ext}"
        # Ensure unique filename
        counter = 1
        stem = Path(filename).stem
        suffix = Path(filename).suffix
        while (folder / filename).exists():
            filename = f"{stem}_{counter}{suffix}"
            counter += 1
        # Save
        out_path = folder / filename
        with open(out_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"    Saved image: {out_path.name}")
        return out_path
    except Exception as e:
        print(f"    Error downloading {img_url}: {e}")
        return None


def process_md_file(md_path):
    """Process a single .md file: extract URL, fetch post, download images."""
    print(f"Processing {md_path.relative_to(ROOT)}")
    try:
        content = md_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  Could not read file: {e}")
        return
    # Find URL line
    url_match = re.search(r'^URL:\s*(https?://\S+)', content, re.M)
    if not url_match:
        print(f"  No URL found in {md_path.name}")
        return
    url = url_match.group(1).strip()
    print(f"  URL: {url}")
    url = normalize_post_url(url)
    # Get activity id
    activity_id = activity_id_from_url(url)
    html_content = ""
    final_url = url
    if activity_id:
        embed_html, embed_url = fetch_embed(activity_id)
        if embed_html:
            html_content = embed_html
            final_url = embed_url
        else:
            print(f"  Embed failed, trying post page")
    if not html_content:
        code, page_html, final_url = fetch_post_page(url)
        if code == 200 and page_html:
            html_content = page_html
        else:
            print(f"  Could not fetch post page (HTTP {code})")
            return
    # Extract images
    img_urls = parse_images_from_html(html_content, final_url)
    if not img_urls:
        print(f"  No images found")
        return
    print(f"  Found {len(img_urls)} image(s)")
    # Download each image
    folder = md_path.parent
    for img_url in img_urls:
        download_image(img_url, folder)


def main():
    # Find all .md files in research/linkedin-posts/*/
    md_files = list(LINKEDIN_POSTS_ROOT.glob('*/*.md'))
    if not md_files:
        print(f"No .md files found in {LINKEDIN_POSTS_ROOT}")
        return
    print(f"Found {len(md_files)} .md files")
    for md_file in md_files:
        process_md_file(md_file)
        print()


if __name__ == "__main__":
    main()