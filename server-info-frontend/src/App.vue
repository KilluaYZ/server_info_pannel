<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

interface ServerInfo {
  operating_system: string
  cpu_usage: number
  memory_usage: {
    total: number
    used: number
  }
  disk_usage: {
    total: number
    used: number
  }
  uptime: {
    day: number
    hour: number
    minute: number
    second: number
  }
  word: {
    content: string
    author: string
  }
}

const serverInfo = ref<ServerInfo | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const fetchServerInfo = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await fetch('/api/server-info')
    // const response = await fetch('http://127.0.0.1:5000/api/server-info')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    serverInfo.value = await response.json()
  } catch (err) {
    error.value = '无法获取服务器信息，请确保后端服务正在运行'
    console.error('Error fetching server info:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchServerInfo()
})
</script>

<template>
  <div class="app">
     <header>
      <h1>已经正常上线 {{ serverInfo ? serverInfo.uptime.day : 0 }} 天</h1>
    </header>
    <main class="main-content">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p style="color: #fff; font-size: clamp(1rem, 3vw, 1.5rem);">欢迎来到ISER实验室知识库...</p>
      </div>

      <div v-else-if="error" class="error">
        <p style="color: #fff; font-size: clamp(1rem, 3vw, 1.5rem);">{{ error }}</p>
        <button @click="fetchServerInfo" class="retry-btn">重试</button>
      </div>

      <div v-else-if="serverInfo" class="server-info">

        <div class="quote-section">
          <div class="quote-card">
            <span class="quote typing-animation">{{ serverInfo.word.content }}</span>
            <span class="author">—— {{ serverInfo.word.author }}</span>
          </div>
        </div>

        <div class="system-info-footer">
          <p>系统: {{ serverInfo.operating_system }} | CPU: {{ serverInfo.cpu_usage.toFixed(2) }}% | 内存: {{ (serverInfo.memory_usage.used / 1024).toFixed(2) }}G/{{ (serverInfo.memory_usage.total / 1024).toFixed(2) }}G | 磁盘: {{ serverInfo.disk_usage.used.toFixed(2) }}G/{{ serverInfo.disk_usage.total.toFixed(2) }}G | 运行: {{ serverInfo.uptime.day }}天{{ serverInfo.uptime.hour }}时{{ serverInfo.uptime.minute }}分</p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app {
  width: 100%;
  height: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  background: #f8f9fa url('/HitokotoBanner04-PC.jpg') center/cover no-repeat;
}

header {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: fit-content;
}

header h1 {
  color:rgb(255, 255, 255);
  font-size: clamp(1rem, 5vw, 3rem);
  width: fit-content;
  height: fit-content;
}

.main-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  justify-content: flex-start;
  position: relative;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes typing {
  from { width: 0 }
  to { width: 100% }
}

@keyframes blink-caret {
  from, to { border-color: transparent }
  50% { border-color: #2c3e50 }
}

.error {
  text-align: center;
  padding: 2rem;
  color: #e74c3c;
}

.retry-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.quote-section {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  z-index: 10;
}

.quote-card {
  text-align: center;
  max-width: 80%;
  padding: 1rem;
}

.quote {
  line-height: 1.6;
  font-weight: bold;
  letter-spacing: 1px;
  word-wrap: break-word;
  white-space: normal;
}

.author {
  font-size: clamp(0.8rem, 2vw, 1.5rem);
  font-style: italic;
  text-align: right;
}

.quote span {
  height: fit-content;
  margin: 0;
  padding: 0;
}

.author, .quote {
  color:rgb(255, 255, 255);
}

.system-info-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.9);
  padding: 0.5rem;
  text-align: center;
  font-size: clamp(0.6rem, 1.5vw, 0.8rem);
  color: #7f8c8d;
  border-top: 1px solid #e0e0e0;
}

.server-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3498db;
}

.quote-card {
  display: flex;
  border: 1px solid rgba(255, 255, 255, 0.2);
  flex-direction: column;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.info-card h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.info-value {
  font-size: 1.2rem;
  color: #34495e;
  margin-bottom: 1rem;
  font-weight: 500;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2980b9);
  transition: width 0.3s ease;
}

.progress-fill.high-usage {
  background: linear-gradient(90deg, #e74c3c, #c0392b);
}

.quote {
  font-style: italic;
  font-size: clamp(1rem, 5vw, 3rem);
  margin: 0;
}

.refresh-btn {
  grid-column: 1 / -1;
  background: #27ae60;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1rem;
  margin-top: 1rem;
}

.refresh-btn:hover {
  background: #229954;
}

/* @media (max-width: 768px) {
  .app {
    padding: 1rem;
  }
  
  header h1 {
    font-size: 2rem;
  }
  
  .server-info {
    grid-template-columns: 1fr;
  }
} */
</style>
