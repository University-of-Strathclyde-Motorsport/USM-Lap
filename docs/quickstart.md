# Quickstart

## Requirements

- [git](https://git-scm.com/install/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

Clone the latest version of the git repository:

```sh
git clone https://github.com/University-of-Strathclyde-Motorsport/USM-Lap.git
```

Use uv to install dependencies and set up the virtual environment:

```sh
uv sync
```

Finally, check that installation was successful:

```sh
uv run usmlap hello
```

This command should print `"Hello from USM Lap!"`

## Usage

Check out [Tutorials](tutorials.md) to find out how to run your first sim.

To view the full list of available commands:

```sh
uv run usmlap --help
```
