#!/usr/bin/env python3
"""
Git Repository Cloner Tool

A tool to clone git repositories into an organized folder structure and maintain
an index of repositories with their metadata.

Usage:
    python git-cloner.py <git_url>         # Clone a repository
    python git-cloner.py <org_user_url>   # Clone all repos from org/user
    python git-cloner.py --sync           # Sync all indexed repositories
    python git-cloner.py --list           # List all indexed repositories
    python git-cloner.py --help           # Show help
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


class GitCloner:
    def __init__(self, base_dir=None):
        """Initialize the Git Cloner with base directory."""
        self.base_dir = Path(base_dir) if base_dir else Path.home() / "code"
        self.index_file = self.base_dir / "repos.jsonl"
        
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def is_org_user_url(self, url):
        """Check if the URL is for an organization/user page rather than a specific repo."""
        try:
            parsed = urlparse(url)
            path = parsed.path.strip("/")
            
            # Remove trailing slash if present
            if path.endswith("/"):
                path = path[:-1]
            
            # Check if it's a user/org URL (only one path segment)
            path_segments = path.split("/")
            return len(path_segments) == 1 and path_segments[0] != ""
        except:
            return False
    
    def parse_org_user_url(self, url):
        """Parse an organization/user URL and extract host and org/user name."""
        try:
            parsed = urlparse(url)
            host = parsed.netloc
            path = parsed.path.strip("/")
            
            # Remove trailing slash if present
            if path.endswith("/"):
                path = path[:-1]
            
            path_segments = path.split("/")
            if len(path_segments) != 1 or path_segments[0] == "":
                raise ValueError(f"Invalid org/user URL format: {url}")
            
            org_user = path_segments[0]
            return host, org_user
        except Exception as e:
            raise ValueError(f"Failed to parse org/user URL '{url}': {e}")
    
    def parse_git_url(self, git_url):
        """Parse a git URL and extract host, org/user, and repository name."""
        # Handle SSH URLs (git@github.com:user/repo.git)
        if git_url.startswith("git@"):
            parts = git_url.split(":")
            if len(parts) != 2:
                raise ValueError(f"Invalid SSH git URL format: {git_url}")
            
            host = parts[0].split("@")[1]
            path_part = parts[1]
            
            # Remove .git suffix if present
            if path_part.endswith(".git"):
                path_part = path_part[:-4]
            
            path_segments = path_part.split("/")
            if len(path_segments) != 2:
                raise ValueError(f"Invalid SSH git URL format: {git_url}")
            
            org, repo = path_segments
            return host, org, repo
        
        # Handle HTTPS URLs
        try:
            parsed = urlparse(git_url)
            host = parsed.netloc
            path = parsed.path.strip("/")
            
            # Remove .git suffix if present
            if path.endswith(".git"):
                path = path[:-4]
            
            path_segments = path.split("/")
            if len(path_segments) != 2:
                raise ValueError(f"Invalid git URL format: {git_url}")
            
            org, repo = path_segments
            return host, org, repo
        except Exception as e:
            raise ValueError(f"Failed to parse git URL '{git_url}': {e}")
    
    def get_local_path(self, host, org, repo):
        """Generate the local path for a repository."""
        return self.base_dir / host / org / repo
    
    def get_git_info(self, repo_path):
        """Get current branch and latest commit hash from a git repository."""
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            branch = result.stdout.strip()
            
            # Get latest commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = result.stdout.strip()
            
            return branch, commit_hash
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get git info: {e}")
    
    def fetch_github_repos(self, host, org_user):
        """Fetch all repositories for a GitHub organization or user."""
        if host != "github.com":
            raise ValueError(f"API fetching only supported for GitHub, not {host}")
        
        repos = []
        page = 1
        per_page = 100
        
        while True:
            try:
                # Try org endpoint first, then user endpoint if that fails
                api_urls = [
                    f"https://api.github.com/orgs/{org_user}/repos?page={page}&per_page={per_page}",
                    f"https://api.github.com/users/{org_user}/repos?page={page}&per_page={per_page}"
                ]
                
                response_data = None
                for api_url in api_urls:
                    try:
                        with urllib.request.urlopen(api_url) as response:
                            if response.status == 200:
                                response_data = json.loads(response.read().decode('utf-8'))
                                break
                    except urllib.error.HTTPError as e:
                        if e.code == 404:
                            continue  # Try next URL
                        else:
                            raise
                
                if response_data is None:
                    raise ValueError(f"Organization or user '{org_user}' not found")
                
                if not response_data:  # Empty page, we're done
                    break
                
                for repo_data in response_data:
                    repos.append({
                        'name': repo_data['name'],
                        'clone_url': repo_data['clone_url'],
                        'ssh_url': repo_data['ssh_url'],
                        'default_branch': repo_data['default_branch'],
                        'description': repo_data.get('description', ''),
                        'private': repo_data['private'],
                        'fork': repo_data['fork']
                    })
                
                page += 1
                
                # Rate limiting - be nice to the API
                time.sleep(0.1)
                
            except urllib.error.HTTPError as e:
                if e.code == 403:  # Rate limited
                    print("⚠️  Rate limited by GitHub API. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    raise RuntimeError(f"GitHub API error: {e}")
            except Exception as e:
                raise RuntimeError(f"Failed to fetch repositories: {e}")
        
        return repos
    
    def clone_org_user_repos(self, url, branch=None, include_forks=False):
        """Clone all repositories from an organization or user."""
        try:
            # Parse the org/user URL
            host, org_user = self.parse_org_user_url(url)
            
            print(f"Fetching repositories for {org_user} from {host}...")
            
            # Fetch repositories
            repos = self.fetch_github_repos(host, org_user)
            
            if not repos:
                print(f"No repositories found for {org_user}")
                return 0
            
            # Filter out forks if requested
            if not include_forks:
                original_count = len(repos)
                repos = [repo for repo in repos if not repo['fork']]
                if len(repos) < original_count:
                    print(f"Filtered out {original_count - len(repos)} forks")
            
            print(f"Found {len(repos)} repositories to clone")
            
            cloned_count = 0
            skipped_count = 0
            
            for repo in repos:
                try:
                    # Use HTTPS URL by default
                    repo_url = repo['clone_url']
                    print(f"\n📦 Cloning {org_user}/{repo['name']}")
                    
                    if repo['description']:
                        print(f"   📝 {repo['description']}")
                    
                    # Clone the repository
                    success = self.clone_repository(repo_url, branch)
                    if success:
                        cloned_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    print(f"❌ Failed to clone {repo['name']}: {e}")
                    skipped_count += 1
            
            print(f"\n✅ Bulk clone complete!")
            print(f"   📦 Cloned: {cloned_count} repositories")
            print(f"   ⏭️  Skipped: {skipped_count} repositories")
            
            return cloned_count
            
        except Exception as e:
            print(f"Error in bulk clone: {e}")
            return 0
    
    def clone_repository(self, git_url, branch=None):
        """Clone a git repository to the organized directory structure."""
        try:
            # Parse the git URL
            host, org, repo = self.parse_git_url(git_url)
            local_path = self.get_local_path(host, org, repo)
            
            # Check if directory already exists
            if local_path.exists():
                print(f"Repository already exists at: {local_path}")
                print("Use --sync to update existing repositories")
                return False
            
            # Create parent directories
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Clone the repository
            clone_cmd = ["git", "clone", git_url, str(local_path)]
            if branch:
                clone_cmd.extend(["-b", branch])
            
            print(f"Cloning {git_url} to {local_path}")
            subprocess.run(clone_cmd, check=True)
            
            # Get git info
            current_branch, commit_hash = self.get_git_info(local_path)
            
            # Create index entry
            index_entry = {
                "url": git_url,
                "local_path": str(local_path),
                "host": host,
                "org": org,
                "repo": repo,
                "branch": current_branch,
                "last_hash": commit_hash,
                "last_pull": datetime.now().isoformat()
            }
            
            # Add to index
            self.add_to_index(index_entry)
            
            print(f"Successfully cloned and indexed repository")
            print(f"Local path: {local_path}")
            print(f"Branch: {current_branch}")
            print(f"Commit: {commit_hash}")
            
            return True
            
        except Exception as e:
            print(f"Error cloning repository: {e}")
            return False
    
    def add_to_index(self, entry):
        """Add or update an entry in the index file."""
        # Read existing entries
        entries = self.read_index()
        
        # Check if entry already exists (by URL)
        existing_index = None
        for i, existing_entry in enumerate(entries):
            if existing_entry["url"] == entry["url"]:
                existing_index = i
                break
        
        # Update existing or add new entry
        if existing_index is not None:
            entries[existing_index] = entry
        else:
            entries.append(entry)
        
        # Write back to index file
        self.write_index(entries)
    
    def read_index(self):
        """Read the index file and return list of entries."""
        if not self.index_file.exists():
            return []
        
        entries = []
        try:
            with open(self.index_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception as e:
            print(f"Error reading index file: {e}")
            return []
        
        return entries
    
    def write_index(self, entries):
        """Write entries to the index file."""
        try:
            with open(self.index_file, 'w') as f:
                for entry in entries:
                    f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"Error writing index file: {e}")
    
    def sync_repositories(self):
        """Sync all repositories in the index."""
        entries = self.read_index()
        
        if not entries:
            print("No repositories found in index")
            return
        
        print(f"Syncing {len(entries)} repositories...")
        
        for entry in entries:
            try:
                local_path = Path(entry["local_path"])
                
                if not local_path.exists():
                    print(f"⚠️  Repository not found: {local_path}")
                    continue
                
                print(f"📥 Syncing {entry['org']}/{entry['repo']}")
                
                # Pull latest changes
                subprocess.run(
                    ["git", "pull", "origin"],
                    cwd=local_path,
                    check=True,
                    capture_output=True
                )
                
                # Update index with new info
                branch, commit_hash = self.get_git_info(local_path)
                entry["branch"] = branch
                entry["last_hash"] = commit_hash
                entry["last_pull"] = datetime.now().isoformat()
                
                print(f"✅ Updated {entry['org']}/{entry['repo']} ({commit_hash[:8]})")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to sync {entry['org']}/{entry['repo']}: {e}")
            except Exception as e:
                print(f"❌ Error syncing {entry['org']}/{entry['repo']}: {e}")
        
        # Write updated index
        self.write_index(entries)
        print("Sync complete!")
    
    def list_repositories(self):
        """List all repositories in the index."""
        entries = self.read_index()
        
        if not entries:
            print("No repositories found in index")
            return
        
        print(f"Found {len(entries)} repositories:")
        print()
        
        for entry in entries:
            print(f"📁 {entry['org']}/{entry['repo']}")
            print(f"   URL: {entry['url']}")
            print(f"   Path: {entry['local_path']}")
            print(f"   Branch: {entry['branch']}")
            print(f"   Last Hash: {entry['last_hash'][:8]}...")
            print(f"   Last Pull: {entry['last_pull']}")
            print()


def main():
    """Main entry point for the git-cloner tool."""
    parser = argparse.ArgumentParser(
        description="Clone git repositories into an organized folder structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://github.com/user/repo.git        # Clone single repo
  %(prog)s https://github.com/username              # Clone all user repos
  %(prog)s https://github.com/organization          # Clone all org repos
  %(prog)s git@github.com:user/repo.git
  %(prog)s --sync
  %(prog)s --list
        """
    )
    
    parser.add_argument(
        "git_url",
        nargs="?",
        help="Git repository URL or organization/user URL to clone"
    )
    
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sync all repositories in the index"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all repositories in the index"
    )
    
    parser.add_argument(
        "--base-dir",
        help="Base directory for repositories (default: ~/code)"
    )
    
    parser.add_argument(
        "--branch",
        help="Specific branch to clone (default: repository default)"
    )
    
    parser.add_argument(
        "--include-forks",
        action="store_true",
        help="Include forked repositories when cloning from org/user"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.git_url, args.sync, args.list]):
        parser.print_help()
        sys.exit(1)
    
    if sum([bool(args.git_url), args.sync, args.list]) > 1:
        print("Error: Please specify only one operation")
        sys.exit(1)
    
    # Initialize cloner
    cloner = GitCloner(args.base_dir)
    
    # Execute requested operation
    try:
        if args.git_url:
            # Check if it's an org/user URL or a specific repository URL
            if cloner.is_org_user_url(args.git_url):
                # Bulk clone all repositories from org/user
                count = cloner.clone_org_user_repos(args.git_url, args.branch, args.include_forks)
                sys.exit(0 if count > 0 else 1)
            else:
                # Clone single repository
                success = cloner.clone_repository(args.git_url, args.branch)
                sys.exit(0 if success else 1)
        elif args.sync:
            cloner.sync_repositories()
        elif args.list:
            cloner.list_repositories()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()