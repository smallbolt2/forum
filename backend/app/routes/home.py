

from collections import defaultdict

from flask import Blueprint, jsonify
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models.topic import Topic
from app.models.user import User
from app.models.prisma_topic_extras import (
  TopicTag,
  TopicSection,
  TopicSectionRelation,
  TopicLike,
)
from app.models.topic_reply import TopicReply
from app.models.prisma_toolset_min import GalgameToolset

home_bp = Blueprint('home', __name__)


def _rollback_session():
    try:
        db.session.rollback()
    except Exception:
        pass


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

    sections_by_topic = defaultdict(list)
    if topic_ids:
        rels = TopicSectionRelation.query.filter(
            TopicSectionRelation.topic_id.in_(topic_ids)
        ).all()
        section_ids = list({r.topic_section_id for r in rels})
        section_map = {}
        if section_ids:
            for s in TopicSection.query.filter(TopicSection.id.in_(section_ids)).all():
                section_map[s.id] = s.name
        for r in rels:
            name = section_map.get(r.topic_section_id)
            if name:
                sections_by_topic[r.topic_id].append(name)

    like_counts = {
        tid: c for tid, c in db.session.query(
            TopicLike.topic_id, func.count(TopicLike.id)
        ).filter(TopicLike.topic_id.in_(topic_ids)).group_by(TopicLike.topic_id).all()
    } if topic_ids else {}

    reply_counts = {
        tid: c for tid, c in db.session.query(
            TopicReply.topic_id, func.count(TopicReply.id)
        ).filter(TopicReply.topic_id.in_(topic_ids)).group_by(TopicReply.topic_id).all()
    } if topic_ids else {}

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
            'likeCount': like_counts.get(t.id, 0),
            'replyCount': reply_counts.get(t.id, 0),
            'commentCount': 0,
            'section': sections_by_topic.get(t.id, []),
            'statusUpdateTime': t.status_update_time.isoformat() if t.status_update_time else None,
            'upvoteTime': t.upvote_time.isoformat() if t.upvote_time else None
        })

    galgames = []

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

    # Toolset creation（无表时跳过）
    try:
        toolset_created_rows = (
            GalgameToolset.query
            .filter(GalgameToolset.status != 1)
            .order_by(GalgameToolset.created.desc())
            .limit(5)
            .all()
        )
    except SQLAlchemyError:
        _rollback_session()
        toolset_created_rows = []

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
