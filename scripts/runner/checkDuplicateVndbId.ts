import { prisma } from '../../prisma/prisma'

const run = async () => {
  try {
    console.log('Checking for duplicate vndb_id (case-insensitive)...\n')

    const galgames = await prisma.galgame.findMany({
      select: {
        id: true,
        vndb_id: true,
        name_en_us: true,
        name_ja_jp: true,
        created: true
      },
      orderBy: { id: 'asc' }
    })

    const groups = new Map<string, typeof galgames>()
    for (const g of galgames) {
      const key = g.vndb_id.toLowerCase()
      const list = groups.get(key) ?? []
      list.push(g)
      groups.set(key, list)
    }

    const duplicates = [...groups.entries()].filter(([, list]) => list.length > 1)

    if (!duplicates.length) {
      console.log('No duplicate vndb_id found.')
      return
    }

    console.log(`Found ${duplicates.length} groups of duplicates:\n`)

    for (const [key, list] of duplicates) {
      console.log(`--- vndb_id (normalized): ${key} ---`)
      for (const g of list) {
        const name = g.name_ja_jp || g.name_en_us || '(no name)'
        console.log(
          `  id=${g.id}  vndb_id="${g.vndb_id}"  name="${name}"  created=${g.created.toISOString()}`
        )
      }
      console.log()
    }

    console.log(`Total: ${duplicates.length} groups, ${duplicates.reduce((sum, [, list]) => sum + list.length, 0)} records`)
  } catch (error) {
    console.error(
      'Check failed:',
      error instanceof Error ? (error.stack ?? error.message) : String(error)
    )
    process.exitCode = 1
  } finally {
    await prisma.$disconnect()
  }
}

run()
