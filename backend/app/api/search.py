from flask import Blueprint, request, jsonify
from app.models import Topic  # 先只导入 Topic

search_bp = Blueprint('search', __name__, url_prefix='/api/search')

@search_bp.route('', methods=['GET'])
def search():
    keywords = request.args.get('keywords', '')
    search_type = request.args.get('type', 'topic')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 12, type=int)
    
    if not keywords:
        return jsonify({'code': 400, 'message': '搜索关键词不能为空'}), 400
    
    offset = (page - 1) * limit
    
    if search_type == 'topic':
        from sqlalchemy import or_
        results = Topic.query.filter(
            or_(
                Topic.title.ilike(f'%{keywords}%'),
                Topic.content.ilike(f'%{keywords}%')
            )
        ).offset(offset).limit(limit).all()
        
        total = Topic.query.filter(
            or_(
                Topic.title.ilike(f'%{keywords}%'),
                Topic.content.ilike(f'%{keywords}%')
            )
        ).count()
    else:
        # 如果需要搜索回复，改这里
        results = []
        total = 0
    
    return jsonify({
        'code': 200,
        'data': [item.to_dict() for item in results],
        'total': total,
        'page': page,
        'limit': limit
    }), 200