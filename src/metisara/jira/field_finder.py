#!/usr/bin/env python3

import requests
import json
import os
import configparser
from dotenv import load_dotenv

def find_jira_fields():
    """Query Jira to find available custom fields"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Load configuration from metisara.conf
    config = configparser.ConfigParser()
    config.read('metisara.conf')
    
    JIRA_URL = config.get('jira', 'url', fallback='https://your-jira-instance.com/')
    api_token = os.getenv('JIRA_API_TOKEN')
    
    if not api_token:
        print("Please set JIRA_API_TOKEN in .env file")
        return
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }
    
    # Get all fields
    url = f"{JIRA_URL.rstrip('/')}/rest/api/2/field"
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            fields = response.json()
            
            print("🔍 Searching for Epic, Story Points, Parent, and Target Start fields...\n")
            
            epic_fields = []
            story_point_fields = []
            parent_fields = []
            target_start_fields = []
            
            for field in fields:
                field_name = field.get('name', '').lower()
                field_id = field.get('id', '')
                field_type = field.get('schema', {}).get('type', '')
                
                # Look for Epic related fields
                if 'epic' in field_name:
                    epic_fields.append({
                        'id': field_id,
                        'name': field.get('name'),
                        'type': field_type,
                        'custom': field.get('custom', False)
                    })
                
                # Look for Story Points related fields
                if 'story' in field_name and 'point' in field_name:
                    story_point_fields.append({
                        'id': field_id,
                        'name': field.get('name'),
                        'type': field_type,
                        'custom': field.get('custom', False)
                    })
                
                # Look for Parent related fields
                if 'parent' in field_name or field_id == 'parent':
                    parent_fields.append({
                        'id': field_id,
                        'name': field.get('name'),
                        'type': field_type,
                        'custom': field.get('custom', False)
                    })
                
                # Look for Target Start related fields
                if 'target' in field_name and 'start' in field_name:
                    target_start_fields.append({
                        'id': field_id,
                        'name': field.get('name'),
                        'type': field_type,
                        'custom': field.get('custom', False)
                    })
            
            print("📝 Epic-related fields:")
            for field in epic_fields:
                print(f"   {field['id']}: {field['name']} (Type: {field['type']}, Custom: {field['custom']})")
            
            print("\n📊 Story Points-related fields:")
            for field in story_point_fields:
                print(f"   {field['id']}: {field['name']} (Type: {field['type']}, Custom: {field['custom']})")
            
            print("\n🔗 Parent-related fields:")
            for field in parent_fields:
                print(f"   {field['id']}: {field['name']} (Type: {field['type']}, Custom: {field['custom']})")
            
            print("\n🎯 Target Start-related fields:")
            for field in target_start_fields:
                print(f"   {field['id']}: {field['name']} (Type: {field['type']}, Custom: {field['custom']})")
            
            # Show key field mappings for bulk create script
            print("\n🎯 Key Field Mappings for Bulk Create Script:")
            print("   Epic Name: customfield_12311141")
            print("   Epic Link: customfield_12311140") 
            print("   Parent Link: customfield_12313140")
            print("   Story Points: customfield_12310243")
            if target_start_fields:
                print(f"   Target Start: {target_start_fields[0]['id']}")
            else:
                print("   Target Start: Not available")
            
            if not epic_fields and not story_point_fields and not parent_fields and not target_start_fields:
                print("❌ No Epic, Story Points, Parent, or Target Start fields found")
                print("\n🔍 Showing all custom fields for reference:")
                custom_fields = [f for f in fields if f.get('custom', False)]
                for field in custom_fields[:20]:  # Show first 20 custom fields
                    print(f"   {field['id']}: {field.get('name')} (Type: {field.get('schema', {}).get('type', 'unknown')})")
                if len(custom_fields) > 20:
                    print(f"   ... and {len(custom_fields) - 20} more custom fields")
        
        else:
            print(f"❌ Failed to get fields: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error querying Jira: {e}")

if __name__ == "__main__":
    find_jira_fields()