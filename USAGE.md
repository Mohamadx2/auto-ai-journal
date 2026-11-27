# Usage Guide – Auto AI Journal

## Basic operation

```bash
# Install
pip install -r requirements.txt

# First run (foreground – useful to see what it detects)
python -m auto_ai_journal

# Background mode (recommended for daily use)
python -m auto_ai_journal --background
```

The program will create a folder (default: `~/Documents/AutoAIJournal`) and write two files every day:

- `YYYY-MM-DD.md`  → human-readable journal
- `YYYY-MM-DD.json` → machine-readable data

### Example Markdown entry

```markdown
## 2026-11-27

- 1.4 hours browser
- 2.1 hours documents
- 1.5 hours gaming
- 0.8 hours coding
- 0.3 hours communication

**Total tracked active time:** 6.1 hours
```

## Running at startup (Windows)

1. Press `Win + R`, type `shell:startup`, press Enter.
2. Create a shortcut to:
   ```
   pythonw.exe -m auto_ai_journal --background
   ```
   (Use `pythonw` so no console window appears.)

Alternatively use Task Scheduler for more control.

## Enabling AI reflective summary

1. Copy `config.example.yaml` → `config.yaml`
2. Set:
   ```yaml
   ai_summary:
     enabled: true
     provider: openai          # or "xai" / "grok"
     model: gpt-4o-mini
     api_key_env: OPENAI_API_KEY
   ```
3. Export your key:
   ```bash
   export OPENAI_API_KEY=sk-...
   # or for xAI
   export OPENAI_API_KEY=xai-...
   ```

The AI summary will be appended to the Markdown file when generated.

## Cloud / Drive option

Currently the safest and simplest method is a local folder that is already synced by Google Drive, OneDrive, Dropbox, or Syncthing:

```yaml
cloud:
  enabled: true
  provider: local_folder
  path: "~/Google Drive/My Drive/AutoAIJournal"
```

The journal will copy the daily `.md` and `.json` files into that folder. True Google Drive API upload is on the roadmap.

## Customizing categories

Edit the `categories` section in `config.yaml`. The first matching keyword wins. Keywords are matched against both the process name and the window title (case-insensitive).

## Privacy notes

- The tracker only looks at the currently focused window.
- No screenshots, keystrokes, or network traffic are recorded.
- Nothing is sent anywhere unless you turn on the AI summary *and* provide an API key yourself.
- You can delete the entire output folder at any time.
