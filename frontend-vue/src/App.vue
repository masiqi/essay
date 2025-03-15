<template>
  <div id="app">
    <nav>
      <router-link to="/subjects">学科</router-link> |
      <router-link to="/questions">题目</router-link>
    </nav>
    <router-view></router-view>
  </div>
</template>

<script>
import { createRouter, createWebHistory } from 'vue-router'
import Subjects from './components/Subjects.vue'
import Questions from './components/Questions.vue' // Ensure this line is present if not already

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/subjects', component: Subjects },
    { path: '/questions', component: Questions }
  ]
})

export default {
  name: 'App',
  router
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
