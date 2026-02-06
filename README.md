# GPT-OSS-20B Google Cloud Client

Python client for calling GPT-OSS-20B LLM via Google Cloud Vertex AI MaaS (Model-as-a-Service).

## Installation

### 1. Install Google Cloud CLI

gcloud CLI requires Python 3.10-3.14 available on your system (not related to project venv).

```bash
# Install gcloud CLI (see https://cloud.google.com/sdk/docs/install)

# Initialize and authenticate
gcloud init
gcloud auth application-default login
```

### 2. Enable GPT-OSS API

Enable the GPT-OSS API Service in [Google Cloud Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) for your project.

### 3. Install uv and run the project

[uv](https://github.com/astral-sh/uv) manages Python versions and dependencies automatically.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run directly (uv handles venv and dependencies automatically)
uv run python client.py -t "Hello"
```

## Configuration

Edit `config.py` to set your GCP project settings:

```python
@dataclass
class Config:
    project_id: str = "your-project-id"
    location: str = "us-central1"
    model_id: str = "openai/gpt-oss-20b-maas"
    max_tokens: int = 8192
    temperature: float = 0.7
    top_p: float = 1.0
```

## Usage

### Single Query (CLI)

```bash
# Text prompt
uv run python client.py -t "Explain what Rust ownership is"

# From file
uv run python client.py -f prompt.txt

# Show full API response
uv run python client.py -t "Hello" --all
```

### Single Query (Python)

```python
from client import GPTOSSClient
from config import Config

# Use default config
client = GPTOSSClient()

# Or customize
client = GPTOSSClient(Config(
    project_id="my-project",
    temperature=0.5
))

# Get full response
response = client.query("What is Python?")
print(response.choices[0].message.content)

# Get text only
text = client.get_text("What is Python?")
print(text)
```

### Batch Processing

Process multiple files through the model:

```bash
uv run python batch_processor.py <input_dir> <output_dir> [file_pattern] [num_workers]

# Examples
uv run python batch_processor.py ./code ./output                    # Process *.rs files
uv run python batch_processor.py ./code ./output "**/*.py" 4        # Process *.py with 4 workers
```

Output structure:
```
output/
├── files_found.txt           # List of all processed files
├── processing_log.1.txt      # Worker logs ([PROCESSED], [EMPTY], [ERROR], [GEN_NONE])
├── raw_responses/            # Full API responses
│   └── path/to/file.txt
└── generated_texts/          # Generated text only
    └── path/to/file.json
```

## Testing

Run all usage tests:

```bash
uv run python run_tests.py
```

Or run individual test modules:

```bash
uv run python tests/test_cli.py         # CLI usage tests
uv run python tests/test_python_api.py  # Python API tests
uv run python tests/test_batch.py       # Batch processing tests
```

## Troubleshooting

### DefaultCredentialsError

```
google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found.
```

Run:
```bash
gcloud auth application-default login
```

### Permission Denied

Make sure the GPT-OSS API Service is enabled in Model Garden and your account has access to the project.
