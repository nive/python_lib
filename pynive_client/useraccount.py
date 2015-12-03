# (c) 2013-2015 Nive GmbH - nive.io
# This file is released under the BSD-License.
#
# Nive User service python client
# ------------------------------------------------
# Documentation: http:#www.nive.co/docs/webapi/useraccount.html#api
#
"""
**Example code 1**

Create a user instance, authenticate and retrieve the users profile values

::

    from pynive_client import useraccount

    niveuser = user.User(domain='mydomain')

    # call the service to obtain a security access token
    # response contains {token, result, lastlogin, messages}
    # the token is automatically stored for the user instance and used in following
    # requests
    token = niveuser.token(identity='username', password='userpw', storeInSession=True)

    # get the users profile values
    profile = niveuser.profile()

    # reset token
    niveuser.token = None


**Example code 2**

Retrieve a security token to access other services

::

    from pynive_client import useraccount
    from pynive_client import kvstore

    niveuser = user.User(domain='mydomain')

    # retrieve a token to connect to other services
    token = niveuser.token(identity='username', password='userpw')

    storage = kvstore.KvStore(service='mystorage',domain='mydomain',token=token)

**Example code 3**

Create a new user and change custom user data.

::

    from pynive_client import useraccount

    niveuser = user.User(domain='mydomain')

    # retrieve a token for a admin user
    token = niveuser.token(identity='admin', password='adminpw')
    if token:
        response = niveuser.signupDirect(
                                name='new-user',
                                email='new-user@mail.com',
                                password='a password',
                                token=token)

        if response.result:
            # success
            newuser = user.User(domain='mydomain')
            token = newuser.token(identity='new-user', password='a password')
            if token:
                newuser.update(data={'info': 'created by python client'}, token=token)


**Example code 4**

Use http sessions for multiple requests.

::

    from pynive_client import useraccount
    from pynive_client import endpoint

    session = user.User.newSession()
    niveuser = user.User(domain='mydomain', session=session)

    # retrieve a token for a admin user
    response = niveuser.signupDirect(identity='admin', password='adminpw')
    if response.result:
         result, invalid, messages = niveuser.signupDirect(
                                                name='new-user',
                                                email='new-user@mail.com',
                                                password='a password')

        if result:
            # disable the user
            response = niveuser.disable()

"""

import endpoint

# todo use exceptions instead tuple return values?

class User(endpoint.Client):
    service_name='users'   # service routing name
    default_version='api'

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
        returned token yourself and pass it manually to calls or set `storeInSession`
        to True to handle the token automatically. In this case a valid session created
        by `newSession()` is required.

        Raises `AuthorizationFailure` if no valid token is returned.

        :param identity:
        :param password:
        :param storeInSession:
        :param reqSettings:
        :return: (string) token
        """
        content, response = self.call('token', dict(identity=identity, password=password), reqSettings)
        if not content or not content.get('token'):
            msg = self._fmtMsgs(content, 'Failed to acquire token.')
            raise endpoint.AuthorizationFailure(msg)
        token = content.get('token')

        if storeInSession and self.session:
            # store token in session for future requests
            self.session.token = token

        return token


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
            msg = self._fmtMsgs(content, 'Failed to sign in.')
            raise endpoint.AuthorizationFailure(msg)
        return True


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
            self.session.token = None
        return


    def identity(self, **reqSettings):
        """
        Returns the users identity.

        :param reqSettings:
        :return: {name, email, reference, realname}
        """
        content, response = self.call('identity', {}, reqSettings)
        return content


    def name(self, **reqSettings):
        """
        Returns the users name.

        :param reqSettings:
        :return: {name, realname}
        """
        content, response = self.call('name', {}, reqSettings)
        return content


    def profile(self, **reqSettings):
        """
        Returns the users profile values. `data`, `realname` and `notify` can
        be changed by calling `update()`. `data` can be used to store arbitrary
        values or json strings.

        :param reqSettings:
        :return: {data, realname, notify, email, name, lastlogin}
        """
        content, response = self.call('profile', {}, reqSettings)
        return content


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
        if content is None:
            return False
        return content.get('result')


    def update(self, data=None, realname=None, notify=None, **reqSettings):
        """

        :param data:
        :param realname:
        :param notify:
        :param reqSettings:
        :return: result, invalid, messages
        """
        values = {}
        if data is not None:
            values['data'] = data
        if realname is not None:
            values['realname'] = realname
        if notify is not None:
            values['notify'] = notify
        content, response = self.call('update', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def updatePassword(self, password, newpassword, **reqSettings):
        """

        :param password:
        :param newpassword:
        :param reqSettings:
        :return: result, invalid, messages
        """
        values = dict(password=password, newpassword=newpassword)
        content, response = self.call('updatePassword', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def updateEmail(self, email, **reqSettings):
        """

        :param email:
        :param reqSettings:
        :return: result, invalid, messages
        """
        values = dict(email=email)
        content, response = self.call('updateEmail', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def verifyEmail(self, email, **reqSettings):
        """

        :param email:
        :param reqSettings:
        :return: result, invalid, messages
        """
        values = dict(email=email)
        content, response = self.call('verifyEmail', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def verifyEmail2(self, token, **reqSettings):
        """

        :param token:
        :param reqSettings:
        :return: result, messages
        """
        values = dict(token=token)
        content, response = self.call('verifyEmail2', values, reqSettings)
        if content is None:
            return False, ()
        return content.get('result'), content.get('messages',())


    def resetPassword(self, identity, **reqSettings):
        """

        :param identity:
        :param reqSettings:
        :return: result, messages
        """
        values = dict(identity=identity)
        content, response = self.call('resetPassword', values, reqSettings)
        if content is None:
            return False, ()
        return content.get('result'), content.get('messages',())


    def resetPassword2(self, token, newpassword, **reqSettings):
        """

        :param token:
        :param newpassword:
        :param reqSettings:
        :return: result, invalid, messages
        """
        values = dict(token=token, newpassword=newpassword)
        content, response = self.call('resetPassword2', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def message(self, message, **reqSettings):
        """

        :param message:
        :param reqSettings:
        :return: result, invalid
        """
        values = dict(message=message)
        content, response = self.call('message', values, reqSettings)
        if content is None:
            return False, ()
        return content.get('result'), content.get('messages',())


    def disable(self, **reqSettings):
        """

        :param reqSettings:
        :return: True or False, messages
        """
        content, response = self.call('disable', {}, reqSettings)
        if content is None:
            return False, ()
        return content.get('result'), content.get('messages',())


    def delete(self, **reqSettings):
        """

        :param reqSettings:
        :return: True or False, messages
        """
        content, response = self.call('delete', {}, reqSettings)
        if content is None:
            return False, ()
        return content.get('result'), content.get('messages',())


    def signupDirect(self, name=None, email=None, password=None, data=None, **reqSettings):
        """
        Create a new user account.

        :param name:
        :param email:
        :param password:
        :param data:
        :param reqSettings:
        :return: result, invalid, messages
        """
        values = dict(
            name=name,
            email=email,
            password=password,
            data=data
        )
        content, response = self.call('signupDirect', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def signupOptin(self, name=None, email=None, password=None, data=None, **reqSettings):
        """
        Create a new user account.

        :param name:
        :param email:
        :param password:
        :param data:
        :param reqSettings:
        :return: result, invalid, messages
        """
        values = dict(
            name=name,
            email=email,
            password=password,
            data=data
        )
        content, response = self.call('signupOptin', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def signupReview(self, name=None, email=None, password=None, data=None, **reqSettings):
        """
        Create a new user account.

        :param name:
        :param email:
        :param password:
        :param data:
        :param reqSettings:
        :return: result, invalid, messages
        """
        values = dict(
            name=name,
            email=email,
            password=password,
            data=data
        )
        content, response = self.call('signupReview', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def signupSendpw(self, name=None, email=None, data=None, **reqSettings):
        """
        Create a new user account.

        :param name:
        :param email:
        :param data:
        :param reqSettings:
        :return: result, invalid, messages
        """
        values = dict(
            name=name,
            email=email,
            data=data
        )
        content, response = self.call('signupSendpw', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def signupUid(self, email=None, password=None, data=None, **reqSettings):
        """
        Create a new user account.

        :param email:
        :param password:
        :param data:
        :param reqSettings:
        :return: result, invalid, messages
        """
        values = dict(
            email=email,
            password=password,
            data=data
        )
        content, response = self.call('signupUid', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('invalid',()), content.get('messages',())


    def signupConfirm(self, token, **reqSettings):
        """
        Activate a new user account. Step 1 is triggered either by calling `signupOptin()` or
        `signupReview()`.

        :param token:
        :param reqSettings:
        :return: result, messages
        """
        values = dict(token=token)
        content, response = self.call('signupConfirm', values, reqSettings)
        if content is None:
            return False, ()
        return content.get('result'), content.get('messages',())


    def review(self, identity, action, **reqSettings):
        """
        Review a new user account. Step 1 is triggered by calling `signupReview()`. The account to be
        reviewed can be accepted or rejected.

        :param identity: the users identity.
        :param action: `accept` or `reject`
        :param reqSettings:
        :return: result, messages
        """
        values = dict(identity=identity, action=action)
        content, response = self.call('review', values, reqSettings)
        if content is None:
            return False, ()
        return content.get('result'), content.get('messages',())


    def getUser(self, identity, **reqSettings):
        """
        Retrieve a users profile.

        :param identity: the users identity.
        :param reqSettings:
        :return: profile values
        """
        values = dict(identity=identity)
        content, response = self.call('getUser', values, reqSettings)
        return content


    def setUser(self, identity, values, **reqSettings):
        """
        Update a users profile.

        :param identity: the users identity.
        :param values: profile values to be updated
        :param reqSettings:
        :return: result, messages, invalid
        """
        values = dict(identity=identity, values=values)
        content, response = self.call('setUser', values, reqSettings)
        if content is None:
            return False, (), ()
        return content.get('result'), content.get('messages',()), content.get('invalid',())


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
        if content is None:
            return False
        return content.get('result')


    def list_(self, active=None, pending=None, start=1, **reqSettings):
        """
        Review a new user account. Step 1 is triggered by calling `signupReview()`. The account to be
        reviewed can be accepted or rejected.

        :param active: only active, inactive or both
        :param pending: only pending
        :param start: batch start value
        :param reqSettings:
        :return: users
        """
        values = dict(start=start)
        if active is not None:
            values["active"] = active
        if pending is not None:
            values["pending"] = pending
        content, response = self.call('list', values, reqSettings)
        if content is None:
            return ()
        return content.get('users', ())


