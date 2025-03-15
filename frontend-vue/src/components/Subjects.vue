<template>
  <div>
    <h1>学科列表</h1>
    <ul>
      <li v-for="subject in subjects" :key="subject.id">
        {{ subject.name }}
        <button @click="editSubject(subject)">编辑</button>
        <button @click="deleteSubject(subject.id)">删除</button>
      </li>
    </ul>
    <button @click="createSubject">添加学科</button>
  </div>
</template>

<script>
import { backendUrl } from '../config.js'

export default {
  name: 'SubjectList',
  data() {
    return {
      subjects: []
    }
  },
  mounted() {
    this.fetchSubjects()
  },
  methods: {
    async fetchSubjects() {
      try {
const response = await fetch(`${backendUrl}subject`)
const data = await response.json()
this.subjects = data.data || []
      } catch (error) {
        console.error('Error fetching subjects:', error)
      }
    },
    async createSubject() {
      const newSubject = { name: prompt('请输入新学科名称') }
      try {
        const response = await fetch(`${backendUrl}subject`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newSubject)
        })
        const createdSubject = await response.json()
        const data = createdSubject.data || createdSubject
this.subjects.push(data)
      } catch (error) {
        console.error('Error creating subject:', error)
      }
    },
    async editSubject(subject) {
      const updatedName = prompt('请输入更新后的学科名称', subject.name)
      if (updatedName) {
        try {
          const response = await fetch(`${backendUrl}subject/${subject.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: updatedName })
          })
console.log('编辑学科前:', this.subjects)
const updatedSubject = await response.json()
console.log('后端返回的更新数据:', updatedSubject)
const actualUpdatedSubject = updatedSubject.data || updatedSubject
console.log('subjects中id的类型:', typeof this.subjects[0].id)
console.log('actualUpdatedSubject中id的类型:', typeof actualUpdatedSubject.id)
const index = this.subjects.findIndex(s => s.id === Number(actualUpdatedSubject.id))
console.log('找到的索引:', index)
if (index !== -1) {
  console.log('更新的数据:', actualUpdatedSubject)
this.subjects.splice(index, 1, actualUpdatedSubject)
console.log('编辑学科后:', this.subjects)
}
        } catch (error) {
          console.error('Error updating subject:', error)
        }
      }
    },
    async deleteSubject(id) {
      if (confirm('确定要删除这个学科吗？')) {
        try {
          await fetch(`${backendUrl}subject/${id}`, { method: 'DELETE' })
          this.subjects = this.subjects.filter(subject => subject.id !== id)
        } catch (error) {
          console.error('Error deleting subject:', error)
        }
      }
    }
  }
}
</script>

<style scoped>
/* Add your styles here */
</style>
