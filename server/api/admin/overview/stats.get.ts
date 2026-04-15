import { prisma } from '~~/prisma/prisma'
import { Prisma } from '@prisma/client'
import {
  subDays,
  startOfDay,
  endOfDay,
  format,
  eachDayOfInterval
} from 'date-fns'
import { getOverviewStatsSchema } from '~/validations/admin'
import { KUN_ADMIN_OVERVIEW_STATS_MODEL_ITEM } from '~/constants/admin'

export default defineEventHandler(async (event) => {
  const input = kunParseGetQuery(event, getOverviewStatsSchema)
  if (typeof input === 'string') {
    return kunError(event, input)
  }

  const { days } = input

  const endDate = endOfDay(new Date())
  const startDate = startOfDay(subDays(endDate, days - 1))

  const queryPromises = KUN_ADMIN_OVERVIEW_STATS_MODEL_ITEM.map(
    async (modelName) => {
      const table = Prisma.raw(`[dbo].[${modelName}]`)
      const result = await prisma.$queryRaw(
        Prisma.sql`
          SELECT
            CAST([created] AS date) AS [date],
            COUNT([id]) AS [count]
          FROM ${table}
          WHERE [created] >= ${startDate} AND [created] <= ${endDate}
          GROUP BY CAST([created] AS date)
          ORDER BY [date] ASC;
        `
      )
      return {
        model: modelName,
        data: result as { date: Date; count: number }[]
      }
    }
  )

  const results = await Promise.all(queryPromises)

  const dailyDataMap = new Map<string, Record<string, number>>()

  const dateInterval = eachDayOfInterval({ start: startDate, end: endDate })

  dateInterval.forEach((day) => {
    const formattedDate = format(day, 'yyyy-MM-dd')
    const initialCounts = Object.fromEntries(
      KUN_ADMIN_OVERVIEW_STATS_MODEL_ITEM.map((model) => [model, 0])
    )
    dailyDataMap.set(formattedDate, { ...initialCounts })
  })

  results.forEach(({ model, data }) => {
    data.forEach(({ date, count }) => {
      const formattedDate = format(date, 'yyyy-MM-dd')
      if (dailyDataMap.has(formattedDate)) {
        const dayData = dailyDataMap.get(formattedDate)!
        dayData[model] = count
      }
    })
  })

  const finalData: AdminOverStats[] = Array.from(dailyDataMap.entries())
    .map(([date, counts]) => ({
      date,
      ...counts
    }))
    .sort((a, b) => a.date.localeCompare(b.date))

  return finalData
})
