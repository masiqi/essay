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
            item-title="name"
            outlined
            dense
            @update:model-value="handleSubjectChange"
          ></v-select>
          <v-card-text v-if="!selectedSubject">
            请选择一个学科开始。
          </v-card-text>
        </v-card>

        <v-card v-if="selectedSubject">
          <v-card-title class="text-h6">最近的主题 ({{ selectedSubject.name }})</v-card-title>
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
import { getSubjects } from '../api/subject'
import type { Subject } from '../api/subject'

const router = useRouter()

// 使用接口类型
const subjects = ref<Subject[]>([])
const selectedSubject = ref<Subject | null>(null) // 初始不选择
const recentTopics = ref<{ id: number; title: string }[]>([])

// 加载最近主题的函数 (暂时保留模拟数据，稍后实现真实的 API 调用)
const loadRecentTopics = (subject: Subject) => {
  console.log(`加载 ${subject.name} 的最近主题...`)
  // 暂时保留模拟数据
  if (subject.name === '英语') {
    recentTopics.value = [
      { id: 1, title: 'My Favorite Hobby' },
      { id: 2, title: 'A Trip to the Zoo' },
    ]
  } else if (subject.name === '语文') {
    recentTopics.value = [
      { id: 3, title: '记一次难忘的活动' },
      { id: 4, title: '我的理想' },
    ]
  } else {
     recentTopics.value = []
  }
}

// 处理学科选择变化
const handleSubjectChange = (subject: Subject | null) => {
  if (subject) {
    // 将选择存储到 localStorage
    localStorage.setItem('selectedSubject', JSON.stringify(subject))
    loadRecentTopics(subject)
  } else {
    localStorage.removeItem('selectedSubject')
    recentTopics.value = []
  }
}

// 加载科目数据
const loadSubjects = async () => {
  try {
    subjects.value = await getSubjects()
  } catch (error) {
    console.error('加载科目数据失败:', error)
  }
}

// 组件挂载时加载科目数据并尝试从 localStorage 加载上次选择的学科
onMounted(async () => {
  await loadSubjects()
  const savedSubjectStr = localStorage.getItem('selectedSubject')
  if (savedSubjectStr) {
    try {
      const savedSubject = JSON.parse(savedSubjectStr)
      // 查找匹配的科目
      const matchedSubject = subjects.value.find(s => s.id === savedSubject.id)
      if (matchedSubject) {
        selectedSubject.value = matchedSubject
        loadRecentTopics(matchedSubject)
      }
    } catch (e) {
      console.error('解析保存的科目数据失败:', e)
      localStorage.removeItem('selectedSubject')
    }
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
