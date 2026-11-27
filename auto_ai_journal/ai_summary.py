"""
Optional AI reflective summary.

This module is deliberately minimal. It only runs when the user explicitly
enables it in config.yaml and provides an API key. All data stays local
unless the user chooses otherwise.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional


def generate_summary(
    activity: Dict[str, float],
    config: dict,
) -> Optional[str]:
    """
    Turn raw seconds-per-category into a short first-person diary paragraph.
    Returns None if AI is disabled or the call fails.
    """
    ai_cfg = config.get("ai_summary", {})
    if not ai_cfg.get("enabled", False):
        return None

    # Build a clean activity string
    lines = []
    for cat, secs in sorted(activity.items(), key=lambda x: -x[1]):
        hours = secs / 3600
        if hours >= 0.05:
            lines.append(f"- {hours:.1f} hours {cat.replace('_', ' ')}")
    activity_text = "\n".join(lines) or "No significant activity recorded."

    template = ai_cfg.get(
        "prompt_template",
        "Write a short reflective diary entry based on this activity:\n{activity}",
    )
    prompt = template.format(activity=activity_text)

    provider = ai_cfg.get("provider", "openai").lower()
    model = ai_cfg.get("model", "gpt-4o-mini")
    api_key_env = ai_cfg.get("api_key_env", "OPENAI_API_KEY")
    api_key = os.environ.get(api_key_env)

    if not api_key:
        return None

    try:
        if provider in ("openai", "grok", "xai"):
            # Works with OpenAI-compatible endpoints (including xAI/Grok)
            from openai import OpenAI

            base_url = None
            if provider in ("grok", "xai"):
                base_url = "https://api.x.ai/v1"

            client = OpenAI(api_key=api_key, base_url=base_url)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You write calm, factual, first-person diary entries. No judgment, no fluff.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.6,
            )
            return response.choices[0].message.content.strip()

        # Future: local Ollama, etc.
        return None
    except Exception:
        return None
