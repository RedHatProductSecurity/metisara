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


def get_authenticated_session() -> requests.Session:
    """
    Create an authenticated requests session using existing machine credentials.
    
    Returns:
        Configured requests session with authentication
    """
    session = requests.Session()
    
    # Try to use existing Google application credentials from environment
    import os
    import subprocess
    
    try:
        # Check multiple possible gcloud locations
        gcloud_paths = [
            'gcloud',  # System PATH
            '~/google-cloud-sdk/bin/gcloud',  # Default install location
            os.path.expanduser('~/google-cloud-sdk/bin/gcloud'),  # Expanded path
            '/usr/bin/gcloud',  # System install
            '/usr/local/bin/gcloud'  # Local install
        ]
        
        access_token = None
        for gcloud_path in gcloud_paths:
            try:
                result = subprocess.run([gcloud_path, 'auth', 'application-default', 'print-access-token'], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    access_token = result.stdout.strip()
                    print(f"🔐 Using gcloud application default credentials (found at: {gcloud_path})")
                    break
                    
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if access_token:
            session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            })
            return session
        else:
            print("⚠️  gcloud CLI not found in any standard location")
            
    except Exception as e:
        print(f"⚠️  Error checking gcloud authentication: {e}")
    
    # Check for service account credentials in environment
    google_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if google_creds and os.path.exists(google_creds):
        try:
            import json
            with open(google_creds, 'r') as f:
                cred_data = json.load(f)
            
            if cred_data.get('type') == 'service_account':
                print("🔐 Found service account credentials in GOOGLE_APPLICATION_CREDENTIALS")
                # For simplicity, we'll try the basic approach first
                # In production, this would use proper OAuth flow
                
        except Exception as e:
            print(f"⚠️  Could not load service account credentials: {e}")
    
    # Check for local gcloud config with proper scopes
    local_creds_file = os.path.expanduser('~/.local_gcloud/application_default_credentials.json')
    if os.path.exists(local_creds_file):
        try:
            # Try to get token using local config
            env = os.environ.copy()
            env['CLOUDSDK_CONFIG'] = os.path.expanduser('~/.local_gcloud')
            
            for gcloud_path in gcloud_paths:
                try:
                    result = subprocess.run([gcloud_path, 'auth', 'application-default', 'print-access-token'], 
                                          capture_output=True, text=True, timeout=10, env=env)
                    
                    if result.returncode == 0:
                        access_token = result.stdout.strip()
                        session.headers.update({
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                        })
                        print(f"🔐 Using local gcloud credentials with Sheets scopes")
                        return session
                        
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    continue
                    
        except Exception as e:
            print(f"⚠️  Could not use local gcloud credentials: {e}")
    
    print("🔓 Falling back to unauthenticated session")
    return session


def download_csv_from_google_sheets(sheets_url: str, output_path: str = None, gid: str = "0") -> bool:
    """
    Download CSV data from a Google Sheets document using Red Hat authentication.
    
    Args:
        sheets_url: Google Sheets URL
        output_path: Path where CSV file should be saved (optional)
        gid: Sheet ID within the spreadsheet (default: "0" for first sheet)
        
    Returns:
        Boolean indicating success/failure
    """
    try:
        sheet_id = extract_sheet_id(sheets_url)
        
        # Extract gid from URL if present
        import re
        gid_match = re.search(r'[#&]gid=([0-9]+)', sheets_url)
        if gid_match:
            gid = gid_match.group(1)
            print(f"   Found sheet gid in URL: {gid}")
        
        # Get authenticated session
        session = get_authenticated_session()
        
        csv_export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        
        print(f"🔗 Downloading from Google Sheets...")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   Export URL: {csv_export_url}")
        
        response = session.get(csv_export_url, timeout=30)
        
        # If authentication fails, try public access
        if response.status_code == 401:
            print("🔄 Authentication failed, trying public access...")
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
        print("💡 Ensure you're authenticated with: gcloud auth application-default login")
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