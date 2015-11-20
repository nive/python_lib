# (c) 2013-2015 Nive GmbH - nive.io
# This file is released under the BSD-License.
#
# Nive api endpoint url construction
# ----------------------------------
# Documentation: http://www.nive.co/docs/webapi/endpoint.html
#

import requests
import json
import logging



def makeUrl(method=None, service=None, domain=None, path=None, secure=None, version=None):
    """
    Construct a service endpoint url based on options

    :param method:
    :param service:
    :param domain:
    :param path:
    :param secure:
    :param version:
    :return: string
    """
    defaultDomain = '.nive.io'
    defaultProtocol = 'https'

    # service service
    if not service:
        raise EndpointException('Invalid service name')

    # method
    if not method:
        raise EndpointException('Invalid method name')

    # domain
    if not domain:
        raise EndpointException('Invalid domain name')
    # if '.' contained in domain, a fully qualified domain expected
    domain = domain+defaultDomain if domain.find('.')==-1 else domain

    # protocol
    protocol = defaultProtocol
    if secure is False:
        protocol = 'http'

    # base path
    if path:
        # relative directory not supported
        if path.startswith('./') or path.startswith('../'):
            raise EndpointException('Relative path not allowed')
        # remove slash
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]

    # make url
    url = [protocol+':/', domain, service] # the single slash gets joined with a second slash
    if version:
        url.append(version)
    if path:
        url.append(path)
    url.append(method)
    return '/'.join(url)


class Client(object):
    """
    Basic client functionality

    Handles enpoint urls, http sessions (based on requests module), connection setup
    and service request processing.
    """

    timeout = 5
    adapter = requests

    def __init__(self, service=None, domain=None, session=None, **options):
        """
        Service client initialisation.

        :param service: service name
        :param domain: endpoint options used to connect to the service
        :param session: http session object to reuse connections
        :param **options: other endpoint options. see makeUrl().
        """
        self.options = {'service': service, 'domain': domain}
        if options:
            self.options.update(options)
        self.session = session
        self.log = logging.getLogger(service)


    def newSession(self, max_retries=3, pool_connections=3, pool_maxsize=5, token=None):
        """
        Create a new http session. Can be used to connect to multiple services. Supports
        authentication cookies.

        :param max_retries :
        :param pool_connections :
        :param pool_maxsize :
        :return: http session
        """
        session = self.adapter.Session()
        # setup requests session
        if hasattr(self.adapter, 'adapters'):
            adapter = self.adapter.adapters.HTTPAdapter(max_retries=max_retries,
                                                        pool_connections=pool_connections,
                                                        pool_maxsize=pool_maxsize)
            session.mount("http://", adapter)
        # use session instance to store token
        # todo rename token attr
        session.token = token
        self.session = session
        return session


    def call(self, method, values, reqSettings):
        """
        Calls a service method and parses the response.

        :param method: Service function name to be called
        :param values: Payload transmitted to the service
        :param reqSettings: additional request settings
        :return: content, response: `content` contains the the parsed body returned by the service, `response`
        is the raw response received.
        """
        url = self.url(method=method)
        response = self._send(url, method, values, reqSettings)
        content, response = self._handleResponse(response, method, values, reqSettings)
        return content, response


    def url(self, method):
        """
        Creates the service endpoint url for the method. Uses the options set on
        client instantioation. see `__init__`

        :param method: Service function name to be called
        :return: string: service method url
        """
        return makeUrl(method=method, **self.options)


    def _send(self, url, method, values, reqSettings):
        req = reqSettings or {}
        if not 'headers' in req:
            req['headers'] = {}

        if values is not None:
            # todo support streaming and file uploads
            if isinstance(values, (dict, list, tuple)):
                req['data'] = json.dumps(values)
                req['headers']['contentType'] = 'application/json'

        if req.get('token'):
            req['headers']['x-auth-token'] = req['token']
        elif self.session and self.session.token:
            req['headers']['x-auth-token'] = self.session.token

        if not req.get('type'):
            httpmethod = 'POST' if values is not None else 'GET'
        else:
            httpmethod = req['type']

        if self.session:
            req['cookies'] = self.session.cookies

        if not 'timeout' in req:
            req['timeout'] = self.timeout

        adapter = self.session or self.adapter
        response = adapter.request(httpmethod, url, **req)
        return response


    def _handleResponse(self, response, method, values, reqSettings):
        # handle status codes
        if response.reason:
            msg = "%s %d: %s" % (response.reason, response.status_code, response.url)
        else:
            msg = "%d: %s" % (response.status_code, response.url)
        if 500 <= response.status_code <= 505:
            # server / network failure
            raise ServiceFailure(msg)
        elif response.status_code in (401,):
            # authentication failure
            raise AuthorizationFailure(msg)
        elif response.status_code in (403,):
            # access not allowed
            raise Forbidden(msg)
        elif 404 <= response.status_code <= 417:
            # client failure
            raise ClientFailure(msg)
        elif response.status_code == 400:
            # Invalid parameter
            raise InvalidParameter(msg)
        self.log.info("Response: "+msg)

        # parse body
        # todo handle streaming response and iterators
        if response.headers.get("Content-Type","").find("/json")!=-1:
            content = response.json()
        else:
            content = response.content
        return content, response


    def _fmtMsgs(self, msgs, default, seperator=' ; '):
        if isinstance(msgs, dict):
            msgs = msgs.get('messages')
        if not msgs:
            return default
        if isinstance(msgs, (list,tuple)):
            return seperator.join(msgs)
        return msgs



class EndpointException(Exception):
    """
    raised in case enpoint url construction fails
    """
    pass


class AuthorizationFailure(Exception):
    """
    raised in case a token or cookie is invalid (401)
    """
    pass


class Forbidden(Exception):
    """
    raised in case a service call is not authorized (403)
    """
    pass


class ClientFailure(Exception):
    """
    raised in case a service call returns not found or a similar error (404, 405-417)
    """
    pass


class InvalidParameter(Exception):
    """
    raised in case a service call fails due to invalid function parameter (400)
    """
    pass

class ServiceFailure(Exception):
    """
    raised in case a service call fails on the server side (500)
    """
    pass

