"""
Git Cloner - A smart Git repository management and cloning tool.

This package provides functionality to clone git repositories into an organized
folder structure and maintain an index of repositories with their metadata.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .git_cloner import GitCloner

__all__ = ["GitCloner"]