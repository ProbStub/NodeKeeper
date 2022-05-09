# TL;DR
NodeKeeper is a Python wrapper to ChainLink nodes API. This allows
you to easily create integration tests on a local development network.
Additionally, you may use NodeKeeper to automate your node operations.

![GitHub commits since latest release (by date) for a branch](https://img.shields.io/github/commits-since/Probstub/NodeKeeper/0.0.1/master)
![GitHub branch checks state](https://img.shields.io/github/checks-status/probstub/NodeKeeper/master)
![Codacy grade](https://img.shields.io/codacy/grade/23890bea152e49b296f411d83a85619c)

# Purpose
Testing for smart contracts that reference oracles is often tedious 
on live chains, and slow. Yet, everyone wants to test as much as possible, 
given many smart contracts manage money in some way. 

NodeKeeper allows to integrate more complex test cases into
your testing strategy and run them faster. ChainLinks oracles offer a hidden
API which is abstracted by the NodeKeeper API. 

You can use the NodeKeeper
functions to create new jobs, change keys and perform many other activities
that usually would require either the ChainLink CLI or web UI.

Performing such activities on a ChainLink node not installed on your local
machine either requires many clicks on a browser based UI or heavy shell
scripting to call up SSH sessions into your node. Neither may be very practical
if all you want to do is write integration tests for your software

# Installation

NodeKeeper is available as a Python package. Additionally, you may choose to 
install from source.

Installation of the Python package:
```
pip install -i cl-node-keeper
```

Installation from source:
```
git clone https://github.com/ProbStub/NodeKeeper
```

# Examples

# Yes, Please!

This is not my main project and pull requests are welcome.

The original code was created as part of another project, and I decided
to contribute here during the ChainLink 2022 SpringHackathon. 
Documentation, testing, coding standards are all under heavy development.
