<template>
  <v-container class="fill-height">
    <v-row class="fill-height" no-gutters>
      <v-col cols="12">
        <!-- Loading and Error States -->
        <div v-if="loading" class="text-center pa-5">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <p class="mt-2">加载题目信息...</p>
        </div>
        <v-alert v-else-if="errorMessage" type="error" dense outlined class="mb-4">
          {{ errorMessage }}
        </v-alert>

        <!-- Topic Information and Mode Selection -->
        <div v-else-if="topic">
          <v-card variant="outlined" class="mb-4">
            <v-card-title>{{ topic.title }}</v-card-title>
            <v-card-subtitle>科目: {{ topic.subjectId }}</v-card-subtitle> <!-- TODO: Fetch and display subject name -->
            <v-card-text>
              <strong>题目要求:</strong>
              <p style="white-space: pre-wrap;">{{ topic.question }}</p>
            </v-card-text>
          </v-card>

          <!-- Mode Selection Buttons (only show if mode not selected) -->
          <div v-if="!selectedMode" class="text-center mb-4">
            <v-btn color="primary" @click="selectGenerateMode" class="mr-2">生成范文</v-btn>
            <v-btn color="secondary" @click="selectModifyMode">修改我的文章</v-btn>
          </div>

          <!-- Chat Interface (show only after mode selection) -->
          <v-card v-if="selectedMode" class="d-flex flex-column fill-height chat-card">
            <v-card-title class="flex-shrink-0">
              {{ selectedMode === 'generate' ? '范文生成' : '文章修改' }}
              <v-btn icon="mdi-arrow-left" variant="text" size="small" @click="resetMode" title="返回选择"></v-btn>
            </v-card-title>
            <v-divider></v-divider>

            <!-- Message Display Area -->
            <v-card-text class="flex-grow-1 overflow-y-auto message-area">
              <div v-for="(msg, index) in messages" :key="index" :class="['message-bubble', msg.isUser ? 'user' : 'bot']">
                <p style="white-space: pre-wrap;">{{ msg.text }}</p>
              </div>
               <!-- Placeholder for initial bot message -->
               <div v-if="messages.length === 0" class="message-bubble bot">
                 <p>你好！请问需要我做什么？</p>
                 <p v-if="selectedMode === 'modify'">你可以输入你的文章内容，或者上传图片。</p>
               </div>
            </v-card-text>

            <v-divider></v-divider>

            <!-- Input Area -->
            <v-card-actions class="flex-shrink-0 pa-4">
              <v-textarea
                v-model="userInput"
                label="输入你的想法或文章..."
                rows="2"
                auto-grow
                outlined
                dense
                hide-details
                class="mr-2"
                @keydown.enter.prevent="handleSend"
              ></v-textarea>
               <!-- Upload Button (only for modify mode) -->
               <v-btn
                 v-if="selectedMode === 'modify'"
                 icon="mdi-paperclip"
                 @click="handleImageUpload"
                 title="上传图片"
                 class="mr-2"
               >
               </v-btn>
              <v-btn icon="mdi-send" color="primary" @click="handleSend" :disabled="!userInput.trim()"></v-btn>
            </v-card-actions>
          </v-card>

        </div>

        <!-- No Topic ID State -->
        <div v-else class="text-center pa-5">
           <v-icon size="x-large" color="grey-lighten-1">mdi-help-circle-outline</v-icon>
           <p class="mt-2 text-grey">请先从题目管理页面选择一个题目。</p>
           <v-btn to="/topics" color="primary" class="mt-4">前往题目管理</v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue' // Removed computed as it's not used currently
import { useRoute } from 'vue-router' // Import useRoute
// Use type-only import for the Question interface
import { getQuestion, type Question } from '../api/question'

// Define props to receive topicId from router
const props = defineProps<{
  topicId?: string | number // Make it optional and accept string or number
}>()

const route = useRoute(); // Use route to access params if props are not directly working as expected

const topic = ref<Question | null>(null)
const loading = ref(false)
const errorMessage = ref<string | null>(null)
const selectedMode = ref<'generate' | 'modify' | null>(null) // 'generate', 'modify', or null

// Chat related refs
const messages = ref<{ text: string; isUser: boolean }[]>([])
const userInput = ref('')

// --- Data Loading ---
const loadTopic = async (id: number) => {
  loading.value = true
  errorMessage.value = null
  try {
    topic.value = await getQuestion(id)
    // Initialize chat based on topic?
    // messages.value = [{ text: `开始处理题目: ${topic.value.title}`, isUser: false }];
  } catch (error) {
    console.error('加载题目详情失败:', error)
    errorMessage.value = '加载题目详情失败，请稍后重试或返回题目列表。'
    topic.value = null
  } finally {
    loading.value = false
  }
}

// --- Mode Selection ---
const selectGenerateMode = () => {
  selectedMode.value = 'generate'
  messages.value = [{ text: `好的，我们将基于题目 "${topic.value?.title}" 生成范文。你想从哪方面开始？`, isUser: false }]
  userInput.value = '' // Clear input
}

const selectModifyMode = () => {
  selectedMode.value = 'modify'
   messages.value = [{ text: `好的，我们将基于题目 "${topic.value?.title}" 修改你的文章。请粘贴你的文章内容，或上传图片。`, isUser: false }]
   userInput.value = '' // Clear input
}

const resetMode = () => {
  selectedMode.value = null
  messages.value = [] // Clear chat history
}

// --- Chat Interaction ---
const handleSend = () => {
  if (!userInput.value.trim()) return

  const text = userInput.value.trim()
  messages.value.push({ text, isUser: true })
  userInput.value = ''

  // Placeholder for bot response / autogen call
  setTimeout(() => {
    let botResponse = "正在处理你的请求..."
    if (selectedMode.value === 'generate') {
        botResponse = `(模拟生成范文...) 根据你的输入 "${text}"，关于 "${topic.value?.title}"，可以这样写...`
    } else {
        botResponse = `(模拟修改文章...) 收到你的内容 "${text}"，针对题目 "${topic.value?.title}"，建议修改如下...`
    }
    messages.value.push({ text: botResponse, isUser: false })
  }, 1000)

  // TODO: Integrate with autogen based on selectedMode and topic.value
}

// --- Image Upload ---
const handleImageUpload = () => {
  // Placeholder for file input logic and OCR call
  console.log("触发图片上传");
  alert("图片上传功能待实现");
  // Simulate receiving OCR text
   setTimeout(() => {
    const ocrText = "(模拟OCR识别结果) 这是图片里的文字内容..."
    messages.value.push({ text: `收到图片，识别内容如下：\n${ocrText}`, isUser: false })
    // Optionally add OCR text to user input?
    // userInput.value = ocrText;
  }, 1500)
}


// --- Lifecycle Hook ---
onMounted(() => {
  // Prefer props, but fallback to route params if needed
  const idFromRoute = route.params.topicId as string | undefined;
  const finalTopicId = props.topicId || idFromRoute;

  if (finalTopicId) {
    const numericTopicId = Number(finalTopicId)
    if (!isNaN(numericTopicId)) {
      loadTopic(numericTopicId)
    } else {
       errorMessage.value = '无效的题目 ID。'
       console.error("Invalid topic ID:", finalTopicId);
    }
  } else {
    // No topic ID provided, the template will show the message to select a topic.
    console.log("No topic ID provided in route.");
  }
})
</script>

<style scoped>
.fill-height {
  height: calc(100vh - 64px - 48px); /* Adjust based on app bar and footer height */
  max-height: calc(100vh - 64px - 48px);
}

.chat-card {
  display: flex;
  flex-direction: column;
  height: 100%; /* Ensure card takes full height */
   max-height: 100%;
}

.message-area {
  flex-grow: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px; /* Add space between bubbles */
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 18px;
  max-width: 80%;
  word-wrap: break-word; /* Ensure long words break */
}

.message-bubble.user {
  background-color: #e3f2fd; /* Light blue for user */
  color: #1e88e5;
  align-self: flex-end;
  border-bottom-right-radius: 4px; /* Flat corner */
}

.message-bubble.bot {
  background-color: #f5f5f5; /* Light grey for bot */
  color: #424242;
  align-self: flex-start;
  border-bottom-left-radius: 4px; /* Flat corner */
}

.v-card-actions {
  background-color: #fff; /* Ensure input area has a background */
  border-top: 1px solid #e0e0e0;
}
</style>
