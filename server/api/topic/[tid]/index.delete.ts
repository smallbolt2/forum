import { prisma } from '~~/prisma/prisma'
import { updateTopicHideStatusSchema } from '~/validations/topic'
import { deleteTopicRepliesRecursive } from '~~/server/utils/topicReply'

export default defineEventHandler(async (event) => {
  // 这里复用 updateTopicHideStatusSchema 只校验 topicId
  const input = kunParseDeleteQuery(event, updateTopicHideStatusSchema)
  if (typeof input === 'string') {
    return kunError(event, input)
  }

  const userInfo = await getCookieTokenInfo(event)
  if (!userInfo) {
    return kunError(event, '用户登录失效', 205)
  }

  const topic = await prisma.topic.findUnique({
    where: { id: input.topicId },
    select: { id: true, user_id: true }
  })
  if (!topic) {
    return kunError(event, '未找到该话题')
  }

  // 仅作者本人或管理员可以彻底删除话题
  if (topic.user_id !== userInfo.uid && userInfo.role < 2) {
    return kunError(event, '您没有权限删除该话题')
  }
// 先删除该话题下的所有回复包括嵌套回复及其评论点赞等，使用已有工具
  await prisma.$transaction(async (tx) => {
    const rootReplies = await tx.topic_reply.findMany({
      where: { topic_id: input.topicId },
      select: { id: true }
    })
    if (rootReplies.length > 0) {
      await deleteTopicRepliesRecursive(
        rootReplies.map((r) => r.id),
        tx as never
      )
    }
// 删除话题本身，其它依赖 topic 的关系（like/favorite/section/tag/poll 等）
// 由 Prisma schema 中的 onDelete: Cascade 处理
    await tx.topic.delete({
      where: { id: input.topicId }
    })
  })

  return 'MOEMOE delete topic permanently!'
})

