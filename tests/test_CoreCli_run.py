import pexpect
import pytest
import re

from expects import *
from unittest.mock import MagicMock
from unittest.mock import Mock

from climatic.CoreCli import CoreCli, NO_ERROR_MARKER


def test_run_defaults(core_cli):
    connection = Mock()
    terminal = Mock()
    terminal.expect.side_effect = [0, 1, 0, 0, 0]
    terminal.sendline = MagicMock(return_value=0)
    connection.terminal = terminal
    cmd = core_cli(connection)
    out = cmd.run("  run this   \t")
    terminal.sendline.assert_called_with("run this")
    terminal.expect.assert_any_call("#", timeout=2)
    terminal.expect.assert_any_call(re.escape("run this"), timeout=2)
    terminal.expect.assert_called_with(["#", pexpect.TIMEOUT, pexpect.EOF, "%"], timeout=15)
    expect(terminal.expect.call_count).to(be(5))

def test_run_defaults_multi_lines(core_cli):
    connection = Mock()
    terminal = Mock()
    terminal.expect.side_effect = [1, 0, 0, 0, 0, 0]
    terminal.sendline = MagicMock(return_value=0)
    connection.terminal = terminal
    cmd = core_cli(connection)
    out = cmd.run("""
        double line command

        line 2
        """)
    terminal.sendline.assert_any_call("double line command")
    terminal.sendline.assert_called_with("line 2")
    terminal.expect.assert_any_call("#", timeout=2)
    terminal.expect.assert_any_call(re.escape("double line command"), timeout=2)
    terminal.expect.assert_any_call(re.escape("line 2"), timeout=2)
    terminal.expect.assert_called_with(["#", pexpect.TIMEOUT, pexpect.EOF, "%"], timeout=15)
    expect(terminal.expect.call_count).to(be(6))

def test_run_custom_params_from_constructor(core_cli):
    connection = Mock()
    terminal = Mock()
    terminal.expect.side_effect = [0, 1, 0, 0, 0]
    terminal.sendline = MagicMock(return_value=0)
    connection.terminal = terminal
    cmd = core_cli(connection, marker="-->", error_marker="!!", timeout=20, sync_timeout=5,
                   wait_cmd=False, wait_cmd_timeout=7, strip_cmds=False)
    out = cmd.run("  run this   \t")
    terminal.sendline.assert_called_with("  run this   \t")
    terminal.expect.assert_any_call("-->", timeout=5)
    terminal.expect.assert_called_with(["-->", pexpect.TIMEOUT, pexpect.EOF, "!!"], timeout=20)
    expect(terminal.expect.call_count).to(be(4))

def test_run_custom_params(core_cli):
    connection = Mock()
    terminal = Mock()
    terminal.expect.side_effect = [0, 1, 0, 0, 0]
    terminal.sendline = MagicMock(return_value=0)
    connection.terminal = terminal
    cmd = core_cli(connection, marker="-->", timeout=20, sync_timeout=5, wait_cmd=False,
                   wait_cmd_timeout=7, strip_cmds=False)
    out = cmd.run("  run this   \t", timeout=16, marker=r"\$", error_marker="Error", sync_timeout=3,
                  wait_cmd=True, wait_cmd_timeout=6, strip_cmds=True)
    terminal.sendline.assert_called_with("run this")
    terminal.expect.assert_any_call(r"\$", timeout=3)
    terminal.expect.assert_any_call(re.escape("run this"), timeout=6)
    terminal.expect.assert_called_with([r"\$", pexpect.TIMEOUT, pexpect.EOF, "Error"], timeout=16)
    expect(terminal.expect.call_count).to(be(5))

def test_run_no_error_marker_from_constructor(core_cli):
    connection = Mock()
    terminal = Mock()
    terminal.expect.side_effect = [0, 1, 0, 0, 0]
    terminal.sendline = MagicMock(return_value=0)
    connection.terminal = terminal
    cmd = core_cli(connection, error_marker=NO_ERROR_MARKER)
    out = cmd.run("  run this   \t")
    terminal.sendline.assert_called_with("run this")
    terminal.expect.assert_any_call("#", timeout=2)
    terminal.expect.assert_any_call(re.escape("run this"), timeout=2)
    terminal.expect.assert_called_with(["#", pexpect.TIMEOUT, pexpect.EOF], timeout=15)
    expect(terminal.expect.call_count).to(be(5))

def test_run_no_error_marker(core_cli):
    connection = Mock()
    terminal = Mock()
    terminal.expect.side_effect = [0, 1, 0, 0, 0]
    terminal.sendline = MagicMock(return_value=0)
    connection.terminal = terminal
    cmd = core_cli(connection)
    out = cmd.run("  run this   \t", error_marker=NO_ERROR_MARKER)
    terminal.sendline.assert_called_with("run this")
    terminal.expect.assert_any_call("#", timeout=2)
    terminal.expect.assert_any_call(re.escape("run this"), timeout=2)
    terminal.expect.assert_called_with(["#", pexpect.TIMEOUT, pexpect.EOF], timeout=15)
    expect(terminal.expect.call_count).to(be(5))

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
