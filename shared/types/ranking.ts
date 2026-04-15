export interface RankingUserItem {
  id: number
  name: string
  avatar: string
  bio: string
  sortField: string
  value: number
}

export interface RankingTopicItem {
  id: number
  title: string
  user: KunUser
  sortField: string
  value: number
}

export interface RankingGalgameItem {
  id: number
  name: KunLanguage
  user: KunUser
  banner: string
  sortField: string
  value: number
}
