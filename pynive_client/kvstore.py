# (c) 2013-2015 Nive GmbH - nive.io
# This file is released under the BSD-License.
#
# Nive Key-Value store service python client
# ------------------------------------------------
# Documentation: http:#www.nive.co/docs/webapi/kvstore.html#api
#
"""
**Example code 1**

Create a user instance, authenticate and retrieve the users profile values

::

    from pynive_client import kvstore

    storage = kvstore.KvStore(service='mystorage',domain='mydomain')

    # list items
    result = storage.list(sort='key', order='<', size=20, start=1)
    for item in result:
        print item["key"], item["value"]



**Example code 2**

Retrieve a security token and add, update, get and remove a item

::

    from pynive_client import useraccount
    from pynive_client import kvstore

    niveuser = useraccount.User(domain='mydomain')

    # retrieve a token to connect to the data storage service
    token = niveuser.token(identity='username', password='userpw')

    storage = kvstore.KvStore(service='mystorage',domain='mydomain',token=token)

    # add a new item
    result = storage.newItem({"key": "key1", "value": "value1"})

    # get a value
    item = storage.getItem(key="key1")
    value = item.get("value")

    # update a existing item
    result = storage.setItem({"key": "key1", "value": "a new value"})

    # remove the item
    result = storage.removeItem(key="key1")

"""

import endpoint


class KvStore(endpoint.Client):

    default_version='api'
    pingurl='ping'


    def __init__(self, service, domain=None, session=None, **options):
        """

        :param service: data storage instance name
        :param domain: domain the service is part of
        :param session: http session object
        :param options: other endpoint options. see endpoint.py.
        """
        super(KvStore, self).__init__(service=service,
                                      domain=domain,
                                      session=session,
                                      **options)
        if not "version" in self.options:
            self.options["version"] = self.default_version


    def getItem(self, key=None, id=None, reqSettings=None):
        """

        :param key:
        :param id:
        :param reqSettings:
        :return: dict
        """
        values = {}
        if key is not None:
            values["key"] = key
        if id is not None:
            values["id"] = id
        content, response = self.call('getItem', values, reqSettings)
        return endpoint.Result(items=content.get('items'),
                               messages=content.get('messages',()),
                               response=response)


    def newItem(self, items, reqSettings=None):
        """

        :param items:
        :param reqSettings:
        :return: result, success. number of stored items, list of keys or ids successfully created
        """
        if isinstance(items, (list, tuple)):
            values = dict(items=items)
        else:
            values = dict(items=(items,))
        content, response = self.call('newItem', values, reqSettings)
        return endpoint.Result(result=content.get('result'),
                               success=content.get('success',()),
                               invalid=content.get('invalid',()),
                               messages=content.get('messages',()),
                               response=response)


    def setItem(self, items, reqSettings=None):
        """

        :param items:
        :param reqSettings:
        :return: result, success. number of stored items, list of keys or ids successfully updated
        """
        if isinstance(items, (list, tuple)):
            values = dict(items=items)
        else:
            values = dict(items=(items,))
        content, response = self.call('setItem', values, reqSettings)
        return endpoint.Result(result=content.get('result'),
                               success=content.get('success',()),
                               invalid=content.get('invalid',()),
                               messages=content.get('messages',()),
                               response=response)


    def removeItem(self, key=None, id=None, reqSettings=None):
        """

        :param key:
        :param id:
        :param reqSettings:
        :return: result, success. number of stored items, list of keys or ids successfully removed
        """
        values = {}
        if key is not None:
            values["key"] = key
        if id is not None:
            values["id"] = id
        content, response = self.call('removeItem', values, reqSettings)
        return endpoint.Result(result=content.get('result'),
                               success=content.get('success',()),
                               messages=content.get('messages',()),
                               response=response)


    def list(self, key=None, id=None, sort=None, order=None, size=None, start=None, owner=None, reqSettings=None):
        """

        :param key:
        :param id:
        :param sort:
        :param order:
        :param size:
        :param start:
        :param owner:
        :param reqSettings:
        :return: item result set {"items":[items], "start":number, "size":number, "total":number}
        """
        values = {}
        if key is not None:
            values["key"] = key
        if id is not None:
            values["id"] = id
        if sort is not None:
            values["sort"] = sort
        if order is not None:
            values["order"] = order
        if size is not None:
            values["size"] = size
        if start is not None:
            values["start"] = start
        if owner is not None:
            values["owner"] = owner
        content, response = self.call('list', values, reqSettings)
        # todo result set class with iterator
        if not content:
            return {"items": (), "start": 1, "size": 0}
        return content


    def keys(self, order=None, size=None, start=None, owner=None, reqSettings=None):
        """

        :param order:
        :param size:
        :param start:
        :param owner:
        :param reqSettings:
        :return: result set {"keys":[strings], "start":number, "size":number, "total":number}
        """
        values = {}
        if order is not None:
            values["order"] = order
        if size is not None:
            values["size"] = size
        if start is not None:
            values["start"] = start
        if owner is not None:
            values["owner"] = owner
        content, response = self.call('keys', values, reqSettings)
        # todo result set class with iterator
        if not content:
            return {"keys": (), "start": 1, "size": 0}
        return content


    def allowed(self, permissions, reqSettings=None):
        """

        :param permission: one or multiple permission names
        :param reqSettings:
        :return: dict {permission: True or False}
        """
        values = dict(permissions=permissions)
        content, response = self.call('allowed', values, reqSettings)
        return endpoint.Result(response=response, **content)


    def getPermissions(self, reqSettings=None):
        """

        :param reqSettings:
        :return: list of permission - group assignments
        """
        values = dict()
        content, response = self.call('getPermissions', values, reqSettings)
        return endpoint.Result(response=response, **content)


    def setPermissions(self, permissions, reqSettings=None):
        """

        :param permissions: dict/list. one or multiple permissions {permission, group, action="replace"}
        :param reqSettings:
        :return: Result(result, messages)
        """
        values = dict(permissions=permissions)
        content, response = self.call('setPermissions', values, reqSettings)
        return endpoint.Result(result=content.get('result'),
                               messages=content.get('messages',()),
                               response=response)


    def getOwner(self, key=None, id=None, reqSettings=None):
        """

        :param key:
        :param id:
        :param reqSettings:
        :return: owner
        """
        values = dict(key=key, id=id)
        content, response = self.call('getOwner', values, reqSettings)
        return endpoint.Result(items=content.get('items'),
                               messages=content.get('messages',()),
                               response=response)


    def setOwner(self, items, reqSettings=None):
        """

        :param items:
        :param reqSettings:
        :return: Result(result, messages)
        """
        values = dict(items=items)
        content, response = self.call('setOwner', values, reqSettings)
        return endpoint.Result(response=response, **content)
