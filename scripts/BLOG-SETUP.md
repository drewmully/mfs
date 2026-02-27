# MFS Daily Blog Generator — Setup Guide

## What This Does
Every day at **7:00 AM EST**, a GitHub Action automatically:
1. Picks a topic from a pool of 30 fulfillment/DTC topics
2. Calls the Claude API to write a brand-aligned blog post
3. Saves it as a Markdown file in `blog/posts/`
4. Commits and pushes it to the repo

Posts follow the MFS brand voice defined in `scripts/brand-voice.md`.

## One-Time Setup (takes ~2 minutes)

### 1. Get an Anthropic API Key
- Go to [console.anthropic.com](https://console.anthropic.com/)
- Create an account or sign in
- Go to **API Keys** → **Create Key**
- Copy the key (starts with `sk-ant-...`)

### 2. Add the Key to GitHub Secrets
- Go to your repo on GitHub
- **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret**
- Name: `ANTHROPIC_API_KEY`
- Value: paste your API key
- Click **Add secret**

### 3. That's It
The workflow will run automatically every morning. Posts appear in `blog/posts/`.

## Manual Trigger
Want a post right now?
- Go to **Actions** → **Daily Blog Post** → **Run workflow**

## Customization

### Change the Schedule
Edit `.github/workflows/daily-blog.yml` and update the cron expression:
```yaml
schedule:
  - cron: "0 12 * * *"  # 12:00 UTC = 7:00 AM EST
```

### Change Topics
Edit the `TOPICS` list in `scripts/generate-blog.py`. Add or remove topics anytime.

### Change Brand Voice
Edit `scripts/brand-voice.md`. The entire file is fed to Claude as writing instructions.

### Change the AI Model
Edit the `MODEL` variable in `scripts/generate-blog.py`. Default is `claude-sonnet-4-6`.

## Cost
Each post uses roughly 2,000-3,000 tokens (~$0.02-0.04 per post with Sonnet). Running daily, that's about **$1/month**.

## File Structure
```
scripts/
  generate-blog.py     # Generation script
  brand-voice.md       # Brand voice & writing guidelines
  BLOG-SETUP.md        # This file
blog/
  posts/               # Generated posts land here
    2026-02-27-your-post-slug.md
.github/
  workflows/
    daily-blog.yml     # The cron workflow
```
