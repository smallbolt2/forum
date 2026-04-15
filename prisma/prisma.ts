//import 'dotenv/config'
//import { PrismaPg } from '@prisma/adapter-pg'
//import { PrismaClient } from './generated/prisma/client'

//const connectionString = `${process.env.KUN_DATABASE_URL}`

//const adapter = new PrismaPg({ connectionString })
//const prisma = new PrismaClient({ adapter })

//export { prisma }
// prisma/prisma.ts 或 lib/prisma.ts
// prisma/prisma.ts
import { PrismaClient } from '@prisma/client'
import { PrismaMssql } from '@prisma/adapter-mssql'

const connectionString = process.env.KUN_DATABASE_URL
if (!connectionString) {
  throw new Error('Missing env var: KUN_DATABASE_URL')
}

// 创建适配器
const adapter = new PrismaMssql(connectionString)

// 创建 PrismaClient 实例时传入适配器
const prisma = new PrismaClient({
  adapter,
  // 注意：这里不需要 datasourceUrl，因为适配器已经处理连接
})

export { prisma }