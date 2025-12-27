<template>
  <div class="paper-view">
    <div class="page-header">
      <h1><el-icon><Document /></el-icon>试卷管理</h1>
      <el-button type="primary" @click="$router.push('/papers/create')">
        <el-icon><Plus /></el-icon>生成试卷
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="papers" v-loading="loading" style="width: 100%">
        <el-table-column prop="title" label="试卷名称" min-width="200" />
        <el-table-column prop="question_count" label="题目数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.question_count }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="总分" width="100" align="center">
          <template #default="{ row }">
            <span class="score-text">{{ row.total_score }} 分</span>
          </template>
        </el-table-column>
        <el-table-column prop="time_limit" label="时限" width="100" align="center">
          <template #default="{ row }">
            <span>{{ row.time_limit ? `${row.time_limit} 分钟` : '不限时' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="previewPaper(row)">
                预览
              </el-button>
              <el-button type="success" size="small" @click="startExam(row.id)">
                开始答题
              </el-button>
              <el-popconfirm title="确定删除此试卷？" @confirm="deletePaper(row.id)">
                <template #reference>
                  <el-button type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="papers.length === 0 && !loading" class="empty-state">
        <el-icon><Document /></el-icon>
        <p>暂无试卷，点击上方按钮生成新试卷</p>
      </div>
    </div>

    <!-- 试卷预览对话框 -->
    <el-dialog v-model="previewVisible" title="试卷预览" width="800px" top="5vh">
      <div v-if="previewPaperData" class="paper-preview">
        <div class="preview-header">
          <h2>{{ previewPaperData.title }}</h2>
          <p v-if="previewPaperData.description">{{ previewPaperData.description }}</p>
          <div class="preview-meta">
            <span>总分：{{ previewPaperData.total_score }} 分</span>
            <span>题目数：{{ previewQuestions.length }}</span>
            <span>时限：{{ previewPaperData.time_limit ? `${previewPaperData.time_limit} 分钟` : '不限时' }}</span>
          </div>
        </div>
        
        <el-divider />
        
        <div v-loading="previewLoading" class="preview-questions">
          <div 
            v-for="(question, index) in previewQuestions" 
            :key="question.id"
            class="question-card"
          >
            <div class="question-header">
              <div class="question-info">
                <span class="question-number">{{ index + 1 }}</span>
                <el-tag :class="['question-type-tag', question.type]" size="small">
                  {{ getTypeLabel(question.type) }}
                </el-tag>
              </div>
              <div class="question-actions">
                <el-button 
                  size="small" 
                  :type="previewFavoriteStatus[question.id] ? 'warning' : 'default'"
                  @click="togglePreviewFavorite(question)"
                >
                  <el-icon><Star /></el-icon>
                  {{ previewFavoriteStatus[question.id] ? '已收藏' : '收藏' }}
                </el-button>
              </div>
            </div>
            <div class="question-content">{{ question.question }}</div>
            <div v-if="question.options?.length" class="question-options">
              <div v-for="option in question.options" :key="option" class="option-item">
                {{ option }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="startExam(previewPaperData?.id)">开始答题</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { paperApi, favoriteApi } from '@/api'

const router = useRouter()

const loading = ref(false)
const papers = ref([])
const previewVisible = ref(false)
const previewLoading = ref(false)
const previewPaperData = ref(null)
const previewQuestions = ref([])
const previewFavoriteStatus = ref({})

const getTypeLabel = (type) => {
  const labels = { single: '单选题', multiple: '多选题', judge: '判断题', fill: '填空题' }
  return labels[type] || type
}

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

const previewPaper = async (paper) => {
  previewPaperData.value = paper
  previewVisible.value = true
  previewLoading.value = true
  previewFavoriteStatus.value = {}
  
  try {
    previewQuestions.value = await paperApi.getQuestions(paper.id)
    // 检查收藏状态
    for (const question of previewQuestions.value) {
      try {
        const result = await favoriteApi.check(question.id)
        previewFavoriteStatus.value[question.id] = result.favorited
      } catch (error) {
        previewFavoriteStatus.value[question.id] = false
      }
    }
  } catch (error) {
    console.error('获取试卷题目失败:', error)
  } finally {
    previewLoading.value = false
  }
}

const togglePreviewFavorite = async (question) => {
  try {
    if (previewFavoriteStatus.value[question.id]) {
      await favoriteApi.remove(question.id)
      previewFavoriteStatus.value[question.id] = false
      ElMessage.success('已取消收藏')
    } else {
      // 试卷预览中的题目需要找到对应的题库ID，这里使用题目的 bank_id
      await favoriteApi.add(question.bank_id || 'unknown', question.id)
      previewFavoriteStatus.value[question.id] = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    console.error('收藏操作失败:', error)
  }
}

const startExam = (paperId) => {
  if (paperId) {
    router.push(`/exam/${paperId}`)
  }
}

const deletePaper = async (id) => {
  try {
    await paperApi.delete(id)
    ElMessage.success('删除成功')
    fetchPapers()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

onMounted(() => {
  fetchPapers()
})
</script>

<style lang="scss" scoped>
.paper-view {
  .score-text {
    color: #e6a23c;
    font-weight: 600;
  }
  
  .action-buttons {
    justify-content: center;
  }
  
  .paper-preview {
    .preview-header {
      text-align: center;
      
      h2 {
        margin: 0 0 10px;
        color: #303133;
      }
      
      .preview-meta {
        display: flex;
        justify-content: center;
        gap: 30px;
        color: #909399;
        font-size: 14px;
      }
    }
    
    .preview-questions {
      max-height: 60vh;
      overflow-y: auto;
    }
    
    .question-number {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: #409eff;
      color: #fff;
      font-size: 14px;
      font-weight: 600;
    }
  }
}
</style>
