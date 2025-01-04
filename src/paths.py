from pathlib import Path

MAIN_DIR = Path("/app/workspace")
DATA_DIR = "data"

JOURNAL_RAW_FILE_NAME = "Journal_04_09_2024_15_46_57.xlsx"
JOURNAL_RAW_FILE_PATH = MAIN_DIR / DATA_DIR / JOURNAL_RAW_FILE_NAME

PLAN_DE_COMPTE_RAW_FILE_NAME = "plan_comptable_definitions_categorise.xlsx"
PLAN_DE_COMPTE_RAW_FILE_PATH = MAIN_DIR / DATA_DIR / PLAN_DE_COMPTE_RAW_FILE_NAME

EXCEL_OUTPUT_FILE_NAME = "test.xlsx"
EXCEL_OUTPUT_FILE_PATH = MAIN_DIR / DATA_DIR / EXCEL_OUTPUT_FILE_NAME