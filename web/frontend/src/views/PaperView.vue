<template>
  <div class="paper-view">
    <div class="page-header">
      <div class="title-section">
        <h1><el-icon><Document /></el-icon>试卷管理</h1>
        <p class="subtitle">管理已生成的试卷，查看详情或开始练习</p>
      </div>
      <div class="header-actions">
        <el-select 
          v-model="filterBank" 
          placeholder="按题库筛选" 
          clearable 
          class="bank-filter"
        >
          <el-option 
            v-for="bank in relatedBanks" 
            :key="bank.id" 
            :label="bank.name" 
            :value="bank.id" 
          />
        </el-select>
        <el-button type="primary" @click="$router.push('/papers/create')" class="create-btn">
          <el-icon><Plus /></el-icon>生成新试卷
        </el-button>
      </div>
    </div>

    <div v-loading="loading" class="content-section">
      <div v-if="filteredPapers.length > 0" class="papers-grid">
        <el-card 
          v-for="paper in filteredPapers" 
          :key="paper.id" 
          class="paper-card" 
          shadow="hover"
        >
          <div class="paper-card-header">
            <div class="paper-icon">
              <el-icon><Files /></el-icon>
            </div>
            <div class="paper-info">
              <h3 class="paper-title">{{ paper.title }}</h3>
              <div class="paper-meta">
                <span class="meta-item">
                  <el-icon><Calendar /></el-icon>
                  {{ formatDate(paper.created_at) }}
                </span>
              </div>
            </div>
          </div>

          <div class="paper-stats">
            <div class="stat-item">
              <div class="stat-value">{{ paper.question_count }}</div>
              <div class="stat-label">题目数量</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-value">{{ paper.total_score }}</div>
              <div class="stat-label">试卷总分</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-value">{{ paper.time_limit || '∞' }}</div>
              <div class="stat-label">限时(分)</div>
            </div>
          </div>

          <div class="paper-actions">
            <el-button type="primary" plain @click="previewPaper(paper)">
              预览试卷
            </el-button>
            <el-button type="primary" @click="startExam(paper.id)">
              开始答题
            </el-button>
            <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, paper)">
              <el-button class="more-btn">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="delete" class="delete-item">
                    <el-icon><Delete /></el-icon>删除试卷
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-card>
      </div>

      <div v-else-if="!loading && papers.length === 0" class="empty-state">
        <div class="empty-illustration">
          <el-icon><Document /></el-icon>
        </div>
        <h3>暂无试卷</h3>
        <p>您还没有生成过试卷，快去创建一个吧！</p>
        <el-button type="primary" round @click="$router.push('/papers/create')">
          立即生成
        </el-button>
      </div>
      <div v-else-if="!loading && filteredPapers.length === 0" class="empty-state">
        <div class="empty-illustration">
          <el-icon><Document /></el-icon>
        </div>
        <h3>筛选结果为空</h3>
        <p>当前筛选条件下没有找到相关试卷</p>
        <el-button type="primary" round @click="filterBank = ''">
          清除筛选
        </el-button>
      </div>
    </div>

    <!-- 试卷预览对话框 -->
    <el-dialog 
      v-model="previewVisible" 
      :title="previewPaperData?.title" 
      width="850px" 
      top="5vh"
      class="paper-preview-dialog"
      destroy-on-close
    >
      <div v-if="previewPaperData" class="paper-preview-content">
        <div class="preview-info-bar">
          <el-tag type="info" effect="plain">总分：{{ previewPaperData.total_score }}分</el-tag>
          <el-tag type="info" effect="plain">题目：{{ previewQuestions.length }}题</el-tag>
          <el-tag type="info" effect="plain">限时：{{ previewPaperData.time_limit ? `${previewPaperData.time_limit}分钟` : '不限时' }}</el-tag>
        </div>
        
        <div v-loading="previewLoading" class="preview-questions-list">
          <div 
            v-for="(question, index) in previewQuestions" 
            :key="question.id"
            class="preview-question-item"
          >
            <div class="q-header">
              <span class="q-index">{{ index + 1 }}.</span>
              <el-tag size="small" :type="getTypeTag(question.type)" effect="dark">
                {{ getTypeLabel(question.type) }}
              </el-tag>
              <!-- 预览模式不显示收藏按钮 -->
            </div>
            <div class="q-body">
              <div class="q-text">{{ question.question }}</div>
              <div v-if="question.options?.length" class="q-options">
                <div 
                  v-for="(opt, optIdx) in question.options" 
                  :key="optIdx"
                  class="q-option"
                >
                  <span class="opt-label">{{ String.fromCharCode(65 + optIdx) }}.</span>
                  <span class="opt-text">{{ opt }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="previewVisible = false">关闭预览</el-button>
          <el-button type="primary" @click="startExam(previewPaperData?.id)">
            立即开始答题
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { paperApi, favoriteApi, bankApi } from '@/api'
import { 
  Document, Plus, Files, Calendar, MoreFilled, 
  Delete, Star, StarFilled 
} from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const papers = ref([])
const allBanks = ref([])
const filterBank = ref('')
const previewVisible = ref(false)
const previewLoading = ref(false)
const previewPaperData = ref(null)
const previewQuestions = ref([])
const previewFavoriteStatus = ref({})

// 计算相关题库（只显示试卷来源涉及的题库）
const relatedBanks = computed(() => {
  const bankIds = new Set()
  papers.value.forEach(paper => {
    if (paper.source_banks) {
      paper.source_banks.forEach(bankId => bankIds.add(bankId))
    }
  })
  return allBanks.value.filter(b => bankIds.has(b.id))
})

// 筛选后的试卷
const filteredPapers = computed(() => {
  if (!filterBank.value) return papers.value
  return papers.value.filter(paper => 
    paper.source_banks && paper.source_banks.includes(filterBank.value)
  )
})

const getTypeLabel = (type) => {
  const labels = { single: '单选题', multiple: '多选题', judge: '判断题', fill: '填空题' }
  return labels[type] || type
}

const getTypeTag = (type) => {
  const tags = { single: '', multiple: 'success', judge: 'warning', fill: 'info' }
  return tags[type] || ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
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

const handleCommand = (command, paper) => {
  if (command === 'delete') {
    deletePaper(paper.id)
  }
}

const deletePaper = (id) => {
  ElMessageBox.confirm('确定要删除这份试卷吗？此操作不可恢复。', '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
    buttonSize: 'default'
  }).then(async () => {
    try {
      await paperApi.delete(id)
      ElMessage.success('试卷已删除')
      fetchPapers()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const previewPaper = async (paper) => {
  previewPaperData.value = paper
  previewVisible.value = true
  previewLoading.value = true
  previewFavoriteStatus.value = {}
  
  try {
    const questions = await paperApi.getQuestions(paper.id)
    previewQuestions.value = questions
    
    // 检查收藏状态
    const favorites = await favoriteApi.getAll()
    questions.forEach(q => {
      previewFavoriteStatus.value[q.id] = favorites.some(f => f.question_id === q.id)
    })
  } catch (error) {
    console.error('获取试卷详情失败:', error)
    ElMessage.error('获取试卷详情失败')
  } finally {
    previewLoading.value = false
  }
}

const togglePreviewFavorite = async (question) => {
  const isFav = previewFavoriteStatus.value[question.id]
  try {
    if (isFav) {
      const favorites = await favoriteApi.getAll()
      const fav = favorites.find(f => f.question_id === question.id)
      if (fav) await favoriteApi.remove(fav.id)
    } else {
      await favoriteApi.add({
        question_id: question.id,
        bank_id: question.bank_id,
        note: ''
      })
    }
    previewFavoriteStatus.value[question.id] = !isFav
    ElMessage.success(isFav ? '已取消收藏' : '收藏成功')
  } catch (error) {
    console.error('操作失败:', error)
  }
}

const startExam = (id) => {
  if (!id) return
  router.push(`/exam/${id}`)
}

const fetchBanks = async () => {
  try {
    allBanks.value = await bankApi.getAll()
  } catch (error) {
    console.error('获取题库失败:', error)
  }
}

onMounted(() => {
  fetchPapers()
  fetchBanks()
})
</script>

<style lang="scss" scoped>
.paper-view {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 32px;

    .title-section {
      h1 {
        margin: 0;
        font-size: 28px;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #1a1a1a;
        .el-icon { color: #409eff; }
      }
      .subtitle {
        margin: 8px 0 0;
        color: #909399;
        font-size: 14px;
      }
    }

    .header-actions {
      display: flex;
      gap: 12px;
      align-items: center;

      .bank-filter {
        width: 180px;
      }
    }

    .create-btn {
      padding: 12px 24px;
      font-weight: 600;
      border-radius: 8px;
    }
  }

  .papers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px;
  }

  .paper-card {
    border-radius: 16px;
    border: 1px solid #ebeef5;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 12px 24px rgba(0,0,0,0.08);
    }

    .paper-card-header {
      display: flex;
      gap: 16px;
      margin-bottom: 20px;

      .paper-icon {
        width: 48px;
        height: 48px;
        background: #ecf5ff;
        color: #409eff;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
      }

      .paper-info {
        flex: 1;
        .paper-title {
          margin: 0;
          font-size: 18px;
          color: #303133;
          line-height: 1.4;
        }
        .paper-meta {
          margin-top: 4px;
          font-size: 13px;
          color: #909399;
          display: flex;
          align-items: center;
          gap: 12px;
          .meta-item {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }
    }

    .paper-stats {
      background: #f8f9fa;
      border-radius: 12px;
      padding: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;

      .stat-item {
        text-align: center;
        flex: 1;
        .stat-value {
          font-size: 18px;
          font-weight: 700;
          color: #303133;
        }
        .stat-label {
          font-size: 12px;
          color: #909399;
          margin-top: 2px;
        }
      }

      .stat-divider {
        width: 1px;
        height: 24px;
        background: #dcdfe6;
      }
    }

    .paper-actions {
      display: flex;
      gap: 10px;
      
      .el-button {
        flex: 1;
        border-radius: 8px;
      }

      .more-btn {
        flex: 0 0 40px;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 80px 0;
    background: #fff;
    border-radius: 16px;
    .empty-illustration {
      font-size: 64px;
      color: #f0f2f5;
      margin-bottom: 16px;
    }
    h3 { color: #303133; margin-bottom: 8px; }
    p { color: #909399; margin-bottom: 24px; }
  }
}

.paper-preview-dialog {
  :deep(.el-dialog__body) {
    padding: 0;
  }

  .paper-preview-content {
    max-height: 70vh;
    overflow-y: auto;
    padding: 24px;

    .preview-info-bar {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      padding: 16px;
      background: #f8f9fa;
      border-radius: 8px;
    }

    .preview-question-item {
      margin-bottom: 24px;
      padding-bottom: 24px;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .q-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;

        .q-index {
          font-weight: 700;
          color: #303133;
        }

        .q-actions {
          margin-left: auto;
        }
      }

      .q-body {
        .q-text {
          font-size: 16px;
          color: #303133;
          line-height: 1.6;
          margin-bottom: 16px;
        }

        .q-options {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 12px;

          .q-option {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            padding: 10px 16px;
            background: #f8f9fa;
            border-radius: 6px;
            font-size: 14px;
            color: #606266;

            .opt-label {
              font-weight: 600;
              color: #409eff;
              flex-shrink: 0;
            }

            .opt-text {
              word-break: break-word;
              overflow-wrap: break-word;
              line-height: 1.5;
            }
          }
        }
      }
    }
  }
}

.delete-item {
  color: #f56c6c !important;
  &:hover {
    background-color: #fef0f0 !important;
  }
}
</style>
