import pexpect
import pytest
import re

from expects import *
from unittest.mock import MagicMock
from unittest.mock import Mock

from climatic.CoreCli import CoreCli


def test_core_cli_constructor_destructor(core_cli):
    connection = Mock()
    cmd = core_cli(connection)
    del cmd
    connection.connect.assert_called_once()
    connection.disconnect.assert_called_once()

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
