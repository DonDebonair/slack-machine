# Installation

This part of the documentation helps you install Slack Machine with the least amount of friction, or the most amount of
flexibility.

## Installing the easy way with pip

Slack Machine is published to the [Python package index](https://pypi.python.org/pypi/slack-machine) so you can easily
add Slack Machine to your uv project by running:

```bash
uv add slack-machine
```

or add it to your [Poetry](https://python-poetry.org/) project:

```bash
poetry add slack-machine
```

Lastly, you can install it using pip (not recommended):

``` bash
$ pip install slack-machine
```

It is **strongly recommended** that you install `slack-machine` inside a
[virtual environment](https://docs.python.org/3/tutorial/venv.html)!

## Installing from source

If you are adventurous, want to modify the core of your Slack Machine instance and want maximum flexibility, you can
also install from source. This way, you can enjoy the latest and greatest!

You can either clone the public repository:

```bash
git clone git://github.com/DonDebonair/slack-machine.git
```

Or, download the
[tarball](https://github.com/DonDebonair/slack-machine/tarball/main):

```bash
curl -OL https://github.com/DonDebonair/slack-machine/tarball/main
```

_Optionally, zipball is also available (for Windows users)._

Once you have a copy of the source, you can embed it in your own Python package, or install it into your virtualenv
easily:

```bash
cd slack-machine
pip install .
```
