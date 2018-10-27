from http.server import HTTPServer
from threading import Thread


class ConfigHttpServer(HTTPServer):
    def serve_forever_non_blocking(self):
        thread = Thread(target=self.non_blocking_run, name="ConfigHttpServerThread", daemon=True)
        thread.start()

    def non_blocking_run(self):
        self.serve_forever()
