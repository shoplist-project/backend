from models import db
from models.shop_list import ShopList, Product, ShopListShare, Access
from services.user_service import UserService
from datetime import datetime


class ShopListService:
    @staticmethod
    def create_shop_list(name, owner_id):
        """
        Create a new shopping list for the specified owner
        """
        owner = UserService.get_user_by_id(owner_id)
        if not owner:
            return None

        shop_list = ShopList(name=name, owner_id=owner_id)

        db.session.add(shop_list)
        db.session.commit()

        return shop_list

    @staticmethod
    def get_shop_list_by_id(shop_list_id):
        """
        Retrieve a shop list by its ID
        """
        return ShopList.query.get(shop_list_id)

    @staticmethod
    def get_shop_lists_for_user(user_id):
        """
        Get all shop lists a user has access to (owned or shared)
        """
        owned_lists = ShopList.query.filter_by(owner_id=user_id).all()

        shared_lists_ids = (
            db.session.query(ShopListShare.shop_list_id)
            .filter_by(user_id=user_id)
            .all()
        )
        shared_lists_ids = [id[0] for id in shared_lists_ids]
        shared_lists = ShopList.query.filter(ShopList.id.in_(shared_lists_ids)).all()

        return owned_lists + shared_lists

    @staticmethod
    def add_product(shop_list_id, name):
        """
        Add a product to a shop list
        """
        shop_list = ShopListService.get_shop_list_by_id(shop_list_id)
        if not shop_list:
            return None

        product = Product(name=name, shop_list_id=shop_list_id)
        db.session.add(product)
        db.session.commit()

        return product

    @staticmethod
    def check_user_access(shop_list_id, user_id, min_level=Access.Read):
        """
        Check what access level a user has to a shop list
        Returns Access enum or None if no access
        """
        shop_list = ShopListService.get_shop_list_by_id(shop_list_id)

        if not shop_list:
            return None

        if shop_list.owner_id == user_id:
            return Access.Write

        share = ShopListShare.query.filter_by(
            shop_list_id=shop_list_id, user_id=user_id
        ).first()

        if share:
            access = Access(share.access)
            if access >= min_level:
                return access

        return None

    @staticmethod
    def share_shop_list(shop_list_id, usernames, access):
        """
        Share a shop list with multiple users at once
        Returns the list of user IDs that the shop list was shared with
        """
        shop_list = ShopListService.get_shop_list_by_id(shop_list_id)
        if not shop_list:
            return None

        shared_user_ids = []

        for username in usernames:
            user = UserService.get_user_by_username(username)
            if not user:
                continue

            if user.id == shop_list.owner_id:
                continue

            existing_share = ShopListShare.query.filter_by(
                shop_list_id=shop_list_id, user_id=user.id
            ).first()

            if existing_share:
                existing_share.access = access
                shared_user_ids.append(user.id)
            else:
                share = ShopListShare(
                    shop_list_id=shop_list_id, user_id=user.id, access=access
                )
                db.session.add(share)
                shared_user_ids.append(user.id)

        db.session.commit()

        return shared_user_ids

    @staticmethod
    def unshare_shop_list(shop_list_id, usernames):
        """
        Remove sharing of a shop list from multiple users at once
        Returns the list of user IDs that the shop list was unshared from
        """
        shop_list = ShopListService.get_shop_list_by_id(shop_list_id)
        if not shop_list:
            return None

        unshared_user_ids = []

        for username in usernames:
            user = UserService.get_user_by_username(username)
            if not user:
                continue

            existing_share = ShopListShare.query.filter_by(
                shop_list_id=shop_list_id, user_id=user.id
            ).first()

            if existing_share:
                db.session.delete(existing_share)
                unshared_user_ids.append(user.id)

        db.session.commit()

        return unshared_user_ids

    @staticmethod
    def delete_shop_list(shop_list_id):
        """
        Delete a shop list and all its associated data (products and shares)
        Returns True if successful, False otherwise
        """
        shop_list = ShopListService.get_shop_list_by_id(shop_list_id)
        if not shop_list:
            return False

        try:
            db.session.delete(shop_list)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting shop list: {e}")
            return False

    @staticmethod
    def update_shop_list(shop_list_id, name):
        """
        Update a shop list's name
        Returns the updated shop list if successful, None otherwise
        """
        shop_list = ShopListService.get_shop_list_by_id(shop_list_id)
        if not shop_list:
            return None

        try:
            shop_list.name = name
            shop_list.updated_at = datetime.utcnow()
            db.session.commit()
            return shop_list
        except Exception as e:
            db.session.rollback()
            print(f"Error updating shop list: {e}")
            return None
