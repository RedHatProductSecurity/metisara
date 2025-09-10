#!/usr/bin/env python3

import requests
import re
import configparser
from pathlib import Path
from urllib.parse import urlparse, parse_qs


def extract_sheet_id(sheets_url: str) -> str:
    """
    Extract Google Sheets ID from a Google Sheets URL.
    
    Args:
        sheets_url: Google Sheets URL
        
    Returns:
        String containing the Google Sheets ID
        
    Raises:
        ValueError: If URL format is invalid or sheet ID cannot be extracted
    """
    patterns = [
        r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
        r'id=([a-zA-Z0-9-_]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, sheets_url)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract Google Sheets ID from URL: {sheets_url}")


def download_csv_from_google_sheets(sheets_url: str, output_path: str = None, gid: str = "0") -> bool:
    """
    Download CSV data from a Google Sheets document.
    
    Args:
        sheets_url: Google Sheets URL (must be publicly accessible)
        output_path: Path where CSV file should be saved (optional)
        gid: Sheet ID within the spreadsheet (default: "0" for first sheet)
        
    Returns:
        Boolean indicating success/failure
    """
    try:
        sheet_id = extract_sheet_id(sheets_url)
        
        csv_export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        
        print(f"🔗 Downloading from Google Sheets...")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   Export URL: {csv_export_url}")
        
        response = requests.get(csv_export_url, timeout=30)
        response.raise_for_status()
        
        if not response.content:
            print("❌ No data received from Google Sheets")
            return False
            
        if output_path is None:
            config = configparser.ConfigParser()
            config.read('metisara.conf')
            output_path = config.get('files', 'csv_file_input', fallback='workspace/input/Metisara Template - Import.csv')
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Successfully downloaded CSV to: {output_file}")
        print(f"   File size: {len(response.content)} bytes")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        print(f"   Lines: {line_count}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error downloading from Google Sheets: {e}")
        return False
    except ValueError as e:
        print(f"❌ URL parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error downloading from Google Sheets: {e}")
        return False


def main():
    """
    Command line interface for Google Sheets CSV download.
    Usage: python google_sheets_handler.py <sheets_url> [output_path] [gid]
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Google Sheets CSV Download Handler")
        print("=" * 40)
        print("Usage: python google_sheets_handler.py <sheets_url> [output_path] [gid]")
        print()
        print("Arguments:")
        print("  sheets_url  - Google Sheets URL (must be publicly accessible)")
        print("  output_path - Optional: Path to save CSV file")
        print("  gid         - Optional: Sheet ID within spreadsheet (default: 0)")
        print()
        print("Examples:")
        print("  python google_sheets_handler.py 'https://docs.google.com/spreadsheets/d/ABC123/edit'")
        print("  python google_sheets_handler.py 'https://docs.google.com/spreadsheets/d/ABC123/edit' 'data.csv'")
        print("  python google_sheets_handler.py 'https://docs.google.com/spreadsheets/d/ABC123/edit' 'data.csv' '123456789'")
        sys.exit(1)
    
    sheets_url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    gid = sys.argv[3] if len(sys.argv) > 3 else "0"
    
    print("Google Sheets CSV Download Handler")
    print("=" * 40)
    
    success = download_csv_from_google_sheets(sheets_url, output_path, gid)
    
    if success:
        print("\n✅ Google Sheets CSV download completed successfully!")
    else:
        print("\n❌ Google Sheets CSV download failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()