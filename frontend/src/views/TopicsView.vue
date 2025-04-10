<template>
  <v-container>
    <v-toolbar flat color="transparent">
      <v-toolbar-title class="text-h5">主题管理 ({{ currentSubject || '未选择学科' }})</v-toolbar-title>
      <v-spacer></v-spacer>
       <!-- 可以添加一个刷新按钮 -->
       <v-btn icon @click="loadTopics">
         <v-icon>mdi-refresh</v-icon>
       </v-btn>
    </v-toolbar>

    <v-alert v-if="!currentSubject" type="warning" dense outlined class="mb-4">
      请先在主页选择一个学科。
    </v-alert>

    <v-row v-if="currentSubject">
      <v-col
        v-for="topic in topics"
        :key="topic.id"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card class="mx-auto" hover>
          <v-card-title>{{ topic.title }}</v-card-title>
          <v-card-subtitle>主题 ID: {{ topic.id }}</v-card-subtitle>
          <v-card-actions>
            <v-btn color="info" variant="text" size="small" @click="viewTopicDetails(topic)">查看</v-btn>
            <v-btn color="primary" variant="text" size="small" @click="openEditDialog(topic)">编辑</v-btn>
            <v-btn color="secondary" variant="text" size="small" @click="generateEssay(topic)">生成范文</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="error" variant="text" size="small" @click="openDeleteDialog(topic)">删除</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
       <v-col cols="12" v-if="topics.length === 0 && currentSubject">
         <v-card-text class="text-center">当前学科下还没有主题，快去添加吧！</v-card-text>
       </v-col>
    </v-row>

    <!-- 添加主题的悬浮按钮 -->
    <v-btn
      v-if="currentSubject"
      fab
      color="primary"
      fixed
      bottom
      right
      @click="openAddDialog"
      class="mb-16 mr-4" <!-- 调整位置避免遮挡 -->
    >
      <v-icon>mdi-plus</v-icon>
    </v-btn>

    <!-- 添加/编辑主题对话框 -->
    <v-dialog v-model="dialog" persistent max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ dialogTitle }}</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-form ref="form" v-model="valid" lazy-validation>
              <v-text-field
                v-model="editedTopic.title"
                label="主题标题*"
                :rules="[v => !!v || '主题标题不能为空']"
                required
              ></v-text-field>
               <!-- 可以添加更多字段，如描述等 -->
            </v-form>
          </v-container>
          <small>*表示必填字段</small>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeDialog">取消</v-btn>
          <v-btn color="blue darken-1" :disabled="!valid" text @click="saveTopic">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 删除确认对话框 -->
    <v-dialog v-model="deleteDialog" persistent max-width="400px">
        <v-card>
            <v-card-title class="text-h5">确认删除</v-card-title>
            <v-card-text>确定要删除主题 "{{ topicToDelete?.title }}" 吗？此操作无法撤销。</v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="grey darken-1" text @click="closeDeleteDialog">取消</v-btn>
                <v-btn color="error darken-1" text @click="confirmDeleteTopic">确认删除</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

     <!-- 查看主题详情对话框 (简单示例) -->
    <v-dialog v-model="viewDialog" max-width="500px">
        <v-card>
            <v-card-title class="text-h5">主题详情</v-card-title>
            <v-card-text v-if="viewingTopic">
                <p><strong>ID:</strong> {{ viewingTopic.id }}</p>
                <p><strong>标题:</strong> {{ viewingTopic.title }}</p>
                <!-- 可以添加更多详情 -->
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" text @click="viewDialog = false">关闭</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

interface Topic {
  id: number;
  title: string;
  // 可以添加其他属性，如 description
}

const router = useRouter()

const topics = ref<Topic[]>([])
const currentSubject = ref<string | null>(null)

// 对话框状态
const dialog = ref(false)
const deleteDialog = ref(false)
const viewDialog = ref(false)
const valid = ref(true) // 表单校验状态
const form = ref<any>(null) // 表单引用

// 编辑/添加相关
const editedIndex = ref(-1) // -1 表示添加，否则为编辑的索引
const editedTopic = ref<Partial<Topic>>({ title: '' }) // 使用 Partial 允许 id 为空
const defaultTopic: Partial<Topic> = { title: '' }

// 删除相关
const topicToDelete = ref<Topic | null>(null)

// 查看相关
const viewingTopic = ref<Topic | null>(null)


const dialogTitle = computed(() => {
  return editedIndex.value === -1 ? '添加新主题' : '编辑主题'
})

// 模拟加载主题数据
const loadTopics = () => {
  currentSubject.value = localStorage.getItem('selectedSubject')
  if (!currentSubject.value) {
    topics.value = []
    return
  }
  console.log(`加载 ${currentSubject.value} 的主题...`)
  // 实际应用中，这里会调用 API 获取数据
  // 模拟数据
  if (currentSubject.value === '英语') {
    topics.value = [
      { id: 1, title: 'My Favorite Hobby' },
      { id: 2, title: 'A Trip to the Zoo' },
      { id: 5, title: 'Environmental Protection' },
    ]
  } else if (currentSubject.value === '语文') {
     topics.value = [
      { id: 3, title: '记一次难忘的活动' },
      { id: 4, title: '我的理想' },
      { id: 6, title: '家乡的变化' },
    ]
  } else {
    topics.value = []
  }
}

// 打开添加对话框
const openAddDialog = () => {
  editedIndex.value = -1
  editedTopic.value = { ...defaultTopic }
  dialog.value = true
  form.value?.resetValidation() // 重置校验状态
}

// 打开编辑对话框
const openEditDialog = (topic: Topic) => {
  editedIndex.value = topics.value.indexOf(topic)
  editedTopic.value = { ...topic } // 复制一份，避免直接修改原始数据
  dialog.value = true
   form.value?.resetValidation()
}

// 打开删除确认对话框
const openDeleteDialog = (topic: Topic) => {
  topicToDelete.value = topic
  deleteDialog.value = true
}

// 关闭添加/编辑对话框
const closeDialog = () => {
  dialog.value = false
  // 延迟重置表单，避免在关闭动画期间看到内容变化
  setTimeout(() => {
    editedTopic.value = { ...defaultTopic }
    editedIndex.value = -1
    form.value?.resetValidation()
  }, 300)
}

// 关闭删除对话框
const closeDeleteDialog = () => {
  deleteDialog.value = false
  setTimeout(() => {
    topicToDelete.value = null
  }, 300)
}

// 保存主题（添加或编辑）
const saveTopic = async () => {
  const isValid = await form.value?.validate()
  if (!isValid || !isValid.valid) return // 检查校验结果

  if (editedIndex.value > -1) {
    // 编辑
    console.log('模拟编辑主题:', editedTopic.value)
    // 实际应用中调用 API 更新
    Object.assign(topics.value[editedIndex.value], editedTopic.value)
  } else {
    // 添加
    console.log('模拟添加主题:', editedTopic.value)
    // 实际应用中调用 API 添加，并获取返回的 ID
    const newId = Math.max(0, ...topics.value.map(t => t.id)) + 1 // 简单模拟 ID 生成
    topics.value.push({ ...editedTopic.value, id: newId } as Topic) // 强制转换为 Topic 类型
  }
  closeDialog()
}

// 确认删除主题
const confirmDeleteTopic = () => {
  if (topicToDelete.value) {
    console.log('模拟删除主题:', topicToDelete.value.id)
    // 实际应用中调用 API 删除
    const index = topics.value.indexOf(topicToDelete.value)
    if (index > -1) {
      topics.value.splice(index, 1)
    }
  }
  closeDeleteDialog()
}

// 查看主题详情
const viewTopicDetails = (topic: Topic) => {
    viewingTopic.value = topic;
    viewDialog.value = true;
}

// 生成范文
const generateEssay = (topic: Topic) => {
  console.log(`为主题 ${topic.id} (${topic.title}) 生成范文`)
  // 实际应用中可能导航到 /essay-tools 并传递 topicId
  router.push('/essay-tools') // 暂时导航到作文工具页
}


// 组件挂载时加载数据
onMounted(() => {
  loadTopics()
})

</script>

<style scoped>
.v-card {
  transition: box-shadow 0.3s ease-in-out;
}
.v-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.v-btn--fab {
  bottom: 70px !important; /* 调整 FAB 按钮位置，避免与底部导航（如果未来添加）重叠 */
}
</style>
