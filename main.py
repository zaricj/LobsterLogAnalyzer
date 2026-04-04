from pathlib import Path
from utility.pipeline import run_pipeline

if __name__ == "__main__":
    
    PATTERNS_CONFIG = Path("patterns/patterns.json")
    PATTERN_KEY = "sql_exceptions"
    FILE_PATTERN = "*.log"
    LOGS_PATH = Path("logs")
    CSV_FILE = Path("CSV_Results.csv")
    
    # Test run config
    SAMPLE_FILE = Path("sample.log")
    
    #TODO Every single pattern key in patterns.json must contain a regex with multiple groups that will be used to search in an event block in log file.
    #TODO This makes sure that a single line contains all the matches from the same even block
    
    normal_run = run_pipeline(
        patterns_config=PATTERNS_CONFIG,
        pattern_key=PATTERN_KEY,
        files=LOGS_PATH,
        file_pattern=FILE_PATTERN,
        output_csv=CSV_FILE,
        event_keyword=""
    )
