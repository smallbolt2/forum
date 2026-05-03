import markdown as md
import bleach


_ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union({
  'p', 'pre', 'code', 'blockquote',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
  'ul', 'ol', 'li',
  'strong', 'em', 'del',
  'hr', 'br',
  'a', 'img',
  'table', 'thead', 'tbody', 'tr', 'th', 'td'
})

_ALLOWED_ATTRS = {
  **bleach.sanitizer.ALLOWED_ATTRIBUTES,
  'a': ['href', 'title', 'target', 'rel'],
  'img': ['src', 'alt', 'title'],
  'code': ['class'],
  'pre': ['class'],
  'th': ['align'],
  'td': ['align']
}


def _unescape_milkdown_tildes_outside_fences(text: str) -> str:
  """Milkdown 导出时会把字面量 ~ 写成 \\~，避免被当成 GFM 删除线；Python-Markdown
  不会按 CommonMark 吃掉该转义，页面上会原样出现 \\~。仅在 fenced code 外还原。"""
  parts = text.split('```')
  for i in range(0, len(parts), 2):
    parts[i] = parts[i].replace('\\~', '~')
  return '```'.join(parts)


def markdown_to_html(text: str) -> str:
  if not text:
    return ''
  text = _unescape_milkdown_tildes_outside_fences(text)
  html = md.markdown(
    text,
    extensions=['fenced_code', 'tables', 'sane_lists']
  )
  return bleach.clean(html, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS, strip=True)

