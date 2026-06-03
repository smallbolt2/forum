import { prisma } from '~~/prisma/prisma'
import { updateReplyDislikeSchema } from '~/validations/topic'

export default defineEventHandler(async (event) => {
  const userInfo = await getCookieTokenInfo(event)
  if (!userInfo) {
    return kunError(event, '用户登录失效', 205)
  }
  const uid = userInfo.uid

  const input = await kunParsePutBody(event, updateReplyDislikeSchema)
  if (typeof input === 'string') {
    return kunError(event, input)
  }

  const reply = await prisma.topic_reply.findUnique({
    where: { id: input.replyId },
    include: {
      like: {
        where: {
          user_id: uid
        }
      },
      dislike: {
        where: {
          user_id: uid
        }
      }
    }
  })
  if (!reply) {
    return kunError(event, '未找到该回复')
  }
  if (reply.user_id === uid) {
    return kunError(event, '您不能给自己点踩')
  }

  const isLikedReply = reply.like.length > 0
  const isDislikedReply = reply.dislike.length > 0
  if (!isDislikedReply && isLikedReply) {
    return kunError(event, '该回复已被您点赞，无法点踩')
  }

  if (isDislikedReply) {
    await prisma.topic_reply_dislike.deleteMany({
      where: {
        user_id: uid,
        topic_reply_id: input.replyId
      }
    })
  } else {
    await prisma.topic_reply_dislike.create({
      data: {
        user_id: uid,
        topic_reply_id: input.replyId
      }
    })
  }

  const dislikeCount = await prisma.topic_reply_dislike.count({
    where: { topic_reply_id: input.replyId }
  })

  return {
    isDisliked: !isDislikedReply,
    dislikeCount
  }
})
