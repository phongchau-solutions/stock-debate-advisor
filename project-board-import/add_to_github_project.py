#!/usr/bin/env python3
"""
Script to add extracted phases, features, and user stories to GitHub Project Board.
Requires: GITHUB_TOKEN environment variable or --token parameter
Usage: python add_to_github_project.py [--token YOUR_TOKEN] [--dry-run]
"""

import json
import os
import sys
import argparse
import requests
from typing import List, Dict, Optional

# GitHub GraphQL API endpoint
GRAPHQL_API = "https://api.github.com/graphql"

# Organization and Project details
ORG_NAME = "phongchau-solutions"
PROJECT_NUMBER = 2


def get_project_id(token: str, org: str, project_number: int) -> Optional[str]:
    """Get the project ID (node ID) from organization and project number."""
    query = """
    query($org: String!, $number: Int!) {
      organization(login: $org) {
        projectV2(number: $number) {
          id
          title
        }
      }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    response = requests.post(
        GRAPHQL_API,
        json={"query": query, "variables": {"org": org, "number": project_number}},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Error fetching project: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}")
        return None
    
    project = data.get("data", {}).get("organization", {}).get("projectV2")
    if project:
        print(f"Found project: {project['title']} (ID: {project['id']})")
        return project['id']
    
    return None


def add_draft_issue(token: str, project_id: str, title: str, body: str) -> Optional[str]:
    """Add a draft issue to the project."""
    mutation = """
    mutation($projectId: ID!, $title: String!, $body: String!) {
      addProjectV2DraftIssue(input: {
        projectId: $projectId
        title: $title
        body: $body
      }) {
        projectItem {
          id
        }
      }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    response = requests.post(
        GRAPHQL_API,
        json={
            "query": mutation,
            "variables": {
                "projectId": project_id,
                "title": title,
                "body": body
            }
        },
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Error adding item '{title}': {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    if "errors" in data:
        print(f"GraphQL errors for '{title}': {data['errors']}")
        return None
    
    item = data.get("data", {}).get("addProjectV2DraftIssue", {}).get("projectItem")
    if item:
        return item['id']
    
    return None


def process_phases(token: str, project_id: str, phases: List[Dict], dry_run: bool = False) -> Dict:
    """Process all phases and add items to the project board."""
    stats = {
        "phases": 0,
        "deliverables": 0,
        "user_stories": 0,
        "failed": 0
    }
    
    for phase in phases:
        phase_name = f"Phase {phase['phase_number']}: {phase['phase_name']}"
        timeline = phase['timeline']
        description = phase['description']
        
        # Add phase as epic/milestone
        phase_title = f"🎯 {phase_name}"
        phase_body = f"""**Timeline:** {timeline}

**Description:** {description}

**Status:** Planning

---
*This is a phase epic that groups related deliverables and user stories.*
"""
        
        print(f"\n{'[DRY RUN] ' if dry_run else ''}Adding phase: {phase_name}")
        
        if not dry_run:
            item_id = add_draft_issue(token, project_id, phase_title, phase_body)
            if item_id:
                stats["phases"] += 1
                print(f"  ✓ Phase added successfully")
            else:
                stats["failed"] += 1
                print(f"  ✗ Failed to add phase")
        else:
            stats["phases"] += 1
            print(f"  [Would add phase: {phase_title}]")
        
        # Add deliverables
        for deliverable in phase['deliverables']:
            item_title = f"📦 {deliverable['title']}"
            item_body = f"""**ID:** {deliverable['id']}
**Phase:** {phase_name}
**Type:** {deliverable['type']}
**Status:** {deliverable['status']}
**Timeline:** {timeline}

---
*Deliverable for {phase_name}*
"""
            
            if not dry_run:
                item_id = add_draft_issue(token, project_id, item_title, item_body)
                if item_id:
                    stats["deliverables"] += 1
                    print(f"  ✓ Deliverable: {deliverable['title']}")
                else:
                    stats["failed"] += 1
                    print(f"  ✗ Failed: {deliverable['title']}")
            else:
                stats["deliverables"] += 1
        
        # Add user stories
        for story in phase['user_stories']:
            story_title = f"👤 {story['title']}"
            story_body = f"""**ID:** {story['id']}
**Phase:** {phase_name}
**Timeline:** {timeline}

**Acceptance Criteria:**
{story['acceptance_criteria']}

---
*User story for {phase_name}*
"""
            
            if not dry_run:
                item_id = add_draft_issue(token, project_id, story_title, story_body)
                if item_id:
                    stats["user_stories"] += 1
                    print(f"  ✓ User Story: {story['title'][:50]}...")
                else:
                    stats["failed"] += 1
                    print(f"  ✗ Failed: {story['title'][:50]}...")
            else:
                stats["user_stories"] += 1
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Add phases, features, and user stories to GitHub Project Board"
    )
    parser.add_argument(
        "--token",
        help="GitHub personal access token (or set GITHUB_TOKEN env var)",
        default=os.getenv("GITHUB_TOKEN")
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be added without actually adding items"
    )
    parser.add_argument(
        "--data-file",
        default="/tmp/extracted_phases_features_stories.json",
        help="Path to the extracted data JSON file"
    )
    
    args = parser.parse_args()
    
    if not args.token and not args.dry_run:
        print("Error: GitHub token is required. Set GITHUB_TOKEN env var or use --token")
        print("To create a token: https://github.com/settings/tokens")
        print("Required scopes: project, repo")
        sys.exit(1)
    
    # Load extracted data
    try:
        with open(args.data_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found: {args.data_file}")
        sys.exit(1)
    
    print(f"Loaded data from: {args.data_file}")
    print(f"Source: {data['metadata']['source']}")
    print(f"Project Board: {data['metadata']['project_board_url']}")
    print(f"\nTotal items to add:")
    print(f"  - Phases: {len(data['phases'])}")
    total_deliverables = sum(len(p['deliverables']) for p in data['phases'])
    total_stories = sum(len(p['user_stories']) for p in data['phases'])
    print(f"  - Deliverables: {total_deliverables}")
    print(f"  - User Stories: {total_stories}")
    print(f"  - Total: {len(data['phases']) + total_deliverables + total_stories}")
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No items will be added")
    else:
        print("\n🚀 Getting project ID...")
        project_id = get_project_id(args.token, ORG_NAME, PROJECT_NUMBER)
        if not project_id:
            print("Error: Could not get project ID")
            sys.exit(1)
    
    # Process phases
    print("\n" + "="*60)
    print("ADDING ITEMS TO PROJECT BOARD")
    print("="*60)
    
    stats = process_phases(
        args.token if not args.dry_run else "",
        project_id if not args.dry_run else "",
        data['phases'],
        dry_run=args.dry_run
    )
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Phases added:        {stats['phases']}")
    print(f"Deliverables added:  {stats['deliverables']}")
    print(f"User stories added:  {stats['user_stories']}")
    print(f"Failed:              {stats['failed']}")
    print(f"Total:               {stats['phases'] + stats['deliverables'] + stats['user_stories']}")
    
    if args.dry_run:
        print("\n⚠️  This was a dry run. Use without --dry-run to actually add items.")
    else:
        print(f"\n✅ All items have been added to the project board!")
        print(f"View at: https://github.com/orgs/{ORG_NAME}/projects/{PROJECT_NUMBER}")


if __name__ == "__main__":
    main()
