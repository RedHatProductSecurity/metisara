#!/usr/bin/env python3

import os
import shutil
import sys
import configparser
from pathlib import Path

def auto_move_csv_from_downloads(force=False):
    """Automatically move the Metisara template CSV file from Downloads to workspace
    
    Args:
        force: If True, move file even if destination already exists
    """
    
    # Load configuration from metisara.conf
    config = configparser.ConfigParser()
    config.read('metisara.conf')
    
    # Get CSV file path from config
    csv_filepath = config.get('files', 'csv_file_input', fallback='workspace/input/Metisara Template - Import.csv')
    
    # Extract just the filename for Downloads lookup
    csv_filename = Path(csv_filepath).name
    
    # Get user's home directory and Downloads folder
    home_dir = Path.home()
    downloads_dir = home_dir / "Downloads"
    
    # Source file in Downloads
    source_file = downloads_dir / csv_filename
    
    # Destination file in workspace
    current_dir = Path.cwd()
    dest_file = current_dir / csv_filepath
    
    # Ensure destination directory exists
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    
    print("Auto CSV File Mover")
    print("=" * 24)
    print(f"Source: {source_file}")
    print(f"Destination: {dest_file}")
    
    # Check if source file exists
    if not source_file.exists():
        print(f"❌ Source file not found: {source_file}")
        print("\nPlease make sure the file is in your Downloads folder with the exact name:")
        print(f"   '{csv_filename}'")
        return False
    
    # Check if destination file already exists
    if dest_file.exists():
        if not force:
            print(f"⚠️  Destination file already exists: {dest_file}")
            print("File already exists - will be overwritten automatically")
            return False
        else:
            print(f"🔄 Force mode: Overwriting existing file...")
    
    try:
        # Move the file
        shutil.move(str(source_file), str(dest_file))
        print(f"✅ Successfully moved file to: {dest_file}")
        
        # Verify the move
        if dest_file.exists() and not source_file.exists():
            print(f"✅ File verified in destination directory")
            print(f"📁 Original file removed from Downloads")
            return True
        else:
            print("❌ File move verification failed")
            return False
            
    except PermissionError:
        print(f"❌ Permission denied. Cannot move file.")
        print("   Make sure you have write access to the destination directory.")
        return False
    except Exception as e:
        print(f"❌ Error moving file: {e}")
        return False


def download_csv_from_google_sheets(sheets_url: str, force=False):
    """Download CSV from Google Sheets and save to workspace
    
    Args:
        sheets_url: Google Sheets URL (must be publicly accessible)
        force: If True, overwrite existing file
    """
    try:
        from .google_sheets_handler import download_csv_from_google_sheets as download_handler
        
        config = configparser.ConfigParser()
        config.read('metisara.conf')
        
        csv_filepath = config.get('files', 'csv_file_input', fallback='workspace/input/Metisara Template - Import.csv')
        dest_file = Path.cwd() / csv_filepath
        
        print("Google Sheets CSV Download")
        print("=" * 30)
        print(f"Source: {sheets_url}")
        print(f"Destination: {dest_file}")
        
        success = download_handler(sheets_url, str(dest_file), force=force)
        return success
        
    except ImportError:
        print("❌ Google Sheets handler not available")
        return False
    except Exception as e:
        print(f"❌ Error downloading from Google Sheets: {e}")
        return False


def main():
    success = auto_move_csv_from_downloads()
    
    if success:
        print("\n✅ Ready to run process_csv.py to replace placeholders!")
    else:
        print("\n❌ File transfer failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()