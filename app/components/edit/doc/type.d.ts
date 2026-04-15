export type DocEditorMode = 'create' | 'rewrite'

export interface DocEditorForm {
  articleId: number | null
  title: string
  slug: string
  description: string
  banner: string
  status: number
  isPin: boolean
  contentMarkdown: string
  categoryId: number
  tagIds: number[]
}
