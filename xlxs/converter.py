import sys
import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse
import requests
import pandas as pd

def is_google_sheets_url(s: str) -> bool:
    return "docs.google.com/spreadsheets" in s

def google_sheets_export_xlsx_url(share_url: str) -> str:
    """
    Convert common Google Sheets share URL to export URL:
    https://docs.google.com/spreadsheets/d/<SHEET_ID>/... -> 
    https://docs.google.com/spreadsheets/d/<SHEET_ID>/export?format=xlsx
    """
    # Try parse /d/<id>/
    m = re.search(r"/d/([a-zA-Z0-9-_]+)", share_url)
    if not m:
        raise ValueError("Couldn't find sheet ID in the Google Sheets URL.")
    sheet_id = m.group(1)
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    return export_url

def download_to_tempfile(url: str, suffix: str = ".xlsx") -> Path:
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    # save to a temp file and return its path
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    with tmp as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return Path(tmp.name)

def sanitize_filename(name: str, max_len: int = 200) -> str:
    # remove path separators and control chars
    name = re.sub(r"[\\/*?<>|:\"']", "", name)
    name = name.strip()
    return name[:max_len]

def get_output_dir_from_input(input_path_or_name: str) -> Path:
    # If it looks like a filename, use stem; else sanitize the input string
    p = Path(input_path_or_name)
    if p.suffix:
        folder = p.stem
    else:
        folder = sanitize_filename(p.name if hasattr(p, "name") else input_path_or_name)
    if not folder:
        folder = "output"
    return Path(folder)

def convert_xlsx_all_sheets_to_csv(xlsx_path: Path, output_dir: Path):
    # read all sheets
    # header row is assumed to be the first row -> pandas default header=0
    xlsx_path = xlsx_path.resolve()
    print(f"Reading: {xlsx_path}")
    try:
        sheets = pd.read_excel(xlsx_path, sheet_name=None, engine="openpyxl")
    except Exception as e:
        raise RuntimeError(f"Failed to read xlsx file: {e}")

    output_dir.mkdir(parents=True, exist_ok=True)
    for sheet_name, df in sheets.items():
        safe_sheet = sanitize_filename(sheet_name) or "Sheet"
        csv_filename = f"{safe_sheet}.csv"
        out_path = output_dir / csv_filename
        # write with utf-8-sig so Excel opens UTF-8 CSV properly on Windows
        try:
            df.to_csv(out_path, index=False, encoding="utf-8-sig")
            print(f"Wrote: {out_path}  (rows: {len(df)}, cols: {len(df.columns)})")
        except Exception as e:
            print(f"Failed to write {out_path}: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python converter.py google_sheet_link_or_local_xlsx_path")
        sys.exit(2)

    inp = sys.argv[1]

    temp_file = None
    try:
        if is_google_sheets_url(inp):
            try:
                export_url = google_sheets_export_xlsx_url(inp)
            except ValueError as e:
                print("Error parsing Google Sheets URL:", e)
                sys.exit(1)
            print("Detected Google Sheets URL. Downloading .xlsx export...")
            temp_path = download_to_tempfile(export_url)
            temp_file = temp_path  # mark to delete later
            input_basename = Path(temp_path.name).stem
            output_dir = get_output_dir_from_input(input_basename)
            convert_xlsx_all_sheets_to_csv(temp_path, output_dir)
        else:
            # assume local path
            p = Path(inp)
            if not p.exists():
                print(f"Local file not found: {p}")
                sys.exit(1)
            if p.suffix.lower() not in [".xlsx", ".xlsm", ".xltx", ".xltm"]:
                print(f"Warning: file extension {p.suffix} is unusual for an xlsx file, continuing anyway.")
            output_dir = get_output_dir_from_input(p)
            convert_xlsx_all_sheets_to_csv(p, output_dir)
    except requests.HTTPError as e:
        print("HTTP error while downloading Google Sheet:", e)
        sys.exit(1)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
    finally:
        if temp_file:
            try:
                os.unlink(temp_file)
            except Exception:
                pass

if __name__ == "__main__":
    main()
