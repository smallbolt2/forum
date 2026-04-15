"""
Nuxt/Nitro 兼容：/api/doc/article（先提供最小可用返回，避免首页轮播报错）
"""

from flask import Blueprint, jsonify, request


kun_doc_article_bp = Blueprint('kun_doc_article', __name__)


@kun_doc_article_bp.route('/article', methods=['GET'])
def list_articles():
  # 返回结构：{ articles, totalCount }
  return jsonify({'articles': [], 'totalCount': 0})

