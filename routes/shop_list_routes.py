from flask import request, jsonify, session
from routes import api
from services.shop_list_service import ShopListService
from models.shop_list import Access
from routes.login_required import login_required


@api.route('/api/shoplists', methods=['POST'])
@login_required
def create_shop_list():
    """
    Create a new shopping list
    """
    user_id = session.get('user_id')

    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({
            'error': 'Missing required field: name'
        }), 400

    name = data['name']

    shop_list = ShopListService.create_shop_list(name, user_id)

    if not shop_list:
        return jsonify({
            'error': 'Failed to create shop list'
        }), 500

    return jsonify(shop_list.to_dict()), 201


@api.route('/api/shoplists', methods=['GET'])
@login_required
def get_shop_lists():
    """
    Get all shop lists for the current user
    """
    user_id = session.get('user_id')

    shop_lists = ShopListService.get_shop_lists_for_user(user_id)

    return jsonify([shop_list.to_dict() for shop_list in shop_lists]), 200


@api.route('/api/shoplists/<shop_list_id>', methods=['GET'])
@login_required
def get_shop_list(shop_list_id):
    """
    Get a specific shop list
    """
    user_id = session.get('user_id')

    access = ShopListService.check_user_access(shop_list_id, user_id)

    if not access:
        return jsonify({
            'error': 'Shop list not found or access denied'
        }), 404

    shop_list = ShopListService.get_shop_list_by_id(shop_list_id)

    return jsonify(shop_list.to_dict()), 200


@api.route('/api/shoplists/<shop_list_id>/share', methods=['POST'])
@login_required
def share_shop_list(shop_list_id):
    """
    Share a shop list with multiple users
    """
    user_id = session.get('user_id')

    shop_list = ShopListService.get_shop_list_by_id(shop_list_id)

    if not shop_list:
        return jsonify({
            'error': 'Shop list not found'
        }), 404

    if shop_list.owner_id != user_id:
        return jsonify({
            'error': 'Only the owner can share this shop list'
        }), 403

    data = request.get_json()

    if not data or 'users' not in data or 'access' not in data:
        return jsonify({
            'error': 'Missing required fields: users, access'
        }), 400

    usernames = data['users']

    if not isinstance(usernames, list):
        return jsonify({
            'error': 'Field users must be an array of usernames'
        }), 400

    try:
        access = int(data['access'])
        if access not in [Access.Read.value, Access.Write.value]:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({
            'error': f'Invalid access value. Must be {Access.Read.value} (Read) or {Access.Write.value} (Write)'
        }), 400

    shared_user_ids = ShopListService.share_shop_list(
        shop_list_id,
        usernames,
        access
    )

    if shared_user_ids is None:
        return jsonify({
            'error': 'Failed to share shop list'
        }), 500

    return jsonify(shared_user_ids), 200

@api.route('/api/shoplists/<shop_list_id>/unshare', methods=['POST'])
@login_required
def unshare_shop_list(shop_list_id):
    """
    Unshare a shop list from multiple users
    """
    user_id = session.get('user_id')

    shop_list = ShopListService.get_shop_list_by_id(shop_list_id)

    if not shop_list:
        return jsonify({
            'error': 'Shop list not found'
        }), 404

    if shop_list.owner_id != user_id:
        return jsonify({
            'error': 'Only the owner can manage sharing for this shop list'
        }), 403

    data = request.get_json()

    if not data or 'users' not in data:
        return jsonify({
            'error': 'Missing required field: users'
        }), 400

    usernames = data['users']

    if not isinstance(usernames, list):
        return jsonify({
            'error': 'Field users must be an array of usernames'
        }), 400

    unshared_user_ids = ShopListService.unshare_shop_list(
        shop_list_id,
        usernames
    )

    if unshared_user_ids is None:
        return jsonify({
            'error': 'Failed to unshare shop list'
        }), 500

    return jsonify(unshared_user_ids), 200


@api.route('/api/shoplists/<shop_list_id>', methods=['DELETE'])
@login_required
def delete_shop_list(shop_list_id):
    """
    Delete a shop list
    Only the owner can delete their shop list
    """
    user_id = session.get('user_id')

    shop_list = ShopListService.get_shop_list_by_id(shop_list_id)

    if not shop_list:
        return jsonify({
            'error': 'Shop list not found'
        }), 404

    if shop_list.owner_id != user_id:
        return jsonify({
            'error': 'Only the owner can delete this shop list'
        }), 403

    success = ShopListService.delete_shop_list(shop_list_id)

    if not success:
        return jsonify({
            'error': 'Failed to delete shop list'
        }), 500

    return '', 204


@api.route('/api/shoplists/<shop_list_id>', methods=['PUT'])
@login_required
def update_shop_list(shop_list_id):
    """
    Update a shop list's name
    Only the owner or users with Write access can update the list
    """
    user_id = session.get('user_id')

    shop_list = ShopListService.get_shop_list_by_id(shop_list_id)

    if not shop_list:
        return jsonify({
            'error': 'Shop list not found'
        }), 404

    if shop_list.owner_id != user_id:
        return jsonify({
            'error': 'Only the owner can edit this shop list'
        }), 403

    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({
            'error': 'Missing required field: name'
        }), 400

    name = data['name']

    if not name or not name.strip():
        return jsonify({
            'error': 'Shop list name cannot be empty'
        }), 400

    updated_shop_list = ShopListService.update_shop_list(shop_list_id, name)

    if not updated_shop_list:
        return jsonify({
            'error': 'Failed to update shop list'
        }), 500

    return jsonify(updated_shop_list.to_dict()), 200
