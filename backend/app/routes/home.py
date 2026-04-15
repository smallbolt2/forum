"""
首页数据接口（Nuxt 前端期望：直接返回 {topics, galgames, activities}）
"""

from flask import Blueprint, jsonify

from app.models.topic import Topic
from app.models.user import User
from app.models.prisma_topic_extras import TopicTag
from app.models.topic_reply import TopicReply
from app.models.prisma_galgame_min import Galgame
from app.models.prisma_toolset_min import GalgameToolset

home_bp = Blueprint('home', __name__)


@home_bp.route('', methods=['GET'])
def get_home():
    # topics: recent 20
    topics_rows = (
        Topic.query
        .filter(Topic.status != 1)
        .order_by(Topic.status_update_time.desc())
        .limit(20)
        .all()
    )
    topic_ids = [t.id for t in topics_rows]

    tags = {}
    if topic_ids:
        for tt in TopicTag.query.filter(TopicTag.topic_id.in_(topic_ids)).all():
            tags.setdefault(tt.topic_id, []).append(tt.tag)

    users = {
        u.id: u for u in User.query.filter(User.id.in_([t.user_id for t in topics_rows])).all()
    } if topics_rows else {}

    topics = []
    for t in topics_rows:
        u = users.get(t.user_id)
        topics.append({
            'id': t.id,
            'title': t.title,
            'view': t.view or 0,
            'tag': tags.get(t.id, []),
            'user': {
                'id': t.user_id,
                'name': u.name if u else '',
                'avatar': u.avatar if u else ''
            },
            'status': t.status,
            'hasBestAnswer': bool(t.best_answer_id),
            'isNSFWTopic': bool(t.is_nsfw),
            'likeCount': 0,
            'replyCount': 0,
            'commentCount': 0,
            'section': [],
            'statusUpdateTime': t.status_update_time.isoformat() if t.status_update_time else None,
            'upvoteTime': t.upvote_time.isoformat() if t.upvote_time else None
        })

    # galgames: recent 12
    galgame_rows = (
        Galgame.query
        .filter(Galgame.status != 1)
        .order_by(Galgame.resource_update_time.desc())
        .limit(12)
        .all()
    )
    galgames = [{
        'id': g.id,
        'name': {
            'en-us': g.name_en_us,
            'ja-jp': g.name_ja_jp,
            'zh-cn': g.name_zh_cn,
            'zh-tw': g.name_zh_tw
        },
        'banner': g.banner,
        'user': {'id': g.user_id, 'name': '', 'avatar': ''},
        'contentLimit': g.content_limit,
        'view': g.view,
        'likeCount': 0,
        'resourceUpdateTime': g.resource_update_time.isoformat() if g.resource_update_time else None,
        'platform': [],
        'language': []
    } for g in galgame_rows]

    # activities: merge multiple event sources
    activities = []

    def actor_payload(user_id: int):
        u = users.get(user_id) or User.query.get(user_id)
        return {
            'id': user_id,
            'name': u.name if u else '',
            'avatar': u.avatar if u else ''
        }

    # Topic creation
    topic_created_rows = (
        Topic.query
        .filter(Topic.status != 1)
        .order_by(Topic.created.desc())
        .limit(10)
        .all()
    )
    for t in topic_created_rows:
        activities.append({
            'uniqueId': f'topic-{t.id}',
            'type': 'TOPIC_CREATION',
            'timestamp': t.created.isoformat() if t.created else None,
            'actor': actor_payload(t.user_id),
            'link': f'/topic/{t.id}',
            'content': t.title
        })

    # Topic reply creation
    reply_rows = (
        TopicReply.query
        .order_by(TopicReply.created.desc())
        .limit(10)
        .all()
    )
    for r in reply_rows:
        activities.append({
            'uniqueId': f'topic-reply-{r.id}',
            'type': 'TOPIC_REPLY_CREATION',
            'timestamp': r.created.isoformat() if r.created else None,
            'actor': actor_payload(r.user_id),
            'link': f'/topic/{r.topic_id}#k{r.id}',
            'content': (r.content or '')[:100]
        })

    # Galgame creation
    galgame_created_rows = (
        Galgame.query
        .filter(Galgame.status != 1)
        .order_by(Galgame.created.desc())
        .limit(5)
        .all()
    )
    for g in galgame_created_rows:
        name = g.name_zh_cn or g.name_zh_tw or g.name_ja_jp or g.name_en_us or ''
        activities.append({
            'uniqueId': f'galgame-{g.id}',
            'type': 'GALGAME_CREATION',
            'timestamp': g.created.isoformat() if g.created else None,
            'actor': actor_payload(g.user_id),
            'link': f'/galgame/{g.id}',
            'content': name[:100]
        })

    # Toolset creation
    toolset_created_rows = (
        GalgameToolset.query
        .filter(GalgameToolset.status != 1)
        .order_by(GalgameToolset.created.desc())
        .limit(5)
        .all()
    )
    for t in toolset_created_rows:
        activities.append({
            'uniqueId': f'toolset-{t.id}',
            'type': 'TOOLSET_CREATION',
            'timestamp': t.created.isoformat() if t.created else None,
            'actor': actor_payload(t.user_id),
            'link': f'/toolset/{t.id}',
            'content': (t.name or '')[:100]
        })

    # Sort desc by timestamp and take 30
    activities.sort(key=lambda x: x.get('timestamp') or '', reverse=True)
    activities = activities[:30]

    return jsonify({
        'topics': topics,
        'galgames': galgames,
        'activities': activities
    })
