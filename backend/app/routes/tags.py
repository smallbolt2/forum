"""
标签路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.tag import Tag

tag_bp = Blueprint('tags', __name__)


@tag_bp.route('', methods=['GET'])
def get_tags():
    """获取标签列表"""
    try:
        tags = Tag.query.order_by(Tag.id.desc()).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [tag.to_dict() for tag in tags]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@tag_bp.route('', methods=['POST'])
def create_tag():
    """创建标签"""
    try:
        data = request.get_json()
        tag = Tag(
            name=data.get('name'),
            slug=data.get('slug') or data.get('name', '').lower().replace(' ', '-'),
            color=data.get('color')
        )
        db.session.add(tag)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': tag.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

