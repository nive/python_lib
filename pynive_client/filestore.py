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

    storage = filestore.FileStore(name='mystorage',domain='mydomain')

    # list items
    result = storage.list(sort='path', order='<', size=20, start=1)
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

    storage = filestore.FileStore(name='mystorage',domain='mydomain',token=token)

    # get a files infos
    file = storage.getItem({"path": "/index.html"})
    print file.name, file.mime, file.size

"""

import endpoint


class FileStore(endpoint.Client):

    default_version='api'

    def __init__(self, name, domain=None, session=None, **options):
        """

        :param name: data storage instance name
        :param domain: domain the service is part of
        :param session: http session object
        :param options: other endpoint options. see endpoint.py.
        """
        super(FileStore, self).__init__(name=name,
                                    domain=domain,
                                    session=session,
                                    **options)
        if not "version" in self.options:
            self.options["version"] = self.default_version


    def getItem(self, path, **reqSettings):
        """

        :param path:
        :param reqSettings:
        :return: file wrapper: name, size, type, mime, mtime
        """
        values = dict(path=path)
        content, response = self.call('getItem', values, reqSettings)
        # todo file wrapper
        return content


    def list(self, path=None, filetype=None, **reqSettings):
        """

        :param path:
        :param filetype:
        :param reqSettings:
        :return: item result set {"items":[files]}
        """
        values = {}
        if path is not None:
            values["path"] = path
        if filetype is not None:
            values["type"] = filetype
        content, response = self.call('list', values, reqSettings)
        # todo result set class with iterator
        if not content:
            return {"items": ()}
        return content


