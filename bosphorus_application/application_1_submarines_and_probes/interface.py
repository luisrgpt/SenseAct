# coding=utf-8
"""Interface

"""

import asyncio
import threading


class Protocol(asyncio.Protocol):
    """Protocol

    """
    transport = None

    def connection_made(self, transport):
        """

        :param transport:
        """
        Protocol.transport = transport

    def data_received(self, data):
        """

        :param data:
        """
        Handler.app += data.decode('utf8')


class Handler(threading.Thread):
    """Handler

    """
    app = None

    def __init__(self, app):
        super().__init__()
        Handler.app = app

    def __iadd__(self, message):
        """

        :param message:
        """
        if isinstance(message, tuple):
            message = "\n".join(message)
        message = "\n" + message + "\n"

        Protocol.transport.write(
            data=message.encode('utf8')
        )

        return self

    def run(self):
        """
        :rtype: object

        """
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        loop = asyncio.new_event_loop()
        server = loop.create_server(
            Protocol,
            '127.0.0.1',
            3000
        )
        loop.run_until_complete(server)
        loop.run_forever()
