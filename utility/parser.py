import re
from pathlib import Path
from typing import Dict
from datetime import datetime


# ========== Utility ==========

def yield_event_block(filepath: str | Path, header_pattern: str | re.Pattern):
    """Yields the files event block, using a header/separator pattern

    Args:
        filepath (str | Path): Thefile to read and yield event blocks from
        header_pattern (str | re.Pattern): The pattern to identify the start of an event block

    Yields:
        str: The text block of the event
    """
    
    if isinstance(header_pattern, str):
        header_pattern = re.compile(header_pattern)
        
    buffer = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if header_pattern.match(line):
                if buffer:
                    yield "".join(buffer)
                    buffer.clear()
                    
            # Ignore keywords can be added here, for now the text "at" will be ignored
            #if line.startswith("at"):
            #    continue
            
            buffer.append(line)
            
        if buffer:
            yield "".join(buffer)
            


def extract_event_fields(event_block: str, compiled_patterns: dict) -> Dict[str, str]:
    """Extract fields using compiled regexes

    Args:
        event_block (str): The text block of the event, which contains all the info we  want to extract from
        compiled_patterns (dict): A dictionary of compiled regex patterns

    Returns:
        dict: A dictionary containing the extracted fields
    """
    row = {}

    # Extract base info (time)
    for name, regex in compiled_patterns["base"].items():
        match = regex.search(event_block)
        if match:
            row.update(match.groupdict())

    # Extract specific patterns
    for name, regex in compiled_patterns["patterns"].items():
        match = regex.search(event_block)
        if match:
            row.update(match.groupdict())
        else:
            row[name] = None  # maintain column consistency

    return row


def extract_log_date(filepath: Path) -> str:
    DATE_REGEX = re.compile(
    r"opened at (?P<date>.+?\d{4})"
)
    with open(filepath, "r", encoding="utf-8") as f:
        for _ in range(10):  # only scan first lines (fast)
            line = f.readline()
            if not line:
                break
            
            match = DATE_REGEX.search(line)
            
            if match:
                raw_date = match.group("date")
                # Remove timezone (CET)
                cleaned_date = re.sub(r"\b[A-Z]{3}\b", "", raw_date).strip()

                # Convert to datetime
                dt = datetime.strptime(cleaned_date, "%a %b %d %H:%M:%S %Y")

                # Return ISO date
                return dt.strftime("%Y-%m-%d")

    return ""


def get_csv_headers_from_sample(filename: str | Path, header_regex: re.Pattern, compiled_regex: dict, event_keyword: str = "") -> list[str]:
    headers = set()
    
    if event_keyword == "":
        # Get headers from sample without keyword
        for block in yield_event_block(filename, header_regex):
            row = extract_event_fields(block, compiled_regex)
            headers.update(row.keys())
    else:
        # Get headers from sample with only the matching keyword in the block of text
        for block in yield_event_block(filename, header_regex):
            if not is_keyword_event(event_keyword, block):
                continue
            
            row = extract_event_fields(block, compiled_regex)
            headers.update(row.keys())
    
    print(f"Headers grabbed from sample: {headers}")
    return list(headers)


def is_keyword_event(keyword: str, event_block: str) -> bool:
    """Use this to filter out event blocks that contain a specific keyword

    Args:
        keyword (str): Keyword to look for in event block
        event_block (str): Event text block in the log file

    Returns:
        bool: True if keyword is in the event block, False otherwise
    """
    return keyword.lower() in event_block.lower()


def clean_block(block: str, ignore_regex: re.Pattern) -> str:
    block = ignore_regex.sub("", block)
    block = re.sub(r"\n{2,}", "\n", block)
    return block.strip()
