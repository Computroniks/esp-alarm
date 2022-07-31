# SPDX-FileCopyrightText: 2022 Matthew Nickson <mnickson@sidingsmedia.com>
# SPDX-License-Identifier: MIT

try:
    import usocket as socket
except:
    import socket
import json
from machine import Pin

from .logging import debug, info, warn, error, fatal
from .utils import alarm, getSubstringFromList

CODES = {
  100: "Continue",
  101: "Switching Protocols",
  200: "OK",
  201: "Created",
  202: "Accepted",
  203: "Non-Authoritative Information",
  204: "No Content",
  205: "Reset Content",
  206: "Partial Content",
  300: "Multiple Choices",
  301: "Moved Permanently",
  302: "Found",
  303: "See Other",
  304: "Not Modified",
  305: "Use Proxy",
  307: "Temporary Redirect",
  400: "Bad Request",
  401: "Unauthorized",
  402: "Payment Required",
  403: "Forbidden",
  404: "Not Found",
  405: "Method Not Allowed",
  406: "Not Acceptable",
  407: "Proxy Authentication Required",
  408: "Request Timeout",
  409: "Conflict",
  410: "Gone",
  411: "Length Required",
  412: "Precondition Failed",
  413: "Request Entity Too Large",
  414: "Request-URI Too Long",
  415: "Unsupported Media Type",
  416: "Requested Range Not Satisfiable",
  417: "Expectation Failed",
  500: "Internal Server Error",
  501: "Not Implemented",
  502: "Bad Gateway",
  503: "Service Unavailable",
  504: "Gateway Timeout",
  505: "HTTP Version Not Supported"
}


class HTTP:
    def __init__(self, port: int, max_con: int, addr_family: str = "INET")  -> None:
        """
        __init__ Initialize the web server

        Initialize the TCP socket to listen on the specified port with the
        specified maximum number of connections.

        :param port: Port to bind to
        :type port: int
        :param max_con: Maximum number of concurrent connections
        :type max_con: int
        :param addr_family: Address family to use. One of INET or INET6,
            defaults to INET
        :type addr_family: str, optional
        :return: Socket to listen on
        :rtype: socket
        """

        info("Network", "Initializing HTTP server")

        self._buzzer = Pin(2, Pin.OUT)
        alarm(self._buzzer, 2000, 250, 500)

        if addr_family == "INET6":
            family = socket.AF_INET6
        else:
            family = socket.AF_INET

        self._s = socket.socket(family, socket.SOCK_STREAM)
        self._s.bind(('', port))
        self._s.listen(max_con)

        info("Network", "HTTP server initialized")        

    def listen(self) -> None:
        """
        listen Listen and respond to HTTP requests
        """

        info("Network", "Waiting for requests")
        

        while True:
            self._conn, addr = self._s.accept()
            info("Network", "Got connection from {}".format(addr))

            # Variables to store request components
            request = ""
        

            # Read request
            while True:
                chunk = self._conn.recv(1024)
                request += chunk.decode("utf-8")

                # Denotes end of request
                if not chunk or chunk == b"\r\n" or b"\r\n" in chunk:
                    break

            # Parse request
            headers, content = request.split("\r\n\r\n")
            headers = headers.split("\r\n")
            # Check it was a post request
            if headers[0][0:4] != "POST":
                info("Network", "Request was not a POST request")
                self._send(405)
                continue

            # Make sure it is json we are using                
            index = getSubstringFromList(headers, "Content-Type: ")
            if index != -1:
                try:
                    content_type = headers[index][14:]
                except IndexError:
                    info("Network", "Could not find Content-Type header")
                    self._send(400)
            else:
                info("Network", "Could not find Content-Type header")
                self._send(400)

            if content_type != "application/json":
                info("Network", "Expected content type application/json. Got {}".format(content_type))
                self._send(400)
                continue

            # Now we process the data and set alarms
            try:
                data = json.loads(content)
            except:
                error("Network", "Failed to load JSON")
                self._send(500)
            
            if data["state"] == "alerting":
                info("Network", "Recieved alerting notification")
                alarm(self._buzzer, 5000, 500, 100)
            
            self._send(204)
            
    def _send(self, code: int) -> None:
        """
        _send Send a response code

        Send a HTTP response code to the client

        :param code: Code to send
        :type code: int
        """

        if code not in CODES:
            raise ValueError("Invalid response code")

        self._conn.send("HTTP/1.1 {} {} \r\n\r\n".format(code, CODES[code]))

        # Ensure connection gets closed at end
        self._conn.close()
        debug("Network", "Closed connection")
