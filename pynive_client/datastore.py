# (c) 2013-2015 Nive GmbH - nive.io
# This file is released under the BSD-License.
#
# Nive Key-Value store service python client
# ------------------------------------------------
# Documentation: http:#www.nive.co/docs/webapi/datastore.html#api
#
"""
**Example code 1**

Create a user instance, authenticate and retrieve the users profile values

::

    from pynive_client import datastore

    storage = datastore.KvStore(service='mystorage',domain='mydomain')

    # list items
    result = storage.list(sort='key', order='<', size=20, start=1)
    for item in result:
        print item["key"], item["value"]



**Example code 2**

Retrieve a security token and add, update, get and remove a item

::

    from pynive_client import useraccount
    from pynive_client import datastore

    niveuser = useraccount.User(domain='mydomain')

    # retrieve a auth-token to connect to the data storage service
    auth = niveuser.token(identity='username', password='userpw')

    storage = datastore.KvStore(service='mystorage',domain='mydomain',auth=auth)

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


    def getItem(self, key=None, owner=None, id=None, **reqSettings):
        """

        :param key:
        :param owner:
        :param id:
        :param reqSettings:
        :return: dict
        """
        values = dict()
        if key is not None:
            values["key"] = key
        if owner is not None:
            values["owner"] = owner
        if id is not None:
            values["id"] = id
        content, response = self.call('getItem', values, reqSettings)
        return endpoint.Result(items=content.get('items'),
                               result=content.get('result',0),
                               message=content.get('message',()),
                               response=response)


    def newItem(self, items=None, key=None, value=None, owner=None, **reqSettings):
        """

        :param items:
        :param key:
        :param value:
        :param owner:
        :param reqSettings:
        :return: result, success. number of stored items, list of keys or ids successfully created
        """
        values = dict()
        if items is not None:
            values["items"] = items
        else:
            if key is not None:
                values["key"] = key
            if value is not None:
                values["value"] = value
            if owner is not None:
                values["owner"] = owner
        content, response = self.call('newItem', values, reqSettings)
        return endpoint.Result(result=content.get('result'),
                               success=content.get('success',()),
                               invalid=content.get('invalid',()),
                               message=content.get('message',()),
                               response=response)


    def setItem(self, items=None, key=None, value=None, owner=None, id=None, **reqSettings):
        """

        :param items:
        :param key:
        :param value:
        :param owner:
        :param id:
        :param reqSettings:
        :return: result, success. number of stored items, list of keys or ids successfully updated
        """
        values = dict()
        if items is not None:
            values["items"] = items
        if key is not None:
            values["key"] = key
        if owner is not None:
            values["owner"] = owner
        if value is not None:
            values["value"] = value
        if id is not None:
            values["id"] = id
        content, response = self.call('setItem', values, reqSettings)
        return endpoint.Result(result=content.get('result'),
                               success=content.get('success',()),
                               invalid=content.get('invalid',()),
                               message=content.get('message',()),
                               response=response)


    def removeItem(self, items=None, key=None, owner=None, id=None, **reqSettings):
        """

        :param items:
        :param key:
        :param owner:
        :param id:
        :param reqSettings:
        :return: result, success. number of stored items, list of keys or ids successfully removed
        """
        values = dict()
        if items is not None:
            values["items"] = items
        if owner is not None:
            values["owner"] = owner
        if key is not None:
            if isinstance(key, (list,tuple)):
                # convert to items if a list of keys
                if not "items" in values:
                    values["items"] = []
                values["items"] = self.toItems(key, owner=owner)
            else:
                values["key"] = key
        if id is not None:
            if isinstance(id, (list,tuple)):
                # convert to items if a list of ids
                if not "items" in values:
                    values["items"] = []
                values["items"] = self.toItems(ids=id, owner=owner)
            else:
                values["id"] = id
        content, response = self.call('removeItem', values, reqSettings)
        return endpoint.Result(result=content.get('result'),
                               success=content.get('success',()),
                               message=content.get('message',()),
                               response=response)


    def list(self, key=None, sort=None, order=None, size=None, start=None, owner=None, **reqSettings):
        """

        :param key:
        :param sort:
        :param order:
        :param size:
        :param start:
        :param owner:
        :param reqSettings:
        :return: item result set {"items":[items], "start":number, "size":number, "total":number}
        """
        values = dict()
        if key is not None:
            values["key"] = key
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
            return endpoint.Result(items=(), start=1, size=0, response=response)
        return endpoint.Result(response=response, **content)


    def keys(self, order=None, size=None, start=None, owner=None, **reqSettings):
        """

        :param order:
        :param size:
        :param start:
        :param owner:
        :param reqSettings:
        :return: result set {"keys":[strings], "start":number, "size":number, "total":number}
        """
        values = dict()
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
            return endpoint.Result(keys=(), start=1, size=0, response=response)
        return endpoint.Result(response=response, **content)


    def allowed(self, permissions, **reqSettings):
        """

        :param permission: one or multiple permission names
        :param reqSettings:
        :return: dict {permission: True or False}
        """
        values = dict(permissions=permissions)
        content, response = self.call('allowed', values, reqSettings)
        return endpoint.Result(response=response, **content)


    def getPermissions(self, **reqSettings):
        """

        :param reqSettings:
        :return: list of permission - group assignments
        """
        values = dict()
        content, response = self.call('getPermissions', values, reqSettings)
        return content


    def setPermissions(self, permissions, **reqSettings):
        """

        :param permissions: dict/list. one or multiple permissions {permission, group, action="replace"}
        :param reqSettings:
        :return: Result(result, message)
        """
        values = dict(permissions=permissions)
        content, response = self.call('setPermissions', values, reqSettings)
        return endpoint.Result(result=content.get('result'),
                               message=content.get('message',()),
                               response=response)


    def getOwner(self, key=None, id=None, **reqSettings):
        """

        :param key:
        :param id:
        :param reqSettings:
        :return: owner
        """
        values = dict(key=key, id=id)
        content, response = self.call('getOwner', values, reqSettings)
        return endpoint.Result(items=content.get('items'),
                               message=content.get('message',()),
                               response=response)


    def setOwner(self, newOwner, items=None, key=None, owner=None, id=None, **reqSettings):
        """

        :param newOwner:
        :param items:
        :param key:
        :param owner:
        :param id:
        :param items:
        :param reqSettings:
        :return: Result(result, message)
        """
        values = dict(newOwner=newOwner)
        if items is not None:
            values["items"] = items
        if key is not None:
            values["key"] = key
        if owner is not None:
            values["owner"] = owner
        if id is not None:
            values["id"] = id
        content, response = self.call('setOwner', values, reqSettings)
        return endpoint.Result(response=response, **content)


    def toItems(self, keys=None, ids=None, owner=None, items=None):
        # convert a list of keys and/or ids to items including owner
        if items is None:
            items = []
        if keys is not None:
            if owner is None:
                for key in keys:
                    item = dict(key=key)
                    items.append(item)
            else:
                for key in keys:
                    item = dict(key=key, owner=owner)
                    items.append(item)
        if ids is not None:
            if owner is None:
                for id in ids:
                    item = dict(id=id)
                    items.append(item)
            else:
                for id in ids:
                    item = dict(id=id, owner=owner)
                    items.append(item)
        return items