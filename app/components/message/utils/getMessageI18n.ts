import type { Message } from '~~/shared/types/message'

const MESSAGE_TYPE_LABEL: Record<string, string> = {
  upvoted: '推了您的话题',
  liked: '赞了您',
  favorite: '收藏了您的内容',
  replied: '回复了您',
  solution: '将您的回复设为最佳答案',
  'pin-reply': '置顶了您的回复',
  commented: '评论了您',
  expired: '资源已过期',
  requested: '向您发起了请求',
  merged: '合并了您的内容',
  declined: '拒绝了您的请求',
  mentioned: '提到了您',
  admin: '管理员通知'
}

export const getMessageI18n = (message: Message) => {
  return MESSAGE_TYPE_LABEL[message.type] || message.type
}
