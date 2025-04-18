import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TopicsView from '../views/TopicsView.vue'
import ChatView from '../views/ChatView.vue'
import EssayToolsView from '../views/EssayToolsView.vue'
import SubjectManagementView from '../views/SubjectManagementView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/topics',
    name: 'Topics',
    component: TopicsView
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatView
  },
  {
    path: '/essay-tools',
    name: 'EssayTools',
    component: EssayToolsView
  },
  {
    path: '/subjects',
    name: 'SubjectManagement',
    component: SubjectManagementView
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
