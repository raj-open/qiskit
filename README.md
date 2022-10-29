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

Users, who wish to use IBM's cloud backend need an [API-token](https://quantum-computing.ibm.com/account). Copy the [.env](templates/.env) file from the [./templates](templates) folder
into the root directory of the repository and insert the API token. E.g. if the token is `a0ad9scjo23u0kaslodi` the file should like this:

```env
TOKEN=a0ad9scjo23u0kaslodi
URL=https://auth.quantum-computing.ibm.com/api
HUB=ibm-q
GROUP=open
PROJECT=main
SEED=12345678
```

### Execution ###

Open the desired notebook from [./notebooks](notebooks) in _e.g._ VSCode
(with appropriate jupyter extensions installed).
Or run
```bash
just notebook xyz # do not include the ipynb extension!
```
to run the notebook `xyz.ipynb` in a browser.

## IBM Lab ##

- **API Key:** <https://quantum-computing.ibm.com/account>.
- **Job monitoring/cancellation:** <https://quantum-computing.ibm.com/jobs>.

**NOTE:** Queued jobs in the cloud can sometimes take hours.
Keep the size of experiments small
(_e.g._ small circuit sizes, small numbers of samples, small number of shots)
or cancel + delete old jobs, that are still pending and which are no longer needed.
