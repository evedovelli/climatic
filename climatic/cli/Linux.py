import pexpect

from ..CoreCli import CoreCli
from ..connections.Ssh import Ssh, PTY_WINSIZE_COLS
from ..connections.Ssh import PTY_WINSIZE_COLS as SSH_PTY_WINSIZE_COLS


####################################################################################################
## Linux

class Linux(CoreCli):
    """ Extend CoreCli with customizations for a Linux shell.
    """

    def run(self, cmds: str, **run_opts):
        """ Execute Linux shell commands

        @param cmds      A multi-line string with commands to be executed.
        @param run_opts  Same options as CoreCli run method.
        """
        if not 'marker' in run_opts:
            run_opts['marker'] = self.marker

        if not 'error_marker' in run_opts:
            run_opts['error_marker'] = None

        return super(Linux, self).run(cmds, **run_opts)


####################################################################################################
## SshLinux

class SshLinux(Linux):
    """ Connects to a remote Linux Shell using SSH.
    Core implementation is done by Ssh and Linux.
    """

    def __init__(self, ip: str, username: str, password: str, port=22, marker='#|>'):
        """ Initialize Linux Shell.
        @param ip        IP address of target. Ex: '234.168.10.12'
        @param username  username for opening SSH connection
        @param password  password for authentication in SSH connection
        @param port      Port used for SSH connection. Defaults to 22
        @param marker    Marker for the shell prompt
        """
        self.marker = marker
        self.name = "Linux.SSH"
        ssh = Ssh(ip, username, port=port)
        Linux.__init__(self, ssh, username=username, password=password, pty_winsize_cols=SSH_PTY_WINSIZE_COLS)

    def login(self):
        """ Login to CLI interface.
        """
        while True:
            index = self.connection.terminal.expect(
                ['Are you sure you want to continue connecting', '.assword'] + [self.marker], timeout=10)

            if index == 0:
                self.connection.terminal.sendline('yes')
            if index == 1:
                self.connection.terminal.waitnoecho()
                self.connection.terminal.sendline(self.password)
            if index >= 2:
                break

    def logout(self):
        """ Logout from CLI interface.
        """
        self.connection.terminal.sendline('exit')
