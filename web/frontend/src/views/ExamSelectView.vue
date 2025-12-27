<template>
  <div class="exam-select-view">
    <div class="page-header">
      <h1><el-icon><Edit /></el-icon>选择试卷开始答题</h1>
    </div>

    <div class="papers-grid">
      <div 
        v-for="paper in papers" 
        :key="paper.id" 
        class="paper-card"
        @click="startExam(paper.id)"
      >
        <div class="paper-icon">
          <el-icon :size="40"><Document /></el-icon>
        </div>
        <div class="paper-info">
          <h3>{{ paper.title }}</h3>
          <p class="description">{{ paper.description || '暂无描述' }}</p>
          <div class="meta">
            <span><el-icon><List /></el-icon>{{ paper.question_count }} 道题</span>
            <span><el-icon><Coin /></el-icon>{{ paper.total_score }} 分</span>
            <span><el-icon><Clock /></el-icon>{{ paper.time_limit ? `${paper.time_limit} 分钟` : '不限时' }}</span>
          </div>
        </div>
        <el-button type="primary" class="start-btn">开始答题</el-button>
      </div>
    </div>

    <div v-if="papers.length === 0 && !loading" class="empty-state">
      <el-icon><Document /></el-icon>
      <p>暂无可用试卷</p>
      <el-button type="primary" @click="$router.push('/papers/create')">
        去生成试卷
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { paperApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const papers = ref([])

const fetchPapers = async () => {
  loading.value = true
  try {
    papers.value = await paperApi.getAll()
  } catch (error) {
    console.error('获取试卷列表失败:', error)
  } finally {
    loading.value = false
  }
}

const startExam = (paperId) => {
  router.push(`/exam/${paperId}`)
}

onMounted(() => {
  fetchPapers()
})
</script>

<style lang="scss" scoped>
.exam-select-view {
  .papers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
  }
  
  .paper-card {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    flex-direction: column;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    
    .paper-icon {
      width: 70px;
      height: 70px;
      border-radius: 12px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      margin-bottom: 16px;
    }
    
    .paper-info {
      flex: 1;
      
      h3 {
        margin: 0 0 8px;
        font-size: 18px;
        color: #303133;
      }
      
      .description {
        margin: 0 0 12px;
        color: #909399;
        font-size: 14px;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      
      .meta {
        display: flex;
        gap: 20px;
        color: #606266;
        font-size: 14px;
        
        span {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
    
    .start-btn {
      margin-top: 16px;
      width: 100%;
    }
  }
}
</style>
