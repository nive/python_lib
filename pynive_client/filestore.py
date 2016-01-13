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

    # retrieve a token to connect to the data storage service
    token = niveuser.token(identity='username', password='userpw')

    storage = filestore.FileStore(service='mystorage',domain='mydomain',token=token)

    # get a files infos
    file = storage.getItem(path="index.html")
    print file.name, file.mime, file.size

"""
from StringIO import StringIO

import endpoint


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


    def getItem(self, path, reqSettings=None):
        """

        :param path:
        :param reqSettings:
        :return: file infos: name, type, size, mime, header, ctime, mtime
        """
        values = dict()
        content, response = self.call('@getItem', values, reqSettings, path)
        return endpoint.Result(response=response,
                               **content)


    def newItem(self, path, name="", type=None, contents=None, mime=None, header=None, decode=False, reqSettings=None):
        """

        :param name:
        :param path: if empty name is split into name and path
        :param contents:
        :param type:
        :param mime:
        :param header:
        :param decode:
        :param reqSettings:
        :return: Result(result, invalid, messages)
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
                               messages=content.get('messages',()),
                               response=response)


    def setItem(self, path, contents=None, mime=None, header=None, decode=False, reqSettings=None):
        """

        :param path:
        :param contents:
        :param mime:
        :param header:
        :param decode:
        :param reqSettings:
        :return: Result(result, invalid, messages)
        """
        values = dict(contents=contents, mime=mime, header=header, decode=decode)
        content, response = self.call('@setItem', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               invalid=content.get('invalid',()),
                               messages=content.get('messages',()),
                               response=response)


    def removeItem(self, path, recursive=False, reqSettings=None):
        """

        :param path:
        :param recursive:
        :param reqSettings:
        :return: Result(result (count deleted), messages)
        """
        values = dict(recursive=recursive)
        content, response = self.call('@removeItem', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               messages=content.get('messages',()),
                               response=response)


    def read(self, path, reqSettings=None):
        """

        :param path:
        :param reqSettings:
        :return: file contents
        """
        values = dict()
        reqSettings = reqSettings or {}
        reqSettings["stream"]=True
        content, response = self.call('@read', values, reqSettings, path)
        return FileWrapper(response)


    def write(self, path, file, reqSettings=None):
        """

        :param path:
        :param file: readable file stream
        :param reqSettings:
        :return: Result(result, messages)
        """
        if isinstance(file, basestring):
            file = StringIO(file)
        content, response = self.call('@write', file, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               messages=content.get('messages',()),
                               response=response)


    def move(self, path, newpath, reqSettings=None):
        """

        :param path:
        :param newpath:
        :param reqSettings:
        :return: Result(result, messages)
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
                               messages=content.get('messages',()),
                               response=response)


    def list(self, path, type=None, sort="name", order=None, size=50, start=1, reqSettings=None):
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


    def allowed(self, path, permission, reqSettings=None):
        """

        :param path:
        :param permission: one or multiple permission names
        :param reqSettings:
        :return: dict {permission: True or False}
        """
        values = dict(permission=permission)
        content, response = self.call('@allowed', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               permission=content.get('permission',{}),
                               messages=content.get('messages',()),
                               response=response)


    def getPermissions(self, path, reqSettings=None):
        """

        :param path:
        :param reqSettings:
        :return: list of permission - group assignments
        """
        values = dict()
        content, response = self.call('@getPermissions', values, reqSettings, path)
        return content


    def setPermissions(self, path, permissions, reqSettings=None):
        """

        :param path:
        :param permissions: dict/list. one or multiple permissions {permission, group, action="allow"}
        :param reqSettings:
        :return: Result(result, messages)
        """
        values = dict(permissions=permissions)
        content, response = self.call('@setPermissions', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               messages=content.get('messages',()),
                               response=response)


    def getOwner(self, path, reqSettings=None):
        """

        :param path:
        :param reqSettings:
        :return: owner
        """
        values = dict()
        content, response = self.call('@getOwner', values, reqSettings, path)
        return content.get('owner')


    def setOwner(self, path, owner, reqSettings=None):
        """

        :param path:
        :param owner:
        :param reqSettings:
        :return: Result(result, messages)
        """
        values = dict(owner=owner)
        content, response = self.call('@setOwner', values, reqSettings, path)
        return endpoint.Result(result=content.get('result'),
                               messages=content.get('messages',()),
                               response=response)


    def view(self, path, options=None, reqSettings=None):
        """

        :param reqSettings:
        :return: status
        """
        content, response = self.call('', None, reqSettings, path)
        return FileWrapper(response)


    def ping(self, options=None, reqSettings=None):
        """

        :param reqSettings:
        :return: status
        """
        values = dict()
        if options:
            values.update(options)
        content, response = self.call('@ping', values, reqSettings, '/')
        return endpoint.Result(result=content.get('result'),
                               response=response)


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
        return self.response.iter_content(size).next()

    def close(self):
        return self.response.close()

