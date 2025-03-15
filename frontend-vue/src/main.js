import { createApp } from 'vue'
import App from './App.vue'

import { createRouter, createWebHistory } from 'vue-router'
import SubjectList from './components/Subjects.vue'
import QuestionList from './components/Questions.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/subjects', component: SubjectList },
    { path: '/questions', component: QuestionList }
  ]
})

createApp(App).use(router).mount('#app')
