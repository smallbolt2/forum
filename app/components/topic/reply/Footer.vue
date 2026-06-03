<script setup lang="ts">
import { useKunCopy } from '~/composables/useKunCopy'

const props = defineProps<{
  title: string
  reply: TopicReply
}>()

const title = props.title
const reply = props.reply

const emits = defineEmits<{
  handleNewComment: [comment: TopicComment]
}>()

const { id } = usePersistUserStore()
const isCommentPanelVisible = ref(false)

const replyLikeCount = ref(props.reply.likeCount)
const replyDislikeCount = ref(props.reply.dislikeCount)
const replyIsLiked = ref(props.reply.isLiked)
const replyIsDisliked = ref(props.reply.isDisliked)

watch(
  () => props.reply.likeCount,
  (value) => {
    replyLikeCount.value = value
  }
)

watch(
  () => props.reply.dislikeCount,
  (value) => {
    replyDislikeCount.value = value
  }
)

watch(
  () => props.reply.isLiked,
  (value) => {
    replyIsLiked.value = value
  }
)

watch(
  () => props.reply.isDisliked,
  (value) => {
    replyIsDisliked.value = value
  }
)

const handleReplyLikeUpdate = (payload: { isLiked: boolean; likeCount: number }) => {
  replyIsLiked.value = payload.isLiked
  replyLikeCount.value = payload.likeCount
  if (payload.isLiked) {
    replyIsDisliked.value = false
  }
}

const handleReplyDislikeUpdate = (payload: { isDisliked: boolean; dislikeCount: number }) => {
  replyIsDisliked.value = payload.isDisliked
  replyDislikeCount.value = payload.dislikeCount
  if (payload.isDisliked) {
    replyIsLiked.value = false
  }
}

const handleClickComment = () => {
  if (!id) {
    useMessage(10216, 'warn', 5000)
    return
  }
  isCommentPanelVisible.value = !isCommentPanelVisible.value
}

const handleNewComment = (comment: TopicComment) => {
  emits('handleNewComment', comment)
  isCommentPanelVisible.value = false
}

const handleReplyShareCopy = () => {
  useKunCopy(`${title}: https://www.kungal.com/topic/${reply.topicId}#k${reply.floor}`)
}
</script>

<template>
  <div class="w-full">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-1">
        <TopicFooterLike
          :topic-id="reply.topicId"
          :reply-id="reply.id"
          :target-user-id="reply.user.id"
          :like-count="replyLikeCount"
          :is-liked="replyIsLiked"
          :is-disliked="replyIsDisliked"
          @update-like="handleReplyLikeUpdate"
        />

        <TopicFooterDislike
          :topic-id="reply.topicId"
          :reply-id="reply.id"
          :target-user-id="reply.user.id"
          :dislike-count="replyDislikeCount"
          :is-disliked="replyIsDisliked"
          :is-liked="replyIsLiked"
          @update-dislike="handleReplyDislikeUpdate"
        />
      </div>

      <div class="flex items-center gap-1">
        <TopicFooterReply
          :target-user-name="reply.user.name"
          :target-user-id="reply.user.id"
          :target-floor="reply.floor"
          :target-reply-id="reply.id"
        />
        <KunTooltip text="分享该回复">
          <KunButton
            :is-icon-only="true"
            variant="light"
            color="default"
            size="lg"
            @click="handleReplyShareCopy"
          >
            <KunIcon name="lucide:share-2" />
          </KunButton>
        </KunTooltip>
        <TopicReplyRewrite :reply="reply" />
        <KunTooltip text="评论">
          <KunButton
            :is-icon-only="true"
            variant="light"
            color="default"
            size="lg"
            @click="handleClickComment"
          >
            <KunIcon name="uil:comment-dots" />
          </KunButton>
        </KunTooltip>
        <!-- ... 更多按钮 ... -->
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
            <TopicReplyPin :reply="reply" />
            <TopicReplyBestAnswer :reply="reply" />
            <TopicReplyDelete :reply="reply" />
          </div>
        </KunPopover>
      </div>
    </div>

    <KunAnimationFadeCard>
      <LazyTopicCommentPanel
        v-if="isCommentPanelVisible"
        class="mt-4"
        :reply-id="reply.id"
        :target-user="reply.user"
        @get-comment="handleNewComment"
        @close-panel="isCommentPanelVisible = false"
      />
    </KunAnimationFadeCard>
  </div>
</template>
