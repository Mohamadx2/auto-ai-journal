# Auto AI Journal

**Automatic background daily journal / diary that requires zero manual writing.**

It runs quietly in the background, observes what you are actually doing on your computer, and writes dated natural-language log entries for you.

### Example output

```
## 2026-11-27

- 1.4 hours in web browser (research & reading)
- 2.1 hours document editing (Word / LibreOffice / Google Docs)
- 1.5 hours gaming / entertainment
- 0.8 hours coding / development
- 0.3 hours communication (Discord / Slack / email)

Total tracked active time: 6.1 hours
```

You can also enable a lightweight AI summarizer (optional) that turns the raw activity into a short reflective diary paragraph.

---

## Features

- Fully automatic — no typing or manual logging
- Runs in the background (system tray on supported platforms)
- Categorizes activity by application + window title
- Daily Markdown + JSON logs with timestamps
- Optional AI-generated reflective summary
- Optional cloud sync (Google Drive / local folder / any path)
- Cross-platform foundation (Windows primary, Linux & macOS support planned)
- Privacy-first: all data stays local unless you explicitly enable cloud upload

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/Mohamadx2/auto-ai-journal.git
cd auto-ai-journal
pip install -r requirements.txt
```

### 2. Run once (foreground test)

```bash
python -m auto_ai_journal
```

### 3. Run in background (recommended)

```bash
python -m auto_ai_journal --background
```

On Windows you can also create a simple startup shortcut or use Task Scheduler.

### 4. View today's journal

Logs are saved in `~/Documents/AutoAIJournal/` (configurable):

- `2026-11-27.md` — human-readable diary
- `2026-11-27.json` — structured data

---

## Configuration

Copy `config.example.yaml` → `config.yaml` and edit:

```yaml
# How often to sample the active window (seconds)
poll_interval: 5

# Minimum continuous time in an app before it is counted (seconds)
min_session_seconds: 15

# Categories (process name / window title keywords → friendly name)
categories:
  browser:
    - chrome
    - firefox
    - edge
    - brave
    - safari
  documents:
    - winword
    - excel
    - powerpnt
    - libreoffice
    - soffice
    - googledocs
    - notion
  coding:
    - code
    - pycharm
    - idea
    - cursor
    - terminal
    - cmd
    - powershell
  gaming:
    - steam
    - epicgameslauncher
    - discord  # can also be communication
  communication:
    - discord
    - slack
    - teams
    - outlook
    - thunderbird

# Output location
output_dir: "~/Documents/AutoAIJournal"

# Optional AI summary (requires OpenAI-compatible API key)
ai_summary:
  enabled: false
  provider: openai          # or "local" / "grok" etc.
  model: gpt-4o-mini
  api_key_env: OPENAI_API_KEY

# Cloud / Drive sync (optional)
cloud:
  enabled: false
  provider: local_folder    # or "google_drive" (coming soon)
  path: "~/Google Drive/AutoAIJournal"
```

---

## How it works (high level)

1. A lightweight background process polls the currently active window every few seconds.
2. It maps the process name + window title to a category.
3. Time is accumulated only while the window stays active above a minimum threshold.
4. At the end of each day (or on demand) a clean Markdown entry is written.
5. Optionally an LLM turns the raw numbers into a short reflective paragraph.
6. Files can be copied/synced to any folder or cloud location you configure.

---

## Privacy & Security

- No data leaves your machine by default.
- Window titles and process names never leave your computer unless you enable AI summary *and* cloud features yourself.
- You control the output directory and can delete logs at any time.

---

## Roadmap

- [x] Core activity sampling + categorization
- [x] Daily Markdown + JSON journals
- [ ] System tray icon + pause/resume
- [ ] Proper Windows service / auto-start
- [ ] Google Drive upload (OAuth)
- [ ] Better macOS & Linux support
- [ ] Local LLM option (Ollama / llama.cpp)
- [ ] Weekly / monthly reflective summaries
- [ ] Export to Notion / Obsidian

---

## Contributing

Pull requests are welcome. Please keep the spirit of the project: **zero friction, maximum privacy, automatic by default**.

---

## License

MIT
