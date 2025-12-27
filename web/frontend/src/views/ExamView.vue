<template>
  <div class="exam-view" v-loading="loading">
    <!-- 顶部信息栏 -->
    <div class="exam-header">
      <div class="header-left">
        <div class="paper-info">
          <el-button icon="ArrowLeft" circle @click="confirmExit" class="back-btn" />
          <div class="title-group">
            <h2>{{ paper?.title }}</h2>
            <div class="exam-meta">
              <el-tag size="small" effect="plain">总分：{{ paper?.total_score }} 分</el-tag>
              <el-tag size="small" effect="plain" type="info">题数：{{ questions.length }}</el-tag>
            </div>
          </div>
        </div>
      </div>
      <div class="header-center">
        <div v-if="paper?.time_limit" class="timer-container" :class="{ warning: remainingTime < 300 }">
          <div class="timer-label">剩余时间</div>
          <div class="timer-value">
            <el-icon><Clock /></el-icon>
            {{ formatTime(remainingTime) }}
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="confirmSubmit" class="submit-btn">
          <el-icon><Checked /></el-icon>交卷
        </el-button>
      </div>
    </div>

    <el-row :gutter="24" class="exam-body">
      <!-- 左侧题目区域 -->
      <el-col :span="18">
        <div class="questions-container">
          <div 
            v-for="(question, index) in questions" 
            :key="question.id"
            :ref="el => questionRefs[index] = el"
            class="question-card"
            :class="{ 'is-answered': isAnswered(question.id), 'is-current': currentIndex === index }"
            @click="currentIndex = index"
          >
            <div class="q-header">
              <div class="q-info">
                <span class="q-number">{{ index + 1 }}</span>
                <el-tag :type="getTypeTagType(question.type)" effect="dark" size="small">
                  {{ getTypeLabel(question.type) }}
                </el-tag>
                <span class="q-score">{{ getQuestionScore(question) }} 分</span>
              </div>
              <div class="q-actions">
                <el-button 
                  link
                  :type="favoriteStatus[question.id] ? 'warning' : 'info'"
                  @click.stop="toggleFavorite(question)"
                >
                  <el-icon><StarFilled v-if="favoriteStatus[question.id]" /><Star v-else /></el-icon>
                  {{ favoriteStatus[question.id] ? '已收藏' : '收藏' }}
                </el-button>
              </div>
            </div>
            
            <div class="q-content">{{ question.question }}</div>
            
            <!-- 单选题 -->
            <div v-if="question.type === 'single'" class="q-options">
              <div 
                v-for="(option, optIdx) in question.options" 
                :key="optIdx"
                class="option-item"
                :class="{ 'is-selected': answers[question.id] === String.fromCharCode(65 + optIdx) }"
                @click="selectAnswer(question.id, String.fromCharCode(65 + optIdx))"
              >
                <div class="option-letter">{{ String.fromCharCode(65 + optIdx) }}</div>
                <div class="option-text">{{ option.substring(2) }}</div>
              </div>
            </div>
            
            <!-- 多选题 -->
            <div v-else-if="question.type === 'multiple'" class="q-options">
              <div 
                v-for="(option, optIdx) in question.options" 
                :key="optIdx"
                class="option-item"
                :class="{ 'is-selected': (answers[question.id] || []).includes(String.fromCharCode(65 + optIdx)) }"
                @click="toggleMultipleAnswer(question.id, String.fromCharCode(65 + optIdx))"
              >
                <div class="option-letter">{{ String.fromCharCode(65 + optIdx) }}</div>
                <div class="option-text">{{ option.substring(2) }}</div>
                <div class="multi-check">
                  <el-icon v-if="(answers[question.id] || []).includes(String.fromCharCode(65 + optIdx))"><Check /></el-icon>
                </div>
              </div>
            </div>
            
            <!-- 判断题 -->
            <div v-else-if="question.type === 'judge'" class="q-options judge-grid">
              <div 
                class="option-item judge-item"
                :class="{ 'is-selected': answers[question.id] === true }"
                @click="selectAnswer(question.id, true)"
              >
                <el-icon class="judge-icon"><Check /></el-icon>
                <span>正确</span>
              </div>
              <div 
                class="option-item judge-item"
                :class="{ 'is-selected': answers[question.id] === false }"
                @click="selectAnswer(question.id, false)"
              >
                <el-icon class="judge-icon"><Close /></el-icon>
                <span>错误</span>
              </div>
            </div>
            
            <!-- 填空题 -->
            <div v-else class="q-fill">
              <el-input 
                v-model="answers[question.id]" 
                type="textarea"
                :rows="2"
                placeholder="请输入您的答案..."
                @input="updateAnswer(question.id)"
              />
            </div>
          </div>
        </div>
      </el-col>
      
      <!-- 右侧答题卡 -->
      <el-col :span="6">
        <div class="exam-sidebar">
          <div class="answer-card">
            <div class="card-header">
              <h3>答题卡</h3>
              <div class="progress-text">
                <span>已答 {{ answeredCount }}</span>
                <span class="separator">/</span>
                <span>总计 {{ questions.length }}</span>
              </div>
            </div>
            
            <el-progress 
              :percentage="Math.round(answeredCount / questions.length * 100)" 
              :show-text="false"
              :stroke-width="8"
              class="progress-bar"
            />
            
            <div class="nav-grid">
              <div 
                v-for="(question, index) in questions" 
                :key="question.id"
                class="nav-item"
                :class="{ 
                  'is-answered': isAnswered(question.id), 
                  'is-current': currentIndex === index 
                }"
                @click="scrollToQuestion(index)"
              >
                {{ index + 1 }}
              </div>
            </div>
            
            <div class="card-legend">
              <div class="legend-item">
                <span class="dot is-answered"></span>
                <span>已答</span>
              </div>
              <div class="legend-item">
                <span class="dot"></span>
                <span>未答</span>
              </div>
              <div class="legend-item">
                <span class="dot is-current"></span>
                <span>当前</span>
              </div>
            </div>
          </div>

          <div class="exam-tips">
            <h4><el-icon><InfoFilled /></el-icon> 考试须知</h4>
            <ul>
              <li>请在规定时间内完成所有题目。</li>
              <li>系统会自动保存您的答题进度。</li>
              <li>交卷后将无法修改答案。</li>
            </ul>
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
import { 
  Clock, Star, StarFilled, Check, Close, 
  ArrowLeft, Checked, InfoFilled 
} from '@element-plus/icons-vue'
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

const getTypeTagType = (type) => {
  const types = { single: '', multiple: 'success', judge: 'warning', fill: 'info' }
  return types[type] || ''
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

const confirmExit = () => {
  ElMessageBox.confirm('考试正在进行中，确定要退出吗？进度将被保存。', '提示', {
    confirmButtonText: '确定退出',
    cancelButtonText: '继续答题',
    type: 'warning'
  }).then(() => {
    router.push('/exam')
  }).catch(() => {})
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
    paper.value = await paperApi.get(paperId)
    questions.value = await paperApi.getQuestions(paperId)
    
    const result = await examApi.start(paperId)
    examId.value = result.exam_id
    
    questions.value.forEach(q => {
      if (q.type === 'multiple') {
        answers.value[q.id] = []
      } else {
        answers.value[q.id] = null
      }
    })
    
    await checkFavoriteStatus()
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
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100vh;
  background: #f5f7fa;

  .exam-header {
    position: sticky;
    top: 0;
    z-index: 100;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fff;
    padding: 16px 32px;
    border-radius: 16px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    
    .header-left {
      .paper-info {
        display: flex;
        align-items: center;
        gap: 20px;

        .back-btn {
          border: 1px solid #ebeef5;
          &:hover { background: #f5f7fa; color: #409eff; }
        }

        .title-group {
          h2 {
            margin: 0 0 4px;
            font-size: 20px;
            color: #1a1a1a;
          }
          .exam-meta {
            display: flex;
            gap: 12px;
          }
        }
      }
    }

    .header-center {
      .timer-container {
        text-align: center;
        padding: 8px 24px;
        background: #f0f7ff;
        border-radius: 12px;
        border: 1px solid #d1e9ff;
        transition: all 0.3s;

        .timer-label {
          font-size: 12px;
          color: #409eff;
          margin-bottom: 2px;
        }

        .timer-value {
          font-size: 24px;
          font-weight: 700;
          color: #409eff;
          display: flex;
          align-items: center;
          gap: 8px;
          font-family: 'Monaco', 'Courier New', monospace;
        }

        &.warning {
          background: #fff1f0;
          border-color: #ffa39e;
          .timer-label, .timer-value { color: #f5222d; }
          animation: pulse 1s infinite;
        }
      }
    }

    .submit-btn {
      padding: 12px 32px;
      font-weight: 600;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
    }
  }

  .exam-body {
    margin-top: 24px;
  }

  .questions-container {
    display: flex;
    flex-direction: column;
    gap: 24px;
    padding-bottom: 100px;
  }

  .question-card {
    background: #fff;
    border-radius: 20px;
    padding: 32px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    border: 2px solid transparent;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }

    &.is-current {
      border-color: #409eff;
      box-shadow: 0 8px 24px rgba(64, 158, 255, 0.12);
    }

    &.is-answered {
      .q-number {
        background: #67c23a;
        color: #fff;
      }
    }

    .q-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;

      .q-info {
        display: flex;
        align-items: center;
        gap: 12px;

        .q-number {
          width: 32px;
          height: 32px;
          background: #f0f2f5;
          color: #909399;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          transition: all 0.3s;
        }

        .q-score {
          color: #e6a23c;
          font-weight: 600;
          font-size: 14px;
        }
      }
    }

    .q-content {
      font-size: 18px;
      line-height: 1.6;
      color: #2c3e50;
      margin-bottom: 32px;
      font-weight: 500;
    }

    .q-options {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .option-item {
        display: flex;
        align-items: flex-start;
        padding: 16px 24px;
        background: #f8f9fa;
        border: 1px solid #f0f0f0;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background: #f0f7ff;
          border-color: #c6e2ff;
        }

        &.is-selected {
          background: #ecf5ff;
          border-color: #409eff;
          .option-letter {
            background: #409eff;
            color: #fff;
            border-color: #409eff;
          }
          .option-text {
            color: #409eff;
            font-weight: 600;
          }
        }

        .option-letter {
          width: 28px;
          height: 28px;
          flex-shrink: 0;
          background: #fff;
          border: 1px solid #dcdfe6;
          border-radius: 6px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          margin-right: 16px;
          font-size: 14px;
          transition: all 0.2s;
          margin-top: -2px; /* 微调对齐 */
        }

        .option-text {
          flex: 1;
          font-size: 15px;
          color: #606266;
          line-height: 1.6;
          word-break: break-word;
          overflow-wrap: break-word;
        }

        .multi-check {
          color: #409eff;
          font-size: 20px;
        }
      }

      &.judge-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;

        .judge-item {
          justify-content: center;
          flex-direction: column;
          gap: 8px;
          padding: 24px;

          .judge-icon {
            font-size: 24px;
          }
        }
      }
    }

    .q-fill {
      :deep(.el-textarea__inner) {
        border-radius: 12px;
        padding: 16px;
        font-size: 15px;
        &:focus {
          box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
        }
      }
    }
  }

  .exam-sidebar {
    position: sticky;
    top: 100px;
    display: flex;
    flex-direction: column;
    gap: 24px;

    .answer-card {
      background: #fff;
      border-radius: 20px;
      padding: 24px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;

        h3 { margin: 0; font-size: 18px; }
        .progress-text {
          font-size: 14px;
          color: #909399;
          .separator { margin: 0 4px; }
        }
      }

      .progress-bar {
        margin-bottom: 24px;
      }

      .nav-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 10px;
        margin-bottom: 24px;

        .nav-item {
          aspect-ratio: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 10px;
          background: #f5f7fa;
          cursor: pointer;
          font-size: 14px;
          font-weight: 600;
          color: #909399;
          transition: all 0.2s;
          border: 2px solid transparent;

          &:hover {
            background: #ecf5ff;
            color: #409eff;
          }

          &.is-answered {
            background: #f0f9eb;
            color: #67c23a;
          }

          &.is-current {
            border-color: #409eff;
            color: #409eff;
            background: #fff;
          }
        }
      }

      .card-legend {
        display: flex;
        justify-content: space-between;
        padding-top: 16px;
        border-top: 1px solid #f0f2f5;
        font-size: 12px;
        color: #909399;

        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;

          .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #f5f7fa;

            &.is-answered { background: #67c23a; }
            &.is-current { background: #fff; border: 1px solid #409eff; }
          }
        }
      }
    }

    .exam-tips {
      background: #fff;
      border-radius: 20px;
      padding: 20px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);

      h4 {
        margin: 0 0 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        color: #e6a23c;
      }

      ul {
        margin: 0;
        padding-left: 20px;
        color: #909399;
        font-size: 13px;
        li { margin-bottom: 8px; }
      }
    }
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}
</style>
