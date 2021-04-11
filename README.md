# CLImatic

[![License](https://img.shields.io/badge/Licence-MIT-brightgreen.svg)](https://www.tldrlegal.com/l/mit) [![PyPI versions](https://img.shields.io/pypi/pyversions/climatic.svg)](https://pypi.python.org/pypi/climatic)

**CLImatic** is tool to ease and automate CLI usage. It abstracts the CLI connection for you and
you just need to send commands and process the returned results.


## Install

Install the last stable release from PyPI using pip or easy_install:

```bash
> pip3 install climatic
```

Or install the latest sources from Github:

```bash
> pip3 install -e git+git://github.com/evedovelli/climatic.git#egg=climatic
```


## Usage

Import the **CLImatic** CLI client, open the connection, and run commands. That's all!

```python
from climatic.cli.Linux import SshLinux

cmd = SshLinux("127.0.0.1", "your.user", "your.password")
cmd.run("mkdir /tmp/test")
cmd.run("ls /tmp/")
```

And what if you need to check the outputs of the commands?

That's easy! Well, some basic validations
are already made inside the `run` method. It verifies if the command hangs, or if and `error_marker`
is outputed.

Besides, the `run` method returns you the outputs of the command which you can use
to make any validation you'd like. When used with the [`expects`](https://github.com/jaimegildesagredo/expects)
library (or with the assertion library of your preference), it becomes a powerfull tool to write
TDD/BDD tests for CLIs. Take a look at this example:

```python
from climatic.cli.Linux import SshLinux
from expects import *

cmd = SshLinux("127.0.0.1", "your.user", "your.password")

cmd.run("mkdir /tmp/test")

# In an expressive manner, you can test if the cmd run output contains a specific term:
expect(cmd.run("ls /tmp/").output).to(contain("test"))

cmd.run("rm -r /tmp/test")

# Or if it does not contain it:
expect(cmd.run("ls /tmp/").output).not_to(contain("test"))

# You can also verify the duration of a command run:
expect(cmd.run("sleep 2").duration).to(be_below(3))
expect(cmd.run("sleep 3").duration).to(be_above(2))
```

> Read the [`expects`](https://github.com/jaimegildesagredo/expects) docs for discovering other matchers or how to build your own.

Also, instead of `run` you can call the `cli` method. In this case you pass as argument a
complete CLI session, and the command will parse the commands, execute them, and match the outputs.
Like this:

```python
from climatic.cli.Linux import SshLinux
from expects import *

cmd = SshLinux("127.0.0.1", "your.user", "your.password")

# Run the commands line by line and expect for outputs
# for the lines without the shell marker:
cmd.cli("""
    ~# mkdir /tmp/test
    ~# ls /tmp/
    test
    ~# rm -rv /tmp/test
    removed directory '/tmp/test'
    """)
```

**CLImatic** includes only a few built-in CLI clients, as the Linux client from the example above,
but you will find many other CLI clients extensions. There a list with supported CLI clients in
[here](#list-of-cli-clients).

In this example, we are accessing and running commands in a remote python3 CLI through a
SSH connection with [CLImatic-Python](https://github.com/evedovelli/climatic-python) client:

```python
from climatic_python.Python3Shell import SshPython3Shell

python_cmd = SshPython3Shell("127.0.0.1", "your.user", "your.password")
python_cmd.run("""
i = 3
for x in range(i):
    print("Iteration {}".format(x))

""")
```


## List of CLI Clients

- [climatic-python](https://github.com/evedovelli/climatic-python)
- [climatic-ipinfusion](https://github.com/evedovelli/climatic-ipinfusion)
