from gevent import http, Greenlet
from urlparse import parse_qsl
import simplejson

import logging
log = logging.getLogger(__name__)


class HttpListener(Greenlet):
    xmpp = None

    def __init__(self, port, address="0.0.0.0"):
        super(HttpListener, self).__init__()
        self._port = port
        self._address = address

    def _get_postdata(self, request, headers):
        # get input data from buffer
        data = "".join(part for part in request.input_buffer)

        if headers.get('content-type') == 'application/x-www-form-urlencoded':
            qs = parse_qsl(data)
            postdata = {}  # convert to dict
            for k, v in qs:
                postdata[k] = v
        else:
            postdata = simplejson.loads(data)

        return postdata

    def _handle_connection(self, request):
        # accept only HTTP POST
        if request.typestr != 'POST':
            request.add_output_header('Allow', 'POST')
            request.add_output_header('Content-Type', 'text/html')
            return request.send_reply(405, 'Method Not Allowed', '<h1>HTTP 405 - Method not allowed</h1>')

        # convert headers to dict (throws out headers with same name)
        headers = {}
        for k, v in request.get_input_headers():
            headers[k.lower()] = v

        postdata = self._get_postdata(request, headers)
        print postdata

        self.xmpp.send_question('viktorstiskala@abdoc.net', "test", "123")

        if request.uri == '/':
            request.add_output_header('Content-Type', 'text/html')
            request.send_reply(200, "OK", '<b>hello world</b>')
        else:
            request.add_output_header('Content-Type', 'text/html')
            request.send_reply(404, "Not Found", "<h1>Not Found</h1>")

    def _run(self):
        log.info('HTTP Listener serving on %s:%d...' % (self._address, self._port))
        http.HTTPServer((self._address, self._port), self._handle_connection).serve_forever()


