#!/usr/bin/env python3
"""
MFS Daily Blog Post Generator
Calls the Anthropic API to generate a brand-aligned blog post,
then saves it as a dated Markdown file in blog/posts/.
"""

import os
import sys
import json
import random
from datetime import date
from pathlib import Path

import anthropic

# ── Config ──────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BRAND_VOICE_PATH = SCRIPT_DIR / "brand-voice.md"
POSTS_DIR = REPO_ROOT / "blog" / "posts"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048

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
    """Check if a post already exists for today."""
    slug = today.isoformat()  # e.g. 2026-02-27
    return any(f.name.startswith(slug) for f in POSTS_DIR.glob("*.md"))


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
---

{post['body']}
"""
    filepath.write_text(content)
    return filepath


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

    filepath = save_post(today, post)
    print(f"Saved: {filepath}")
    print(f"Title: {post['title']}")

    # Write outputs for GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"filepath={filepath}\n")
            f.write(f"title={post['title']}\n")
            f.write(f"slug={post.get('slug', 'untitled')}\n")


if __name__ == "__main__":
    main()
