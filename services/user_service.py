from models.user import User
from models import db


class UserService:
    @staticmethod
    def create_user(username, password):
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return None

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate a user by username and password
        Returns the user if authentication succeeds, None otherwise
        """
        user = UserService.get_user_by_username(username)

        if user and user.check_password(password):
            return user

        return None
