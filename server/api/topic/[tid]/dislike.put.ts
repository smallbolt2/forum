import { prisma } from '~~/prisma/prisma'
import { updateTopicDislikeSchema } from '~/validations/topic'

export default defineEventHandler(async (event) => {
  const userInfo = await getCookieTokenInfo(event)
  if (!userInfo) {
    return kunError(event, '用户登录失效', 205)
  }
  const uid = userInfo.uid

  const input = await kunParsePutBody(event, updateTopicDislikeSchema)
  if (typeof input === 'string') {
    return kunError(event, input)
  }

  const topic = await prisma.topic.findUnique({
    where: { id: input.topicId, status: { not: 1 } },
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
  if (!topic) {
    return kunError(event, '未找到该话题')
  }
  if (topic.user_id === uid) {
    return kunError(event, '您不能给自己点踩')
  }

  const isLiked = topic.like.length > 0
  const isDisliked = topic.dislike.length > 0
  if (!isDisliked && isLiked) {
    return kunError(event, '该话题已被您点赞，无法点踩')
  }

  if (isDisliked) {
    await prisma.topic_dislike.deleteMany({
      where: {
        user_id: uid,
        topic_id: input.topicId
      }
    })
  } else {
    await prisma.topic_dislike.create({
      data: {
        user_id: uid,
        topic_id: input.topicId
      }
    })
  }

  const dislikeCount = await prisma.topic_dislike.count({
    where: { topic_id: input.topicId }
  })

  return {
    isDisliked: !isDisliked,
    dislikeCount
  }
})
