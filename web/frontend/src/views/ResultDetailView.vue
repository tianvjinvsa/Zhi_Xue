<template>
  <div class="result-detail-view" v-loading="loading">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.push('/results')" text>
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
        <h1><el-icon><DataAnalysis /></el-icon>成绩详情</h1>
      </div>
    </div>

    <!-- 成绩概览 -->
    <div class="score-overview">
      <div class="score-main">
        <div class="score-circle" :class="scoreLevel">
          <span class="score-value">{{ result?.user_score || 0 }}</span>
          <span class="score-label">得分</span>
        </div>
        <div class="score-info">
          <h2>{{ result?.paper_title }}</h2>
          <div class="score-meta">
            <span>满分 {{ result?.total_score }} 分</span>
            <span>正确率 {{ correctRate }}%</span>
          </div>
        </div>
      </div>
      
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <div class="stat-card green">
            <div class="stat-value">{{ correctCount }}</div>
            <div class="stat-label">答对题数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card orange">
            <div class="stat-value">{{ wrongCount }}</div>
            <div class="stat-label">答错题数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-value">{{ unansweredCount }}</div>
            <div class="stat-label">未答题数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card blue">
            <div class="stat-value">{{ formatDuration }}</div>
            <div class="stat-label">答题用时</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 答题详情 -->
    <div class="card-container">
      <div class="filter-bar">
        <el-radio-group v-model="filterStatus">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="correct">正确</el-radio-button>
          <el-radio-button value="wrong">错误</el-radio-button>
        </el-radio-group>
      </div>

      <div class="questions-list">
        <div 
          v-for="detail in filteredDetails" 
          :key="detail.question_id"
          class="question-card result-question"
          :class="{ correct: detail.is_correct, wrong: !detail.is_correct && detail.user_answer != null }"
        >
          <div class="question-header">
            <div class="question-info">
              <span class="question-number">{{ getQuestionIndex(detail) + 1 }}</span>
              <el-tag :class="['question-type-tag', detail.question_type]" size="small">
                {{ getTypeLabel(detail.question_type) }}
              </el-tag>
              <el-tag :type="detail.is_correct ? 'success' : 'danger'" size="small">
                {{ detail.is_correct ? '正确' : '错误' }} {{ detail.score }}/{{ detail.max_score }}分
              </el-tag>
            </div>
            <div class="question-actions">
              <el-button 
                size="small" 
                :type="favoriteStatus[detail.question_id] ? 'warning' : 'default'"
                @click="toggleFavorite(detail)"
              >
                <el-icon><Star /></el-icon>
                {{ favoriteStatus[detail.question_id] ? '已收藏' : '收藏' }}
              </el-button>
            </div>
          </div>
          
          <div class="question-content">{{ getQuestion(detail.question_id)?.question }}</div>
          
          <div v-if="getQuestion(detail.question_id)?.options?.length" class="question-options">
            <div 
              v-for="option in getQuestion(detail.question_id)?.options" 
              :key="option"
              class="option-item"
              :class="getOptionClass(detail, option)"
            >
              {{ option }}
              <el-icon v-if="isUserAnswer(detail, option) && !isCorrectAnswer(detail, option)" class="wrong-icon"><Close /></el-icon>
              <el-icon v-if="isCorrectAnswer(detail, option)" class="correct-icon"><Check /></el-icon>
            </div>
          </div>
          
          <div v-else-if="detail.question_type === 'judge'" class="judge-result">
            <span class="your-answer">
              你的答案：<strong :class="detail.is_correct ? 'correct' : 'wrong'">
                {{ detail.user_answer === true ? '正确' : detail.user_answer === false ? '错误' : '未作答' }}
              </strong>
            </span>
            <span class="correct-answer">正确答案：<strong>{{ detail.correct_answer ? '正确' : '错误' }}</strong></span>
          </div>
          
          <div class="question-answer">
            <div class="answer-label">✓ 正确答案</div>
            <div class="answer-value">{{ formatAnswer(detail.correct_answer, detail.question_type) }}</div>
          </div>
          
          <div v-if="getQuestion(detail.question_id)?.explanation" class="question-explanation">
            <strong>解析：</strong>{{ getQuestion(detail.question_id)?.explanation }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { resultApi, paperApi, favoriteApi } from '@/api'

const route = useRoute()
const resultId = route.params.id

const loading = ref(true)
const result = ref(null)
const questions = ref([])
const filterStatus = ref('all')
const favoriteStatus = ref({})

const getTypeLabel = (type) => {
  const labels = { single: '单选题', multiple: '多选题', judge: '判断题', fill: '填空题' }
  return labels[type] || type
}

const correctRate = computed(() => {
  if (!result.value) return 0
  return Math.round(result.value.user_score / result.value.total_score * 100)
})

const scoreLevel = computed(() => {
  const rate = correctRate.value
  if (rate >= 90) return 'excellent'
  if (rate >= 60) return 'pass'
  return 'fail'
})

const correctCount = computed(() => {
  return result.value?.details?.filter(d => d.is_correct).length || 0
})

const wrongCount = computed(() => {
  return result.value?.details?.filter(d => !d.is_correct && d.user_answer != null).length || 0
})

const unansweredCount = computed(() => {
  return result.value?.details?.filter(d => d.user_answer == null).length || 0
})

const formatDuration = computed(() => {
  if (!result.value?.start_time || !result.value?.end_time) return '--'
  const start = new Date(result.value.start_time)
  const end = new Date(result.value.end_time)
  const diff = Math.floor((end - start) / 1000)
  const m = Math.floor(diff / 60)
  const s = diff % 60
  return `${m}分${s}秒`
})

const filteredDetails = computed(() => {
  if (!result.value?.details) return []
  if (filterStatus.value === 'all') return result.value.details
  if (filterStatus.value === 'correct') return result.value.details.filter(d => d.is_correct)
  return result.value.details.filter(d => !d.is_correct)
})

const getQuestion = (questionId) => {
  return questions.value.find(q => q.id === questionId)
}

const getQuestionIndex = (detail) => {
  return result.value?.details?.findIndex(d => d.question_id === detail.question_id) || 0
}

const formatAnswer = (answer, type) => {
  if (type === 'judge') return answer ? '正确' : '错误'
  if (Array.isArray(answer)) return answer.join('、')
  return answer
}

const isUserAnswer = (detail, option) => {
  const letter = option.charAt(0)
  if (Array.isArray(detail.user_answer)) {
    return detail.user_answer.includes(letter)
  }
  return detail.user_answer === letter
}

const isCorrectAnswer = (detail, option) => {
  const letter = option.charAt(0)
  if (Array.isArray(detail.correct_answer)) {
    return detail.correct_answer.includes(letter)
  }
  return detail.correct_answer === letter
}

const getOptionClass = (detail, option) => {
  const isUser = isUserAnswer(detail, option)
  const isCorrect = isCorrectAnswer(detail, option)
  
  if (isCorrect) return 'correct'
  if (isUser && !isCorrect) return 'wrong'
  return ''
}

const fetchData = async () => {
  loading.value = true
  try {
    result.value = await resultApi.get(resultId)
    if (result.value?.paper_id) {
      questions.value = await paperApi.getQuestions(result.value.paper_id)
    }
    // 检查收藏状态
    await checkFavoriteStatus()
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const checkFavoriteStatus = async () => {
  if (!result.value?.details) return
  for (const detail of result.value.details) {
    try {
      const res = await favoriteApi.check(detail.question_id)
      favoriteStatus.value[detail.question_id] = res.favorited
    } catch (error) {
      favoriteStatus.value[detail.question_id] = false
    }
  }
}

const toggleFavorite = async (detail) => {
  const question = getQuestion(detail.question_id)
  try {
    if (favoriteStatus.value[detail.question_id]) {
      await favoriteApi.remove(detail.question_id)
      favoriteStatus.value[detail.question_id] = false
      ElMessage.success('已取消收藏')
    } else {
      await favoriteApi.add(question?.bank_id || 'unknown', detail.question_id)
      favoriteStatus.value[detail.question_id] = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    console.error('收藏操作失败:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.result-detail-view {
  .header-left {
    display: flex;
    align-items: center;
    gap: 10px;
    
    h1 {
      margin: 0;
    }
  }
  
  .score-overview {
    background: #fff;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    
    .score-main {
      display: flex;
      align-items: center;
      gap: 30px;
      margin-bottom: 30px;
      
      .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        
        &.excellent {
          background: linear-gradient(135deg, #67c23a, #85ce61);
        }
        &.pass {
          background: linear-gradient(135deg, #e6a23c, #f5b461);
        }
        &.fail {
          background: linear-gradient(135deg, #f56c6c, #f78989);
        }
        
        .score-value {
          font-size: 36px;
          font-weight: 700;
          color: #fff;
        }
        
        .score-label {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.9);
        }
      }
      
      .score-info {
        h2 {
          margin: 0 0 10px;
          color: #303133;
        }
        
        .score-meta {
          color: #909399;
          
          span {
            margin-right: 20px;
          }
        }
      }
    }
  }
  
  .filter-bar {
    margin-bottom: 20px;
  }
  
  .result-question {
    &.correct {
      border-left: 4px solid #67c23a;
    }
    
    &.wrong {
      border-left: 4px solid #f56c6c;
    }
    
    .option-item {
      display: flex;
      align-items: center;
      gap: 8px;
      
      &.correct {
        color: #67c23a;
        background-color: #f0f9eb;
      }
      
      &.wrong {
        color: #f56c6c;
        background-color: #fef0f0;
        text-decoration: line-through;
      }
      
      .correct-icon {
        color: #67c23a;
      }
      
      .wrong-icon {
        color: #f56c6c;
      }
    }
    
    .judge-result {
      display: flex;
      gap: 30px;
      padding: 10px 0;
      font-size: 14px;
      
      .correct { color: #67c23a; }
      .wrong { color: #f56c6c; }
    }
  }
}
</style>
