# Release Dashboard
[![Build Status](https://travis-ci.org/ashcrow/release-dashboard.svg)](https://travis-ci.org/ashcrow/release-dashboard)

## Requirements

- python3
- python3-libguestfs
- bs4 (python3-beautifulsoup4)
- requests (python3-requests)

## Install

### Source
```
# Install libguestfs. It's not part of pypi.
$ sudo dnf install -y python3-libguestfs
...
# Install the needed libraries (use --user if not in virtualenv)
$ pip install -r requirements.txt
# Install the code
$ python setup.py install
```
