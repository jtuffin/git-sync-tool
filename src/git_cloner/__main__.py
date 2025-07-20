"""
Main entry point for the git-cloner command-line tool.
"""

import argparse
import os
import sys
from .git_cloner import GitCloner


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
  %(prog)s --base-dir /path/to/repos https://github.com/user/repo.git
  export REPOS_BASE_DIR=/path/to/repos && %(prog)s --sync
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
        help="Base directory for repositories (default: ~/code, or REPOS_BASE_DIR env var)"
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
    
    # Initialize cloner with base directory priority: CLI arg > env var > default
    base_dir = args.base_dir or os.environ.get('REPOS_BASE_DIR')
    cloner = GitCloner(base_dir)
    
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