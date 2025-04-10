<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card class="pa-4 mb-6">
          <v-card-title class="text-h5 mb-3">选择主题领域</v-card-title>
          <v-select
            v-model="selectedSubject"
            :items="subjects"
            label="选择学科"
            outlined
            dense
            @update:model-value="handleSubjectChange"
          ></v-select>
          <v-card-text v-if="!selectedSubject">
            请选择一个学科开始。
          </v-card-text>
        </v-card>

        <v-card v-if="selectedSubject">
          <v-card-title class="text-h6">最近的主题 ({{ selectedSubject }})</v-card-title>
          <v-list lines="two">
            <!-- 模拟数据，稍后替换为真实数据 -->
            <v-list-item
              v-for="topic in recentTopics"
              :key="topic.id"
              :title="topic.title"
              subtitle="这是一个主题的简短描述..."
            >
              <template v-slot:append>
                <v-btn color="primary" variant="text" size="small" @click="viewTopic(topic.id)">查看</v-btn>
                <v-btn color="secondary" variant="text" size="small" class="ml-2" @click="generateEssay(topic.id)">生成范文</v-btn>
              </template>
            </v-list-item>
             <v-list-item v-if="recentTopics.length === 0">
                <v-list-item-title>暂无最近主题</v-list-item-title>
             </v-list-item>
          </v-list>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="startWriting">
              开始写作
              <v-icon end>mdi-pencil</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const subjects = ref(['英语', '语文'])
const selectedSubject = ref<string | null>(null) // 初始不选择
const recentTopics = ref<{ id: number; title: string }[]>([])

// 模拟加载最近主题的函数
const loadRecentTopics = (subject: string) => {
  console.log(`加载 ${subject} 的最近主题...`)
  // 在实际应用中，这里会调用 API 获取数据
  if (subject === '英语') {
    recentTopics.value = [
      { id: 1, title: 'My Favorite Hobby' },
      { id: 2, title: 'A Trip to the Zoo' },
    ]
  } else if (subject === '语文') {
    recentTopics.value = [
      { id: 3, title: '记一次难忘的活动' },
      { id: 4, title: '我的理想' },
    ]
  } else {
     recentTopics.value = []
  }
}

// 处理学科选择变化
const handleSubjectChange = (subject: string | null) => {
  if (subject) {
    // 可以将选择存储到 localStorage 或 Vuex
    localStorage.setItem('selectedSubject', subject)
    loadRecentTopics(subject)
  } else {
    localStorage.removeItem('selectedSubject')
    recentTopics.value = []
  }
}

// 组件挂载时尝试从 localStorage 加载上次选择的学科
onMounted(() => {
  const savedSubject = localStorage.getItem('selectedSubject')
  if (savedSubject && subjects.value.includes(savedSubject)) {
    selectedSubject.value = savedSubject
    loadRecentTopics(savedSubject)
  } else {
    // 如果没有保存的或无效，可以设置一个默认值，或者保持 null 让用户选择
    // selectedSubject.value = subjects.value[0]; // 默认选第一个
    // handleSubjectChange(selectedSubject.value);
  }
})

// 模拟导航到主题详情
const viewTopic = (topicId: number) => {
  console.log(`查看主题 ${topicId}`)
  // 实际应用中可能导航到 /topics/:id 或类似路由
  router.push('/topics') // 暂时导航到主题管理页
}

// 模拟导航到作文工具并预设主题
const generateEssay = (topicId: number) => {
  console.log(`为主题 ${topicId} 生成范文`)
  // 实际应用中可能导航到 /essay-tools 并传递 topicId
  router.push('/essay-tools') // 暂时导航到作文工具页
}

// 导航到作文工具页
const startWriting = () => {
  router.push('/essay-tools')
}

</script>

<style scoped>
/* 可以添加特定于 HomeView 的样式 */
.v-card {
  transition: box-shadow 0.3s ease-in-out;
}
.v-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
