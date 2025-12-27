<template>
  <div class="exam-view" v-loading="loading">
    <!-- 顶部信息栏 -->
    <div class="exam-header">
      <div class="header-left">
        <h2>{{ paper?.title }}</h2>
        <div class="exam-meta">
          <span>总分：{{ paper?.total_score }} 分</span>
          <span>题数：{{ questions.length }}</span>
        </div>
      </div>
      <div class="header-right">
        <div v-if="paper?.time_limit" class="timer" :class="{ warning: remainingTime < 300 }">
          <el-icon><Clock /></el-icon>
          剩余时间：{{ formatTime(remainingTime) }}
        </div>
        <el-button type="primary" @click="confirmSubmit">交卷</el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧题目区域 -->
      <el-col :span="18">
        <div class="questions-container">
          <div 
            v-for="(question, index) in questions" 
            :key="question.id"
            :ref="el => questionRefs[index] = el"
            class="question-card exam-question"
            :class="{ answered: isAnswered(question.id) }"
          >
            <div class="question-header">
              <div class="question-info">
                <span class="question-number">{{ index + 1 }}</span>
                <el-tag :class="['question-type-tag', question.type]" size="small">
                  {{ getTypeLabel(question.type) }}
                </el-tag>
                <span class="question-score">（{{ getQuestionScore(question) }} 分）</span>
              </div>
              <div class="question-actions">
                <el-button 
                  size="small" 
                  :type="favoriteStatus[question.id] ? 'warning' : 'default'"
                  @click="toggleFavorite(question)"
                >
                  <el-icon><Star /></el-icon>
                  {{ favoriteStatus[question.id] ? '已收藏' : '收藏' }}
                </el-button>
              </div>
            </div>
            
            <div class="question-content">{{ question.question }}</div>
            
            <!-- 单选题 -->
            <div v-if="question.type === 'single'" class="question-options">
              <div 
                v-for="option in question.options" 
                :key="option"
                class="option-item"
                :class="{ selected: answers[question.id] === option.charAt(0) }"
                @click="selectAnswer(question.id, option.charAt(0))"
              >
                <el-radio 
                  :model-value="answers[question.id]" 
                  :value="option.charAt(0)"
                  @change="selectAnswer(question.id, option.charAt(0))"
                >
                  {{ option }}
                </el-radio>
              </div>
            </div>
            
            <!-- 多选题 -->
            <div v-else-if="question.type === 'multiple'" class="question-options">
              <div 
                v-for="option in question.options" 
                :key="option"
                class="option-item"
                :class="{ selected: (answers[question.id] || []).includes(option.charAt(0)) }"
                @click="toggleMultipleAnswer(question.id, option.charAt(0))"
              >
                <el-checkbox 
                  :model-value="(answers[question.id] || []).includes(option.charAt(0))"
                  @change="toggleMultipleAnswer(question.id, option.charAt(0))"
                >
                  {{ option }}
                </el-checkbox>
              </div>
            </div>
            
            <!-- 判断题 -->
            <div v-else-if="question.type === 'judge'" class="question-options judge-options">
              <div 
                class="option-item"
                :class="{ selected: answers[question.id] === true }"
                @click="selectAnswer(question.id, true)"
              >
                <el-radio :model-value="answers[question.id]" :value="true">正确</el-radio>
              </div>
              <div 
                class="option-item"
                :class="{ selected: answers[question.id] === false }"
                @click="selectAnswer(question.id, false)"
              >
                <el-radio :model-value="answers[question.id]" :value="false">错误</el-radio>
              </div>
            </div>
            
            <!-- 填空题 -->
            <div v-else class="fill-answer">
              <el-input 
                v-model="answers[question.id]" 
                placeholder="请输入答案"
                @input="updateAnswer(question.id)"
              />
            </div>
          </div>
        </div>
      </el-col>
      
      <!-- 右侧答题卡 -->
      <el-col :span="6">
        <div class="answer-card">
          <h3>答题卡</h3>
          <div class="progress-info">
            <el-progress 
              :percentage="Math.round(answeredCount / questions.length * 100)" 
              :stroke-width="10"
            />
            <p>已答 {{ answeredCount }} / {{ questions.length }} 题</p>
          </div>
          
          <div class="question-nav">
            <div 
              v-for="(question, index) in questions" 
              :key="question.id"
              class="nav-item"
              :class="{ answered: isAnswered(question.id), current: currentIndex === index }"
              @click="scrollToQuestion(index)"
            >
              {{ index + 1 }}
            </div>
          </div>
          
          <div class="legend">
            <span class="legend-item"><i class="dot answered"></i>已答</span>
            <span class="legend-item"><i class="dot"></i>未答</span>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { paperApi, examApi, favoriteApi } from '@/api'

const route = useRoute()
const router = useRouter()
const paperId = route.params.paperId

const loading = ref(true)
const paper = ref(null)
const questions = ref([])
const examId = ref(null)
const answers = ref({})
const currentIndex = ref(0)
const remainingTime = ref(0)
const questionRefs = ref([])
const favoriteStatus = ref({})

let timerInterval = null

const getTypeLabel = (type) => {
  const labels = { single: '单选题', multiple: '多选题', judge: '判断题', fill: '填空题' }
  return labels[type] || type
}

const getQuestionScore = (question) => {
  return paper.value?.score_rules?.[question.type] || 5
}

const isAnswered = (questionId) => {
  const answer = answers.value[questionId]
  if (answer === undefined || answer === null || answer === '') return false
  if (Array.isArray(answer) && answer.length === 0) return false
  return true
}

const answeredCount = computed(() => {
  return questions.value.filter(q => isAnswered(q.id)).length
})

const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) {
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }
  return `${m}:${String(s).padStart(2, '0')}`
}

const selectAnswer = (questionId, value) => {
  answers.value[questionId] = value
  saveAnswer(questionId)
}

const toggleMultipleAnswer = (questionId, letter) => {
  if (!answers.value[questionId]) {
    answers.value[questionId] = []
  }
  const idx = answers.value[questionId].indexOf(letter)
  if (idx > -1) {
    answers.value[questionId].splice(idx, 1)
  } else {
    answers.value[questionId].push(letter)
    answers.value[questionId].sort()
  }
  saveAnswer(questionId)
}

const updateAnswer = (questionId) => {
  saveAnswer(questionId)
}

const saveAnswer = async (questionId) => {
  if (!examId.value) return
  try {
    await examApi.submitAnswer(examId.value, {
      question_id: questionId,
      answer: answers.value[questionId]
    })
  } catch (error) {
    console.error('保存答案失败:', error)
  }
}

const scrollToQuestion = (index) => {
  currentIndex.value = index
  questionRefs.value[index]?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

const confirmSubmit = async () => {
  const unanswered = questions.value.length - answeredCount.value
  
  let message = '确定要交卷吗？'
  if (unanswered > 0) {
    message = `还有 ${unanswered} 道题未作答，确定要交卷吗？`
  }
  
  try {
    await ElMessageBox.confirm(message, '提示', {
      confirmButtonText: '确定交卷',
      cancelButtonText: '继续答题',
      type: 'warning'
    })
    
    submitExam()
  } catch {
    // 用户取消
  }
}

const submitExam = async () => {
  loading.value = true
  try {
    const result = await examApi.finish(examId.value)
    ElMessage.success('交卷成功！')
    router.push(`/results/${result.id}`)
  } catch (error) {
    console.error('交卷失败:', error)
    loading.value = false
  }
}

const startTimer = () => {
  if (!paper.value?.time_limit) return
  
  remainingTime.value = paper.value.time_limit * 60
  
  timerInterval = setInterval(() => {
    remainingTime.value--
    if (remainingTime.value <= 0) {
      clearInterval(timerInterval)
      ElMessage.warning('时间到，自动交卷！')
      submitExam()
    }
  }, 1000)
}

const initExam = async () => {
  loading.value = true
  try {
    // 获取试卷信息
    paper.value = await paperApi.get(paperId)
    questions.value = await paperApi.getQuestions(paperId)
    
    // 开始考试
    const result = await examApi.start(paperId)
    examId.value = result.exam_id
    
    // 初始化答案对象
    questions.value.forEach(q => {
      if (q.type === 'multiple') {
        answers.value[q.id] = []
      } else {
        answers.value[q.id] = null
      }
    })
    
    // 检查收藏状态
    await checkFavoriteStatus()
    
    // 开始计时
    startTimer()
  } catch (error) {
    console.error('初始化考试失败:', error)
    ElMessage.error('加载试卷失败')
    router.push('/exam')
  } finally {
    loading.value = false
  }
}

const checkFavoriteStatus = async () => {
  for (const question of questions.value) {
    try {
      const result = await favoriteApi.check(question.id)
      favoriteStatus.value[question.id] = result.favorited
    } catch (error) {
      favoriteStatus.value[question.id] = false
    }
  }
}

const toggleFavorite = async (question) => {
  try {
    if (favoriteStatus.value[question.id]) {
      await favoriteApi.remove(question.id)
      favoriteStatus.value[question.id] = false
      ElMessage.success('已取消收藏')
    } else {
      await favoriteApi.add(question.bank_id || 'unknown', question.id)
      favoriteStatus.value[question.id] = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    console.error('收藏操作失败:', error)
  }
}

onMounted(() => {
  initExam()
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})
</script>

<style lang="scss" scoped>
.exam-view {
  .exam-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fff;
    padding: 16px 24px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    
    .header-left {
      h2 {
        margin: 0 0 8px;
        color: #303133;
      }
      
      .exam-meta {
        color: #909399;
        font-size: 14px;
        
        span {
          margin-right: 20px;
        }
      }
    }
    
    .header-right {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .timer {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 18px;
        font-weight: 600;
        color: #303133;
        
        &.warning {
          color: #f56c6c;
          animation: pulse 1s infinite;
        }
      }
    }
  }
  
  .questions-container {
    .exam-question {
      &.answered {
        border-left: 4px solid #67c23a;
      }
      
      .question-score {
        color: #e6a23c;
        font-size: 14px;
      }
      
      .judge-options {
        display: flex;
        gap: 30px;
      }
      
      .fill-answer {
        padding: 10px 0;
        
        .el-input {
          max-width: 400px;
        }
      }
    }
  }
  
  .answer-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    position: sticky;
    top: 20px;
    
    h3 {
      margin: 0 0 15px;
      color: #303133;
    }
    
    .progress-info {
      margin-bottom: 20px;
      
      p {
        margin: 10px 0 0;
        text-align: center;
        color: #606266;
        font-size: 14px;
      }
    }
    
    .question-nav {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 10px;
      margin-bottom: 20px;
      
      .nav-item {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        background: #f5f7fa;
        cursor: pointer;
        font-size: 14px;
        color: #606266;
        transition: all 0.2s;
        
        &:hover {
          background: #ecf5ff;
          color: #409eff;
        }
        
        &.answered {
          background: #67c23a;
          color: #fff;
        }
        
        &.current {
          border: 2px solid #409eff;
        }
      }
    }
    
    .legend {
      display: flex;
      justify-content: center;
      gap: 20px;
      font-size: 12px;
      color: #909399;
      
      .legend-item {
        display: flex;
        align-items: center;
        gap: 5px;
        
        .dot {
          width: 12px;
          height: 12px;
          border-radius: 3px;
          background: #f5f7fa;
          
          &.answered {
            background: #67c23a;
          }
        }
      }
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
