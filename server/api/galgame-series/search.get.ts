import { prisma } from '~~/prisma/prisma'
import { getSearchResultSchema } from '~/validations/galgame-series'

export default defineEventHandler(async (event) => {
  const input = kunParseGetQuery(event, getSearchResultSchema)
  if (typeof input === 'string') {
    return kunError(event, input)
  }

  const keywordsArray: string[] = input.keywords
    .trim()
    .slice(0, 107)
    .split(' ')
    .filter((keyword) => keyword.trim() !== '')

  const galgames = await prisma.galgame.findMany({
    where: {
      status: { not: 1 },
      AND: keywordsArray.map((kw) => ({
        OR: [
          { vndb_id: { in: keywordsArray } },
          {
            tag: {
              some: {
                tag: {
                  name: { contains: kw }
                }
              }
            }
          },
          { name_en_us: { contains: kw } },
          { name_ja_jp: { contains: kw } },
          { name_zh_cn: { contains: kw } },
          { name_zh_tw: { contains: kw } },
          {
            alias: {
              some: {
                name: { contains: kw }
              }
            }
          }
        ]
      }))
    },
    select: {
      id: true,
      name_en_us: true,
      name_ja_jp: true,
      name_zh_cn: true,
      name_zh_tw: true
    },
    take: 20
  })

  const formattedResult: GalgameSeriesSearchItem[] = galgames.map((g) => ({
    id: g.id,
    name: getPreferredLanguageText({
      'en-us': g.name_en_us,
      'ja-jp': g.name_ja_jp,
      'zh-cn': g.name_zh_cn,
      'zh-tw': g.name_zh_tw
    })
  }))

  return formattedResult
})
