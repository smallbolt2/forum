import { z } from 'zod'

const slugSchema = z
  .string()
  .trim()
  .min(1, 'slug 不能为空')
  .max(233, 'slug 最长 233 个字符')
  .regex(/^[a-z0-9-]+$/i, 'slug 仅能包含字母、数字与连接符')
  .transform((value) => value.toLowerCase())

const optionalString = (max: number, defaultValue = '') =>
  z.string().trim().max(max).optional().default(defaultValue)

const paginationSchema = {
  page: z.coerce.number<number>().min(1).max(9999999).default(1),
  limit: z.coerce.number<number>().min(1).max(100).default(20),
  keyword: z.string().trim().max(200).optional().default('')
}

export const getDocCategoryListSchema = z.object(paginationSchema)

export const createDocCategorySchema = z.object({
  slug: slugSchema,
  title: z
    .string()
    .trim()
    .min(1, '分类标题不能为空')
    .max(233, '分类标题最长 233 个字符'),
  description: optionalString(777),
  icon: optionalString(128),
  sortOrder: z.coerce.number<number>().int().min(0).max(9999).default(0)
})

export const updateDocCategorySchema = createDocCategorySchema.merge(
  z.object({
    categoryId: z.coerce.number<number>().min(1).max(9999999)
  })
)

export const deleteDocCategorySchema = z.object({
  categoryId: z.coerce.number<number>().min(1).max(9999999)
})

export const getDocTagListSchema = z.object(paginationSchema)

export const createDocTagSchema = z.object({
  slug: slugSchema,
  title: z
    .string()
    .trim()
    .min(1, '标签名称不能为空')
    .max(128, '标签名称最长 128 个字符'),
  description: optionalString(255)
})

export const updateDocTagSchema = createDocTagSchema.merge(
  z.object({
    tagId: z.coerce.number<number>().min(1).max(9999999)
  })
)

export const deleteDocTagSchema = z.object({
  tagId: z.coerce.number<number>().min(1).max(9999999)
})

const docArticleOrderFields = [
  'published_time',
  'created',
  'view',
  'updated'
] as const

export const getDocArticleListSchema = z.object({
  ...paginationSchema,
  categoryId: z.coerce.number<number>().min(1).max(9999999).optional(),
  status: z.coerce.number<number>().int().min(0).max(2).optional(),
  isPin: z.coerce.boolean().optional(),
  tagId: z.coerce.number<number>().min(1).max(9999999).optional(),
  orderBy: z.enum(docArticleOrderFields).default('published_time'),
  sortOrder: z.enum(['asc', 'desc']).default('desc')
})

const docArticleBaseSchema = z.object({
  title: z
    .string()
    .trim()
    .min(1, '文档标题不能为空')
    .max(233, '标题最长 233 个字符'),
  slug: slugSchema,
  description: z
    .string()
    .trim()
    .min(1, '文档简介不能为空')
    .max(777, '简介最长 777 个字符'),
  banner: optionalString(777),
  status: z.coerce.number<number>().int().min(0).max(2).default(1),
  isPin: z.coerce.boolean().default(false),
  contentMarkdown: z
    .string()
    .trim()
    .min(1, '正文内容不能为空')
    .max(100007, '正文长度超出限制'),
  categoryId: z.coerce.number<number>().min(1).max(9999999),
  tagIds: z
    .array(z.coerce.number<number>().min(1).max(9999999))
    .optional()
    .default([])
})

export const createDocArticleSchema = docArticleBaseSchema

export const updateDocArticleSchema = docArticleBaseSchema.merge(
  z.object({
    articleId: z.coerce.number<number>().min(1).max(9999999)
  })
)

export const deleteDocArticleSchema = z.object({
  articleId: z.coerce.number<number>().min(1).max(9999999)
})
