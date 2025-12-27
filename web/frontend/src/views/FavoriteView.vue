<template>
  <div class="favorite-view">
    <div class="page-header">
      <h1><el-icon><Star /></el-icon>我的收藏</h1>
      <div class="header-actions">
        <el-select 
          v-model="filterBank" 
          placeholder="筛选题库" 
          clearable 
          style="width: 200px; margin-right: 10px;"
        >
          <el-option 
            v-for="bank in banks" 
            :key="bank.id" 
            :label="bank.name" 
            :value="bank.id" 
          />
        </el-select>
        <el-popconfirm 
          title="确定要清空所有收藏吗？此操作不可撤销！" 
          @confirm="clearAllFavorites"
          v-if="favorites.length > 0"
        >
          <template #reference>
            <el-button type="danger">
              <el-icon><Delete /></el-icon>清空收藏
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-cards" v-if="statistics">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <el-icon :size="32" color="#409EFF"><Star /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.total }}</div>
                <div class="stat-label">收藏总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <el-icon :size="32" color="#67C23A"><Folder /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.bank_count }}</div>
                <div class="stat-label">涉及题库</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <el-icon :size="32" color="#E6A23C"><Select /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.type_stats?.single || 0 }}</div>
                <div class="stat-label">单选题</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <el-icon :size="32" color="#F56C6C"><Check /></el-icon>
              <div class="stat-info">
                <div class="stat-value">{{ statistics.type_stats?.judge || 0 }}</div>
                <div class="stat-label">判断题</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 收藏列表 -->
    <div class="card-container">
      <div v-loading="loading">
        <div v-if="filteredFavorites.length === 0 && !loading" class="empty-state">
          <el-icon><StarFilled /></el-icon>
          <p v-if="filterBank">当前筛选条件下没有收藏的题目</p>
          <p v-else>还没有收藏任何题目，去题库中收藏你感兴趣的题目吧！</p>
          <el-button type="primary" @click="$router.push('/banks')" v-if="!filterBank">
            浏览题库
          </el-button>
        </div>

        <div v-else class="favorites-list">
          <el-card 
            v-for="(fav, index) in filteredFavorites" 
            :key="fav.question_id" 
            class="favorite-card"
            shadow="hover"
          >
            <div class="card-header">
              <div class="question-info">
                <el-tag :type="getTypeTagType(fav.question_type)" size="small">
                  {{ getTypeName(fav.question_type) }}
                </el-tag>
                <el-tag type="info" size="small" class="bank-tag">
                  {{ fav.bank_name }}
                </el-tag>
                <el-rate 
                  v-model="fav.difficulty" 
                  disabled 
                  size="small"
                  class="difficulty-rate"
                />
              </div>
              <div class="card-actions">
                <el-button 
                  type="warning" 
                  size="small" 
                  circle
                  @click="removeFavorite(fav.question_id)"
                >
                  <el-icon><Star /></el-icon>
                </el-button>
              </div>
            </div>

            <div class="question-content">
              <span class="question-index">{{ index + 1 }}. </span>
              {{ fav.question_content }}
            </div>

            <!-- 选项 -->
            <div class="options-list" v-if="fav.options && fav.options.length > 0">
              <div 
                v-for="(option, optIndex) in fav.options" 
                :key="optIndex"
                class="option-item"
                :class="{ 'correct-option': isCorrectOption(fav, optIndex) }"
              >
                <span class="option-letter">{{ String.fromCharCode(65 + optIndex) }}.</span>
                <span class="option-text">{{ option }}</span>
              </div>
            </div>

            <!-- 判断题答案 -->
            <div class="judge-answer" v-if="fav.question_type === 'judge'">
              <span class="answer-label">正确答案：</span>
              <el-tag :type="fav.answer ? 'success' : 'danger'">
                {{ fav.answer ? '正确' : '错误' }}
              </el-tag>
            </div>

            <!-- 答案和解析 -->
            <el-collapse v-model="expandedItems" class="answer-collapse">
              <el-collapse-item :name="fav.question_id">
                <template #title>
                  <span class="collapse-title">
                    <el-icon><View /></el-icon>
                    查看答案与解析
                  </span>
                </template>
                <div class="answer-section">
                  <div class="answer-row" v-if="fav.question_type !== 'judge'">
                    <span class="answer-label">正确答案：</span>
                    <span class="answer-value">{{ formatAnswer(fav) }}</span>
                  </div>
                  <div class="explanation-row" v-if="fav.explanation">
                    <span class="explanation-label">解析：</span>
                    <span class="explanation-text">{{ fav.explanation }}</span>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>

            <!-- 标签 -->
            <div class="tags-row" v-if="fav.tags && fav.tags.length > 0">
              <el-tag 
                v-for="tag in fav.tags" 
                :key="tag" 
                size="small" 
                type="info"
                class="question-tag"
              >
                {{ tag }}
              </el-tag>
            </div>

            <div class="card-footer">
              <span class="collect-time">
                收藏于 {{ formatDate(fav.collected_at) }}
              </span>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { favoriteApi } from '@/api'

const loading = ref(false)
const favorites = ref([])
const banks = ref([])
const statistics = ref(null)
const filterBank = ref('')
const expandedItems = ref([])

const filteredFavorites = computed(() => {
  if (!filterBank.value) {
    return favorites.value
  }
  return favorites.value.filter(f => f.bank_id === filterBank.value)
})

const fetchFavorites = async () => {
  loading.value = true
  try {
    const [favData, statsData, banksData] = await Promise.all([
      favoriteApi.getAll().catch(() => []),
      favoriteApi.getStatistics().catch(() => ({ total: 0, bank_count: 0, type_stats: {} })),
      favoriteApi.getBanks().catch(() => [])
    ])
    favorites.value = favData || []
    statistics.value = statsData || { total: 0, bank_count: 0, type_stats: {} }
    banks.value = banksData || []
  } catch (error) {
    console.error('获取收藏失败:', error)
    favorites.value = []
    statistics.value = { total: 0, bank_count: 0, type_stats: {} }
    banks.value = []
  } finally {
    loading.value = false
  }
}

const removeFavorite = async (questionId) => {
  try {
    await favoriteApi.remove(questionId)
    ElMessage.success('已取消收藏')
    fetchFavorites()
  } catch (error) {
    console.error('取消收藏失败:', error)
  }
}

const clearAllFavorites = async () => {
  try {
    await favoriteApi.clearAll()
    ElMessage.success('已清空所有收藏')
    fetchFavorites()
  } catch (error) {
    console.error('清空收藏失败:', error)
  }
}

const getTypeName = (type) => {
  const typeMap = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题',
    fill: '填空题'
  }
  return typeMap[type] || type
}

const getTypeTagType = (type) => {
  const typeMap = {
    single: 'primary',
    multiple: 'success',
    judge: 'warning',
    fill: 'info'
  }
  return typeMap[type] || 'info'
}

const isCorrectOption = (fav, optIndex) => {
  const letter = String.fromCharCode(65 + optIndex)
  if (fav.question_type === 'single') {
    return fav.answer === letter
  } else if (fav.question_type === 'multiple') {
    return Array.isArray(fav.answer) && fav.answer.includes(letter)
  }
  return false
}

const formatAnswer = (fav) => {
  if (fav.question_type === 'multiple' && Array.isArray(fav.answer)) {
    return fav.answer.join('、')
  }
  return fav.answer
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchFavorites()
})
</script>

<style lang="scss" scoped>
.favorite-view {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h1 {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }

    .header-actions {
      display: flex;
      align-items: center;
    }
  }

  .stats-cards {
    margin-bottom: 24px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;

        .stat-info {
          .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: #303133;
          }

          .stat-label {
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }

  .card-container {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    min-height: 400px;
  }

  .empty-state {
    text-align: center;
    padding: 80px 20px;
    color: #909399;

    .el-icon {
      font-size: 64px;
      margin-bottom: 16px;
      color: #dcdfe6;
    }

    p {
      margin-bottom: 20px;
      font-size: 16px;
    }
  }

  .favorites-list {
    .favorite-card {
      margin-bottom: 16px;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .question-info {
          display: flex;
          align-items: center;
          gap: 8px;

          .bank-tag {
            margin-left: 4px;
          }

          .difficulty-rate {
            margin-left: 8px;
          }
        }
      }

      .question-content {
        font-size: 16px;
        line-height: 1.6;
        color: #303133;
        margin-bottom: 16px;

        .question-index {
          font-weight: 600;
          color: #409EFF;
        }
      }

      .options-list {
        margin-bottom: 16px;

        .option-item {
          padding: 8px 12px;
          margin-bottom: 8px;
          border-radius: 4px;
          background: #f5f7fa;
          display: flex;
          align-items: flex-start;

          &.correct-option {
            background: #f0f9eb;
            border: 1px solid #67C23A;
          }

          .option-letter {
            font-weight: 600;
            margin-right: 8px;
            color: #606266;
          }

          .option-text {
            color: #606266;
          }
        }
      }

      .judge-answer {
        margin-bottom: 16px;

        .answer-label {
          font-weight: 500;
          color: #606266;
          margin-right: 8px;
        }
      }

      .answer-collapse {
        margin-bottom: 12px;
        border: none;

        .collapse-title {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          color: #409EFF;
        }

        .answer-section {
          padding: 12px;
          background: #f5f7fa;
          border-radius: 4px;

          .answer-row,
          .explanation-row {
            margin-bottom: 8px;

            &:last-child {
              margin-bottom: 0;
            }
          }

          .answer-label,
          .explanation-label {
            font-weight: 500;
            color: #606266;
          }

          .answer-value {
            color: #67C23A;
            font-weight: 600;
          }

          .explanation-text {
            color: #606266;
            line-height: 1.5;
          }
        }
      }

      .tags-row {
        margin-bottom: 12px;

        .question-tag {
          margin-right: 6px;
        }
      }

      .card-footer {
        display: flex;
        justify-content: flex-end;
        color: #909399;
        font-size: 12px;
      }
    }
  }
}
</style>
