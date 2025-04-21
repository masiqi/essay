<template>
  <v-container>
    <v-toolbar flat color="transparent">
      <v-toolbar-title class="text-h5">题目管理</v-toolbar-title>
      <v-spacer></v-spacer>
       <!-- 可以添加一个刷新按钮 -->
       <v-btn icon @click="loadTopics">
         <v-icon>mdi-refresh</v-icon>
       </v-btn>
    </v-toolbar>

    <v-alert v-if="errorMessage" type="error" dense outlined class="mb-4">
      {{ errorMessage }}
    </v-alert>

    <!-- Loading State -->
    <div v-if="loading" class="text-center pa-5">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
      <p class="mt-2">加载中...</p>
    </div>

    <!-- No Data State -->
    <div v-else-if="topics.length === 0" class="text-center pa-5">
      <v-icon size="x-large" color="grey-lighten-1">mdi-text-box-outline</v-icon>
      <p class="mt-2 text-grey">暂无题目，点击右下角按钮添加</p>
    </div>

    <!-- Data List State -->
    <v-row v-else>
      <v-col
        v-for="topic in topics"
        :key="topic.id"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card class="mx-auto" hover>
          <v-card-title>{{ topic.title }}</v-card-title>
          <!-- 2. 更新卡片副标题以显示科目 -->
          <v-card-subtitle>科目: {{ getSubjectName(topic.subjectId) }} (ID: {{ topic.id }})</v-card-subtitle>
          <v-card-actions>
            <v-btn color="info" variant="text" size="small" @click="viewTopicDetails(topic)">查看</v-btn>
            <v-btn color="primary" variant="text" size="small" @click="openEditDialog(topic)">编辑</v-btn>
            <v-btn color="secondary" variant="text" size="small" @click="generateEssay(topic)">生成范文</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="error" variant="text" size="small" @click="openDeleteDialog(topic)">删除</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- 添加题目的悬浮按钮 -->
    <v-btn
      fab
      color="primary"
      fixed
      bottom
      right
      @click="openAddDialog"
      class="mb-16 mr-4"
    >
      <!-- 调整位置避免遮挡 -->
      <v-icon>mdi-plus</v-icon>
    </v-btn>

    <!-- 添加/编辑题目对话框 -->
    <v-dialog v-model="dialog" persistent max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ dialogTitle }}</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-form ref="form" v-model="valid" lazy-validation>
              <!-- 1. 更新标题字段 -->
              <v-text-field
                v-model="editedTopic.title"
                label="标题*"
                :rules="[(v: string) => !!v || '标题不能为空']"
                required
                counter="100"
              ></v-text-field>
              <!-- 1. 添加题目内容字段 -->
              <v-textarea
                v-model="editedTopic.question"
                label="题目内容*"
                :rules="[(v: string) => !!v || '题目内容不能为空']"
                required
                rows="3"
                auto-grow
              ></v-textarea>
              <!-- 1. 添加科目选择下拉框 -->
              <v-select
                v-model="editedTopic.subjectId"
                :items="subjects"
                item-title="name"
                item-value="id"
                label="所属科目*"
                :rules="[(v: number | null) => v !== null || '请选择科目']"
                required
                :loading="loading"
                :disabled="loading"
              ></v-select>
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
            <v-card-text>确定要删除题目 "{{ topicToDelete?.title }}" 吗？此操作无法撤销。</v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="grey darken-1" text @click="closeDeleteDialog">取消</v-btn>
                <v-btn color="error darken-1" text @click="confirmDeleteTopic">确认删除</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

     <!-- 查看题目详情对话框 (简单示例) -->
    <v-dialog v-model="viewDialog" max-width="500px">
        <v-card>
            <v-card-title class="text-h5">题目详情</v-card-title>
             <!-- 3. 更新查看详情对话框 -->
            <v-card-text v-if="viewingTopic">
                <p><strong>ID:</strong> {{ viewingTopic.id }}</p>
                <p><strong>科目:</strong> {{ getSubjectName(viewingTopic.subjectId) }}</p>
                <p><strong>标题:</strong> {{ viewingTopic.title }}</p>
                <p><strong>题目内容:</strong></p>
                <p style="white-space: pre-wrap;">{{ viewingTopic.question }}</p>
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
import { getQuestions, createQuestion, updateQuestion, deleteQuestion } from '../api/question'
import { getSubjects } from '../api/subject' // 1. 引入科目 API

// 2. 定义科目接口
interface Subject {
  id: number;
  name: string;
}

// 3. 定义题目接口 (更新)
interface Topic {
  id: number;
  title: string;
  question: string; // 添加 question 字段
  subjectId: number | null; // 添加 subjectId 字段
}

const router = useRouter()

const subjects = ref<Subject[]>([]) // 4. 存储科目列表

const topics = ref<Topic[]>([]) // 使用正确的 Topic 类型
const loading = ref(false)
const errorMessage = ref<string | null>(null)

// 对话框状态
const dialog = ref(false)
const deleteDialog = ref(false)
const viewDialog = ref(false)
const valid = ref(true) // 表单校验状态
const form = ref<any>(null) // 表单引用

// 编辑/添加相关
const editedIndex = ref(-1) // -1 表示添加，否则为编辑的索引
// 5. 更新编辑/添加的数据模型
const editedTopic = ref<Partial<Topic>>({ title: '', question: '', subjectId: null })
const defaultTopic: Partial<Topic> = { title: '', question: '', subjectId: null }

// 删除相关
const topicToDelete = ref<Topic | null>(null)

// 查看相关
const viewingTopic = ref<Topic | null>(null)


const dialogTitle = computed(() => {
  return editedIndex.value === -1 ? '添加新题目' : '编辑题目'
})

// 6. 获取科目名称的辅助函数
const getSubjectName = (subjectId: number | null): string => {
  if (subjectId === null) return '未指定科目';
  const subject = subjects.value.find(s => s.id === subjectId);
  return subject ? subject.name : '未知科目';
}


// 加载题目数据
const loadTopics = async () => {
  try {
    loading.value = true
    errorMessage.value = null
    topics.value = await getQuestions()
  } catch (error) {
    console.error('加载题目数据失败:', error)
    errorMessage.value = '加载题目数据失败，请稍后重试。'
    topics.value = []
  } finally {
    loading.value = false
  }
}

// 7. 加载科目数据
const loadSubjects = async () => {
  try {
    subjects.value = await getSubjects();
  } catch (error) {
    console.error('加载科目数据失败:', error);
    // 可以在这里设置一个错误消息提示用户
    errorMessage.value = '加载科目列表失败。';
    subjects.value = []; // 清空以防万一
  }
};


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

// 保存题目（添加或编辑）
const saveTopic = async () => {
  const isValid = await form.value?.validate()
  if (!isValid || !isValid.valid) return // 检查校验结果


  try {
    loading.value = true
    errorMessage.value = null
    // 准备基础数据
    const baseTopicData = {
      title: editedTopic.value.title || '',
      question: editedTopic.value.question || '',
      subjectId: editedTopic.value.subjectId
    };

    // 校验 subjectId 是否已选择
    if (baseTopicData.subjectId === null || baseTopicData.subjectId === undefined) {
       errorMessage.value = '请选择一个科目。';
       loading.value = false;
       return;
    }

    // 此时 subjectId 必定是 number 类型
    const finalSubjectId: number = baseTopicData.subjectId;

    if (editedIndex.value > -1) {
      // 编辑
      const currentTopicId = topics.value[editedIndex.value].id;
      // 构造符合 updateQuestion 签名的数据
      const updateData = {
        title: baseTopicData.title,
        question: baseTopicData.question,
        subjectId: finalSubjectId // 显式使用 number 类型
      };
      const updatedTopic = await updateQuestion(currentTopicId, updateData);
      Object.assign(topics.value[editedIndex.value], updatedTopic);
    } else {
      // 添加
      // 重新计算 ID
      const maxId = Math.max(0, ...topics.value.map(t => t.id));
      const newId = maxId + 1;
      // 构造符合 createQuestion 签名的数据
      const createData = {
        id: newId, // 添加 ID
        title: baseTopicData.title,
        question: baseTopicData.question,
        subjectId: finalSubjectId // 显式使用 number 类型
      };
      const newTopic = await createQuestion(createData);
      topics.value.push(newTopic);
    }
    closeDialog()
  } catch (error) {
    console.error('保存题目失败:', error)
    errorMessage.value = '保存题目失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

// 确认删除题目
const confirmDeleteTopic = async () => {
  if (topicToDelete.value) {
    try {
      loading.value = true
      errorMessage.value = null
      await deleteQuestion(topicToDelete.value.id)
      const index = topics.value.indexOf(topicToDelete.value)
      if (index > -1) {
        topics.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除题目失败:', error)
      errorMessage.value = '删除题目失败，请稍后重试。'
    } finally {
      loading.value = false
      closeDeleteDialog()
    }
  }
}

// 查看题目详情
const viewTopicDetails = (topic: Topic) => {
    viewingTopic.value = topic;
    viewDialog.value = true;
}

// 生成范文
const generateEssay = (topic: Topic) => {
  console.log(`为主题 ${topic.id} (${topic.title}) 生成范文`)
  // 导航到 /essay-tools 并传递 topicId 作为参数
  router.push({ name: 'EssayTools', params: { topicId: topic.id } })
}

// 组件挂载时加载数据
onMounted(() => {
  loadTopics()
  loadSubjects() // 7. 调用加载科目函数
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
