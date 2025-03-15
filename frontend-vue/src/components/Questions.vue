<template>
  <div>
    <h1>题目列表</h1>
    <ul>
      <li v-for="question in questions" :key="question.id">
        {{ question.text }}
      </li>
    </ul>
  </div>
</template>

<script>
import { backendUrl } from '../config.js'

export default {
  name: 'QuestionList',
  data() {
    return {
      questions: []
    }
  },
  mounted() {
    this.fetchQuestions()
  },
  methods: {
    async fetchQuestions() {
      try {
        const response = await fetch(`${backendUrl}questions`)
        this.questions = await response.json()
      } catch (error) {
        console.error('Error fetching questions:', error)
      }
    }
  }
}
</script>

<style scoped>
/* Add your styles here */
</style>
