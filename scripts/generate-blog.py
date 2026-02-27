#!/usr/bin/env python3
"""
MFS Daily Blog Post Generator
Calls the Anthropic API to generate a brand-aligned blog post,
saves the Markdown source, renders an HTML page from the site template,
updates the blog index and sitemap so the post appears on the website.
"""

import os
import sys
import json
import math
import random
from datetime import date
from pathlib import Path

import anthropic
import markdown

# ── Config ──────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BRAND_VOICE_PATH = SCRIPT_DIR / "brand-voice.md"
BLOG_DIR = REPO_ROOT / "blog"
POSTS_DIR = BLOG_DIR / "posts"
POSTS_JSON = BLOG_DIR / "posts.json"
TEMPLATE_PATH = BLOG_DIR / "_template.html"
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048

# Default social sharing image (MFS brand image, 1200x630)
DEFAULT_OG_IMAGE = "https://cdn.shopify.com/s/files/1/0561/0530/4256/files/Untitled_design_19.png?v=1772057565"

# Default CTA content (consistent across all posts)
CTA_LABEL = "Ready to Switch?"
CTA_HEADING = 'See If MFS Is the Right <span style="color: var(--color-teal)">Fit.</span>'
CTA_TEXT = "We partner with growth-focused eCommerce brands that demand speed, precision, and transparency from their fulfillment operations."

# Topic pool — the script picks one at random each day.
# Add/remove topics whenever you want to steer the content calendar.
TOPICS = [
    "The hidden costs of slow fulfillment and how faster shipping improves customer LTV",
    "When a DTC brand should outsource fulfillment — the revenue benchmarks and warning signs",
    "How order accuracy directly impacts your brand's reviews and repeat purchase rate",
    "Peak season fulfillment prep: what smart DTC brands do 90 days before Q4",
    "Why boutique 3PLs outperform mega-warehouses for brands doing $100K-$2M/month",
    "The real cost of fulfillment errors — returns, refunds, and lost customers",
    "Subscription box fulfillment: the operational challenges most brands underestimate",
    "How shipping speed became the #1 driver of e-commerce customer satisfaction",
    "Red flags to watch for when evaluating a new 3PL partner",
    "The math behind free shipping: when it makes sense and when it kills your margins",
    "How influencer drops and flash sales break unprepared fulfillment operations",
    "Carrier diversification: why relying on one shipping carrier is a risk",
    "Packaging optimization — how the right box size saves thousands per year",
    "What DTC brands get wrong about fulfillment SLAs (and what to actually negotiate)",
    "Behind the scenes: how a 99.9% accuracy rate is maintained at scale",
    "Fulfillment as a competitive moat — why ops excellence wins in DTC",
    "The founder's guide to reading a 3PL invoice (and spotting hidden fees)",
    "How same-day fulfillment changes the customer experience for DTC brands",
    "Returns processing: the fulfillment step most 3PLs get wrong",
    "Why your 3PL should feel like an extension of your team, not a vendor",
    "Kitting and assembly: how custom packaging builds brand loyalty",
    "The impact of warehouse location on shipping speed and cost",
    "How to evaluate fulfillment performance — the 5 metrics that actually matter",
    "Scaling from self-fulfillment to a 3PL without losing control",
    "International shipping for DTC brands: when to expand and how to start",
    "How real-time inventory visibility prevents overselling and stockouts",
    "The link between fast fulfillment and lower customer acquisition costs",
    "Why transparency in fulfillment pricing builds long-term brand partnerships",
    "Seasonal inventory planning: avoiding dead stock without missing demand",
    "What a great unboxing experience actually requires from your 3PL",
]


def load_brand_voice() -> str:
    """Read the brand voice guide from disk."""
    return BRAND_VOICE_PATH.read_text()


def pick_topic(today: date) -> str:
    """Pick a topic. Uses the date as seed so re-runs on the same day get the same topic."""
    rng = random.Random(today.toordinal())
    return rng.choice(TOPICS)


def already_posted_today(today: date) -> bool:
    """Check if a fully published post already exists for today."""
    slug_prefix = today.isoformat()
    has_markdown = any(f.name.startswith(slug_prefix) for f in POSTS_DIR.glob("*.md"))
    if not has_markdown:
        return False
    # Also verify it's in posts.json (i.e. fully published)
    posts = json.loads(POSTS_JSON.read_text()) if POSTS_JSON.exists() else []
    return any(p["date"] == slug_prefix for p in posts)


def generate_post(brand_voice: str, topic: str) -> dict:
    """Call the Anthropic API to generate a blog post."""
    client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var

    system_prompt = f"""You are the content writer for MFS (Mully Fulfillment Services).
Your job is to write a single blog post that will be published on the MFS website.

Here is the brand voice guide you MUST follow:

<brand-voice>
{brand_voice}
</brand-voice>

Output ONLY valid JSON with these keys:
- "title": the blog post title (compelling, SEO-friendly, under 70 chars)
- "meta_description": under 160 characters, for SEO
- "primary_keyword": the main SEO keyword targeted
- "tag": a short category label for the post (1-3 words, e.g. "Fulfillment", "3PL Guide", "Shipping", "DTC Strategy", "Warehouse Ops")
- "excerpt": a 1-2 sentence teaser for the blog index card (under 200 chars)
- "body": the full blog post in Markdown (use ## for subheadings, no H1)
- "slug": a URL-friendly slug derived from the title (lowercase, hyphens, no special chars)

Do NOT include any text outside the JSON object."""

    user_prompt = f"Write a blog post about: {topic}"

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Extract the text response
    raw = message.content[0].text.strip()

    # Handle potential markdown code fences around JSON
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]  # remove opening fence line
        raw = raw.rsplit("```", 1)[0]  # remove closing fence

    return json.loads(raw)


def save_post(today: date, post: dict) -> Path:
    """Save the generated post as a dated Markdown file."""
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = post.get("slug", "untitled")
    filename = f"{today.isoformat()}-{slug}.md"
    filepath = POSTS_DIR / filename

    content = f"""---
title: "{post['title']}"
date: {today.isoformat()}
meta_description: "{post['meta_description']}"
primary_keyword: "{post['primary_keyword']}"
tag: "{post.get('tag', 'Fulfillment')}"
excerpt: "{post.get('excerpt', post['meta_description'])}"
---

{post['body']}
"""
    filepath.write_text(content)
    return filepath


def format_date_display(today: date) -> str:
    """Format date for display, e.g. 'February 27, 2026'."""
    return today.strftime("%B %d, %Y").replace(" 0", " ")


def calculate_read_time(text: str) -> int:
    """Estimate reading time in minutes (assumes ~230 wpm)."""
    words = len(text.split())
    return max(1, math.ceil(words / 230))


def render_html_page(today: date, post: dict) -> Path:
    """Render the blog post HTML page from the template."""
    template = TEMPLATE_PATH.read_text()
    slug = post.get("slug", "untitled")

    # Convert markdown body to HTML
    md = markdown.Markdown(extensions=["extra"])
    body_html = md.convert(post["body"])

    # Fill template placeholders
    html = template
    html = html.replace("{{SLUG}}", slug)
    html = html.replace("{{TITLE}}", post["title"])
    html = html.replace("{{TAG}}", post.get("tag", "Fulfillment"))
    html = html.replace("{{DATE}}", today.isoformat())
    html = html.replace("{{DATE_DISPLAY}}", format_date_display(today))
    html = html.replace("{{READ_TIME}}", str(calculate_read_time(post["body"])))
    html = html.replace("{{META_DESCRIPTION}}", post["meta_description"])
    html = html.replace("{{BODY_HTML}}", body_html)
    html = html.replace("{{OG_IMAGE}}", DEFAULT_OG_IMAGE)
    html = html.replace("{{CTA_LABEL}}", CTA_LABEL)
    html = html.replace("{{CTA_HEADING}}", CTA_HEADING)
    html = html.replace("{{CTA_TEXT}}", CTA_TEXT)

    # Write to blog/{slug}/index.html
    page_dir = BLOG_DIR / slug
    page_dir.mkdir(parents=True, exist_ok=True)
    page_path = page_dir / "index.html"
    page_path.write_text(html)
    return page_path


def update_posts_index(today: date, post: dict):
    """Add the new post to posts.json so it appears on the blog index."""
    posts = json.loads(POSTS_JSON.read_text()) if POSTS_JSON.exists() else []

    slug = post.get("slug", "untitled")

    # Don't add duplicate entries
    if any(p["slug"] == slug for p in posts):
        return

    posts.append({
        "slug": slug,
        "title": post["title"],
        "excerpt": post.get("excerpt", post["meta_description"]),
        "date": today.isoformat(),
        "tag": post.get("tag", "Fulfillment"),
    })

    # Sort newest first
    posts.sort(key=lambda p: p["date"], reverse=True)

    POSTS_JSON.write_text(json.dumps(posts, indent=2) + "\n")


def update_sitemap(today: date, post: dict):
    """Add the new post to sitemap.xml and update lastmod dates."""
    slug = post.get("slug", "untitled")
    post_url = f"https://mullyfulfillment.com/blog/{slug}"
    today_str = today.isoformat()

    # Read existing sitemap
    if SITEMAP_PATH.exists():
        content = SITEMAP_PATH.read_text()
    else:
        content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>\n'

    # Don't add duplicate entries
    if post_url in content:
        return

    # Build the new <url> entry
    new_entry = f"""  <url>
    <loc>{post_url}</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>"""

    # Insert before closing </urlset>
    content = content.replace("</urlset>", f"{new_entry}\n</urlset>")

    # Update blog index lastmod to today
    import re
    content = re.sub(
        r"(<loc>https://mullyfulfillment\.com/blog/</loc>\s*<lastmod>)\d{4}-\d{2}-\d{2}(</lastmod>)",
        rf"\g<1>{today_str}\2",
        content,
    )

    SITEMAP_PATH.write_text(content)


def main():
    today = date.today()

    # Don't double-post
    if already_posted_today(today):
        print(f"Post already exists for {today}. Skipping.")
        sys.exit(0)

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        sys.exit(1)

    brand_voice = load_brand_voice()
    topic = pick_topic(today)

    print(f"Date:  {today}")
    print(f"Topic: {topic}")
    print("Generating post...")

    post = generate_post(brand_voice, topic)

    # 1. Save markdown source
    filepath = save_post(today, post)
    print(f"Saved markdown: {filepath}")

    # 2. Render HTML page
    page_path = render_html_page(today, post)
    print(f"Rendered HTML:  {page_path}")

    # 3. Update blog index
    update_posts_index(today, post)
    print(f"Updated index:  {POSTS_JSON}")

    # 4. Update sitemap
    update_sitemap(today, post)
    print(f"Updated sitemap: {SITEMAP_PATH}")

    print(f"Title: {post['title']}")
    print("Post published successfully.")

    # Write outputs for GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"filepath={filepath}\n")
            f.write(f"title={post['title']}\n")
            f.write(f"slug={post.get('slug', 'untitled')}\n")


if __name__ == "__main__":
    main()
