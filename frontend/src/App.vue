<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="bg-white p-8 rounded-xl shadow-lg w-full max-w-xl space-y-6">
      <h1 class="text-2xl font-bold text-center text-gray-800">📄 Local RAG with Qwen</h1>

      <input
        v-model="apiKey"
        placeholder="🔑 输入你的 API Token"
        class="w-full border border-gray-300 rounded px-4 py-2 focus:ring focus:ring-blue-200"
      />
      <textarea
        v-model="query"
        placeholder="💬 输入你的问题..."
        rows="4"
        class="w-full border border-gray-300 rounded px-4 py-2 focus:ring focus:ring-blue-200 resize-none"
      ></textarea>

      <button
        @click="submitQuery"
        class="w-full bg-blue-600 text-white font-semibold px-4 py-2 rounded hover:bg-blue-700 transition"
        :disabled="loading"
      >
        🚀 {{ loading ? '正在查询...' : '提交查询' }}
      </button>

      <div v-if="loading" class="text-blue-600 text-sm animate-pulse">🌀 正在生成，请稍候...</div>

      <div v-if="response" class="mt-4 bg-gray-100 p-4 rounded border text-gray-800">
        <strong>📣 回答：</strong>
        <p class="whitespace-pre-line mt-2">{{ response }}</p>
      </div>

      <div v-if="references.length" class="mt-4 bg-yellow-50 p-4 rounded border border-yellow-200">
        <strong>📚 使用的参考内容：</strong>
        <ul class="list-disc pl-6 mt-2 text-sm text-gray-600 space-y-2">
          <li v-for="(ref, i) in references" :key="i">{{ ref }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const apiKey = ref('')
const query = ref('')
const response = ref('')
const references = ref([])
const loading = ref(false)

const submitQuery = async () => {
  if (!apiKey.value || !query.value) {
    alert('请填写 API Key 和问题')
    return
  }

  loading.value = true
  response.value = ''
  references.value = []

  try {
    const res = await axios.post('http://localhost:8000/api/query', {
      api_key: apiKey.value,
      query: query.value
    })
    response.value = res.data.answer
    references.value = res.data.references || []
  } catch (e) {
    response.value = '❌ 查询失败，请检查 API Key 或后端服务'
  }

  loading.value = false
}
</script>
