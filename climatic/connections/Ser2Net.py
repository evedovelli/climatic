import pexpect

from .Connection import Connection

# Increase the PTY window size to to try to avoid truncating command output
PTY_WINSIZE_ROWS = 24
PTY_WINSIZE_COLS = 500

class Ser2Net(Connection):
    """ Connects to a CLI using Ser2net.
    The Ser2Net should be available and configured with an IP and port
    """

    def __init__(self, ip: str, port: int):
        """ Initialize the Ser2Net connection object.
        @param ip    IP address to connect to. Ex: '192.168.33.4'.
        @param port  The port corresponding to the desired serial device.
        """
        self.ip = ip
        self.port = port

        Connection.__init__(self)

    def connect(self, logfile, logger=None):
        """ Start the SSH connection.
        @param logfile  Log file to save connection outputs.
        @param logger   Optional logger for debug messages
        """
        if logger != None:
            logger.debug("Connecting to Ser2Net (%s %s).", self.ip, selp.port)

        self.terminal = pexpect.spawn(
            'telnet {0} {1}'.format(self.ip, self.port), logfile=logfile, encoding='utf-8')
        self.terminal.sendline()
        self.terminal.setwinsize(PTY_WINSIZE_ROWS, PTY_WINSIZE_COLS)

    def disconnect(self, logger=None):
        """ For SSH, the connection is closed during the logout
        @param logger   Optional logger for debug messages
        """
        if logger != None:
            logger.debug("Disconnecting from Ser2Net (%s %s).", self.ip, selp.port)
        self.terminal.close()
