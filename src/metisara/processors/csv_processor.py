import csv
import sys
import subprocess
import json
import configparser
from typing import Dict
from pathlib import Path

def generate_ra_tickets(config: Dict) -> list:
    """
    Generate additional resource allocation ticket rows based on team configuration.
    
    Args:
        config: Configuration dictionary containing resource allocation teams
        
    Returns:
        List of CSV rows for resource allocation tickets
    """
    ra_tickets = []
    
    if 'resource_allocation_teams' not in config:
        return ra_tickets
    
    # Get actual values from config
    project_key = config.get('replacements', {}).get('<project_key>', 'PROJECT')
    program_manager = config.get('replacements', {}).get('<program_manager>', '')
    project_target_start = config.get('replacements', {}).get('<project_target_start>', '')
    project_due_date = config.get('replacements', {}).get('<project_due_date>', '')
    
    for i, team in enumerate(config['resource_allocation_teams']):
        # Generate ticket for each team member with actual values
        ticket_row = [
            'Resource Allocation',  # Milestone
            'Tracker',  # Issue Type
            f"{project_key}M00: RA - {team['role']} - {team['name']}",  # Summary with actual values
            '',  # Description
            'Normal',  # Priority
            '<resource_alocation_epic>',  # Epic Link - will be replaced by bulk_create script
            '',  # Epic Name
            program_manager,  # Reporter - actual value
            team['email'] if team['email'] else '',  # Assignee - actual email
            '<parent_link>',  # Parent Link - will be replaced by bulk_create script
            project_target_start,  # Target Start - actual value
            project_due_date,  # Due Date - actual value
            'Resource Allocation',  # Component
            ''  # Story Points
        ]
        ra_tickets.append(ticket_row)
    
    return ra_tickets

def generate_conception_review_tickets(config: Dict) -> list:
    """
    Generate conception review tickets for each team member.
    
    Args:
        config: Configuration dictionary containing conception teams
        
    Returns:
        List of CSV rows for conception review tickets
    """
    review_tickets = []
    
    if 'conception_teams' not in config:
        return review_tickets
    
    # Get actual values from config
    program_manager = config.get('replacements', {}).get('<program_manager>', '')
    project_charter = config.get('replacements', {}).get('<project_charter>', '')
    review_due_date = config.get('replacements', {}).get('<review_due_date>', '')
    
    for i, team in enumerate(config['conception_teams']):
        # Generate review ticket for each team member with actual values
        ticket_row = [
            'Conception',  # Milestone
            'Story',  # Issue Type
            f"Team, Review Project Charter - {team['role']} - {team['name']}",  # Summary with actual role and name
            f'Please review the [Project Charter|{project_charter}] and provide your sign-off by resolving this ticket. If you have any questions, concerns, or suggestions, please add inline comments to the charter document.',  # Description with actual charter link
            'Normal',  # Priority
            '<conception_epic>',  # Epic Link - will be replaced by bulk_create script
            '',  # Epic Name
            program_manager,  # Reporter - actual value
            team['email'] if team['email'] else '',  # Assignee - actual email
            '<parent_link>',  # Parent Link - will be replaced by bulk_create script
            '',  # Target Start
            review_due_date,  # Due Date - actual value
            'Review',  # Component
            '1'  # Story Points
        ]
        review_tickets.append(ticket_row)
    
    return review_tickets

def replace_placeholders_in_csv(input_file: str, output_file: str, replacements: Dict[str, str], config: Dict = None):
    """
    Replace placeholder keys in a CSV file with actual values and add dynamic resource allocation tickets.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        replacements: Dictionary mapping placeholder keys to replacement values
        config: Full configuration dictionary for generating additional tickets
    """
    try:
        # Import the disclaimer function
        import sys
        from pathlib import Path
        
        # Add the CLI module to path to access disclaimer function
        script_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(script_dir))
        
        try:
            from cli import get_ai_disclaimer
        except ImportError:
            # Fallback if import fails
            def get_ai_disclaimer():
                from datetime import datetime
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return f"# AI-Generated file - Review before production use | Generated: {current_date}\n"
        
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            # Write AI disclaimer at the beginning of the file as CSV comments
            disclaimer = get_ai_disclaimer()
            # Split disclaimer into lines and prefix each with # for CSV comments
            disclaimer_lines = disclaimer.strip().split('\n')
            for line in disclaimer_lines:
                if line.strip():  # Skip empty lines
                    outfile.write(f"{line}\n")
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            rows_written = 0
            ra_tickets_added = False
            conception_tickets_added = False
            in_config_section = False
            
            for row in reader:
                # Check if we're entering a configuration section
                first_cell = row[0] if row else ''
                if first_cell in ['General Configuration', 'Resource Allocation Tickets', 'Conception Tickets']:
                    in_config_section = True
                elif first_cell and not first_cell.startswith('<') and not in_config_section:
                    in_config_section = False
                elif first_cell == '':
                    in_config_section = False
                
                # Skip specific template rows that are placeholders for data entry
                # These are rows like <ra_role>, <conception_name> that are templates for user input
                is_user_template_row = (not in_config_section and 
                                       len(row) > 2 and 
                                       (('<ra_role>' in str(row[2]) and '<ra_name>' in str(row[2])) or
                                        ('<conception_role>' in str(row[2]) and '<conception_name>' in str(row[2]))))
                
                if is_user_template_row:
                    # Skip user input template rows in ticket sections
                    continue
                
                # Skip placeholder replacement in configuration sections
                if in_config_section:
                    # Keep configuration sections as-is
                    processed_row = row[:]
                else:
                    # Replace placeholders in regular ticket rows
                    processed_row = []
                    for cell in row:
                        processed_cell = cell
                        for placeholder, replacement in replacements.items():
                            processed_cell = processed_cell.replace(placeholder, replacement)
                        processed_row.append(processed_cell)
                
                writer.writerow(processed_row)
                rows_written += 1
                
                # Add resource allocation tickets after all Project Level epics
                if (config and len(processed_row) > 1 and 
                    'Epic' in processed_row[1] and 
                    'UAT / Project Closure' in processed_row[2] and 
                    not ra_tickets_added):
                    
                    ra_tickets = generate_ra_tickets(config)
                    for ticket in ra_tickets:
                        # Replace remaining placeholders in generated tickets
                        processed_ticket = []
                        for cell in ticket:
                            processed_cell = cell
                            for placeholder, replacement in replacements.items():
                                processed_cell = processed_cell.replace(placeholder, replacement)
                            processed_ticket.append(processed_cell)
                        
                        writer.writerow(processed_ticket)
                        rows_written += 1
                    
                    ra_tickets_added = True
                    if ra_tickets:
                        print(f"✅ Added {len(ra_tickets)} resource allocation tickets")
                
                # Add conception review tickets after existing conception tickets
                if (config and len(processed_row) > 1 and 
                    'Conception' in processed_row[0] and 
                    'Story' in processed_row[1] and
                    'Fill in project charter' in processed_row[2] and
                    not conception_tickets_added):
                    
                    review_tickets = generate_conception_review_tickets(config)
                    for ticket in review_tickets:
                        # Replace remaining placeholders in generated tickets
                        processed_ticket = []
                        for cell in ticket:
                            processed_cell = cell
                            for placeholder, replacement in replacements.items():
                                processed_cell = processed_cell.replace(placeholder, replacement)
                            processed_ticket.append(processed_cell)
                        
                        writer.writerow(processed_ticket)
                        rows_written += 1
                    
                    conception_tickets_added = True
                    if review_tickets:
                        print(f"✅ Added {len(review_tickets)} conception review tickets")
        
        print(f"Successfully processed {input_file} -> {output_file} ({rows_written} total rows)")
        
    except FileNotFoundError:
        print(f"Error: File {input_file} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

def extract_config_from_csv(csv_file: str) -> Dict:
    """
    Extract configuration from CSV file sections:
    - General Configuration
    - Resource Allocation Tickets 
    - Conception Tickets
    
    Args:
        csv_file: Path to input CSV file
        
    Returns:
        Dictionary containing extracted configuration
    """
    # Load default project from metisara.conf
    metisara_config = configparser.ConfigParser()
    metisara_config.read('metisara.conf')
    default_project = metisara_config.get('project', 'default_project', fallback='PROJ')
    
    config = {
        "replacements": {},
        "jira_settings": {
            "target_project": default_project
        }
    }
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            current_section = None
            
            for row_num, row in enumerate(reader, start=1):
                # Get the first column value to check for section headers
                first_col = None
                for key, value in row.items():
                    if value and value.strip():
                        first_col = value.strip()
                        break
                
                
                if not first_col:
                    continue
                
                # Identify sections by first column content
                if first_col == 'General Configuration':
                    current_section = 'general'
                    continue
                elif first_col == 'Resource Allocation Tickets':
                    current_section = 'resource_allocation'
                    continue
                elif first_col == 'Conception Tickets':
                    current_section = 'conception'
                    continue
                elif first_col in ['Team', 'Role', 'Name', 'Email']:
                    # Skip header rows
                    continue
                
                # Extract configuration values
                if current_section == 'general':
                    # In general section, placeholder is in Milestone column, value is in Issue Type column
                    placeholder = row.get('Milestone', '').strip()
                    value = row.get('Issue Type', '').strip()
                    
                    if placeholder and value and placeholder.startswith('<') and placeholder.endswith('>'):
                        if placeholder == '<target_project>':
                            config["jira_settings"]["target_project"] = value
                            config["replacements"]["<target_project>"] = value
                        elif placeholder in ['<project_key>', '<project_name>', '<project_charter>', 
                                           '<program_manager>', '<project_target_start>', '<project_due_date>', 
                                           '<review_due_date>']:
                            config["replacements"][placeholder] = value
                        # Keep epic placeholders as-is for now
                        elif placeholder in ['<parent_link>', '<resource_alocation_epic>', '<conception_epic>', 
                                           '<initiation_epic>', '<enablement_epic>', '<uat_closure_epic>']:
                            config["replacements"][placeholder] = placeholder
                
                elif current_section == 'resource_allocation':
                    # Extract resource allocation team members - data is in different columns
                    ra_team = row.get('Milestone', '').strip()
                    ra_role = row.get('Issue Type', '').strip() 
                    ra_name = row.get('Summary', '').strip()
                    ra_email = row.get('Description', '').strip()
                    
                    # Skip rows with placeholder values or empty data
                    if (ra_team and ra_role and ra_name and 
                        not ra_team.startswith('<') and 
                        not ra_role.startswith('<') and 
                        not ra_name.startswith('<')):
                        
                        if 'resource_allocation_teams' not in config:
                            config['resource_allocation_teams'] = []
                        
                        config['resource_allocation_teams'].append({
                            'team': ra_team,
                            'role': ra_role,
                            'name': ra_name,
                            'email': ra_email
                        })
                
                elif current_section == 'conception':
                    # Extract conception team members - data is in different columns  
                    conception_team = row.get('Milestone', '').strip()
                    conception_role = row.get('Issue Type', '').strip() 
                    conception_name = row.get('Summary', '').strip()
                    conception_email = row.get('Description', '').strip()
                    
                    # Skip rows with placeholder values or empty data
                    if (conception_team and conception_role and conception_name and 
                        not conception_team.startswith('<') and 
                        not conception_role.startswith('<') and 
                        not conception_name.startswith('<')):
                        
                        if 'conception_teams' not in config:
                            config['conception_teams'] = []
                        
                        config['conception_teams'].append({
                            'team': conception_team,
                            'role': conception_role,
                            'name': conception_name,
                            'email': conception_email
                        })
            
            # Set default epic placeholders
            config["replacements"]["<parent_link>"] = "<parent_link>"
            config["replacements"]["<resource_alocation_epic>"] = "<resource_alocation_epic>"
            config["replacements"]["<conception_epic>"] = "<conception_epic>"
            config["replacements"]["<initiation_epic>"] = "<initiation_epic>"
            config["replacements"]["<enablement_epic>"] = "<enablement_epic>"
            config["replacements"]["<uat_closure_epic>"] = "<uat_closure_epic>"
            
            # Generate placeholders for resource allocation teams
            if 'resource_allocation_teams' in config:
                for i, team in enumerate(config['resource_allocation_teams']):
                    config["replacements"][f"<ra_team_{i}>"] = team['team']
                    config["replacements"][f"<ra_role_{i}>"] = team['role'] 
                    config["replacements"][f"<ra_name_{i}>"] = team['name']
                    config["replacements"][f"<ra_email_{i}>"] = team['email']
            
            # Generate placeholders for conception teams
            if 'conception_teams' in config:
                for i, team in enumerate(config['conception_teams']):
                    config["replacements"][f"<conception_team_{i}>"] = team['team']
                    config["replacements"][f"<conception_role_{i}>"] = team['role'] 
                    config["replacements"][f"<conception_name_{i}>"] = team['name']
                    config["replacements"][f"<conception_email_{i}>"] = team['email']
            
        return config
        
    except FileNotFoundError:
        print(f"Error: CSV file {csv_file} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

def load_config(config_file: str = 'workspace/config/csv_replacements.json') -> Dict:
    """
    Load configuration from JSON file.
    
    Args:
        config_file: Path to configuration JSON file
        
    Returns:
        Dictionary containing configuration data
    """
    try:
        # Make config_file path absolute
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = Path.cwd() / config_file
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found")
        print("Please create the configuration file with replacement mappings")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {config_file}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

def save_config(config: Dict, config_file: str = 'workspace/config/csv_replacements.json'):
    """
    Save configuration to JSON file, replacing existing file if it exists.
    
    Args:
        config: Configuration dictionary to save
        config_file: Path to output JSON file
    """
    import os
    
    try:
        # Import the disclaimer function
        import sys
        
        # Add the CLI module to path to access disclaimer function
        script_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(script_dir))
        
        try:
            from cli import get_ai_disclaimer
        except ImportError:
            # Fallback if import fails
            def get_ai_disclaimer():
                from datetime import datetime
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return f"AI-Generated file - Review before production use | Generated: {current_date}"
        
        # Ensure directory exists
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists and inform user
        if config_path.exists():
            print(f"🔄 Replacing existing {config_file}")
        
        # Add AI disclaimer to config
        config_with_disclaimer = {
            "_ai_disclaimer": get_ai_disclaimer().replace('\n', ' | ').replace('#', '').strip(),
            **config
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_with_disclaimer, f, indent=2, ensure_ascii=False)
        print(f"✅ Configuration saved to {config_file}")
    except Exception as e:
        print(f"Error saving configuration: {e}")
        sys.exit(1)

def main():
    print("CSV Placeholder Replacement Tool")
    print("=" * 40)
    
    # Check flags
    skip_auto_move = '--skip-auto-move' in sys.argv
    generate_config = '--generate-config' in sys.argv
    
    # Check for Google Sheets URL
    google_sheets_url = None
    if '--google-sheets' in sys.argv:
        try:
            google_sheets_index = sys.argv.index('--google-sheets')
            if google_sheets_index + 1 < len(sys.argv):
                google_sheets_url = sys.argv[google_sheets_index + 1]
        except (ValueError, IndexError):
            print("❌ Error: --google-sheets requires a URL argument")
            sys.exit(1)
    
    # Check if we should generate config from CSV
    if generate_config:
        if google_sheets_url:
            print("Step 1: Downloading CSV from Google Sheets...")
            from pathlib import Path
            script_dir = Path(__file__).parent.parent
            sys.path.insert(0, str(script_dir))
            
            try:
                from utils.file_manager import download_csv_from_google_sheets
                success = download_csv_from_google_sheets(google_sheets_url)
                if not success:
                    print("❌ Failed to download CSV from Google Sheets")
                    sys.exit(1)
            except ImportError as e:
                print(f"❌ Error importing Google Sheets handler: {e}")
                sys.exit(1)
            
            print("\nStep 2: Extracting configuration from CSV...")
        elif not skip_auto_move:
            # Check if CSV file already exists before trying to move it
            metisara_config = configparser.ConfigParser()
            metisara_config.read('metisara.conf')
            input_file = metisara_config.get('files', 'csv_file_input', fallback='Metisara Template - Import.csv')
            
            if Path(input_file).exists():
                print(f"Step 1: {input_file} already exists in current directory, skipping auto-move")
            else:
                print("Step 1: Moving CSV file from Downloads...")
                
                try:
                    result = subprocess.run([sys.executable, 'auto_move_csv.py'], 
                                          capture_output=True, text=True, check=True)
                    print(result.stdout)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error running auto_move_csv.py: {e}")
                    print(f"Error output: {e.stderr}")
                    sys.exit(1)
                except FileNotFoundError:
                    print("❌ auto_move_csv.py not found in current directory")
                    sys.exit(1)
            
            print("\nStep 2: Extracting configuration from CSV...")
        else:
            print("Step 1: Extracting configuration from CSV (skipping auto_move_csv.py)...")
        
        metisara_config = configparser.ConfigParser()
        metisara_config.read('metisara.conf')
        input_file = metisara_config.get('files', 'csv_file_input', fallback='Metisara Template - Import.csv')
        
        # Search for CSV file in multiple locations when skip_auto_move is used
        if skip_auto_move:
            csv_path = Path(input_file)
            possible_paths = [
                csv_path,  # Direct path as specified in config
                Path("workspace/input") / input_file,  # In workspace/input directory
                Path("workspace/input") / csv_path.name,  # Just filename in workspace/input
            ]
            
            file_found = False
            actual_path = None
            for path in possible_paths:
                if path.exists():
                    file_found = True
                    actual_path = path
                    break
            
            if not file_found:
                print(f"Error: CSV file {input_file} not found in any of these locations:")
                for path in possible_paths:
                    print(f"   - {path}")
                print("💡 Try placing the file in workspace/input/ directory")
                sys.exit(1)
            else:
                input_file = str(actual_path)
                print(f"Found CSV file at: {input_file}")
        
        config = extract_config_from_csv(input_file)
        
        print("\nExtracted configuration:")
        print("General Configuration:")
        for key, value in config["replacements"].items():
            if not key.startswith('<resource_') and not key.startswith('<conception_') and not key.startswith('<initiation_') and not key.startswith('<enablement_') and not key.startswith('<uat_'):
                print(f"  {key} -> {value}")
        
        print(f"\nJIRA Settings:")
        for key, value in config["jira_settings"].items():
            print(f"  {key} -> {value}")
        
        # Display resource allocation teams
        if 'resource_allocation_teams' in config:
            print(f"\nResource Allocation Teams ({len(config['resource_allocation_teams'])} teams):")
            for i, team in enumerate(config['resource_allocation_teams']):
                print(f"  Team {i+1}: {team['role']} - {team['name']} ({team['email']}) - {team['team']}")
            
            print("\nGenerated RA placeholders:")
            for key, value in config["replacements"].items():
                if key.startswith('<ra_'):
                    print(f"  {key} -> {value}")
        
        # Display conception teams
        if 'conception_teams' in config:
            print(f"\nConception Teams ({len(config['conception_teams'])} teams):")
            for i, team in enumerate(config['conception_teams']):
                print(f"  Team {i+1}: {team['role']} - {team['name']} ({team['email']}) - {team['team']}")
            
            print("\nGenerated Conception placeholders:")
            for key, value in config["replacements"].items():
                if key.startswith('<conception_'):
                    print(f"  {key} -> {value}")
        
        save_config(config)
        print("\n✅ Configuration generation complete!")
        return
    
    # Original functionality - load existing config and process CSV
    if google_sheets_url:
        print("Step 1: Downloading CSV from Google Sheets...")
        from pathlib import Path
        script_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(script_dir))
        
        try:
            from utils.file_manager import download_csv_from_google_sheets
            success = download_csv_from_google_sheets(google_sheets_url)
            if not success:
                print("❌ Failed to download CSV from Google Sheets")
                sys.exit(1)
        except ImportError as e:
            print(f"❌ Error importing Google Sheets handler: {e}")
            sys.exit(1)
        
        print("\nStep 2: Processing CSV file...")
    elif not skip_auto_move:
        # Check if CSV file already exists before trying to move it
        metisara_config = configparser.ConfigParser()
        metisara_config.read('metisara.conf')
        input_file = metisara_config.get('files', 'csv_file_input', fallback='Metisara Template - Import.csv')
        
        if Path(input_file).exists():
            print(f"Step 1: {input_file} already exists in current directory, skipping auto-move")
        else:
            print("Step 1: Moving CSV file from Downloads...")
            
            try:
                result = subprocess.run([sys.executable, 'auto_move_csv.py'], 
                                      capture_output=True, text=True, check=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"❌ Error running auto_move_csv.py: {e}")
                print(f"Error output: {e.stderr}")
                sys.exit(1)
            except FileNotFoundError:
                print("❌ auto_move_csv.py not found in current directory")
                sys.exit(1)
        
        print("\nStep 2: Processing CSV file...")
    else:
        print("Step 1: Processing CSV file (skipping auto_move_csv.py)...")
    
    # Load configuration from external file
    config = load_config()
    replacements = config.get('replacements', {})
    
    # Read file paths directly from metisara.conf
    metisara_config = configparser.ConfigParser()
    metisara_config.read('metisara.conf')
    input_file = metisara_config.get('files', 'csv_file_input', fallback='workspace/input/Metisara Template - Import.csv')
    output_file = metisara_config.get('files', 'csv_file_output', fallback='workspace/output/project-tickets-processed.csv')
    
    # Search for CSV file in multiple locations when skip_auto_move is used
    if skip_auto_move:
        csv_path = Path(input_file)
        possible_paths = [
            csv_path,  # Direct path as specified in config
            Path("workspace/input") / input_file,  # In workspace/input directory
            Path("workspace/input") / csv_path.name,  # Just filename in workspace/input
        ]
        
        file_found = False
        actual_path = None
        for path in possible_paths:
            if path.exists():
                file_found = True
                actual_path = path
                break
        
        if not file_found:
            print(f"Error: CSV file {input_file} not found in any of these locations:")
            for path in possible_paths:
                print(f"   - {path}")
            print("💡 Try placing the file in workspace/input/ directory")
            sys.exit(1)
        else:
            input_file = str(actual_path)
            print(f"Found CSV file at: {input_file}")
    
    # Make file paths absolute
    input_path = Path(input_file)
    output_path = Path(output_file)
    if not input_path.is_absolute():
        input_path = Path.cwd() / input_file
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_file
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("\nReplacements to be made:")
    for placeholder, value in replacements.items():
        print(f"  {placeholder} -> {value}")
    
    print("\nProceeding with replacement...")
    
    replace_placeholders_in_csv(str(input_path), str(output_path), replacements, config)

if __name__ == "__main__":
    main()
