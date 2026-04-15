"""
分类路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.category import Category

category_bp = Blueprint('categories', __name__)


@category_bp.route('', methods=['GET'])
def get_categories():
    """获取分类列表"""
    try:
        categories = Category.query.order_by(Category.order.desc(), Category.id.desc()).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [category.to_dict() for category in categories]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """获取分类详情"""
    try:
        category = Category.query.get_or_404(category_id)
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': category.to_dict()
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@category_bp.route('', methods=['POST'])
def create_category():
    """创建分类"""
    try:
        data = request.get_json()
        category = Category(
            name=data.get('name'),
            slug=data.get('slug') or data.get('name', '').lower().replace(' ', '-'),
            description=data.get('description'),
            order=data.get('order', 0)
        )
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': category.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

