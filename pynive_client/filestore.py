# (c) 2013-2015 Nive GmbH - nive.io
# This file is released under the BSD-License.
#
# Nive Filestore service python client
# ------------------------------------------------
# Documentation: http://www.nive.co/docs/webapi/filestore.html#api
#
"""
**Example code 1**

::

    from pynive_client import filestore

    storage = filestore.FileStore(service='mystorage', domain='mydomain')

    # list items
    items = storage.list(path="/", sort='path', order='<', size=20, start=1)
    for item in items:
        print item["name"], item["size"]



**Example code 2**

Retrieve a security token and add, update, get and remove a item

::

    from pynive_client import useraccount
    from pynive_client import filestore

    niveuser = useraccount.User(domain='mydomain')

    # retrieve a auth-token to connect to the data storage service
    auth = niveuser.token(identity='username', password='userpw')

    storage = filestore.FileStore(service='mystorage',domain='mydomain',auth=auth)

    # get a files infos
    file = storage.getItem(path="index.html")
    print file.name, file.mime, file.size

"""
from io import StringIO

from pynive_client import endpoint

# python 2/3
try:
    import basestring
except ImportError:
    basestring = str


class FileStore(endpoint.Client):

    default_version='api'

    def __init__(self, service, domain=None, session=None, **options):
        """

        :param service: data storage instance name
        :param domain: domain the service is part of
        :param session: http session object
        :param options: other endpoint options. see endpoint.py.
        """
        super(FileStore, self).__init__(service=service,
                                        domain=domain,
                                        session=session,
                                        **options)
        if not "version" in self.options:
            self.options["version"] = self.default_version


    def getItem(self, path, **reqSettings):
        """

        :param path:
        :param reqSettings:
        :return: file infos: name, type, size, mime, header, ctime, mtime
        """
        values = dict()
        content, response = self.call('@getItem', values, reqSettings, path)
        return endpoint.Result(response=response,
                               **content)


    def newItem(self, path, name="", type=None, contents=None, mime=None, header=None, decode=False, **reqSettings):
        """

        :param name:
        :param path: if empty name is split into name and path
        :param contents:
        :param type:
        :param mime:
        :param header:
        :param decode:
        :param reqSettings:
        :return: Result(result, invalid, message)
        """
        # map name / path
        if not path and name.find("/")>-1:
            parts = name.split("/")
            name = parts[-1]
            path = "/".join(parts[:-1])
        elif not name and path.find("/")>-1:
            parts = path.split("/")
            name = parts[-1]
            path = "/".join(parts[:-1])
        elif not name and path:
            name = path
            path = ""
        values = dict(name=name, type=type, contents=contents, mime=mime, header=header, decode=decode)
        content, response = self.call('@newItem', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               invalid=content.get('invalid',()),
                               message=content.get('message',()),
                               response=response)


    def setItem(self, path, contents=None, mime=None, header=None, decode=False, **reqSettings):
        """

        :param path:
        :param contents:
        :param mime:
        :param header:
        :param decode:
        :param reqSettings:
        :return: Result(result, invalid, message)
        """
        values = dict(contents=contents, mime=mime, header=header, decode=decode)
        content, response = self.call('@setItem', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               invalid=content.get('invalid',()),
                               message=content.get('message',()),
                               response=response)


    def removeItem(self, path, recursive=False, **reqSettings):
        """

        :param path:
        :param recursive:
        :param reqSettings:
        :return: Result(result (count deleted), message)
        """
        values = dict(recursive=recursive)
        content, response = self.call('@removeItem', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               message=content.get('message',()),
                               response=response)


    def read(self, path, **reqSettings):
        """

        :param path:
        :param reqSettings:
        :return: file contents
        """
        values = dict()
        reqSettings = reqSettings or {}
        reqSettings["stream"]=True
        content, response = self.call('@read', values, reqSettings, path)
        return endpoint.FileWrapper(response)


    def write(self, path, file, mime=None, **reqSettings):
        """

        :param path:
        :param file: readable file stream
        :param reqSettings:
        :return: Result(result, message)
        """
        if isinstance(file, basestring):
            file = StringIO(file)
        reqSettings = reqSettings or {}
        reqSettings["type"] = "PUT"
        if mime:
            reqSettings["headers"] = reqSettings.get("headers") or {}
            reqSettings["headers"]["Content-type"] = mime
        content, response = self.call('@write', file, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               message=content.get('message',()),
                               response=response)


    def move(self, path, newpath, **reqSettings):
        """

        :param path:
        :param newpath:
        :param reqSettings:
        :return: Result(result, message)
        """
        # handle relative new path
        basepath = self.options.get("path")
        if basepath and not newpath.startswith("/"):
            if not basepath.endswith("/"):
                basepath += "/"
            newpath = basepath + newpath

        values = dict(newpath=newpath)
        content, response = self.call('@move', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               message=content.get('message',()),
                               response=response)


    def list(self, path, type=None, sort="name", order=None, size=50, start=1, **reqSettings):
        """

        :param path:
        :param type:
        :param sort:
        :param order:
        :param size:
        :param start:
        :param reqSettings:
        :return: items including {name, type, size, mime, mtime, ctime}
        """
        values = dict(type=type, sort=sort, order=order, size=size, start=start)
        content, response = self.call('@list', values, reqSettings, path)
        # todo result set class with iterator
        if not content:
            return ()
        return content["items"]


    def allowed(self, path, permissions, **reqSettings):
        """

        :param path:
        :param permissions: one or multiple permission names
        :param reqSettings:
        :return: dict {permission: True or False}
        """
        values = dict(permissions=permissions)
        content, response = self.call('@allowed', values, reqSettings, path)
        return endpoint.Result(response=response, **content)


    def getPermissions(self, path, **reqSettings):
        """

        :param path:
        :param reqSettings:
        :return: list of permission - group assignments
        """
        values = dict()
        content, response = self.call('@getPermissions', values, reqSettings, path)
        return content


    def setPermissions(self, path, permissions, **reqSettings):
        """

        :param path:
        :param permissions: dict/list. one or multiple permissions {permission, group, action="replace"}
        :param reqSettings:
        :return: Result(result, message)
        """
        values = dict(permissions=permissions)
        content, response = self.call('@setPermissions', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               message=content.get('message',()),
                               response=response)


    def getOwner(self, path, **reqSettings):
        """

        :param path:
        :param reqSettings:
        :return: owner
        """
        values = dict()
        content, response = self.call('@getOwner', values, reqSettings, path)
        return content.get('owner')


    def setOwner(self, path, owner, **reqSettings):
        """

        :param path:
        :param owner:
        :param reqSettings:
        :return: Result(result, message)
        """
        values = dict(owner=owner)
        content, response = self.call('@setOwner', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               message=content.get('message',()),
                               response=response)


    def view(self, path, options=None, **reqSettings):
        """

        :param reqSettings:
        :return: status
        """
        content, response = self.call('', None, reqSettings, path)
        return endpoint.FileWrapper(response)


