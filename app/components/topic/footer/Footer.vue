<script setup lang="ts">
import { useKunCopy } from '~/composables/useKunCopy'

const props = defineProps<{
  topic: TopicDetail
}>()

const topic = props.topic
const { id } = usePersistUserStore()

const topicLikeCount = ref(props.topic.likeCount)
const topicDislikeCount = ref(props.topic.dislikeCount)
const topicIsLiked = ref(props.topic.isLiked)
const topicIsDisliked = ref(props.topic.isDisliked)

watch(
  () => props.topic.likeCount,
  (value) => {
    topicLikeCount.value = value
  }
)

watch(
  () => props.topic.dislikeCount,
  (value) => {
    topicDislikeCount.value = value
  }
)

watch(
  () => props.topic.isLiked,
  (value) => {
    topicIsLiked.value = value
  }
)

watch(
  () => props.topic.isDisliked,
  (value) => {
    topicIsDisliked.value = value
  }
)

const handleTopicLikeUpdate = (payload: { isLiked: boolean; likeCount: number }) => {
  topicIsLiked.value = payload.isLiked
  topicLikeCount.value = payload.likeCount
  if (payload.isLiked) {
    topicIsDisliked.value = false
  }
}

const handleTopicDislikeUpdate = (payload: { isDisliked: boolean; dislikeCount: number }) => {
  topicIsDisliked.value = payload.isDisliked
  topicDislikeCount.value = payload.dislikeCount
  if (payload.isDisliked) {
    topicIsLiked.value = false
  }
}

const handleTopicShareCopy = () => {
  useKunCopy(`${topic.title}: https://www.kungal.com/topic/${topic.id}`)
}
</script>

<template>
  <div class="mt-auto flex items-center justify-between">
    <div class="flex items-center gap-1">
      <TopicFooterUpvote
        :topic-id="topic.id"
        :target-user-id="topic.user.id"
        :upvote-count="topic.upvoteCount"
        :is-upvoted="topic.isUpvoted"
      />

      <TopicFooterLike
        :topic-id="topic.id"
        :target-user-id="topic.user.id"
        :like-count="topicLikeCount"
        :is-liked="topicIsLiked"
        :is-disliked="topicIsDisliked"
        @update-like="handleTopicLikeUpdate"
      />

      <TopicFooterDislike
        :topic-id="topic.id"
        :target-user-id="topic.user.id"
        :dislike-count="topicDislikeCount"
        :is-disliked="topicIsDisliked"
        :is-liked="topicIsLiked"
        @update-dislike="handleTopicDislikeUpdate"
      />

      <TopicFooterFavorite
        :topic-id="topic.id"
        :target-user-id="topic.user.id"
        :favorite-count="topic.favoriteCount"
        :is-favorite="topic.isFavorited"
      />
    </div>

    <div class="flex items-center gap-1">
      <TopicFooterReply
        :target-user-name="topic.user.name"
        :target-user-id="topic.user.id"
        :target-floor="0"
      />

      <KunTooltip text="分享">
        <KunButton
          :is-icon-only="true"
          variant="light"
          color="default"
          size="lg"
          @click="handleTopicShareCopy"
        >
          <KunIcon name="lucide:share-2" />
        </KunButton>
      </KunTooltip>

      <TopicFooterRewrite :topic="topic" />

      <KunPopover position="top-end">
        <template v-if="id" #trigger>
          <KunButton
            :is-icon-only="true"
            variant="light"
            color="default"
            size="lg"
          >
            <KunIcon name="lucide:ellipsis" />
          </KunButton>
        </template>

        <div class="flex w-54 flex-col gap-2 p-2">
          <TopicFooterHide :topic-id="topic.id" />
        </div>
      </KunPopover>
    </div>
  </div>
</template>
