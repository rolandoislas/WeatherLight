import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import requests
from util.config import Config
from util.light_controller import LightController
from util.logger import Logger
from util.weather_watcher import WeatherWatcher


class ConfigServerHandler(BaseHTTPRequestHandler):
    # noinspection PyPep8Naming
    def do_GET(self):
        """
        Main entry point for GET requests
        This is called by HTTPServer automatically
        :return: None
        """
        try:
            body, content_type, status_code, status_message = self.get_body_for_path(self.path, self.headers)
        except Exception as e:
            Logger.get_logger().exception(e)
            self.send_error(500, "Server Error", "A server error has occurred")
            return
        if body is None:
            self.send_error(404, "Not Found", "The requested page was not found on this server")
            return
        content_type = content_type if content_type is not None else "text/html"
        status_code = status_code if status_code is not None else 200
        status_message = status_message if status_message is not None else "OK"
        body = body if body is not None else ""
        self.send_response(status_code, status_message)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def get_body_for_path(self, path, headers):
        """
        Gets a response body for a path on the server
        :param path: path of file - this should be absolute with root considered to be the web root
        :param headers: HTTP headers
        :return: A tuple of response body in bytes or none if not found, the content type, status code, and
        status message is returned.
        """
        path = urlparse(self.path)
        query_params = parse_qs(path.query)
        static, content_type, status_code, status_message = self.get_static_file(path.path)
        if static is not None:
            return static, content_type, status_code, status_message
        elif path.path == "/search":
            return self.get_search(query_params)
        elif path.path == "/config":
            return self.get_config()
        return None, None, None, None

    @staticmethod
    def get_static_file(web_path):
        """
        Try to get a static file from the web root
        :param web_path: path of file
        :return: body, content_type, status_code, status_message
        """
        web_path = web_path if web_path is not None else ""
        web_path = web_path.lstrip("/")
        static_file_path = None
        content_type = "text/plain"
        static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "resources", "static")
        if web_path == "":
            static_file_path = os.path.join(static_path, "index.html")
        else:
            for path, dirs, files, in os.walk(static_path):
                for directory in dirs:
                    if os.path.join(static_path, web_path).rstrip("/") == \
                            os.path.join(path, directory).rstrip("/"):
                        static_file_path = os.path.join(path, directory, "index.html")
                for file in files:
                    if os.path.join(static_path, web_path) == os.path.join(path, file):
                        static_file_path = os.path.join(path, file)
        if static_file_path is None:
            return static_file_path, content_type, None, None
        static = None
        try:
            with open(static_file_path, "rb") as static_file:
                static = static_file.read()
        except OSError:
            pass
        split = os.path.splitext(static_file_path)
        if len(split) > 0:
            ext = split[len(split) - 1]
            ext = ext if ext is not None else ""
            ext = ext.upper().lstrip(".")
            if ext == "HTML" or ext == "HTM":
                content_type = "text/html"
            elif ext == "XML":
                content_type = "text/xml"
            elif ext == "CSS":
                content_type = "text/css"
            elif ext == "JS":
                content_type = "application/javascript"
            elif ext == "JSON":
                content_type = "application/json"
            elif ext == "PNG":
                content_type = "image/png"
            elif ext == "JPG":
                content_type = "image/jpg"
            elif ext == "jpeg":
                content_type = "image/jpeg"
            elif ext == "ICO":
                content_type = "image/x-icon"
            elif ext == "GIF":
                content_type = "image/gif"
        return static, content_type, None, None

    # noinspection PyPep8Naming
    def do_POST(self):
        """
        Main entry point for POST requests
        This is called by HTTPServer automatically
        :return: None
        """
        content_length = int(self.headers.get("Content-Length", "0"))
        content_type = self.headers.get("Content-Type")
        body = None
        if content_length > 0:
            body = self.rfile.read(content_length).decode("utf-8")
        try:
            success, status_code, status_message, response_body, content_type = \
                self.handle_post(self.path, body, self.headers, content_type)
        except Exception as e:
            Logger.get_logger().exception(e)
            self.send_error(500, "Server Error", "A server error has occurred")
            return
        if success is None or not success:
            self.send_error(status_code, status_message, response_body)
            return
        content_type = content_type if content_type is not None else "text/html"
        status_code = status_code if status_code is not None else 200
        status_message = status_message if status_message is not None else "OK"
        response_body = response_body if response_body is not None else b""
        self.send_response(status_code, status_message)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(response_body))
        self.end_headers()
        self.wfile.write(response_body)

    @classmethod
    def handle_post(cls, path, body, headers, content_type):
        """
        Handle a POST request
        :param content_type: content type
        :param path: path of post
        :param body: optional body
        :param headers:
        :return: success, status code, message, response_body, content_type
        """
        if path == "/config":
            return cls.post_config(body, headers, content_type)
        elif path == "/light":
            return cls.post_light(body, headers, content_type)
        return False, 404, "Not Found", "The requested page was not found on this server", "text/plain"

    def get_config(self):
        """
        Get the config JSON
        :return: tuple(response in bytes, content type string)
        """
        config = Config.get_config()
        json_bytes = json.dumps(config).encode("utf-8")
        return json_bytes, "application/json", None, None

    @classmethod
    def post_config(cls, body, headers, content_type):
        """
        Post the config JSON
        :param content_type: content_type
        :param body: post body
        :param headers: post headers
        :return: success, status code, message, response_body, content_type
        """
        if content_type != "application/json":
            return False, 400, "Bad request", "Invalid content type", None
        if body is None:
            return False, 400, "Bad Request", "Missing JSON body", None
        try:
            body_json = json.loads(body)
            if not Config.verify_config(body_json):
                return False, 400, "Bad Request", "Invalid config format", None
            else:
                Config.set_config(body_json)
                Config.load()
        except ValueError:
            return False, 400, "Bad Request", "Invalid JSON body", None
        if not Config.verify_config(body_json):
            return False, 400, "Bad Request", "Invalid JSON body", None
        return True, 200, "OK", b"OK", None

    @staticmethod
    def get_search(query_params):
        """
        Search OpenWeatherMap for cities
        :return: tuple(response in bytes, content type string)
        """
        query = query_params.get("query", "")
        response = requests.get("https://api.openweathermap.org/data/2.5/find", params={
            "q": query,
            "type": "like",
            "mode": "json",
            "appid": WeatherWatcher.API_KEY,
            "cnt": "5"
        })
        return response.content, response.headers.get("Content-Type"), response.status_code, response.reason

    @classmethod
    def post_light(cls, body, headers, content_type):
        """
        Post light JSON RGB values
        :param content_type: content_type
        :param body: post body
        :param headers: post headers
        :return: success, status code, message, response_body, content_type
        """
        if content_type != "application/json":
            return False, 400, "Bad request", "Invalid content type", None
        if body is None:
            return False, 400, "Bad Request", "Missing JSON body", None
        try:
            body_json = json.loads(body)
            if type(body_json.get("r")) is not int or type(body_json.get("g")) is not int or \
                    type(body_json.get("b")) is not int:
                return False, 400, "Bad Request", "Invalid JSON format", None
            LightController.set_color(body_json["r"], body_json["g"], body_json["b"])
        except ValueError:
            return False, 400, "Bad Request", "Invalid JSON body", None
        return True, 200, "OK", b"OK", None
