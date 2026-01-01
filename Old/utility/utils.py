import re
import json
from pathlib import Path

# ---------- Load & Compile Patterns ----------
def load_patterns_json(filepath: Path) -> dict:
    with filepath.open("r", encoding="utf-8") as f:
        return json.load(f)


def compile_regex(pattern: str, flags=0):
    return re.compile(pattern, flags)


def compile_regex_dict(patterns_dict: dict):
    return {
        name: re.compile(pattern, re.MULTILINE | re.DOTALL)
        for name, pattern in patterns_dict.items()
    }
    
# ---------- Utility ----------
def read_log_file(filepath: Path):
    with filepath.open("r", encoding="utf-8") as f:
        return f.read()


def clean_block(block: str, ignore_regex: re.Pattern) -> str:
    block = ignore_regex.sub("", block)
    block = re.sub(r"\n{2,}", "\n", block)
    return block.strip()