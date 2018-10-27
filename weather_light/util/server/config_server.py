from util.server.config_http_server import ConfigHttpServer
from util.server.config_server_handler import ConfigServerHandler


class ConfigServer:
    def __init__(self):
        pass

    def start(self):
        http_server = ConfigHttpServer(("0.0.0.0", 80), ConfigServerHandler)
        http_server.serve_forever_non_blocking()
