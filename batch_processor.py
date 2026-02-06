"""Batch processor for running GPT-OSS-20B on multiple files."""

import os
import sys
from functools import partial
from multiprocessing import Pool, Value, Lock
from pathlib import Path

from tqdm import tqdm

from client import GPTOSSClient
from config import Config


class BatchConfig:
    """Configuration for batch processing."""

    def __init__(self, input_dir: str, output_dir: str, file_pattern: str = "**/*.rs"):
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.file_pattern = file_pattern
        self.raw_dir = self.output_dir / "raw_responses"
        self.generated_dir = self.output_dir / "generated_texts"

        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.generated_dir, exist_ok=True)


def init_worker(counter, lock):
    """Initialize worker with unique ID."""
    global WORKER_ID
    with lock:
        counter.value += 1
        WORKER_ID = counter.value


def process_file(batch_config: BatchConfig, input_filepath: Path) -> int:
    """Process a single file through the model."""
    global WORKER_ID
    idx = WORKER_ID

    client = GPTOSSClient()
    log_path = batch_config.output_dir / f"processing_log.{idx}.txt"

    with open(input_filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"[EMPTY] {input_filepath.relative_to(batch_config.input_dir)}\n")
        return idx

    relative_path = input_filepath.relative_to(batch_config.input_dir)
    filename = input_filepath.stem

    raw_path = batch_config.raw_dir / relative_path.parent / f"{filename}.txt"
    gen_path = batch_config.generated_dir / relative_path.parent / f"{filename}.json"

    os.makedirs(raw_path.parent, exist_ok=True)
    os.makedirs(gen_path.parent, exist_ok=True)

    try:
        response = client.query(content)
    except Exception as e:
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"[ERROR] {relative_path}: {e}\n")
        return idx

    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(str(response))

    generated_text = response.choices[0].message.content
    if generated_text:
        with open(gen_path, "w", encoding="utf-8") as f:
            f.write(generated_text)
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"[PROCESSED] {relative_path}\n")
    else:
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"[GEN_NONE] {relative_path}\n")

    return idx


def run_batch(input_dir: str, output_dir: str, file_pattern: str = "**/*.rs", num_workers: int = 1):
    """Run batch processing on all matching files."""
    batch_config = BatchConfig(input_dir, output_dir, file_pattern)

    files = list(batch_config.input_dir.glob(file_pattern))
    print(f"Found {len(files)} files matching '{file_pattern}'")

    with open(batch_config.output_dir / "files_found.txt", "w", encoding="utf-8") as f:
        for filepath in files:
            f.write(str(filepath) + "\n")

    counter = Value('i', 0)
    lock = Lock()

    with Pool(processes=num_workers, initializer=init_worker, initargs=(counter, lock)) as pool:
        func = partial(process_file, batch_config)
        for _ in tqdm(pool.imap_unordered(func, files), total=len(files)):
            pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch_processor.py <input_dir> <output_dir> [file_pattern] [num_workers]")
        print("  file_pattern: glob pattern (default: **/*.rs)")
        print("  num_workers: number of parallel workers (default: 1)")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    file_pattern = sys.argv[3] if len(sys.argv) > 3 else "**/*.rs"
    num_workers = int(sys.argv[4]) if len(sys.argv) > 4 else 1

    run_batch(input_dir, output_dir, file_pattern, num_workers)
