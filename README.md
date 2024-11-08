# sram-graph-vis

[![Python 3.13](https://img.shields.io/badge/python-3.13-e72ac9.svg)](https://www.python.org/downloads/release/python-3130/)
[![Code style: Ruff](https://img.shields.io/badge/code_style-ruff-black.svg)](https://github.com/astral-sh/ruff)

Python code to visualise SRAM

## Prerequisite

The project uses `pdm` as a Python package management tool. See [pdm](https://pdm-project.org/en/latest/)
for more information on how to use the tool and how to install it.

Quick `pdm` installing [instructions](https://pdm-project.org/en/latest/#other-installation-methods)

## How to visualise SRAM relations and dependencies

```bash
pdm run draw_graph.py
```

## Notes

### Adding Python packages

To add a new Python package use:

```bash
pdm add <packagge>
```

and commit `pdm.lock`

### Obtaining a Python version

In case your standard packaging tool does not provide a python version you are
looking for, you van use `pyenv`. It will download, compile if necessary, all
necessary bits and pieces for the requested Python version.

#### How to get `pyenv`

If you trust the source, use:

```bash
curl https://pyenv.run | bash
```

More information can be found at [pyenv](https://github.com/pyenv/pyenv/blob/master/README.md) itself.

#### How to get you Python version

Run `pyenv` as follows:

```bash
pyenv install 3.13.0
```

Once `pyenv` has finished, running `pdm install` should install Python 3.13.0
in the newly created virtual environment. In case `pyenv` sees multiple
candidate, it will ask for the correct one to use.
