import pexpect
import re
import sys
import time

from io import StringIO
from string import printable
from typing import Dict, List

from . import Logger


####################################################################################################
## RunResults

class RunResults(object):
    """ Represents the results of the execution of a CLI command with the run method
    """

    def __init__(self, duration: time, output: str):
        """ Initialize RunResults
        @duration  The time spent between the execution of the commands;
        @output    A string with the output of the commands.
        """
        self.duration = duration
        self.output = output


####################################################################################################
## CoreCli

class CoreCli(object):
    """ This class represents the core of a CLI and provides the methods enter commands into
    this CLI. It should be extended by the specialized CLI classes.

    Some of the methods are defined but not implemented here, as they are very specific and
    should be override accordingly for the specialized CLI classes whose extend this one.

    Two of these methods are the 'login' and 'logout', that will contain the command sequence
    necessary for login and logout to the equipment.

    Your extension class should also implement two methods: 'connect' for connecting to the
    equipment and 'disconnect' for disconnecting from it. The 'connect' method should open and
    return a pexpect connection. The 'disconnect' will close the pexpect connection.
    """

    def __init__(self, connection, username='admin', password='admin', timeout=15, pty_winsize_cols=80):
        """ Initialize BaseCLI.
        @param connection  The connection object to be used for accessing the CLI.
        @param username    String with username to login into the connection that provides access to
                           the CLI.
        @param password    String with password corresponding to the username to login into the
                           connection that provides access to the CLI.
        @param timeout     Default maximum timeout on each CLI command. When specified in a CLI
                           command, the specific timeout takes precedence.
        """
        if not hasattr(self, 'name'):
           self.name = self.__class__.__name__
        self.logger = Logger.start(self.name)
        self.connection = connection
        self.username = username
        self.password = password
        self.timeout = timeout

        # Number of columns of the window
        self.pty_winsize_cols = pty_winsize_cols

        # Connect to the CLI
        startup_log = StringIO()
        self.connection.connect(startup_log)  # [Connection]
        try:
            self.login()  # [CLI]
        except:
            self.connection.terminal.close()
            self.logger.error("Error while trying to login. Output -->\n" + startup_log.getvalue() +
                              "\n<-- End of output\n", exc_info=True)
            raise
        finally:
            # Close temporary file as it was only used for startup debugging.
            self.connection.terminal.logfile = None
            self.logger.debug(startup_log.close())


    def __del__(self):
        """ Close all connections (if existing) on destruction
        """
        # If pexpect connection is not active there is nothing to close
        if not self.connection.terminal or not self.connection.terminal.isalive():
            return

        self.logout()
        self.connection.disconnect()


    def run(self, cmds: str, timeout=None, quiet=False, marker="#", error_marker="%", sync_timeout=1,
            wait_cmd=True, wait_cmd_timeout=1) -> RunResults:
        """ Runs CLI commands
        @param cmds              Commands in a multi-line string. Each line is a command.
        @param timeout           Maximum time to wait for command completion. Defaults to the
                                 timeout defined on the constructor.
        @param quiet             If True, do not print command execution logs. Default is False.
        @param marker            Regex used that identifies the start of a command line.
                                 Default is "#".
        @param error_marker      Regex used to identify when error occurs during the command
                                 execution. Default is "%". Set "error_marker = None" to not check
                                 errors.
        @param sync_timeout      Maximum time to wait for syncing the command. Default is 1.
                                 Set to None to use the global timeout defined on constructor.
        @param wait_cmd          If True, verifies the echo of the sent command. Default is true.
        @param wait_cmd_timeout  Timeout for receiving the echo of the sent command. Default is 1.
                                 Set to None to use the global timeout defined on constructor.
        @return                  The results as an object of RunResults. They include:
                                 - duration: The time spent between the execution of the commands;
                                 - output: A string with the output of the commands.
        """

        # Initialize list of unexpected elements
        unexpected = [pexpect.TIMEOUT, pexpect.EOF]
        if error_marker != None:
            unexpected.append(error_marker)

        if timeout == None:
            timeout = self.timeout
        if sync_timeout == None:
            sync_timeout = self.timeout
        if wait_cmd_timeout == None:
            wait_cmd_timeout = self.timeout

        self.open_logfile()
        start_time = time.time()

        # Sync prompt: ignore all previews occurrences of the prompt marker.
        self.sync(marker)

        # Send new line to get the prompt marker and get ready for sending the command
        self.connection.terminal.sendline()
        self.connection.terminal.expect(marker, timeout=sync_timeout)

        # Each line is executed as separate command
        for cmd in cmds.splitlines():

            # Remove extra spaces at the begin and end of the command
            cmd = cmd.strip(' \t')

            # Ignore empty lines
            if not cmd:
                continue

            # Prepare cmd echo expects
            if wait_cmd == True:
                prompt_size = self.get_prompt_size()
                cmd_echo_expects = self.prepare_expect_for_cmd_echo(cmd, prompt_size)

            # Send command to terminal (Finally!)
            self.connection.terminal.sendline(cmd)

            # Check that all the command was sent
            if wait_cmd == True:
                for cmd_echo in cmd_echo_expects:
                    self.connection.terminal.expect(re.escape(cmd_echo), timeout=wait_cmd_timeout)

            # Wait for the marker or unexpected elements (errors)
            expectations = [marker] + unexpected
            index = self.connection.terminal.expect(expectations, timeout=timeout)

            # Only the marker is accepted. All the others are errors
            if index != 0:
                # Keep reading until the marker (if possible) to complete the error message
                try:
                    self.connection.terminal.expect(marker, timeout=1)
                except:
                    pass

                self.register_log(self.close_logfile(), quiet=quiet)

                if index == 1:  # timeout
                    assertion_msg = "Timeout expecting '{0}' while executing '{1}'. Current timeout is set to '{2}'".format(
                            marker, cmd, timeout)
                else:
                    assertion_msg = "Expected '{0}' but received '{1}' while executing '{2}'".format(
                            marker, expectations[index], cmd)
                # Raise error
                raise AssertionError(assertion_msg)

        current_log = self.register_log(self.close_logfile(), quiet=quiet)

        return RunResults(duration=time.time() - start_time, output=current_log)



    def sync(self, marker: str):
        """ This method is used to make sure the CLI has consumed all previous marked and will not
        misunderstand a previous marker with the end of the command.

        To do so, all the markers are consumed in a loop until there are no more markers to consume.

        Override this method if necessary for your custom CLI implementation.

        @param marker  regex used to identify the start of a command line.
        """
        # consume all markers since last 'expect'
        while self.connection.terminal.expect([marker, pexpect.TIMEOUT], timeout=0.01) == 0:
            continue


    def get_prompt_size(self) -> int:
        """ Returns the prompt size: the number of visible chars from the beginning of the
        line until the end of the marker

        Call this function after an expect for the marker

        @return  An integer with the size of the prompt at the beginning of the line
        """

        # The prompt size is the sum of the marker size with all the visible chars before
        # the marker.

        # Get the length of visible marker that is the 'self.connection.terminal.after'.
        prompt_size = len(self.connection.terminal.after)

        # Iterate on chars from 'self.connection.terminal.before' (before the marker) until
        # the first non visible char (such as ANSI color code or \n).
        for c in self.connection.terminal.before[::-1]:  # iterate over all char in reverse order
            if c in printable and c != '\n':
                prompt_size += 1
            else:
                break

        return prompt_size


    def prepare_expect_for_cmd_echo(self, cmd: str, prompt_size: int) -> List[str]:
        """ break the command into multiple lines according to the terminal number of columns

        @param cmd          The command
        @param prompt_size  Size from the start of the line until the end of the marker
        @return             A list with strings to expect for "consuming" the echo of the command
        """
        first_line_left_cols = self.pty_winsize_cols - prompt_size
        if len(cmd) > first_line_left_cols:
            expects = [cmd[:first_line_left_cols]]
            for i in range(first_line_left_cols, len(cmd), pty_winsize_cols):
                expects.append(cmd[i:i+self.pty_winsize_cols])
        else:
            expects = [cmd]

        return expects


    def register_log(self, log: str, quiet=False) -> str:
        """ Clean the received log and add it to the logger

        @param log    The log to be processed
        @param quiet  If True, do not print command execution logs. Default is False.
        @return       The processed log string
        """
        # remove extra blank lines
        current_log = re.sub(r'\r\r', r'\r', log)
        if not quiet:
            self.logger.info(current_log)
        else:
            self.logger.debug(current_log)

        return current_log


    ################################################################################################
    ## Equipment interface

    def login(self):
        """ login to CLI interface.
        """
        raise NotImplementedError("MUST implement 'login' method.")


    def logout(self):
        """ Logout from CLI interface.
        """
        raise NotImplementedError("MUST implement 'logout' method.")


    ################################################################################################
    ## Log manipulation

    def open_logfile(self):
        """ Opens a logfile to save terminal output.
        """
        # When log is already created, close it before opening
        if self.connection.terminal.logfile_read:
            self.logger.warning("Logfile already exists. Closing it!")
            if hasattr(self.connection.terminal.logfile_read, 'close'):
                self.connection.terminal.logfile_read.close()
        self.connection.terminal.logfile_read = StringIO()


    def close_logfile(self) -> str:
        """ Close logfile and returns the captured log.

        @return  the contents of logfile
        """
        log = ''
        if not self.connection.terminal.logfile_read:
            self.logger.warning("Logfile is already closed!")
        else:
            file = self.connection.terminal.logfile_read
            self.connection.terminal.logfile_read = None
            log = file.getvalue()
            file.close()
        return log
