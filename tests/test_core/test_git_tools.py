"""Unit tests for the `usmlap.core.git_tools` module."""

import git

from usmlap.core.git_tools import get_git_hash, get_repository


def test_get_repository():
    repo = get_repository()
    assert isinstance(repo, git.Repo)


def test_get_git_hash():
    git_hash = get_git_hash()
    assert isinstance(git_hash, str)
