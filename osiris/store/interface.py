"""UserStore Interface

All backend stores for OAuth tokens should implement the TokenStore interface
as defined here.

"""


class TokenStore(object):
    """This is the interface for storing token data information"""

    def retrieve(self, token):
        """This method retrieves the data for a token from the storage.

        :param token: The token to retrieve.
        :returns: Token information
        :rtype: dict

        """
        raise NotImplementedError  # pragma: no cover

    def store(self, token, username, scope, expires_in):
        """This method stores token data class dict in the storage.

        :param token: The token to store the value under.
        :param username: The username related to the token to store.
        :param expires_in: Optional expiration time in seconds from now.
        :type value: dict
        :returns: True if the data was stored successfully, False otherwise.
        :rtype: boolean

        """
        raise NotImplementedError  # pragma: no cover

    def delete(self, token):
        """This method deletes a token data dict from the storage

        :param token: The token of the data to be removed.

        :returns: True if the delete proceeded ok, regardless of if the key
                  actually existed or not.
        :rtype: boolean

        """
        raise NotImplementedError  # pragma: no cover

    def purge_expired(self):
        """This method purges all expired data from the storage

        All expired data should be purged from the TokenStore when this method
        is called. TokenStore's that automatically expire old data must still
        implement this method, but can do nothing.

        """
        raise NotImplementedError  # pragma: no cover
