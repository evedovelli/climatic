from telnetlib import TELNET_PORT
import pexpect

from .Connection import Connection

# Increase the PTY window size to to try to avoid truncating command output
PTY_WINSIZE_ROWS = 24
PTY_WINSIZE_COLS = 500


class Telnet(Connection):
    """ Connects to a CLI using Telnet.
    The device should have the IP configured.
    """

    def __init__(self, ip: str, user: str, port=TELNET_PORT):
        """ Initialize the Telnet connection object.
        @param ip    IP address to connect to. Ex: '192.168.33.4'.
        @param user  The Telnet connection user.
        @param port  The Telnet connection port. Default is 23.
        """
        self.user = user
        self.ip = ip
        self.port = port

        Connection.__init__(self)

    def connect(self, logfile, logger=None):
        """ Start the Telnet connection.
        @param logfile  Log file to save connection outputs.
        @param logger   Optional logger for debug messages
        """
        if logger != None:
            logger.debug("Connecting to Telnet (%s).", self.ip)
        self.terminal = pexpect.spawn(
            'telnet {0} {1}'.format(self.ip, self.port), logfile=logfile, encoding='utf-8')
        self.terminal.setwinsize(PTY_WINSIZE_ROWS, PTY_WINSIZE_COLS)

    def disconnect(self, logger=None):
        """ For Telnet, the connection is closed during the logout
        @param logger   Optional logger for debug messages
        """
        if logger != None:
            logger.debug("Disconnecting from Telnet (%s).", self.ip)
