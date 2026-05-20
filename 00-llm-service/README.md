# 00 - LLM Service

First step of the journey. Foundations of LLM API interaction.

## What's here

- `hello.py` — First Gemini API call. Hello world.
- `classify_email.py` — Email classifier with structured JSON output.
- `tool_use_demo.py` — Augmented LLM with tool use (CRM lookup).

## Stack

- Python 3.12
- Google Gemini API (free tier)
- python-dotenv for environment variables

## Concepts covered

- LLM API basics
- Structured outputs (JSON mode)
- Function calling / tool use
- The agent ping-pong: model decides → code executes → model responds