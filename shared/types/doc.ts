export interface DocTocLink {
  id: string
  text: string
  depth: number
  children?: DocTocLink[]
}

export interface DocCategoryItem {
  id: number
  slug: string
  title: string
  description: string
  icon: string
  sortOrder: number
  created: Date | string
  updated: Date | string
}

export interface DocCategoryListResponse {
  categories: DocCategoryItem[]
  totalCount: number
  page: number
  limit: number
}

export interface DocTagItem {
  id: number
  slug: string
  title: string
  description: string
  created: Date | string
  updated: Date | string
}

export interface DocTagListResponse {
  tags: DocTagItem[]
  totalCount: number
  page: number
  limit: number
}

export interface DocArticleCategorySummary {
  id: number
  slug: string
  title: string
}

export interface DocArticleAuthorSummary {
  id: number
  name: string
  avatar: string
}

export interface DocArticleSummary {
  id: number
  title: string
  slug: string
  path: string
  description: string
  banner: string
  status: number
  isPin: boolean
  view: number
  publishedTime: Date | string
  editedTime: Date | string | null
  created: Date | string
  updated: Date | string
  category: DocArticleCategorySummary
  author: DocArticleAuthorSummary
  tags: DocTagItem[]
}

export interface DocArticleDetail extends DocArticleSummary {
  contentMarkdown: string
  contentHtml: string
  toc: DocTocLink[]
}

export interface DocArticleListResponse {
  articles: DocArticleSummary[]
  totalCount: number
  page: number
  limit: number
}
