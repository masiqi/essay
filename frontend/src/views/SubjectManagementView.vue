<template>
  <v-container>
    <v-toolbar flat color="transparent">
      <v-toolbar-title class="text-h5">学科管理</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn color="primary" @click="openAddDialog">
        <v-icon start>mdi-plus</v-icon>
        添加学科
      </v-btn>
    </v-toolbar>

    <v-alert v-if="errorMessage" type="error" dense outlined class="mb-4">
      {{ errorMessage }}
    </v-alert>

    <v-data-table
      :headers="headers"
      :items="subjects"
      :loading="loading"
      class="elevation-1"
      item-value="id"
    >
      <template v-slot:item.actions="{ item }">
        <v-icon small class="mr-2" @click="openEditDialog(item)">mdi-pencil</v-icon>
        <v-icon small @click="openDeleteDialog(item)">mdi-delete</v-icon>
      </template>
      <template v-slot:no-data>
        <v-alert :value="true" color="info" icon="mdi-information-outline">
          暂无学科数据。
        </v-alert>
      </template>
       <template v-slot:loading>
        <v-skeleton-loader type="table-row@5"></v-skeleton-loader>
      </template>
    </v-data-table>

    <!-- 添加/编辑学科对话框 -->
    <v-dialog v-model="dialog" persistent max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ dialogTitle }}</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-form ref="form" v-model="valid" lazy-validation>
              <v-text-field
                v-model="editedSubject.name"
                label="学科名称*"
                :rules="[(v: string) => !!v || '学科名称不能为空']"
                required
              ></v-text-field>
            </v-form>
          </v-container>
          <small>*表示必填字段</small>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="closeDialog">取消</v-btn>
          <v-btn color="blue darken-1" :disabled="!valid" text @click="saveSubject">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 删除确认对话框 -->
    <v-dialog v-model="deleteDialog" persistent max-width="400px">
        <v-card>
            <v-card-title class="text-h5">确认删除</v-card-title>
            <v-card-text>确定要删除学科 "{{ subjectToDelete?.name }}" 吗？此操作无法撤销。</v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="grey darken-1" text @click="closeDeleteDialog">取消</v-btn>
                <v-btn color="error darken-1" text @click="confirmDeleteSubject">确认删除</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getSubjects, createSubject, updateSubject, deleteSubject } from '../api/subject'
import type { Subject } from '../api/subject'

// 表格 Headers
const headers = ref([
  { title: 'ID', key: 'id', align: 'start', sortable: true },
  { title: '学科名称', key: 'name', sortable: true },
  { title: '操作', key: 'actions', sortable: false, align: 'end' },
])

const subjects = ref<Subject[]>([])
const loading = ref(false)
const errorMessage = ref<string | null>(null)

// 对话框状态
const dialog = ref(false)
const deleteDialog = ref(false)
const valid = ref(true) // 表单校验状态
const form = ref<any>(null) // 表单引用

// 编辑/添加相关
const editedIndex = ref(-1) // -1 表示添加，否则为编辑的索引
const editedSubject = ref<Partial<Subject>>({ name: '' }) // 使用 Partial 允许 id 为空
const defaultSubject: Partial<Subject> = { name: '' }

// 删除相关
const subjectToDelete = ref<Subject | null>(null)

const dialogTitle = computed(() => {
  return editedIndex.value === -1 ? '添加新学科' : '编辑学科'
})

// 加载学科数据
const loadSubjects = async () => {
  loading.value = true
  errorMessage.value = null
  try {
    subjects.value = await getSubjects()
  } catch (error) {
    console.error('加载学科数据失败:', error)
    errorMessage.value = '加载学科数据失败，请稍后重试。'
    subjects.value = []
  } finally {
    loading.value = false
  }
}

// 打开添加对话框
const openAddDialog = () => {
  editedIndex.value = -1
  editedSubject.value = { ...defaultSubject }
  dialog.value = true
  form.value?.resetValidation() // 重置校验状态
}

// 打开编辑对话框
const openEditDialog = (subject: Subject) => {
  editedIndex.value = subjects.value.findIndex(s => s.id === subject.id)
  editedSubject.value = { ...subject } // 复制一份，避免直接修改原始数据
  dialog.value = true
  form.value?.resetValidation()
}

// 打开删除确认对话框
const openDeleteDialog = (subject: Subject) => {
  subjectToDelete.value = subject
  deleteDialog.value = true
}

// 关闭添加/编辑对话框
const closeDialog = () => {
  dialog.value = false
  // 延迟重置表单
  setTimeout(() => {
    editedSubject.value = { ...defaultSubject }
    editedIndex.value = -1
    form.value?.resetValidation()
  }, 300)
}

// 关闭删除对话框
const closeDeleteDialog = () => {
  deleteDialog.value = false
  setTimeout(() => {
    subjectToDelete.value = null
  }, 300)
}

// 保存学科（添加或编辑）
const saveSubject = async () => {
  const isValid = await form.value?.validate()
  if (!isValid || !isValid.valid) return // 检查校验结果

  loading.value = true // 开始加载状态
  errorMessage.value = null
  try {
    if (editedIndex.value > -1 && editedSubject.value.id) {
      // 编辑
      const updated = await updateSubject(editedSubject.value.id, { name: editedSubject.value.name || '' })
      Object.assign(subjects.value[editedIndex.value], updated)
    } else {
      // 添加
      const newSubject = await createSubject({ name: editedSubject.value.name || '' })
      subjects.value.push(newSubject)
    }
    closeDialog()
  } catch (error) {
    console.error('保存学科失败:', error)
    errorMessage.value = '保存学科失败，请稍后重试。'
  } finally {
    loading.value = false // 结束加载状态
  }
}

// 确认删除学科
const confirmDeleteSubject = async () => {
  if (subjectToDelete.value) {
    loading.value = true // 开始加载状态
    errorMessage.value = null
    try {
      await deleteSubject(subjectToDelete.value.id)
      const index = subjects.value.findIndex(s => s.id === subjectToDelete.value!.id)
      if (index > -1) {
        subjects.value.splice(index, 1)
      }
    } catch (error) {
      console.error('删除学科失败:', error)
      errorMessage.value = '删除学科失败，请稍后重试。'
    } finally {
      loading.value = false // 结束加载状态
      closeDeleteDialog()
    }
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadSubjects()
})

</script>

<style scoped>
/* 可以添加特定于此视图的样式 */
</style>
