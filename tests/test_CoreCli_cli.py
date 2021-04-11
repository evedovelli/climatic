import pexpect
import pytest
import re

from expects import *
from unittest.mock import MagicMock
from unittest.mock import Mock

from climatic.CoreCli import CoreCli, RunResults, NO_ERROR_MARKER


def test_cli_defaults_pass(core_cli):
    connection = Mock()
    terminal = Mock()
    terminal.expect.side_effect = [1, 0, 0, 0, 1, 0, 0, 0]
    terminal.sendline = MagicMock(return_value=0)
    connection.terminal = terminal
    cmd = core_cli(connection)
    cmd.run = Mock()
    cmd.run.side_effect = [RunResults(1, ""),
                           RunResults(1, "first interface   200 Mbps"),
                           RunResults(1, "expect this\r\n\r\nand that")]
    out = cmd.cli(r"""
        os#run this
        os#execute that
        first interface   \d+ Mbps
        os#and that
        expect this

        and that
        """)
    cmd.run.assert_any_call("run this")
    cmd.run.assert_any_call("execute that")
    cmd.run.assert_any_call("and that")
    expect(len(out)).to(be(3))
    expect(out[1].output).to(contain("first interface   200 Mbps"))
    expect(out[2].output).to(contain("expect this\r\n\r\nand that"))

def test_cli_defaults_failure(core_cli):
    connection = Mock()
    terminal = Mock()
    terminal.expect.side_effect = [1, 0, 0, 0, 1, 0, 0, 0]
    terminal.sendline = MagicMock(return_value=0)
    connection.terminal = terminal
    cmd = core_cli(connection)
    cmd.run = Mock()
    cmd.run.side_effect = [RunResults(1, "and continue")]

    with pytest.raises(AssertionError):
        cmd.cli(r"""
            os#run command
            and raises error
            """)

def test_cli_custom_params_from_constructor(core_cli):
    connection = Mock()
    terminal = Mock()
    terminal.expect.side_effect = [0, 1, 0, 0, 0]
    terminal.sendline = MagicMock(return_value=0)
    connection.terminal = terminal
    cmd = core_cli(connection, marker="os>", strip_cmds=False)
    cmd.run = Mock()
    cmd.run.side_effect = [RunResults(1, ""),
                           RunResults(1, "first interface   200 Mbps"),
                           RunResults(1, "expect this\r\n\r\nand that")]
    out = cmd.cli(r"""
  os>run this  
  os>execute that
first interface   \d+ Mbps
  os>and that
expect this

and that
""")
    cmd.run.assert_any_call("run this  ")
    cmd.run.assert_any_call("execute that")
    cmd.run.assert_any_call("and that")
    expect(len(out)).to(be(3))
    expect(out[1].output).to(contain("first interface   200 Mbps"))
    expect(out[2].output).to(contain("expect this\r\n\r\nand that"))

def test_cli_custom_params(core_cli):
    connection = Mock()
    terminal = Mock()
    terminal.expect.side_effect = [0, 1, 0, 0, 0]
    terminal.sendline = MagicMock(return_value=0)
    connection.terminal = terminal
    cmd = core_cli(connection, marker="os>", strip_cmds=False)
    cmd.run = Mock()
    cmd.run.side_effect = [RunResults(1, ""),
                           RunResults(1, "first interface   200 Mbps"),
                           RunResults(1, "expect this\r\n\r\nand that")]
    out = cmd.cli(r"""
        os#run this
        os#execute that
        first interface   \d+ Mbps
        os#and that
        expect this

        and that
        """, marker=r"\n.+#", strip_cmds=True)
    cmd.run.assert_any_call("run this", marker=r"\n.+#", strip_cmds=True)
    cmd.run.assert_any_call("execute that", marker=r"\n.+#", strip_cmds=True)
    cmd.run.assert_any_call("and that", marker=r"\n.+#", strip_cmds=True)
    expect(len(out)).to(be(3))
    expect(out[1].output).to(contain("first interface   200 Mbps"))
    expect(out[2].output).to(contain("expect this\r\n\r\nand that"))


@pytest.fixture
def core_cli():
    class CoreCliExtension(CoreCli):
        def login(self):
            pass
        def logout(self):
            pass
        def _get_prompt_size(self):
            return 3
    return CoreCliExtension
