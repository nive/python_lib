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
import time


def makeUrl(method=None, service=None, domain=None, path=None, secure=None, version=None, extendedPath=None, **kw):
    """
    Construct a service endpoint url based on options

    :param method:
    :param service:
    :param domain:
    :param path: base path set on client instance level
    :param extendedPath: addition
    :param secure:
    :param version:
    :return: string
    """
    defaultDomain = '.nive.io'
    defaultProtocol = 'https'

    # service service
    if not service:
        raise EndpointException('Invalid service name')

    # domain
    if not domain:
        raise EndpointException('Invalid domain name')

    # method
    #if not method:
    #    raise EndpointException('Invalid method name')

    # if '.' contained in domain, a fully qualified domain expected
    domain = domain+defaultDomain if domain.find('.')==-1 else domain

    # protocol
    protocol = defaultProtocol
    if secure is False:
        protocol = 'http'

    # construct path by concatenating `path` and `extendedPath`
    basepath = path
    path = extendedPath
    if path or basepath:
        # this option is not supported by all services
        if not path:
            path = basepath
        elif basepath and not path.startswith('/'):
            if basepath.endswith('/'):
                path = basepath + path
            else:
                path = basepath + '/' + path
        # remove slash
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]\

    # make url
    url = [protocol+':/', domain, service] # the single slash gets joined with a second slash
    if version:
        url.append(version)
    if path:
        url.append(path)
    if method:
        url.append(method)
    return '/'.join(url)


class Client(object):
    """
    Basic client functionality

    Handles enpoint urls, http sessions (based on requests module), connection setup
    and service request processing.
    """

    timeout = None
    adapter = requests
    pingurl = '@ping'
    counter = tcounter = 0

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
        self.counter = 0
        self.tcounter = 0
        return session


    def call(self, method, values, reqSettings, extendedPath=None):
        """
        Calls a service method and parses the response.

        Exceptions:

        - pynive exceptions: ServiceFailure, AuthorizationFailure, Forbidden, InvalidParameter, ClientFailure
        - requests package excps: see `requests.exceptions`

        :param method: Service function name to be called
        :param values: Payload transmitted to the service
        :param reqSettings: additional request settings
        :return: content, response: `content` contains the the parsed body returned by the service, `response`
        is the raw response received.
        """
        url = self.url(method=method, extendedPath=extendedPath)
        reqSettings = reqSettings or {}
        response = self._send(url, method, values, **reqSettings)
        self.counter += 1
        self.tcounter += response.elapsed.total_seconds()
        content, response = self._handleResponse(response, method, values, reqSettings)
        return content, response


    def url(self, method, extendedPath=None):
        """
        Creates the service endpoint url for the method. Uses the options set on
        client instantioation. see `__init__`

        :param method: Service function name to be called
        :param extendedPath: additional path info
        :return: string: service method url
        """
        return makeUrl(method=method, extendedPath=extendedPath, **self.options)


    def request(self, path, **reqSettings):
        """
        Calls a url.

        :param reqSettings: additional request settings

        :return: FileWrapper instance
        """
        method=""
        values=None
        url = self.url(method=method, extendedPath=path)
        response = self._send(url, method, values, **reqSettings)
        content, response = self._handleResponse(response, method, values, reqSettings)
        return FileWrapper(response)


    def ping(self, options=None, **reqSettings):
        """

        :param reqSettings:
        :return: status
        """
        values = dict()
        if options:
            values.update(options)
        content, response = self.call(self.pingurl, values, reqSettings, '/')
        return Result(result=content.get('result'),
                      response=response)


    def _send(self, url, method, values, **reqSettings):
        req = reqSettings
        if not 'headers' in req:
            req['headers'] = {}

        charset = req.get("charset")
        if values is not None:
            if isinstance(values, (dict, list, tuple)):
                req['data'] = json.dumps(values, encoding=charset or 'utf-8')
                ct = 'application/json'
                if charset:
                    ct += '; charset='+charset
                req['headers']['Content-type'] = ct

            else:
                # stream writer
                req['data'] = values

        if req.get('token'):
            req['headers']['x-auth-token'] = req['token']
            del req['token']
        elif self.session and self.session.token:
            req['headers']['x-auth-token'] = self.session.token
        elif self.options and self.options.get('token'):
            req['headers']['x-auth-token'] = self.options['token']

        if not req.get('type'):
            httpmethod = 'POST' if values is not None else 'GET'
        else:
            httpmethod = req['type']
            del req['type']

        if 'charset' in req:
            del req['charset']

        if self.session:
            req['cookies'] = self.session.cookies

        if not 'timeout' in req:
            req['timeout'] = self.timeout

        adapter = self.session or self.adapter
        response = adapter.request(httpmethod, url, **req)
        if response.status_code==503:
            # service not ready -> retry
            for retry in (0.3, 0.5, 0.5, 0.5, 1):
                time.sleep(retry)
                self.log.warning("Service not ready (503). Retrying.")
                response = adapter.request(httpmethod, url, **req)
                if response.status_code!=503:
                    break
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
        elif response.status_code == 401:
            # authentication failure
            raise AuthorizationFailure(msg)
        elif response.status_code == 403:
            # access not allowed
            raise Forbidden(msg)
        elif response.status_code == 404:
            # not found
            raise NotFound(msg)
        elif response.status_code == 422:
            # Invalid parameter
            try:
                result = response.json()
            except ValueError:
                result = {}
            if not isinstance(result, dict):
                result = {}
            raise InvalidParameter(msg, **result)
        elif response.status_code == 413:
            # Invalid parameter
            try:
                result = response.json()
            except ValueError:
                result = {}
            if not isinstance(result, dict):
                result = {}
            raise ServiceLimits(msg, **result)
        elif 400 <= response.status_code <= 499:
            # client failure
            try:
                result = response.json()
            except ValueError:
                result = {}
            if not isinstance(result, dict):
                result = {}
            raise ClientFailure(msg, **result)
        self.log.info("Response: "+msg)

        # parse body
        # todo handle streaming response and iterators
        if response.headers.get("Content-Type","").find("/json")!=-1:
            content = response.json()
        else:
            content = response.content
        if content is None:
            content = dict()
        return content, response


    def _fmtMsgs(self, msgs, default, seperator=' ; '):
        if isinstance(msgs, dict):
            msgs = msgs.get('messages')
        if not msgs:
            return default
        if isinstance(msgs, (list,tuple)):
            return seperator.join(msgs)
        return msgs


class Result(object):
    # wrapper for api call results
    result = 1

    def __init__(self, **kws):
        if not kws:
            self.result = 0
        elif len(kws)==1 and kws.get("response"):
            self.result = 0
            self.response = kws["response"]
        else:
            self.result = 1
            self.__dict__.update(kws)

    def __len__(self):
        return 1 if self.result else 0

    def __eq__(self, other):
        if isinstance(other, bool):
            return other == bool(self.result)
        if isinstance(other, (int,long)):
            return other == int(self.result)
        return other == self.result

    def __getitem__(self, key):
        return self.__dict__[key]

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def __repr__(self):
        return str(self.__dict__)



class FileWrapper(object):
    # turns a response iterator int a readable file object

    def __init__(self, response):
        self.response = response

    def read(self, size=5000):
        if size==-1:
            # read all and return. not supported by iter_content
            data = ""
            for raw in self.response.iter_content(999999):
                data+=raw
            return data
        try:
            return self.response.iter_content(size).next()
        except StopIteration:
            return ""

    def close(self):
        return self.response.close()

class EndpointException(Exception):
    """
    raised in case enpoint url construction fails
    """


class AuthorizationFailure(Exception):
    """
    raised in case a token or cookie is invalid (401)
    """


class Forbidden(Exception):
    """
    raised in case a service call is not authorized (403)
    """


class NotFound(Exception):
    """
    raised in case a ressource is not found (404)
    """


class ClientFailure(Exception):
    """
    raised in case a service call returns not found or a similar error (404, 405-417)
    """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        super(ClientFailure, self).__init__(*args)


class ServiceLimits(Exception):
    """
    raised in case a service call returns limits or a similar error (413)
    """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        super(ServiceLimits, self).__init__(*args)


class InvalidParameter(Exception):
    """
    raised in case a service call fails due to invalid function parameter (400)
    """
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        super(InvalidParameter, self).__init__(*args)


class ServiceFailure(Exception):
    """
    raised in case a service call fails on the server side (500)
    """

