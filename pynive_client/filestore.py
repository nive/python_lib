# (c) 2013-2015 Nive GmbH - nive.io
# This file is released under the BSD-License.
#
# Nive User service python client
# ------------------------------------------------
# Documentation: http:#www.nive.co/docs/webapi/filestore.html#api
#
"""
**Example code 1**


::

    from pynive_client import filestore

    storage = filestore.FileStore(service='mystorage', domain='mydomain')

    # list items
    result = storage.list(path="/", sort='path', order='<', size=20, start=1)
    for item in result:
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


    def getItem(self, name, **reqSettings):
        """

        :param name:
        :param reqSettings:
        :return: file infos: name, type, size, mime, header, ctime, mtime
        """
        values = dict(name=name)
        content, response = self.call('getItem', values, reqSettings)
        # todo file wrapper
        return content


    def newItem(self, name, type=None, contents=None, mime=None, header=None, **reqSettings):
        """

        :param name:
        :param contents:
        :param type:
        :param mime:
        :param header:
        :param reqSettings:
        :return: result, invalid, messages
        """
        #todo handle streams
        values = dict(name=name, type=type, contents=contents, mime=mime, header=header)
        content, response = self.call('newItem', values, reqSettings)
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def setItem(self, name, contents=None, mime=None, header=None, **reqSettings):
        """

        :param name:
        :param contents:
        :param mime:
        :param header:
        :param reqSettings:
        :return: result, invalid, messages
        """
        #todo handle streams
        values = dict(name=name, contents=contents, mime=mime, header=header)
        content, response = self.call('setItem', values, reqSettings)
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def removeItem(self, name, recursive=False, **reqSettings):
        """

        :param name:
        :param recursive:
        :param reqSettings:
        :return: count deleted, messages
        """
        values = dict()
        content, response = self.call('removeItem', values, reqSettings)
        return content.get('result'), content.get('messages',())


    def read(self, name, **reqSettings):
        """

        :param name:
        :param reqSettings:
        :return: file contents
        """
        values = dict(name=name)
        content, response = self.call('read', values, reqSettings)
        # todo file wrapper
        return content


    def write(self, name, contents, **reqSettings):
        """

        :param name:
        :param contents:
        :param reqSettings:
        :return: result, messages
        """
        #todo handle streams
        values = dict(name=name, contents=contents)
        content, response = self.call('write', values, reqSettings)
        return content.get('result'), content.get('messages',())


    def move(self, name, newpath, **reqSettings):
        """

        :param name:
        :param newpath:
        :param reqSettings:
        :return: result, messages
        """
        values = dict(name=name, newpath=newpath)
        content, response = self.call('move', values, reqSettings)
        return content.get('result'), content.get('messages',())


    def list(self, name=None, type=None, sort="name", order=None, size=50, start=1, **reqSettings):
        """

        :param name:
        :param type:
        :param sort:
        :param order:
        :param size:
        :param start:
        :param reqSettings:
        :return: items including {name, type, size, mime, mtime, ctime}
        """
        values = dict(name=name, type=type, sort=sort, order=order, size=size, start=start)
        content, response = self.call('list', values, reqSettings)
        # todo result set class with iterator
        if not content:
            return ()
        return content["items"]


    def allowed(self, name, permission, **reqSettings):
        """

        :param name:
        :param permission: one or multiple permission names
        :param reqSettings:
        :return: dict {permission: True or False}
        """
        values = dict(name=name, permission=permission)
        content, response = self.call('allowed', values, reqSettings)
        return content


    def getPermissions(self, name, **reqSettings):
        """

        :param name:
        :param reqSettings:
        :return: list of permission - group assignments
        """
        values = dict(name=name)
        content, response = self.call('getPermissions', values, reqSettings)
        return content


    def setPermissions(self, name, permission, group, action="allow", **reqSettings):
        """

        :param name:
        :param permission:
        :param group:
        :param action:
        :param reqSettings:
        :return: result, messages
        """
        values = dict(name=name, permission=permission, group=group, action=action)
        content, response = self.call('setPermissions', values, reqSettings)
        return content.get('result'), content.get('messages',())


    def getOwner(self, name, **reqSettings):
        """

        :param name:
        :param reqSettings:
        :return: owner
        """
        values = dict(name=name)
        content, response = self.call('getOwner', values, reqSettings)
        return content


    def setOwner(self, name, owner, **reqSettings):
        """

        :param name:
        :param owner:
        :param reqSettings:
        :return: result, messages
        """
        values = dict(name=name, owner=owner)
        content, response = self.call('setOwner', values, reqSettings)
        return content.get('result'), content.get('messages',())







