import csv
import sys
import os
import json
import configparser
from datetime import datetime
from dotenv import load_dotenv
from jira import JIRA

class JiraBulkCreator:
    def __init__(self, base_url, username, api_token, dry_run=False):
        self.base_url = base_url.rstrip('/')
        self.dry_run = dry_run
        
        if not dry_run:
            # Initialize JIRA client with token authentication
            self.jira = JIRA(
                server=self.base_url,
                token_auth=api_token
            )
        else:
            self.jira = None
            print("🔍 DRY RUN MODE - No issues will be created")
            
        self.created_issues = {}  # Track created issues for epic linking
        self.epic_placeholders = {}  # Track epic placeholders to actual keys
        self.parent_project_key = None  # Track the parent project issue
        self.dry_run_counter = 0  # Counter for dry-run fake keys
    
    def convert_date(self, date_str):
        """Convert date from various formats to YYYY-MM-DD format"""
        if not date_str or date_str.strip() == '':
            return None
        
        date_formats = [
            "%d/%b/%y",    # 4/Sep/25 or 04/Sep/25
            "%d/%m/%y",    # 18/11/25
            "%d-%m-%y",    # 18-11-25
            "%d.%m.%y",    # 18.11.25
            "%d/%b/%Y",    # 4/Sep/2025
            "%d/%m/%Y",    # 18/11/2025
        ]
        
        for date_format in date_formats:
            try:
                date_obj = datetime.strptime(date_str.strip(), date_format)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        print(f"⚠️  Could not parse date: {date_str}")
        return None
    
    def load_config(self, config_file='workspace/config/csv_replacements.json'):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"⚠️  Configuration file {config_file} not found, using defaults")
            return {}
        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON in {config_file}: {e}, using defaults")
            return {}
    
    def resolve_epic_placeholder(self, epic_link):
        """Resolve epic placeholder to actual epic key"""
        if epic_link.startswith('<') and epic_link.endswith('>'):
            # This is a placeholder, try to resolve it
            resolved_key = self.epic_placeholders.get(epic_link)
            if resolved_key:
                return resolved_key
            else:
                print(f"⚠️  Epic placeholder {epic_link} not yet resolved, skipping epic link")
                return None
        else:
            # Direct epic key, use as-is
            return epic_link
    
    
    def create_issue_from_row(self, row, config=None):
        """Create a Jira issue from CSV row data"""
        
        # Extract fields from CSV row
        issue_type = row.get('Issue Type', '').strip()
        summary = row.get('Summary', '').strip()
        description = row.get('Description', '').strip()
        priority = row.get('Priority', 'Normal').strip()
        assignee = row.get('Assignee', '').strip()
        reporter = row.get('Reporter', '').strip()
        epic_name = row.get('Epic Name', '').strip()
        epic_link = row.get('Epic Link', '').strip()
        due_date = self.convert_date(row.get('Due Date', ''))
        target_start = self.convert_date(row.get('Target Start', ''))
        component = row.get('Component', '').strip()
        story_points = row.get('Story Points', '').strip()
        parent_link = row.get('Parent Link', '').strip()
        
        # Skip empty rows
        if not summary or not issue_type:
            return None
        
        # Get target project from config
        target_project = "GUARD"  # Default fallback
        if config:
            jira_settings = config.get('jira_settings', {})
            target_project = jira_settings.get('target_project', 'GUARD')
        
        # Build issue payload
        issue_data = {
            "fields": {
                "project": {"key": target_project},
                "summary": summary,
                "issuetype": {"name": issue_type},
                "priority": {"name": priority if priority else "Normal"}
            }
        }
        
        # Add description if provided
        if description:
            issue_data["fields"]["description"] = description
        
        # Add assignee if provided
        if assignee and assignee != '':
            issue_data["fields"]["assignee"] = {"name": assignee}
        
        # Add reporter if provided
        if reporter and reporter != '':
            issue_data["fields"]["reporter"] = {"name": reporter}
        
        # Add due date if provided
        if due_date:
            issue_data["fields"]["duedate"] = due_date
        
        # Add target start date if provided
        if target_start:
            issue_data["fields"]["customfield_12313941"] = target_start  # Target Start field
        
        # Add story points if provided (custom field - ID may vary)
        if story_points and story_points.isdigit():
            issue_data["fields"]["customfield_12310243"] = float(story_points)  # Story Points field
        
        # Add component if provided
        if component:
            issue_data["fields"]["components"] = [{"name": component}]
        
        # For Epics, add Epic Name
        if issue_type.lower() == 'epic' and epic_name:
            issue_data["fields"]["customfield_12311141"] = epic_name  # Epic Name field
        
        # Add epic link if provided - resolve placeholders to actual epic keys
        if epic_link:
            resolved_epic_link = self.resolve_epic_placeholder(epic_link)
            if resolved_epic_link:
                issue_data["fields"]["customfield_12311140"] = resolved_epic_link  # Epic Link field
        
        # Add parent link if provided - resolve <parent_link> placeholder to first project issue
        if parent_link:
            if parent_link == '<parent_link>' and self.parent_project_key:
                issue_data["fields"]["customfield_12313140"] = self.parent_project_key  # Parent Link field (string)
            elif parent_link != '<parent_link>' and parent_link.strip():
                issue_data["fields"]["customfield_12313140"] = parent_link  # Parent Link field (string)
        
        return self.create_issue(issue_data, summary, issue_type, epic_name)
    
    def create_issue(self, issue_data, summary, issue_type=None, epic_name=None):
        """Create a single issue via JIRA library"""
        if self.dry_run:
            # Simulate creating issue - generate fake key for tracking
            self.dry_run_counter += 1
            fake_key = f"DRY-{self.dry_run_counter:04d}"
            print(f"🔍 DRY RUN - Would create: {fake_key} - {summary}")
            print(f"   Project: {issue_data['fields']['project']['key']}")
            print(f"   Type: {issue_data['fields']['issuetype']['name']}")
            print(f"   Priority: {issue_data['fields']['priority']['name']}")
            if 'assignee' in issue_data['fields']:
                print(f"   Assignee: {issue_data['fields']['assignee']['name']}")
            if 'duedate' in issue_data['fields']:
                print(f"   Due Date: {issue_data['fields']['duedate']}")
            if 'description' in issue_data['fields']:
                print(f"   Description: {issue_data['fields']['description'][:100]}...")
            
            # If this is an epic, store its key for placeholder resolution
            if issue_type and issue_type.lower() == 'epic' and epic_name:
                # Map epic name to its key for future reference
                self.created_issues[epic_name] = fake_key
                
                # Map specific epic types to their placeholders
                epic_lower = epic_name.lower()
                if 'resource allocation' in epic_lower or 'm00' in epic_lower:
                    self.epic_placeholders["<resource_alocation_epic>"] = fake_key
                    print(f"🔗 Mapped <resource_alocation_epic> -> {fake_key}")
                elif 'conception' in epic_lower or 'm01' in epic_lower:
                    self.epic_placeholders["<conception_epic>"] = fake_key
                    print(f"🔗 Mapped <conception_epic> -> {fake_key}")
                elif 'initiation' in epic_lower or 'm02' in epic_lower:
                    self.epic_placeholders["<initiation_epic>"] = fake_key
                    print(f"🔗 Mapped <initiation_epic> -> {fake_key}")
                elif 'enablement' in epic_lower or 'm03' in epic_lower:
                    self.epic_placeholders["<enablement_epic>"] = fake_key
                    print(f"🔗 Mapped <enablement_epic> -> {fake_key}")
                elif 'uat' in epic_lower or 'closure' in epic_lower or 'm04' in epic_lower:
                    self.epic_placeholders["<uat_closure_epic>"] = fake_key
                    print(f"🔗 Mapped <uat_closure_epic> -> {fake_key}")
            
            return {"key": fake_key, "id": f"dry-{len(self.created_issues) + 1}"}
        
        try:
            # Create issue using JIRA library
            issue = self.jira.create_issue(fields=issue_data["fields"])
            print(f"✅ Created: {issue.key} - {summary}")
            
            # If this is an epic, store its key for placeholder resolution
            if issue_type and issue_type.lower() == 'epic' and epic_name:
                # Map epic name to its key for future reference
                self.created_issues[epic_name] = issue.key
                
                # Map specific epic types to their placeholders
                epic_lower = epic_name.lower()
                if 'resource allocation' in epic_lower or 'm00' in epic_lower:
                    self.epic_placeholders["<resource_alocation_epic>"] = issue.key
                    print(f"🔗 Mapped <resource_alocation_epic> -> {issue.key}")
                elif 'conception' in epic_lower or 'm01' in epic_lower:
                    self.epic_placeholders["<conception_epic>"] = issue.key
                    print(f"🔗 Mapped <conception_epic> -> {issue.key}")
                elif 'initiation' in epic_lower or 'm02' in epic_lower:
                    self.epic_placeholders["<initiation_epic>"] = issue.key
                    print(f"🔗 Mapped <initiation_epic> -> {issue.key}")
                elif 'enablement' in epic_lower or 'm03' in epic_lower:
                    self.epic_placeholders["<enablement_epic>"] = issue.key
                    print(f"🔗 Mapped <enablement_epic> -> {issue.key}")
                elif 'uat' in epic_lower or 'closure' in epic_lower or 'm04' in epic_lower:
                    self.epic_placeholders["<uat_closure_epic>"] = issue.key
                    print(f"🔗 Mapped <uat_closure_epic> -> {issue.key}")
                
            return {"key": issue.key, "id": issue.id}
                
        except Exception as e:
            print(f"❌ Error creating issue '{summary}': {e}")
            return None
    
    def process_csv(self, csv_file):
        """Process CSV file and create issues"""
        created_count = 0
        failed_count = 0
        
        # Load configuration 
        config = self.load_config()
        
        try:
            # Read all rows first, filtering out comment lines
            all_rows = []
            with open(csv_file, 'r', encoding='utf-8') as file:
                # Filter out comment lines starting with #
                filtered_lines = [line for line in file if not line.strip().startswith('#')]
                
                # Reset file pointer and create reader with filtered content
                from io import StringIO
                filtered_content = ''.join(filtered_lines)
                reader = csv.DictReader(StringIO(filtered_content))
                for row_num, row in enumerate(reader, start=2):
                    # Skip configuration sections
                    first_col = row.get('Milestone', '').strip()
                    if first_col in ['General Configuration', 'Resource Allocation Tickets', 'Conception Tickets']:
                        break  # Stop processing when we hit configuration sections
                    
                    # Skip empty rows
                    if not any(value.strip() for value in row.values() if value):
                        continue
                        
                    all_rows.append((row_num, row))
            
            # Process in correct hierarchy: Project → Epic → Story/Tracker/Other
            project_rows = [(row_num, row) for row_num, row in all_rows if row.get('Issue Type', '').strip().lower() == 'project']
            epic_rows = [(row_num, row) for row_num, row in all_rows if row.get('Issue Type', '').strip().lower() == 'epic']
            other_rows = [(row_num, row) for row_num, row in all_rows if row.get('Issue Type', '').strip().lower() not in ['project', 'epic']]
            
            # Phase 1: Process Project issues - store first project issue key as parent
            if project_rows:
                print(f"\n🏗️  Phase 1: Processing {len(project_rows)} Project issues...")
                for row_num, row in project_rows:
                    print(f"\nProcessing project row {row_num}...")
                    result = self.create_issue_from_row(row, config)
                    if result:
                        created_count += 1
                        # Store first project issue as parent for <parent_link> references
                        if not self.parent_project_key:
                            self.parent_project_key = result['key']
                            print(f"🎯 Using {result['key']} as parent project key for <parent_link> references")
                    else:
                        failed_count += 1
            
            # Phase 2: Process Epic issues
            if epic_rows:
                print(f"\n📋 Phase 2: Processing {len(epic_rows)} Epic issues...")
                for row_num, row in epic_rows:
                    print(f"\nProcessing epic row {row_num}...")
                    result = self.create_issue_from_row(row, config)
                    if result:
                        created_count += 1
                    else:
                        failed_count += 1
            
            # Phase 3: Process Story/Tracker/Other issues
            if other_rows:
                print(f"\n📝 Phase 3: Processing {len(other_rows)} Story/Tracker/Other issues...")
                for row_num, row in other_rows:
                    print(f"\nProcessing row {row_num}...")
                    result = self.create_issue_from_row(row, config)
                    if result:
                        created_count += 1
                    else:
                        failed_count += 1
                        
        except FileNotFoundError:
            print(f"❌ File not found: {csv_file}")
            return
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
            return
        
        print(f"\n📊 Summary:")
        if self.dry_run:
            print(f"   🔍 Would create: {created_count} issues")
            print(f"   ❌ Would fail: {failed_count} issues")
        else:
            print(f"   ✅ Created: {created_count} issues")
            print(f"   ❌ Failed: {failed_count} issues")
        if self.parent_project_key:
            print(f"   🎯 Parent project issue: {self.parent_project_key}")

def main():
    print("Jira Bulk Issue Creator (Production)")
    print("=" * 40)
    
    # Check for dry-run flag
    dry_run = '--dry-run' in sys.argv or '--pretend' in sys.argv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Load configuration from metisara.conf
    config = configparser.ConfigParser()
    config.read('metisara.conf')
    
    JIRA_URL = config.get('jira', 'url', fallback='https://your-jira-instance.com/')
    USERNAME = config.get('jira', 'username', fallback='user@example.com')
    CSV_FILE = config.get('files', 'csv_file_output', fallback='project-tickets-processed.csv')
    
    print(f"Jira URL: {JIRA_URL}")
    print(f"Username: {USERNAME}")
    print(f"CSV File: {CSV_FILE}")
    if dry_run:
        print("Mode: DRY RUN (no issues will be created)")
    
    # Get API token from .env file, environment variable, or command line
    # Skip token requirement in dry-run mode
    api_token = None
    if not dry_run:
        api_token = os.getenv('JIRA_API_TOKEN')
        
        if not api_token:
            # Filter out dry-run flags when looking for token
            args = [arg for arg in sys.argv[1:] if arg not in ['--dry-run', '--pretend']]
            if args:
                api_token = args[0]
            else:
                print("Please provide API token via:")
                print("  .env file: Add JIRA_API_TOKEN=your_token to .env file")
                print("  Environment variable: export JIRA_API_TOKEN=your_token")
                print("  Command line: python3 ticket_creator.py your_token")
                print("  Or use --dry-run flag to simulate without token")
                sys.exit(1)
    
    # Automatically proceed without confirmation
    action = "simulating" if dry_run else "creating issues in"
    print(f"\nProcessing {CSV_FILE} and {action} Jira Production...")
    
    # Initialize bulk creator and process CSV
    creator = JiraBulkCreator(JIRA_URL, USERNAME, api_token, dry_run=dry_run)
    creator.process_csv(CSV_FILE)

if __name__ == "__main__":
    main()