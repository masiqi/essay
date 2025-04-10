<template>
  <v-app>
    <!-- 顶部导航栏 -->
    <v-app-bar app color="primary" dark>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>作文助手</v-toolbar-title>
      <v-spacer></v-spacer>
      <!-- 可以添加设置或帮助图标 -->
      <!-- <v-btn icon>
        <v-icon>mdi-cog</v-icon>
      </v-btn> -->
    </v-app-bar>

    <!-- 侧边栏导航 -->
    <!-- 侧边栏导航 -->
    <v-navigation-drawer
      v-model="drawer"
      app
      :temporary="$vuetify.display.mobile"
      color="#303F9F"
      dark
    >
      <!-- 在移动设备上临时显示 -->
      <!-- 深蓝色背景 -->
      <v-list dense nav>
        <v-list-item
          v-for="item in navItems"
          :key="item.title"
          :to="item.to"
          link
        >
          <template v-slot:prepend>
             <v-icon>{{ item.icon }}</v-icon>
          </template>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- 主内容区域 -->
    <!-- 主内容区域 -->
    <v-main>
      <v-container fluid>
        <router-view></router-view> <!-- 路由视图将在这里渲染 -->
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useDisplay } from 'vuetify' // Vuetify 3 的正确导入方式

const drawer = ref(true) // 控制侧边栏显示/隐藏
const display = useDisplay() // 获取屏幕信息

// 在 setup 中初始化 drawer 的状态，确保非移动端默认展开
if (!display.mobile) {
  drawer.value = true;
} else {
  drawer.value = false; // 移动端默认收起
}


const navItems = ref([
  { title: '主页', icon: 'mdi-home', to: '/' },
  { title: '主题管理', icon: 'mdi-format-list-bulleted', to: '/topics' },
  { title: '聊天', icon: 'mdi-chat', to: '/chat' },
  { title: '作文工具', icon: 'mdi-tools', to: '/essay-tools' },
])
</script>

<style scoped>
/* 可以添加一些全局或特定于 App.vue 的样式 */
.v-main {
  background-color: var(--v-theme-background); /* 使用 Vuetify 主题背景色 */
}
</style>
