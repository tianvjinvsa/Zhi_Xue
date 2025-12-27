<template>
  <div class="result-view">
    <div class="page-header">
      <h1><el-icon><DataAnalysis /></el-icon>成绩查看</h1>
    </div>

    <div class="card-container">
      <el-table :data="results" v-loading="loading" style="width: 100%">
        <el-table-column prop="paper_title" label="试卷名称" min-width="200" />
        <el-table-column label="得分" width="150" align="center">
          <template #default="{ row }">
            <span class="score-display">
              <span class="user-score" :class="getScoreClass(row)">{{ row.user_score }}</span>
              <span class="separator">/</span>
              <span class="total-score">{{ row.total_score }}</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="正确率" width="120" align="center">
          <template #default="{ row }">
            <el-progress 
              type="circle" 
              :percentage="Math.round(row.user_score / row.total_score * 100)" 
              :width="50"
              :stroke-width="5"
              :color="getProgressColor(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180" />
        <el-table-column prop="end_time" label="结束时间" width="180" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
              {{ row.status === 'completed' ? '已完成' : '进行中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="viewDetail(row.id)">
                详情
              </el-button>
              <el-popconfirm title="确定删除此记录？" @confirm="deleteResult(row.id)">
                <template #reference>
                  <el-button type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="results.length === 0 && !loading" class="empty-state">
        <el-icon><DataAnalysis /></el-icon>
        <p>暂无答题记录</p>
        <el-button type="primary" @click="$router.push('/exam')">去答题</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { resultApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const results = ref([])

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
  .score-display {
    font-size: 16px;
    
    .user-score {
      font-weight: 700;
      
      &.excellent { color: #67c23a; }
      &.pass { color: #e6a23c; }
      &.fail { color: #f56c6c; }
    }
    
    .separator {
      margin: 0 5px;
      color: #909399;
    }
    
    .total-score {
      color: #606266;
    }
  }
  
  .action-buttons {
    justify-content: center;
  }
}
</style>
