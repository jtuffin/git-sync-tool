# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation & Setup
```bash
# Install in development mode
pip install -e .

# Or use the install script
./install.sh

# Run without installation
python -m git_cloner --help
```

### Testing the CLI
```bash
# Test CLI entry points
git-cloner --help
python -m git_cloner --help

# Test basic functionality
git-cloner --list
git-cloner --sync
```

### Package Building
```bash
# Build package
python -m build

# Install from local build
pip install dist/git_cloner-1.0.0-py3-none-any.whl
```

## Architecture Overview

This is a Python CLI tool that provides organized Git repository management with the following structure:

### Core Components

**GitCloner Class** (`src/git_cloner/git_cloner.py`):
- Main business logic for cloning, syncing, and managing repositories
- Handles both single repository and bulk organization/user cloning
- Maintains a JSONL index file (`~/code/repos.jsonl`) with repository metadata
- Supports both HTTPS and SSH Git URLs
- Integrates with GitHub API for bulk operations

**CLI Interface** (`src/git_cloner/__main__.py`):
- Command-line argument parsing and validation
- Entry point for the `git-cloner` command
- Handles three main operations: clone, sync, list

### Key Features

**Directory Organization**: Repositories are cloned into `~/code/{host}/{org}/{repo}/` structure (e.g., `~/code/github.com/user/repo/`)

**Repository Index**: JSON Lines format storing metadata:
- URL, local path, host, org, repo name
- Current branch, last commit hash, last pull timestamp

**Bulk Operations**: 
- Clone all repositories from GitHub organizations/users
- Sync all indexed repositories with latest changes
- List all managed repositories with status

**URL Parsing**: Handles multiple Git URL formats including SSH (`git@github.com:user/repo.git`) and HTTPS (`https://github.com/user/repo.git`)

## Package Structure

- `src/git_cloner/`: Main package directory
  - `__init__.py`: Package initialization
  - `__main__.py`: CLI entry point and argument parsing
  - `git_cloner.py`: Core GitCloner class with all business logic
- `pyproject.toml`: Python package configuration and metadata
- `install.sh`: Development installation script

## Key Implementation Details

- Uses `subprocess` for Git operations rather than GitPython for minimal dependencies
- GitHub API integration for fetching organization/user repositories
- Rate limiting and error handling for API calls
- Cross-platform path handling using `pathlib.Path`
- JSONL format for the index file allows for atomic updates and easy parsing