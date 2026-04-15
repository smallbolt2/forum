export interface RSSGalgame {
  id: number
  name: string
  banner: string
  user: KunUser

  created: Date | string
  description: string
}

export interface RSSTopic {
  id: number
  name: string
  user: KunUser

  created: Date | string
  description: string
}
