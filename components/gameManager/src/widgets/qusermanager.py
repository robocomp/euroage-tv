from datetime import datetime

import bcrypt


class QUserManager:
    """
    This class encapsulate the needed methods to get the user and checks for login from the ddbb
    """

    def __init__(self, parent=None, ddbb=None, **kwargs):
        if ddbb is None:
            raise ValueError("You need to provide a DDBB instance for the QUserManager")
        else:
            self.ddbb = ddbb


    def check_user_password(self, username, password_to_check):
        """
        Ckecks the password for a given user.
        :param username: username to check the passsword for
        :param password_to_check: password to check
        :return: True if exists and password match , False
        """

        result, user = self.ddbb.get_therapist_by_username(username)
        if result and user is not None:
            return bcrypt.checkpw(password_to_check.encode('utf8'), user.hash.encode('utf8'))
        else:
            return False

    def set_username_password(self, username, plain_password):
        """
        Stores a new user with it password on the DDBB.
        :param username: username for the new user
        :param plain_password: password for the new user.
        :return: --
        """
        result, user = self.ddbb.get_therapist_by_username(username)
        if not result or user is None:
            salt = bcrypt.gensalt()
            hash = bcrypt.hashpw(plain_password.encode('utf-8'), salt.encode('utf-8'))
            self.ddbb.new_therapist(nombre="", username=username, hash=hash, salt=salt, centro="", telefono="", profesion="", observaciones="", fechaAlta=datetime.now())
        else:
            raise ValueError("The provided username exists.")

    def check_user(self, username):
        """
        Check if a username exists on the DDBB
        :param username: username to check existence of
        :return: True if exists, False if not.
        """
        result, user = self.ddbb.get_therapist_by_username(username)
        if result and user is not None:
            return True
        else:
            return False