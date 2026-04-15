"""
用户路由
"""
import os
import time

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from app import db
from app.models.user import User
from app.utils.auth import token_required

user_bp = Blueprint('users', __name__)


@user_bp.route('', methods=['GET'])
def get_users():
    """获取用户列表"""
    try:
        users = User.query.filter_by(status=1).all()
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': [user.to_dict() for user in users]
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取用户详情"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': user.to_dict()
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@user_bp.route('', methods=['POST'])
def create_user():
    """创建用户（注册）"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('username'):
            return jsonify({'code': 400, 'message': '用户名不能为空'}), 400
        if not data.get('email'):
            return jsonify({'code': 400, 'message': '邮箱不能为空'}), 400
        if not data.get('password'):
            return jsonify({'code': 400, 'message': '密码不能为空'}), 400
        
        if len(data.get('password', '')) < 6:
            return jsonify({'code': 400, 'message': '密码长度至少6位'}), 400
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'code': 400, 'message': '用户名已存在'}), 400
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'code': 400, 'message': '邮箱已存在'}), 400
        
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            nickname=data.get('nickname'),
            avatar=data.get('avatar'),
            bio=data.get('bio')
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id, current_user=None):
    """更新用户信息"""
    try:
        # 只能更新自己的信息或管理员可以更新任何用户
        if current_user.id != user_id and current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '无权修改此用户信息'}), 403
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # 更新允许修改的字段
        if 'nickname' in data:
            user.nickname = data.get('nickname')
        if 'avatar' in data:
            user.avatar = data.get('avatar')
        if 'bio' in data:
            user.bio = data.get('bio')
        
        # 管理员可以修改角色和状态
        if current_user.role == 'admin':
            if 'role' in data:
                user.role = data.get('role')
            if 'status' in data:
                user.status = data.get('status')
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@user_bp.route('/<int:user_id>/avatar', methods=['POST'])
@token_required
def upload_avatar(user_id, current_user=None):
    """上传用户头像"""
    try:
        if current_user.id != user_id and current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '无权修改此用户头像'}), 403

        user = User.query.get_or_404(user_id)

        if 'avatar' not in request.files:
            return jsonify({'code': 400, 'message': '未找到头像文件'}), 400

        file = request.files['avatar']
        if not file or file.filename == '':
            return jsonify({'code': 400, 'message': '请选择头像文件'}), 400

        # 限制文件类型
        allowed_ext = {'.png', '.jpg', '.jpeg', '.gif'}
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_ext:
            return jsonify({'code': 400, 'message': '只支持 png/jpg/jpeg/gif 格式'}), 400

        # 保存文件到后端静态目录
        upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'avatars'))
        os.makedirs(upload_dir, exist_ok=True)
        new_filename = f'user_{user_id}_{int(time.time())}{ext}'
        file_path = os.path.join(upload_dir, new_filename)
        file.save(file_path)

        avatar_url = f"{request.host_url.rstrip('/')}/static/uploads/avatars/{new_filename}"
        user.avatar = avatar_url
        db.session.commit()

        return jsonify({'code': 200, 'message': '上传成功', 'avatar': avatar_url})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500
