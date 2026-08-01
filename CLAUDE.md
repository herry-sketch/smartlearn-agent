# SmartLearn Agent

## Project

SmartLearn Agent is an AI-powered learning assistant that helps students read PDF documents, summarize content, and ask questions based on supplied evidence.

## Tech Stack

- Python 3.12
- OpenRouter API
- Google Gemma 4 free model
- python-dotenv
- OpenAI-compatible Python SDK
- Git and GitHub

## AI Coding Environment

- Claude Code is the AI coding tool used during development.
- Claude Code connects directly to DeepSeek through `ANTHROPIC_BASE_URL`.
- The Python application connects to OpenRouter separately.
- Claude Code and the Python application use different API keys.

## Conventions

- Write beginner-friendly Python code.
- Use clear function names and short functions.
- Read secrets from environment variables.
- Never put API keys directly in source code.
- Make one focused change at a time.
- Explain changes before making large modifications.
- Run a syntax check after modifying Python files.
- Review `git diff` before every commit.

## Security Rules

- Read `OPENROUTER_API_KEY` from `.env`.
- Never print, reveal, commit, or modify API keys.
- Confirm that `.env` remains ignored by Git.
- Do not send empty input to an AI API.

## Do Not Modify

- `.env`
- `venv/`
- `.git/`
- API keys or authentication settings
- Unrelated files outside the requested task

## Testing

Run syntax checks with:

```bash
python -m py_compile <python-file>
