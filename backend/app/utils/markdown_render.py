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


def markdown_to_html(text: str) -> str:
  if not text:
    return ''
  html = md.markdown(
    text,
    extensions=['fenced_code', 'tables', 'sane_lists']
  )
  return bleach.clean(html, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRS, strip=True)

