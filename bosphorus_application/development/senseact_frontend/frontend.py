import asyncio

class Protocol(asyncio.Protocol):
  transport = None

  def connection_made(self, transport):
    Protocol.transport = transport

  def data_received(self, data):
    Handler.app += data.decode('utf8')

class Handler:
  app = None

  def __init__(self, app):
    super().__init__()
    Handler.app = app

  def __iadd__(self, message):
    if isinstance(message, tuple):
      message = '\n'.join(message)
    message = '\n' + message + '\n'

    Protocol.transport.write(
      data=message.encode('utf8')
    )

    return self

  def start(self):
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
