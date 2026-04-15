// prisma.config.ts
import type { PrismaConfig } from 'prisma'
import { PrismaMssql } from '@prisma/adapter-mssql'

export default {
  earlyAccess: true,
  schema: 'prisma/schema',
  datasourceUrl: process.env.KUN_DATABASE_URL,
  onGenerate: async (client) => {
    const connectionString = process.env.KUN_DATABASE_URL
    if (!connectionString) {
      throw new Error('Missing env var: KUN_DATABASE_URL')
    }
    const adapter = new PrismaMssql(connectionString)
    client.$connectWithAdapter(adapter)
  },
} satisfies PrismaConfig