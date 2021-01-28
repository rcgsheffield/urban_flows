import logging
import socket
from getpass import getpass
from typing import Iterable, Tuple

import ssh2.channel
import ssh2.session

LOGGER = logging.getLogger(__name__)


class RemoteHost:
    """
    Connect to a remote host and run one SSH command at a time.
    """

    def __init__(self, host: str, username: str, timeout: int = 0, port: int = 22):
        self.host = host
        self.port = port
        self.username = username
        self.timeout = timeout
        self._socket = None
        self._session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close(self):
        try:
            self._session.disconnect()
        except AttributeError:
            pass
        try:
            self._socket.close()
        except AttributeError:
            pass

    @property
    def address(self) -> Tuple[str, int]:
        return self.host, self.port

    @property
    def password(self) -> str:
        return getpass('Enter password for user {}: '.format(self.username))

    @property
    def socket(self) -> socket.socket:
        """
        Connect to remote host
        """
        if not self._socket:
            self._socket = socket.socket()
            self._socket.connect(self.address)
        return self._socket

    def authenticate(self):
        self.session.userauth_password(self.username, self.password)
        LOGGER.info('Logged in as %s', self.username)

    @property
    def session(self) -> ssh2.session.Session:
        """
        SSH session
        """
        if not self._session:
            # Initialise
            self._session = ssh2.session.Session()
            self._session.handshake(self.socket)

            # Set timeout (By default, no time out)
            self._session.set_timeout(self.timeout)

            self.authenticate()

        return self._session

    @classmethod
    def read(cls, channel: ssh2.channel.Channel, stderr: bool = False) -> Iterable[bytes]:
        """
        Read (stream) channel response

        :param stderr: Read standard error output
        """
        total_size = 0

        while True:
            size, data = channel.read_stderr() if stderr else channel.read()

            # Negative values are error codes.
            if size < 0:
                raise RuntimeError(size, data)
            # No more data
            elif size == 0:
                break
            else:
                total_size += size
                yield data

        LOGGER.info('Retrieved %s bytes', total_size)

    def open(self) -> ssh2.channel.Channel:
        return self.session.open_session()

    def execute(self, command: str) -> iter:
        """
        Run a command.
        """

        # Open one channel per command (to run parallel commands in a single session)
        channel = self.open()

        LOGGER.debug("Command %s", repr(command))

        channel.execute(command)

        channel.wait_eof()
        channel.close()
        channel.wait_closed()

        exit_status = channel.get_exit_status()
        LOGGER.debug("Exit status: %s", exit_status)

        # Errors
        if exit_status:
            for line in self.read(channel, stderr=True):
                LOGGER.error(line)
            raise RuntimeError(exit_status)

        yield from self.read(channel)

    def execute_decode(self, *args, **kwargs) -> Iterable[str]:
        """
        Decode response data into strings
        """
        for data in self.execute(*args, **kwargs):
            yield data.decode()
