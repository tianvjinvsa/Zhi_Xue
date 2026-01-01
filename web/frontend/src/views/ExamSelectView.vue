<template>
  <div class="exam-select-view">
    <div class="page-header">
      <h1><el-icon><Edit /></el-icon>选择试卷开始答题</h1>
      <div class="header-desc">选择一份试卷，检验你的学习成果</div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section" v-if="papers.length > 0">
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
    </div>

    <div v-loading="loading">
      <div v-if="filteredPapers.length > 0" class="papers-grid">
        <div 
          v-for="paper in filteredPapers" 
          :key="paper.id" 
          class="paper-card"
          @click="startExam(paper.id)"
        >
          <div class="paper-card-inner">
            <div class="paper-icon">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="paper-content">
              <h3>{{ paper.title }}</h3>
              <p class="description">{{ paper.description || '暂无描述信息，点击开始挑战吧！' }}</p>
              
              <div class="paper-meta">
                <div class="meta-item">
                  <el-icon><List /></el-icon>
                  <span>{{ paper.question_count }} 题</span>
                </div>
                <div class="meta-item">
                  <el-icon><Coin /></el-icon>
                  <span>{{ paper.total_score }} 分</span>
                </div>
                <div class="meta-item">
                  <el-icon><Clock /></el-icon>
                  <span>{{ paper.time_limit ? `${paper.time_limit} 分` : '不限时' }}</span>
                </div>
              </div>
            </div>
            <div class="paper-footer">
              <el-button type="primary" round class="start-btn">
                立即开始 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!loading && papers.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon><Document /></el-icon>
        </div>
        <h3>暂无可用试卷</h3>
        <p>你可以先去题库管理中整理题目，然后生成一份试卷</p>
        <el-button type="primary" size="large" @click="$router.push('/papers/create')">
          去生成试卷
        </el-button>
      </div>
      <div v-else-if="!loading && filteredPapers.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon><Document /></el-icon>
        </div>
        <h3>筛选结果为空</h3>
        <p>当前筛选条件下没有找到相关试卷</p>
        <el-button type="primary" size="large" @click="filterBank = ''">
          清除筛选
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { paperApi, bankApi } from '@/api'
import { Edit, Document, List, Coin, Clock, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const papers = ref([])
const allBanks = ref([])
const filterBank = ref('')

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

const fetchBanks = async () => {
  try {
    allBanks.value = await bankApi.getAll()
  } catch (error) {
    console.error('获取题库失败:', error)
  }
}

const startExam = (paperId) => {
  router.push(`/exam/${paperId}`)
}

onMounted(() => {
  fetchPapers()
  fetchBanks()
})
</script>

<style lang="scss" scoped>
.exam-select-view {
  .page-header {
    margin-bottom: 20px;
    h1 {
      margin-bottom: 8px;
    }
    .header-desc {
      color: #909399;
      font-size: 14px;
    }
  }

  .filter-section {
    margin-bottom: 24px;
    .bank-filter {
      width: 200px;
    }
  }

  .papers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 24px;
  }
  
  .paper-card {
    perspective: 1000px;
    cursor: pointer;
    
    &:hover {
      .paper-card-inner {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        border-color: #409eff;
      }
      .paper-icon {
        transform: scale(1.1) rotate(5deg);
      }
      .start-btn {
        background: #409eff;
        color: #fff;
      }
    }
  }

  .paper-card-inner {
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
    transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    border: 1px solid #f0f0f0;
    overflow: hidden;

    .paper-badge {
      position: absolute;
      top: 12px;
      right: -30px;
      background: #f56c6c;
      color: #fff;
      font-size: 10px;
      font-weight: bold;
      padding: 2px 30px;
      transform: rotate(45deg);
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .paper-icon {
      width: 56px;
      height: 56px;
      border-radius: 14px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      margin-bottom: 20px;
      transition: all 0.3s;
    }

    .paper-content {
      flex: 1;
      
      h3 {
        margin: 0 0 10px;
        font-size: 20px;
        color: #2c3e50;
        font-weight: 600;
      }
      
      .description {
        margin: 0 0 20px;
        color: #7f8c8d;
        font-size: 14px;
        line-height: 1.6;
        height: 45px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      
      .paper-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        margin-bottom: 20px;
        
        .meta-item {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #606266;
          font-size: 13px;
          background: #f8f9fa;
          padding: 4px 10px;
          border-radius: 6px;

          .el-icon {
            color: #409eff;
          }
        }
      }
    }
    
    .paper-footer {
      .start-btn {
        width: 100%;
        height: 40px;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s;
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 80px 20px;
    background: #fff;
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);

    .empty-icon {
      font-size: 80px;
      color: #e0e0e0;
      margin-bottom: 20px;
    }

    h3 {
      font-size: 22px;
      color: #34495e;
      margin-bottom: 10px;
    }

    p {
      color: #95a5a6;
      margin-bottom: 30px;
    }
  }
}
</style>
