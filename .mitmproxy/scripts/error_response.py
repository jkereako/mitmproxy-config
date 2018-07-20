import json
import time
from urllib.parse import urlparse, parse_qsl

class ErrorResponse(object):
    """
    Stub a response from the server.
    """
    def __init__(self):
        self.response_delay = 0
        self.status_code = 0
        self.error_code = ''
        self.error_response = {'errorStatus': {'code': '', 'message': 'Stubbed response from MITM Proxy'}}

    def request(self, flow):
        query_pairs = self.parse_query_string(flow)

        for query_pair in query_pairs:
            param = query_pair[0]
            arg  = query_pair[1]

            # Clear Cookies
            if param == 'clear_cookies':
                try:
                     if int(arg) == 1:
                        flow.request.cookies = []
                except ValueError:
                    # Do not clear the cookies if we can't parse the argument
                    pass

            # Error Code
            if param == 'code':
                self.error_code = str(arg)

            # Checks for a value in the parameter, attempts to cast it to an int and,
            # if the cast fails, then reset the instance properties to their default
            # values.
            
            # Response Delay
            elif param == 'delay':
                try:
                    self.response_delay = int(arg)
                except ValueError:
                    self.response_delay = 0

            # Status Code
            elif param == 'status':
                try:
                    self.status_code = int(arg)
                except ValueError:
                     self.status_code = 0

    def responseheaders(self, flow):
        flow.response.headers["X-Proxy"] = "Intercepted by MITM Proxy"

        if self.status_code == 0:
            return

        flow.response.status_code = self.status_code

    def response(self, flow):
        # Delay the response by the specified number of seconds
        if self.response_delay > 0:
            time.sleep(self.response_delay)
            # Reset `response_delay` to 0 to prevent every request from having 
            # a response delay.
            self.response_delay = 0

        if self.error_code == '':
            return

        self.error_response['errorStatus']['code'] = self.error_code
        flow.response.headers['Content-Type'] = 'application/json'
        flow.response.content = json.dumps(self.error_response).encode()

    def parse_query_string(self, flow):
        url = urlparse(flow.request.path)

        return parse_qsl(url.query)

# Load
addons = [ErrorResponse()]
