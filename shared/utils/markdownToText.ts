/** Milkdown 导出字面量 ~ 为 \\~，纯文本摘要里应还原（与后端 markdown_render 一致） */
function unescapeMilkdownTildesOutsideFences(text: string): string {
  const parts = text.split('```')
  for (let i = 0; i < parts.length; i += 2) {
    parts[i] = parts[i].replace(/\\~/g, '~')
  }
  return parts.join('```')
}

export const markdownToText = (markdown: string) => {
  return unescapeMilkdownTildesOutsideFences(markdown)
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1')
    .replace(/(\*\*|__)(.*?)\1/g, '$2')
    .replace(/(\*|_)(.*?)\1/g, '$2')
    .replace(/^\s*(#{1,6})\s+(.*)/gm, '$2')
    .replace(/`/g, '')
    .replace(/^(-{3,}|\*{3,})$/gm, '')
    .replace(/^\s*([-*+]|\d+\.)\s+/gm, '')
    .replace(/\n+/g, ' ')
    .trim()
}
