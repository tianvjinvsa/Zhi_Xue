<template>
  <div class="result-view">
    <div class="page-header">
      <h1><el-icon><DataAnalysis /></el-icon>成绩查看</h1>
      <div class="header-actions">
        <el-button type="primary" plain @click="fetchResults">
          <el-icon><Refresh /></el-icon>刷新
        </el-button>
      </div>
    </div>

    <!-- 概览统计 -->
    <div class="stats-overview" v-if="results.length > 0">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-box total">
            <div class="stat-icon"><Document /></div>
            <div class="stat-data">
              <div class="value">{{ results.length }}</div>
              <div class="label">累计答题</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-box average">
            <div class="stat-icon"><PieChart /></div>
            <div class="stat-data">
              <div class="value">{{ averageAccuracy }}%</div>
              <div class="label">平均正确率</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-box highest">
            <div class="stat-icon"><Trophy /></div>
            <div class="stat-data">
              <div class="value">{{ highestScore }}</div>
              <div class="label">最高得分</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-box time">
            <div class="stat-icon"><Timer /></div>
            <div class="stat-data">
              <div class="value">{{ totalTimeSpent }}</div>
              <div class="label">累计用时</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="card-container">
      <el-table 
        :data="results" 
        v-loading="loading" 
        style="width: 100%"
        :header-cell-style="{ background: '#f8f9fa', color: '#606266', fontWeight: '600' }"
      >
        <el-table-column prop="paper_title" label="试卷名称" min-width="200">
          <template #default="{ row }">
            <div class="paper-title-cell">
              <el-icon><Document /></el-icon>
              <span>{{ row.paper_title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="得分" width="150" align="center">
          <template #default="{ row }">
            <div class="score-cell">
              <span class="user-score" :class="getScoreClass(row)">{{ row.user_score }}</span>
              <span class="separator">/</span>
              <span class="total-score">{{ row.total_score }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="正确率" width="120" align="center">
          <template #default="{ row }">
            <el-progress 
              type="circle" 
              :percentage="Math.round(row.user_score / row.total_score * 100)" 
              :width="45"
              :stroke-width="4"
              :color="getProgressColor(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="答题时间" width="200">
          <template #default="{ row }">
            <div class="time-cell">
              <div class="date">{{ formatDate(row.start_time) }}</div>
              <div class="duration">{{ getDuration(row.start_time, row.end_time) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" link @click="viewDetail(row.id)">
                查看详情
              </el-button>
              <el-divider direction="vertical" />
              <el-popconfirm title="确定删除此记录？" @confirm="deleteResult(row.id)">
                <template #reference>
                  <el-button type="danger" link>删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="results.length === 0 && !loading" class="empty-state">
        <div class="empty-illustration">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <p>暂无答题记录，快去挑战一份试卷吧！</p>
        <el-button type="primary" round @click="$router.push('/exam')">
          立即去答题
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { resultApi } from '@/api'
import { DataAnalysis, Document, Refresh, PieChart, Trophy, Timer } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const results = ref([])

// 统计计算
const averageAccuracy = computed(() => {
  if (results.value.length === 0) return 0
  const totalAccuracy = results.value.reduce((acc, curr) => {
    return acc + (curr.user_score / curr.total_score)
  }, 0)
  return Math.round((totalAccuracy / results.value.length) * 100)
})

const highestScore = computed(() => {
  if (results.value.length === 0) return 0
  return Math.max(...results.value.map(r => r.user_score))
})

const totalTimeSpent = computed(() => {
  if (results.value.length === 0) return '0分'
  let totalSeconds = 0
  results.value.forEach(r => {
    if (r.start_time && r.end_time) {
      totalSeconds += (new Date(r.end_time) - new Date(r.start_time)) / 1000
    }
  })
  const minutes = Math.floor(totalSeconds / 60)
  if (minutes < 60) return `${minutes}分`
  return `${Math.floor(minutes / 60)}时${minutes % 60}分`
})

const getScoreClass = (row) => {
  const ratio = row.user_score / row.total_score
  if (ratio >= 0.9) return 'excellent'
  if (ratio >= 0.6) return 'pass'
  return 'fail'
}

const getProgressColor = (row) => {
  const ratio = row.user_score / row.total_score
  if (ratio >= 0.9) return '#67c23a'
  if (ratio >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getDuration = (start, end) => {
  if (!start || !end) return '-'
  const duration = (new Date(end) - new Date(start)) / 1000
  const minutes = Math.floor(duration / 60)
  const seconds = Math.floor(duration % 60)
  return `${minutes}分${seconds}秒`
}

const fetchResults = async () => {
  loading.value = true
  try {
    results.value = await resultApi.getAll()
  } catch (error) {
    console.error('获取成绩列表失败:', error)
  } finally {
    loading.value = false
  }
}

const viewDetail = (id) => {
  router.push(`/results/${id}`)
}

const deleteResult = async (id) => {
  try {
    await resultApi.delete(id)
    ElMessage.success('删除成功')
    fetchResults()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

onMounted(() => {
  fetchResults()
})
</script>

<style lang="scss" scoped>
.result-view {
  .stats-overview {
    margin-bottom: 24px;
    
    .stat-box {
      background: #fff;
      border-radius: 12px;
      padding: 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.04);
      border: 1px solid #f0f0f0;

      .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: #fff;
      }

      &.total .stat-icon { background: linear-gradient(135deg, #409eff, #79bbff); }
      &.average .stat-icon { background: linear-gradient(135deg, #67c23a, #95d475); }
      &.highest .stat-icon { background: linear-gradient(135deg, #e6a23c, #eebe77); }
      &.time .stat-icon { background: linear-gradient(135deg, #909399, #c8c9cc); }

      .stat-data {
        .value {
          font-size: 22px;
          font-weight: 700;
          color: #303133;
          line-height: 1.2;
        }
        .label {
          font-size: 13px;
          color: #909399;
          margin-top: 4px;
        }
      }
    }
  }

  .paper-title-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #303133;
    font-weight: 500;
    .el-icon { color: #409eff; }
  }

  .score-cell {
    font-size: 16px;
    .user-score {
      font-weight: 700;
      &.excellent { color: #67c23a; }
      &.pass { color: #e6a23c; }
      &.fail { color: #f56c6c; }
    }
    .separator { margin: 0 4px; color: #dcdfe6; }
    .total-score { color: #909399; font-size: 14px; }
  }

  .time-cell {
    .date { color: #303133; font-size: 14px; }
    .duration { color: #909399; font-size: 12px; margin-top: 2px; }
  }

  .empty-state {
    text-align: center;
    padding: 60px 0;
    .empty-illustration {
      font-size: 64px;
      color: #f0f2f5;
      margin-bottom: 16px;
    }
    p { color: #909399; margin-bottom: 20px; }
  }
}
</style>
