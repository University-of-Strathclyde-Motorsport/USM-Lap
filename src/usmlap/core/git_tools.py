"""
This module provides access to git repository information.
"""

import git

from usmlap.core.filepath import PROJECT_ROOT


def get_repository() -> git.Repo:
    """Get the current project repository."""
    return git.Repo(PROJECT_ROOT)


def get_git_hash() -> str:
    """Get the hash of the current commit."""
    repo = get_repository()
    return repo.head.object.hexsha
