export interface CategoryLatestTopicInfo {
  id: number
  title: string
  created: Date | string
}

export interface CategorySectionStats {
  id: number
  name: string
  topicCount: number
  viewCount: number
  latestTopic: CategoryLatestTopicInfo | null
}
