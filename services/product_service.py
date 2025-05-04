from models import db
from models.shop_list import Product, ShopList
from services.shop_list_service import ShopListService
from datetime import datetime


class ProductService:
    @staticmethod
    def add_product(shop_list_id, name):
        """
        Add a product to a shop list
        Returns the created product if successful, None otherwise
        """
        shop_list = ShopListService.get_shop_list_by_id(shop_list_id)
        if not shop_list:
            return None

        try:
            product = Product(
                name=name,
                shop_list_id=shop_list_id,
                strikeout=False
            )

            db.session.add(product)
            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            print(f"Error adding product: {e}")
            return None

    @staticmethod
    def get_product_by_id(product_id):
        """
        Get a product by ID
        """
        return Product.query.get(product_id)

    @staticmethod
    def get_products_for_shop_list(shop_list_id):
        """
        Get all products in a shop list
        """
        return Product.query.filter_by(shop_list_id=shop_list_id).order_by(Product.created_at).all()

    @staticmethod
    def update_product(product_id, name=None, strikeout=None):
        """
        Update a product
        Parameters:
            product_id: The ID of the product to update
            name: New name (optional)
            strikeout: New strikeout status (optional)
        Returns the updated product if successful, None otherwise
        """
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return None

        try:
            if name is not None:
                product.name = name

            if strikeout is not None:
                product.strikeout = strikeout

            product.updated_at = datetime.utcnow()
            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            print(f"Error updating product: {e}")
            return None

    @staticmethod
    def delete_product(product_id):
        """
        Delete a product
        Returns True if successful, False otherwise
        """
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return False

        try:
            db.session.delete(product)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting product: {e}")
            return False

    @staticmethod
    def toggle_product_strikeout(product_id):
        """
        Toggle the strikeout status of a product
        Returns the updated product if successful, None otherwise
        """
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return None

        try:
            product.strikeout = not product.strikeout
            product.updated_at = datetime.utcnow()
            db.session.commit()
            return product
        except Exception as e:
            db.session.rollback()
            print(f"Error toggling product strikeout: {e}")
            return None