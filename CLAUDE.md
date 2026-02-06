# Claude Code Instructions

## Project Overview

This is a Python client for calling GPT-OSS-20B LLM via Google Cloud Vertex AI MaaS.

## Key Files

- `config.py` - Configuration dataclass with GCP settings and model parameters
- `client.py` - GPTOSSClient class for API calls, also works as CLI
- `batch_processor.py` - Parallel batch processing for multiple files
- `pyproject.toml` - Project dependencies

## Important Rules

1. **Always update README.md** when making changes to:
   - New features or CLI options
   - Configuration changes
   - New files or modules
   - Installation or usage instructions
   - API changes

2. **Configuration** - Default project_id is "YOUR-PROJECT-ID". Users must set their own.

3. **Dependencies** - Use `uv` for package management. Add new dependencies to `pyproject.toml`.

4. **Code Style** - Keep code simple and focused. Use type hints.

## Running the Project

```bash
uv venv && source .venv/bin/activate
uv pip install -e .
python client.py -t "test prompt"
```
