# Git Repository Cloner

A Python tool to clone git repositories into an organized folder structure and maintain an index of repositories with their metadata.

## Features

- **Organized Directory Structure**: Clones repositories into `~/code/{git_host}/{org_or_user}/{repo_name}/`
- **Repository Index**: Maintains a JSON Lines index file with repository metadata
- **Multiple Git URL Formats**: Supports both HTTPS and SSH git URLs
- **Bulk Organization/User Cloning**: Clone all repositories from a GitHub organization or user
- **Synchronization**: Bulk sync all indexed repositories
- **Repository Listing**: View all indexed repositories with their status

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install git-cloner
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/git-cloner.git
cd git-cloner

# Install in development mode
pip install -e .

# Or run the install script
./install.sh
```

### Option 3: Run Without Installation

```bash
# Clone and run directly
git clone https://github.com/yourusername/git-cloner.git
cd git-cloner
python -m git_cloner --help
```

### Requirements

- Python 3.6 or higher
- Git command-line tool
- Network access to git repositories

## Usage

### Clone a Repository

```bash
# Clone using HTTPS URL
git-cloner https://github.com/user/repo.git

# Clone using SSH URL
git-cloner git@github.com:user/repo.git

# Clone a specific branch
git-cloner https://github.com/user/repo.git --branch develop
```

### Clone All Repositories from Organization/User

```bash
# Clone all repositories from a GitHub user
git-cloner https://github.com/username

# Clone all repositories from a GitHub organization
git-cloner https://github.com/organization

# Include forked repositories
git-cloner https://github.com/username --include-forks

# Clone all repos from org with specific branch (if available)
git-cloner https://github.com/organization --branch develop
```

### Sync All Repositories

```bash
# Pull latest changes for all indexed repositories
git-cloner --sync
```

### List All Repositories

```bash
# Show all indexed repositories with their status
git-cloner --list
```

### Custom Base Directory

```bash
# Use a custom base directory instead of ~/code
git-cloner https://github.com/user/repo.git --base-dir /path/to/repos
```

## Directory Structure

The tool organizes repositories in the following structure:

```
~/code/
├── github.com/
│   ├── user1/
│   │   ├── repo1/
│   │   └── repo2/
│   └── user2/
│       └── repo3/
├── gitlab.com/
│   └── organization/
│       └── project/
└── repos.jsonl  # Index file
```

## Index File Format

The `repos.jsonl` file contains one JSON object per line with the following structure:

```json
{
  "url": "https://github.com/user/repo.git",
  "local_path": "/home/user/code/github.com/user/repo",
  "host": "github.com",
  "org": "user",
  "repo": "repo",
  "branch": "main",
  "last_hash": "abc123def456...",
  "last_pull": "2024-01-15T10:30:00.123456"
}
```

## Examples

### Basic Usage

```bash
# Clone a repository
$ git-cloner https://github.com/torvalds/linux.git

Cloning https://github.com/torvalds/linux.git to /home/user/code/github.com/torvalds/linux
Successfully cloned and indexed repository
Local path: /home/user/code/github.com/torvalds/linux
Branch: master
Commit: abc123def456...
```

### Bulk Clone Organization/User

```bash
# Clone all repositories from a user
$ git-cloner https://github.com/octocat

Fetching repositories for octocat from github.com...
Found 8 repositories to clone

📦 Cloning octocat/Hello-World
   📝 My first repository on GitHub!
Successfully cloned and indexed repository
Local path: /home/user/code/github.com/octocat/Hello-World
Branch: master
Commit: 7fd1a60b...

📦 Cloning octocat/Spoon-Knife
   📝 This repo is for demonstration purposes only.
Successfully cloned and indexed repository
Local path: /home/user/code/github.com/octocat/Spoon-Knife
Branch: main
Commit: d0dd1f61...

✅ Bulk clone complete!
   📦 Cloned: 8 repositories
   ⏭️  Skipped: 0 repositories
```

### Sync All Repositories

```bash
$ git-cloner --sync

Syncing 5 repositories...
📥 Syncing torvalds/linux
✅ Updated torvalds/linux (abc123de)
📥 Syncing user/repo1
✅ Updated user/repo1 (def456ab)
📥 Syncing user/repo2
✅ Updated user/repo2 (789cdef0)
Sync complete!
```

### List Repositories

```bash
$ git-cloner --list

Found 3 repositories:

📁 torvalds/linux
   URL: https://github.com/torvalds/linux.git
   Path: /home/user/code/github.com/torvalds/linux
   Branch: master
   Last Hash: abc123de...
   Last Pull: 2024-01-15T10:30:00.123456

📁 user/repo1
   URL: https://github.com/user/repo1.git
   Path: /home/user/code/github.com/user/repo1
   Branch: main
   Last Hash: def456ab...
   Last Pull: 2024-01-15T10:32:15.789012
```

## Alternative Usage

If you don't want to install the package, you can still run it directly:

```bash
# After cloning the repository
python -m git_cloner --help
python -m git_cloner https://github.com/user/repo.git

# Or use the original script
python git-cloner.py --help
```

## Supported Git Hosts

The tool supports any git host that provides standard git URLs, including:

- GitHub (github.com)
- GitLab (gitlab.com)
- Bitbucket (bitbucket.org)
- Self-hosted Git servers
- Any git server accessible via HTTPS or SSH

## Error Handling

The tool includes comprehensive error handling for:

- Invalid git URLs
- Network connectivity issues
- Permission problems
- Repository conflicts
- Git command failures

## Requirements

- Python 3.6 or higher
- Git command-line tool
- Network access to git repositories

## License

This tool is provided as-is for educational and development purposes.