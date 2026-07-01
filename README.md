# Portfolio Project Setup

## Overview

This repository documents the setup process requested as part of the portfolio project.

The purpose of this project was to install modern AI-assisted development tools, create a GitHub repository, and document the entire setup process.

---

## Tools Installed

### Cursor IDE

- Installed the latest version of Cursor IDE
- Logged into Cursor successfully

### Claude Code Extension

- Installed using the Extensions marketplace
- Logged into Claude Code

### Codex Extension

- Installed using the Extensions marketplace
- Logged into Codex

### Git

- Used Git for version control

### GitHub

- Created a public GitHub repository
- Connected the local repository with GitHub

---

## Steps Completed

1. Installed Cursor IDE
2. Logged into Cursor
3. Installed Claude Code extension
4. Logged into Claude Code
5. Installed Codex extension
6. Logged into Codex
7. Created a public GitHub repository
8. Opened the repository in Cursor
9. Created this README.md file
10. Committed the project
11. Pushed the project to GitHub successfully

---

## Issues Encountered

### Issue 1

Git was not configured with my username and email.

Solution:

Configured Git using:

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### Issue 2

Initially I was unfamiliar with cloning a repository inside Cursor.

Solution:

Used the GitHub repository URL and cloned the repository directly through Cursor.

### Issue 3

At first, i didnt know how Git commits and pushes work.

Solution:

Learned how Git commits and pushes work using Cursor.
Used Cursor's built-in Git interface to stage changes, commit, and push to GitHub.

# Step Two:

# AI-Powered SEO Content Production Research Database

This repository is a portfolio research project on how industry experts use AI to create, optimize, and scale SEO content. It is designed as a structured evidence base for a future AI SEO playbook.

## Why This Topic

AI-powered search is changing how content is discovered, cited, and evaluated. The project focuses on practitioners who publish concrete guidance about AI Overviews, AEO/GEO, topical authority, content optimization, and scalable production workflows.

## Research Methodology

Collection prioritizes official and legitimate sources: YouTube channels, YouTube public caption endpoints, official RSS feeds, WordPress REST APIs, official blogs, conference talks, podcasts, and LinkedIn posts collected through verified public post URLs and LinkedIn embed endpoints.

## Experts Researched

- Matt Diggity
- Nathan Gotch
- Koray Tugberk Gubur
- Lily Ray
- Aleyda Solis
- Gael Breton
- Mark Webster
- Mike King
- Bernard Huang
- Cyrus Shepard

## Repository Structure

- `research/sources.md`: expert profiles and source annotations
- `research/youtube-transcripts/`: YouTube metadata and transcripts
- `research/linkedin-posts/`: LinkedIn posts collected via public embed endpoints
- `research/blogs/`: blog and article records
- `research/podcasts/`: podcast, interview, and conference talk records
- `research/other/`: reserved for datasets, reports, and additional source types
- `research_tools/`: reproducible collection scripts

## Data Collection Workflow

1. Resolve official expert/source channels.
2. Collect YouTube metadata from official RSS or public search where necessary.
3. Extract transcripts from YouTube timedtext captions with Innertube metadata fallback.
4. Collect blog metadata from official RSS and WordPress REST APIs where available.
5. Collect LinkedIn posts from verified public post URLs and LinkedIn embed endpoints.
6. Store every resource as markdown with title, date, URL, source, author, metadata, and collection method.

## Tools Used

- YouTube Transcript API-style public caption extraction
- Official RSS feeds
- Official WordPress REST APIs
- LinkedIn public embed endpoint extraction
- Git
- Claude Code
- Cursor
- Markdown

## Future Work

- Add authenticated YouTube Data API support when an API key is available.
- Import additional LinkedIn posts through approved exports, official APIs, or user-provided post URLs.
- Expand summaries into reusable playbook patterns.
- Build a complete AI SEO playbook from the collected evidence.
