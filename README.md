# `qiskit` #

This repository contains basic `qiskit` code in the form of submodules (see in particular the [./src/algorithms](src/algorithms) folder) and [./notebooks](notebooks).
All scripts were created by the owner of the repository, unless otherwise stated.

## Usage ##

### System requirements ###

Windows users are first recommended to install

- [bash](https://gitforwindows.org);
- [Chocolatey](https://chocolatey.org/install).

All users:

- [python 3.10.x](https://www.python.org/downloads/);
- the [justfile tool](https://github.com/casey/just#installation).

### Setup ###

Run
```bash
just build
```
or
```
python3 -m pip install -r requirements.txt
# windows users:
py -3 -m pip install -r requirements.txt
```

### Execution ###

Open the desired notebook from [./notebooks](notebooks) in _e.g._ VSCode
(with appropriate jupyter extensions installed).
Or run
```bash
just notebook xyz # do not include the ipynb extension!
```
to run the notebook `xyz.ipynb` in a browser.
