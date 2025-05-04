from flask import request, jsonify, session
from routes import api
from services.product_service import ProductService
from services.shop_list_service import ShopListService
from models.shop_list import Access
from routes.login_required import login_required


@api.route("/api/shoplists/<shop_list_id>/products", methods=["POST"])
@login_required
def add_product(shop_list_id):
    """
    Add a product to a shop list
    Requires the user to have Write access to the shop list
    """
    user_id = session.get("user_id")

    access = ShopListService.check_user_access(shop_list_id, user_id, Access.Write)

    if not access:
        return jsonify({"error": "Shop list not found or access denied"}), 404

    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Missing required field: name"}), 400

    name = data["name"]

    if not name or not name.strip():
        return jsonify({"error": "Product name cannot be empty"}), 400

    product = ProductService.add_product(shop_list_id, name)

    if not product:
        return jsonify({"error": "Failed to add product"}), 500

    return jsonify(product.to_dict()), 201


@api.route("/api/shoplists/<shop_list_id>/products", methods=["GET"])
@login_required
def get_products(shop_list_id):
    """
    Get all products in a shop list
    Requires the user to have at least Read access to the shop list
    """
    user_id = session.get("user_id")

    access = ShopListService.check_user_access(shop_list_id, user_id)

    if not access:
        return jsonify({"error": "Shop list not found or access denied"}), 404

    products = ProductService.get_products_for_shop_list(shop_list_id)

    return jsonify([product.to_dict() for product in products]), 200


@api.route("/api/shoplists/<shop_list_id>/products<product_id>", methods=["PUT"])
@login_required
def update_product(shop_list_id, product_id):
    """
    Update a product
    Requires the user to have Write access to the parent shop list
    """
    user_id = session.get("user_id")

    product = ProductService.get_product_by_id(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    access = ShopListService.check_user_access(
        product.shop_list_id, user_id, Access.Write
    )

    if not access:
        return jsonify({"error": "Access denied to parent shop list"}), 403

    data = request.get_json()

    if not data or ("name" not in data and "strikeout" not in data):
        return jsonify({"error": "No fields to update provided"}), 400

    name = data.get("name")
    strikeout = data.get("strikeout", False)

    if name is not None and (not name or not name.strip()):
        return jsonify({"error": "Product name cannot be empty"}), 400

    updated_product = ProductService.update_product(product_id, name, strikeout)

    if not updated_product:
        return jsonify({"error": "Failed to update product"}), 500

    return jsonify(updated_product.to_dict()), 200


@api.route("/api/shoplists/<shop_list_id>/products/<product_id>", methods=["DELETE"])
@login_required
def delete_product(shop_list_id, product_id):
    """
    Delete a product
    Requires the user to have Write access to the parent shop list
    """
    user_id = session.get("user_id")

    product = ProductService.get_product_by_id(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    access = ShopListService.check_user_access(
        product.shop_list_id, user_id, Access.Write
    )

    if not access:
        return jsonify({"error": "Access denied to parent shop list"}), 404

    success = ProductService.delete_product(product_id)

    if not success:
        return jsonify({"error": "Failed to delete product"}), 500

    return "", 204
