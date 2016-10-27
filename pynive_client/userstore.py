# (c) 2013-2015 Nive GmbH - nive.io
# This file is released under the BSD-License.
#
# Nive User service python client
# ------------------------------------------------
# Documentation: http:#www.nive.co/docs/webapi/userstore.html#api
#
"""
**Example code 1**

Create a user instance, authenticate and retrieve the users profile values

::

    from pynive_client import userstore

    niveuser = user.User(domain='mydomain')

    # call the service to obtain a security access token
    # response contains {token, result, lastlogin, message}
    # the token is automatically stored for the user instance and used in following
    # requests
    auth = niveuser.token(identity='username', password='userpw', storeInSession=True)

    # get the users profile values
    profile = niveuser.profile()

    # reset auth-token
    niveuser.authtoken = None


**Example code 2**

Retrieve a security token to access other services

::

    from pynive_client import userstore
    from pynive_client import datastore

    niveuser = user.User(domain='mydomain')

    # retrieve a auth-token to connect to other services
    auth = niveuser.token(identity='username', password='userpw')

    storage = datastore.DataStore(service='mystorage',domain='mydomain',auth=auth)

**Example code 3**

Create a new user and change custom user data.

::

    from pynive_client import userstore

    niveuser = user.User(domain='mydomain')

    # retrieve a auth-token for a admin user
    auth = niveuser.token(identity='admin', password='adminpw')
    if auth:
        response = niveuser.signupDirect(
                                name='new-user',
                                email='new-user@mail.com',
                                password='a password',
                                auth=auth)

        if response.result:
            # success
            newuser = user.User(domain='mydomain')
            auth = newuser.token(identity='new-user', password='a password')
            if auth:
                newuser.update(data={'info': 'created by python client'}, auth=auth)


**Example code 4**

Use http sessions for multiple requests.

::

    from pynive_client import userstore
    from pynive_client import endpoint

    session = user.User.newSession()
    niveuser = user.User(domain='mydomain', session=session)

    # retrieve a auth-token for a admin user
    response = niveuser.signupDirect(identity='admin', password='adminpw')
    if response.result:
         result, invalid, message = niveuser.signupDirect(
                                                name='new-user',
                                                email='new-user@mail.com',
                                                password='a password')

        if result:
            # disable the user
            response = niveuser.disable()

"""

import endpoint

# todo use exceptions instead tuple return values?
# todo fnc doc

class User(endpoint.Client):
    service_name='users'   # service routing name
    default_version='api'
    pingurl='ping'

    def __init__(self, domain=None, session=None, **options):
        """

        :param domain: endpoint options used to connect to the service
        :param session: http session object
        :param options: other endpoint options. see endpoint.py.
        """
        super(User, self).__init__(domain=domain,
                                   session=session,
                                   service=self.service_name,
                                   **options)
        if not "version" in self.options:
            self.options["version"] = self.default_version

    def token(self, identity=None, password=None, storeInSession=False, **reqSettings):
        """
        Obtain a security for authentication of future calls. You can either manage the
        returned auth-token yourself and pass it manually to calls or set `storeInSession`
        to True to handle the token automatically. In this case a valid session created
        by `newSession()` is required.

        Raises `AuthorizationFailure` if no valid token is returned.

        :param identity:
        :param password:
        :param storeInSession:
        :param reqSettings:
        :return: (string) auth-token
        """
        content, response = self.call('token', dict(identity=identity, password=password), reqSettings)
        if not content or not content.get('token'):
            msg = self._fmtMsgs(content, 'token_failure')
            raise endpoint.AuthorizationFailure(msg)
        token = content.get('token')

        if storeInSession and self.session:
            # store token in session for future requests
            self.session.authtoken = token

        return endpoint.Result(token=token,
                               message=content.get('message'),
                               response=response)


    def signin(self, identity=None, password=None, **reqSettings):
        """
        Sign in and start a cookie session. Authorization of future calls are automatically
        handled by the session. `signin` requires a valid session created by `newSession()`.

        Raises `AuthorizationFailure` if signin fails.

        :param identity:
        :param password:
        :param reqSettings:
        :return: True. Raises `AuthorizationFailure` if signin fails.
        """
        content, response =  self.call('signin', dict(identity=identity, password=password), reqSettings)
        if not content or not content.get('result'):
            msg = self._fmtMsgs(content, 'sign_in_failure')
            raise endpoint.AuthorizationFailure(msg)
        return endpoint.Result(result=content.get('result'),
                               message=content.get('message'),
                               response=response)



    def signout(self, **reqSettings):
        """
        Calls the servers signout method and removes stored credentials (cookie, token) from the
        current session. Also the services' signout method is called to terminate any user-session
        handled by the service.

        The session itself can still be used for further calls.

        :param reqSettings:
        :return: None
        """
        content, response = self.call('signout', {}, reqSettings)
        if self.session:
            # the cookie is reset by the server. the token is reset here.
            self.session.authtoken = None
        return endpoint.Result(result=content.get('result'),
                               response=response)


    def identity(self, **reqSettings):
        """
        Returns the users identity.

        :param reqSettings:
        :return: {name, email, reference, realname}
        """
        content, response = self.call('identity', {}, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def name(self, **reqSettings):
        """
        Returns the users name.

        :param reqSettings:
        :return: {name, realname}
        """
        content, response = self.call('name', {}, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def profile(self, **reqSettings):
        """
        Returns the users profile values. `data`, `realname` and `notify` can
        be changed by calling `update()`. `data` can be used to store arbitrary
        values or json strings.

        :param reqSettings:
        :return: {data, realname, notify, email, name, lastlogin}
        """
        content, response = self.call('profile', {}, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def authenticated(self, groups=None, **reqSettings):
        """
        Queries whether the current user is authenticated. If `groups` is set the result
        indicates if the user is assigned to one of at least the groups.

        :param groups: None, a single group, or a list of groups
        :param reqSettings:
        :return: True or False
        """
        if isinstance(groups, (list, tuple)):
            values={'groups': groups}
        elif isinstance(groups, basestring):
            values = {'groups': [groups]}
        else:
            values = {}
        content, response = self.call('authenticated', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def signupDirect(self, name=None, email=None, password=None, data=None, realname=None, notify=None, **reqSettings):
        """
        Create a new user account.

        :param name:
        :param email:
        :param password:
        :param data:
        :param realname:
        :param notify:
        :param reqSettings:
        :return: result, invalid, message
        """
        values = dict(
            name=name,
            email=email,
            password=password,
            data=data
        )
        content, response = self.call('signupDirect', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def signupOptin(self, name=None, email=None, password=None, data=None, realname=None, notify=None, **reqSettings):
        """
        Create a new user account.

        :param name:
        :param email:
        :param password:
        :param data:
        :param realname:
        :param notify:
        :param reqSettings:
        :return: result, invalid, message
        """
        values = dict(
            name=name,
            email=email,
            password=password,
            data=data
        )
        content, response = self.call('signupOptin', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def signupReview(self, name=None, email=None, password=None, data=None, realname=None, notify=None, **reqSettings):
        """
        Create a new user account.

        :param name:
        :param email:
        :param password:
        :param data:
        :param realname:
        :param notify:
        :param reqSettings:
        :return: result, invalid, message
        """
        values = dict(
            name=name,
            email=email,
            password=password,
            data=data
        )
        content, response = self.call('signupReview', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def signupSendpw(self, name=None, email=None, data=None, realname=None, notify=None, **reqSettings):
        """
        Create a new user account.

        :param name:
        :param email:
        :param data:
        :param realname:
        :param notify:
        :param reqSettings:
        :return: result, invalid, message
        """
        values = dict(
            name=name,
            email=email,
            data=data
        )
        content, response = self.call('signupSendpw', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def signupUid(self, email=None, password=None, data=None, realname=None, notify=None, **reqSettings):
        """
        Create a new user account.

        :param email:
        :param password:
        :param data:
        :param realname:
        :param notify:
        :param reqSettings:
        :return: result, invalid, message
        """
        values = dict(
            email=email,
            password=password,
            data=data
        )
        content, response = self.call('signupUid', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def activate(self, token, **reqSettings):
        """
        Activate a new user account. Step 1 is triggered either by calling `signupOptin()` or
        `signupReview()`.

        :param token:
        :param reqSettings:
        :return: result, message
        """
        values = dict(token=token)
        content, response = self.call('activate', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def update(self, data=None, realname=None, notify=None, **reqSettings):
        """

        :param data:
        :param realname:
        :param notify:
        :param reqSettings:
        :return: result, invalid, message
        """
        values = {}
        if data is not None:
            values['data'] = data
        if realname is not None:
            values['realname'] = realname
        if notify is not None:
            values['notify'] = notify
        content, response = self.call('update', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def updatePassword(self, password, newpassword, **reqSettings):
        """

        :param password:
        :param newpassword:
        :param reqSettings:
        :return: result, invalid, message
        """
        values = dict(password=password, newpassword=newpassword)
        content, response = self.call('updatePassword', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def updateEmail(self, email, **reqSettings):
        """

        :param email:
        :param reqSettings:
        :return: result, invalid, message
        """
        values = dict(email=email)
        content, response = self.call('updateEmail', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def verifyEmail(self, email, **reqSettings):
        """

        :param email:
        :param reqSettings:
        :return: result, invalid, message
        """
        values = dict(email=email)
        content, response = self.call('verifyEmail', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def verifyEmail2(self, token, **reqSettings):
        """

        :param token:
        :param reqSettings:
        :return: result, message
        """
        values = dict(token=token)
        content, response = self.call('verifyEmail2', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def resetPassword(self, identity, **reqSettings):
        """

        :param identity:
        :param reqSettings:
        :return: result, message
        """
        values = dict(identity=identity)
        content, response = self.call('resetPassword', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def resetPassword2(self, token, newpassword, **reqSettings):
        """

        :param token:
        :param newpassword:
        :param reqSettings:
        :return: result, invalid, message
        """
        values = dict(token=token, newpassword=newpassword)
        content, response = self.call('resetPassword2', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def message(self, message, **reqSettings):
        """

        :param message:
        :param reqSettings:
        :return: result, invalid
        """
        values = dict(message=message)
        content, response = self.call('message', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def allowed(self, permissions, **reqSettings):
        """

        :param permission: one or multiple permission names
        :param reqSettings:
        :return: dict {permission: True or False}
        """
        values = dict(permissions=permissions)
        content, response = self.call('allowed', values, reqSettings)
        return endpoint.Result(response=response, **content)


    def disable(self, **reqSettings):
        """

        :param reqSettings:
        :return: True or False, message
        """
        content, response = self.call('disable', {}, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def delete(self, **reqSettings):
        """

        :param reqSettings:
        :return: True or False, message
        """
        content, response = self.call('delete', {}, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def review(self, identity, action, **reqSettings):
        """
        Review a new user account. Step 1 is triggered by calling `signupReview()`. The account to be
        reviewed can be accepted or rejected.

        :param identity: the users identity.
        :param action: `accept`, `optin`, `reject`, `activate` or `disable`
        :param reqSettings:
        :return: result, message
        """
        values = dict(identity=identity, action=action)
        content, response = self.call('review', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def getUser(self, identity, **reqSettings):
        """
        Retrieve a users profile.

        :param identity: the users identity.
        :param reqSettings:
        :return: profile values
        """
        values = dict(identity=identity)
        content, response = self.call('getUser', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def setUser(self, identity, values, **reqSettings):
        """
        Update a users profile.

        :param identity: the users identity.
        :param values: profile values to be updated
        :param reqSettings:
        :return: result, message, invalid
        """
        values = dict(identity=identity, values=values)
        content, response = self.call('setUser', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def removeUser(self, identity, **reqSettings):
        """
        Review a new user account. Step 1 is triggered by calling `signupReview()`. The account to be
        reviewed can be accepted or rejected.

        :param identity: the users identity.
        :param reqSettings:
        :return: result
        """
        values = dict(identity=identity)
        content, response = self.call('removeUser', values, reqSettings)
        return endpoint.Result(response=response,
                               **content)


    def list(self, active=None, pending=None, start=None, size=None, sort=None, order=None, **reqSettings):
        """
        Administration command. Each returned user contains (reference, name, email, realname, pending, active, activity)

        :param active: only active, inactive or both
        :param pending: only pending
        :param sort:
        :param order:
        :param size:
        :param start: batch start value
        :param reqSettings:
        :return: users
        """
        values = dict(start=start)
        if active is not None:
            values["active"] = active
        if pending is not None:
            values["pending"] = pending
        if sort is not None:
            values["sort"] = sort
        if order is not None:
            values["order"] = order
        if size is not None:
            values["size"] = size
        if start is not None:
            values["start"] = start
        content, response = self.call('list', values, reqSettings)
        # todo iterator
        return endpoint.Result(response=response,
                               **content)


    def identities(self, active=None, pending=None, start=None, size=None, order=None, **reqSettings):
        """
        Administration command. Lists user identites as string only (reference, name/email ).

        :param active: only active, inactive or both
        :param pending: only pending
        :param order:
        :param size:
        :param start: batch start value
        :param reqSettings:
        :return: users
        """
        values = dict(start=start)
        if active is not None:
            values["active"] = active
        if pending is not None:
            values["pending"] = pending
        if order is not None:
            values["order"] = order
        if size is not None:
            values["size"] = size
        if start is not None:
            values["start"] = start
        content, response = self.call('identities', values, reqSettings)
        # todo iterator
        return endpoint.Result(response=response,
                               **content)


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


