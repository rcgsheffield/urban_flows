import socket
import logging

from getpass import getpass
from typing import Iterable, Tuple

import ssh2.channel
import ssh2.session

LOGGER = logging.getLogger(__name__)


class RemoteHost:
    """
    Connect to a remote host and run one SSH command at a time.
    """

    def __init__(self, host: str, port: int, username: str, timeout: int = None):
        self.host = host
        self.port = port
        self.username = username
        self.timeout = timeout or 0
        self._socket = None
        self._session = None
        self._channel = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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

    @property
    def channel(self):
        if not self._channel:
            self._channel = self.session.open_session()
        return self._channel

    @channel.deleter
    def channel(self):
        self._channel = None

    def read(self, stderr: bool = False) -> Iterable[bytes]:
        """
        Read (stream) channel response

        :param stderr: Read standard error output
        """
        total_size = 0

        while True:
            size, data = self.channel.read_stderr() if stderr else self.channel.read()

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

    def execute(self, command: str) -> iter:
        """
        Run a commmand
        """

        LOGGER.debug("Command %s", repr(command))

        self.channel.execute(command)

        self._channel.wait_eof()
        self._channel.close()
        self._channel.wait_closed()

        exit_status = self.channel.get_exit_status()
        LOGGER.debug("Exit status: %s", exit_status)

        # Errors
        if exit_status:
            for line in self.read(stderr=True):
                LOGGER.error(line)
            raise RuntimeError(exit_status)

        yield from self.read()

        # Remove channel object so a new one is created next time
        del self.channel

    def execute_decode(self, *args, **kwargs) -> Iterable[str]:
        """
        Decode response data into a string
        """
        for data in self.execute(*args, **kwargs):
            yield data.decode()

    def execute_decode_lines(self, *args, **kwargs) -> Iterable[str]:
        """
        Generate one string per output line in the response.

        This may be used to break apart all returned ls lines and build a single list.
        """
        for s in self.execute_decode(*args, **kwargs):
            yield from s.split()
