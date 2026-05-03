import { reactive } from 'vue'

interface Question {
  id: number
  text: string
  options: string[]
  correctOption: string
  isHard: boolean
}

export const questionsCN: Question[] = reactive([
  {
    id: 1,
    text: '1+1=?',
    options: ['1', '2', '3', '4'],
    correctOption: '2',
    isHard: false
  },
  {
    id: 2,
    text: '1+2=?',
    options: ['2', '1', '3', '4'],
    correctOption: '3',
    isHard: false
  }
])
