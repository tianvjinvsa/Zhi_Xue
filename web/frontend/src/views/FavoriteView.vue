<template>
  <div class="favorite-view">
    <div class="page-header">
      <div class="title-section">
        <h1><el-icon><StarFilled /></el-icon>我的收藏</h1>
        <p class="subtitle">回顾和复习您收藏的重点题目</p>
      </div>
      <div class="header-actions">
        <el-select 
          v-model="filterBank" 
          placeholder="按题库筛选" 
          clearable 
          class="bank-filter"
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
            <el-button type="danger" plain>
              <el-icon><Delete /></el-icon>清空全部
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-overview" v-if="statistics">
      <el-row :gutter="20">
        <el-col :span="4">
          <div class="stat-box total">
            <div class="stat-icon"><Star /></div>
            <div class="stat-data">
              <div class="value">{{ statistics.total }}</div>
              <div class="label">收藏总数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box banks">
            <div class="stat-icon"><Folder /></div>
            <div class="stat-data">
              <div class="value">{{ statistics.bank_count }}</div>
              <div class="label">涉及题库</div>
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box single">
            <div class="stat-icon"><Select /></div>
            <div class="stat-data">
              <div class="value">{{ statistics.type_stats?.single || 0 }}</div>
              <div class="label">单选题</div>
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box multiple">
            <div class="stat-icon"><Finished /></div>
            <div class="stat-data">
              <div class="value">{{ statistics.type_stats?.multiple || 0 }}</div>
              <div class="label">多选题</div>
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box judge">
            <div class="stat-icon"><Check /></div>
            <div class="stat-data">
              <div class="value">{{ statistics.type_stats?.judge || 0 }}</div>
              <div class="label">判断题</div>
            </div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-box fill">
            <div class="stat-icon"><EditPen /></div>
            <div class="stat-data">
              <div class="value">{{ statistics.type_stats?.fill || 0 }}</div>
              <div class="label">填空题</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 收藏列表 -->
    <div v-loading="loading" class="content-section">
      <div v-if="filteredFavorites.length === 0 && !loading" class="empty-state">
        <div class="empty-illustration">
          <el-icon><Star /></el-icon>
        </div>
        <h3>暂无收藏</h3>
        <p>{{ filterBank ? '当前筛选条件下没有收藏的题目' : '还没有收藏任何题目，去题库中看看吧！' }}</p>
        <el-button type="primary" round @click="$router.push('/banks')" v-if="!filterBank">
          浏览题库
        </el-button>
      </div>

      <div v-else class="favorites-grid">
        <el-card 
          v-for="fav in filteredFavorites" 
          :key="fav.question_id" 
          class="favorite-card"
          shadow="hover"
        >
          <div class="card-header">
            <div class="q-meta">
              <el-tag :type="getTypeTagType(fav.question_type)" size="small" effect="dark">
                {{ getTypeName(fav.question_type) }}
              </el-tag>
              <span class="bank-name">
                <el-icon><Folder /></el-icon>
                {{ fav.bank_name }}
              </span>
              <el-rate v-model="fav.difficulty" disabled size="small" />
            </div>
            <div class="q-actions">
              <el-tooltip content="取消收藏" placement="top">
                <el-button 
                  type="warning" 
                  circle 
                  size="small"
                  @click="removeFavorite(fav.question_id)"
                >
                  <el-icon><StarFilled /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>

          <div class="q-content">
            <div class="q-text">{{ fav.question_text }}</div>
            
            <div v-if="fav.options?.length" class="q-options">
              <div 
                v-for="(opt, optIdx) in fav.options" 
                :key="optIdx"
                class="q-option"
                :class="{ 'is-answer': isCorrectOption(fav, optIdx) && fav.showAnswer }"
              >
                <span class="opt-label">{{ String.fromCharCode(65 + optIdx) }}</span>
                <span class="opt-text">{{ opt }}</span>
              </div>
            </div>
          </div>

          <div class="card-footer">
            <div class="footer-left">
              <span class="fav-time">
                <el-icon><Clock /></el-icon>
                收藏于 {{ formatDate(fav.favorite_time) }}
              </span>
            </div>
            <div class="footer-right">
              <el-button 
                :type="fav.showAnswer ? 'info' : 'primary'" 
                link 
                @click="fav.showAnswer = !fav.showAnswer"
              >
                {{ fav.showAnswer ? '隐藏答案' : '查看答案' }}
              </el-button>
            </div>
          </div>

          <el-collapse-transition>
            <div v-if="fav.showAnswer" class="answer-panel">
              <div class="answer-row">
                <strong>正确答案：</strong>
                <span class="answer-text">{{ formatAnswer(fav) }}</span>
              </div>
              <div v-if="fav.explanation" class="analysis-row">
                <strong>解析：</strong>
                <p>{{ fav.explanation }}</p>
              </div>
            </div>
          </el-collapse-transition>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Star, StarFilled, Folder, Select, Finished, 
  Check, EditPen, Clock, Delete 
} from '@element-plus/icons-vue'
import { favoriteApi, bankApi } from '@/api'

const route = useRoute()
const loading = ref(false)
const favorites = ref([])
const banks = ref([])
const statistics = ref(null)
const filterBank = ref('')

const getTypeName = (type) => {
  const names = { single: '单选题', multiple: '多选题', judge: '判断题', fill: '填空题' }
  return names[type] || type
}

const getTypeTagType = (type) => {
  const types = { single: '', multiple: 'success', judge: 'warning', fill: 'info' }
  return types[type] || ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const isCorrectOption = (fav, idx) => {
  const label = String.fromCharCode(65 + idx)
  if (Array.isArray(fav.answer)) {
    return fav.answer.includes(label)
  }
  return fav.answer === label
}

const formatAnswer = (fav) => {
  if (Array.isArray(fav.answer)) return fav.answer.join(', ')
  return fav.answer
}

const filteredFavorites = computed(() => {
  if (!filterBank.value) return favorites.value
  return favorites.value.filter(f => f.bank_id === filterBank.value)
})

const fetchFavorites = async () => {
  loading.value = true
  try {
    const data = await favoriteApi.getAll()
    favorites.value = data.map(f => ({ ...f, showAnswer: false }))
    statistics.value = await favoriteApi.getStatistics()
    // 获取收藏中涉及的题库
    await fetchRelatedBanks()
  } catch (error) {
    console.error('获取收藏失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchRelatedBanks = async () => {
  try {
    // 获取收藏题目涉及的所有题库ID
    const bankIds = [...new Set(favorites.value.map(f => f.bank_id).filter(Boolean))]
    if (bankIds.length === 0) {
      banks.value = []
      return
    }
    // 获取所有题库，只保留相关的
    const allBanks = await bankApi.getAll()
    banks.value = allBanks.filter(b => bankIds.includes(b.id))
  } catch (error) {
    console.error('获取题库失败:', error)
  }
}

const removeFavorite = async (questionId) => {
  try {
    // 直接使用 question_id 调用API
    await favoriteApi.remove(questionId)
    ElMessage.success('已取消收藏')
    fetchFavorites()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const clearAllFavorites = async () => {
  try {
    await favoriteApi.clear()
    ElMessage.success('已清空所有收藏')
    fetchFavorites()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 监听路由进入，自动刷新数据
watch(() => route.path, (newPath) => {
  if (newPath === '/favorites') {
    fetchFavorites()
  }
})

onMounted(() => {
  fetchFavorites()
})
</script>

<style lang="scss" scoped>
.favorite-view {
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
        .el-icon { color: #f7ba2a; }
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
      .bank-filter { width: 200px; }
    }
  }

  .stats-overview {
    margin-bottom: 32px;
    
    .stat-box {
      background: #fff;
      border-radius: 12px;
      padding: 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.04);
      border: 1px solid #f0f0f0;

      .stat-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: #fff;
      }

      &.total .stat-icon { background: linear-gradient(135deg, #f7ba2a, #f9d423); }
      &.banks .stat-icon { background: linear-gradient(135deg, #409eff, #79bbff); }
      &.single .stat-icon { background: linear-gradient(135deg, #67c23a, #95d475); }
      &.multiple .stat-icon { background: linear-gradient(135deg, #b37feb, #d3adf7); }
      &.judge .stat-icon { background: linear-gradient(135deg, #ff7875, #ffa39e); }
      &.fill .stat-icon { background: linear-gradient(135deg, #909399, #c8c9cc); }

      .stat-data {
        .value {
          font-size: 20px;
          font-weight: 700;
          color: #303133;
          line-height: 1.2;
        }
        .label {
          font-size: 12px;
          color: #909399;
          margin-top: 2px;
        }
      }
    }
  }

  .favorites-grid {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .favorite-card {
    border-radius: 16px;
    border: 1px solid #ebeef5;
    transition: all 0.3s;

    &:hover {
      box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .q-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .bank-name {
          font-size: 13px;
          color: #909399;
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }

    .q-content {
      .q-text {
        font-size: 16px;
        color: #303133;
        line-height: 1.6;
        margin-bottom: 20px;
        font-weight: 500;
      }

      .q-options {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 12px;
        margin-bottom: 20px;

        .q-option {
          display: flex;
          align-items: flex-start;
          gap: 8px;
          padding: 12px 16px;
          background: #f8f9fa;
          border-radius: 8px;
          font-size: 14px;
          color: #606266;
          border: 1px solid transparent;

          &.is-answer {
            background: #f0f9eb;
            color: #67c23a;
            border-color: #c2e7b0;
            .opt-label { color: #67c23a; }
          }

          .opt-label {
            font-weight: 700;
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

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 16px;
      border-top: 1px solid #f0f0f0;

      .fav-time {
        font-size: 12px;
        color: #909399;
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .footer-right {
        display: flex;
        gap: 16px;
      }
    }

    .answer-panel {
      margin-top: 16px;
      padding: 16px;
      background: #fdf6ec;
      border-radius: 8px;
      font-size: 14px;

      .answer-row {
        margin-bottom: 12px;
        .answer-text { color: #67c23a; font-weight: 700; font-size: 16px; }
      }

      .analysis-row, .note-row {
        margin-top: 12px;
        p { margin: 4px 0 0; color: #606266; line-height: 1.6; }
      }

      .note-row {
        border-top: 1px dashed #e6a23c;
        padding-top: 12px;
        p { color: #e6a23c; font-style: italic; }
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
</style>
