<template>
  <div class="bank-detail-view">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.push('/banks')" text>
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
        <h1><el-icon><Folder /></el-icon>{{ bank?.name || '加载中...' }}</h1>
      </div>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>添加题目
      </el-button>
    </div>

    <!-- 题库统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card blue">
          <div class="stat-value">{{ questions.length }}</div>
          <div class="stat-label">总题目数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card green">
          <div class="stat-value">{{ singleCount }}</div>
          <div class="stat-label">单选题</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="stat-value">{{ multipleCount }}</div>
          <div class="stat-label">多选题</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card orange">
          <div class="stat-value">{{ judgeCount }}</div>
          <div class="stat-label">判断题</div>
        </div>
      </el-col>
    </el-row>

    <!-- 题目列表 -->
    <div class="card-container">
      <div class="filter-bar">
        <el-select v-model="filterType" placeholder="题目类型" clearable style="width: 120px">
          <el-option label="单选题" value="single" />
          <el-option label="多选题" value="multiple" />
          <el-option label="判断题" value="judge" />
          <el-option label="填空题" value="fill" />
        </el-select>
        <el-select v-model="filterDifficulty" placeholder="难度" clearable style="width: 100px">
          <el-option v-for="i in 5" :key="i" :label="`${i}星`" :value="i" />
        </el-select>
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索题目内容..."
          style="width: 250px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <div v-loading="loading" class="questions-list">
        <div 
          v-for="(question, index) in filteredQuestions" 
          :key="question.id"
          class="question-card"
        >
          <div class="question-header">
            <div class="question-info">
              <span class="question-number">{{ index + 1 }}</span>
              <el-tag :class="['question-type-tag', question.type]" size="small">
                {{ getTypeLabel(question.type) }}
              </el-tag>
              <div class="difficulty-stars">
                <el-icon v-for="i in question.difficulty" :key="i"><Star /></el-icon>
              </div>
            </div>
            <div class="action-buttons">
              <el-button 
                size="small" 
                :type="favoriteStatus[question.id] ? 'warning' : 'default'"
                @click="toggleFavorite(question)"
              >
                <el-icon><Star /></el-icon>
                {{ favoriteStatus[question.id] ? '已收藏' : '收藏' }}
              </el-button>
              <el-button size="small" @click="showEditDialog(question)">编辑</el-button>
              <el-popconfirm title="确定删除此题目？" @confirm="deleteQuestion(question.id)">
                <template #reference>
                  <el-button size="small" type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>
          
          <div class="question-content">{{ question.question }}</div>
          
          <div v-if="question.options && question.options.length" class="question-options">
            <div 
              v-for="option in question.options" 
              :key="option" 
              class="option-item"
              :class="{ correct: isCorrectOption(question, option) }"
            >
              {{ option }}
            </div>
          </div>
          
          <div class="question-answer">
            <div class="answer-label">✓ 正确答案</div>
            <div class="answer-value">{{ formatAnswer(question) }}</div>
          </div>
          
          <div v-if="question.explanation" class="question-explanation">
            <strong>解析：</strong>{{ question.explanation }}
          </div>
        </div>

        <div v-if="filteredQuestions.length === 0 && !loading" class="empty-state">
          <el-icon><Document /></el-icon>
          <p>{{ questions.length === 0 ? '暂无题目，点击上方按钮添加题目' : '没有符合条件的题目' }}</p>
        </div>
      </div>
    </div>

    <!-- 添加/编辑题目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑题目' : '添加题目'"
      width="700px"
      top="5vh"
    >
      <el-form :model="questionForm" label-width="100px" :rules="questionRules" ref="questionFormRef">
        <el-form-item label="题目类型" prop="type">
          <el-radio-group v-model="questionForm.type">
            <el-radio value="single">单选题</el-radio>
            <el-radio value="multiple">多选题</el-radio>
            <el-radio value="judge">判断题</el-radio>
            <el-radio value="fill">填空题</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="题目内容" prop="question">
          <el-input 
            v-model="questionForm.question" 
            type="textarea" 
            :rows="3"
            placeholder="请输入题目内容" 
          />
        </el-form-item>
        
        <el-form-item 
          v-if="['single', 'multiple'].includes(questionForm.type)" 
          label="选项"
          prop="options"
        >
          <div class="options-editor">
            <div 
              v-for="(option, index) in questionForm.options" 
              :key="index" 
              class="option-row"
            >
              <el-input v-model="questionForm.options[index]" :placeholder="`选项 ${String.fromCharCode(65 + index)}`" />
              <el-button 
                v-if="questionForm.options.length > 2"
                type="danger" 
                :icon="Delete" 
                circle 
                @click="removeOption(index)"
              />
            </div>
            <el-button 
              v-if="questionForm.options.length < 6"
              type="primary" 
              text 
              @click="addOption"
            >
              <el-icon><Plus /></el-icon>添加选项
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="正确答案" prop="answer">
          <template v-if="questionForm.type === 'single'">
            <el-radio-group v-model="questionForm.answer">
              <el-radio 
                v-for="(_, index) in questionForm.options" 
                :key="index" 
                :value="String.fromCharCode(65 + index)"
              >
                {{ String.fromCharCode(65 + index) }}
              </el-radio>
            </el-radio-group>
          </template>
          
          <template v-else-if="questionForm.type === 'multiple'">
            <el-checkbox-group v-model="questionForm.answerArray">
              <el-checkbox 
                v-for="(_, index) in questionForm.options" 
                :key="index" 
                :value="String.fromCharCode(65 + index)"
              >
                {{ String.fromCharCode(65 + index) }}
              </el-checkbox>
            </el-checkbox-group>
          </template>
          
          <template v-else-if="questionForm.type === 'judge'">
            <el-radio-group v-model="questionForm.answerBool">
              <el-radio :value="true">正确</el-radio>
              <el-radio :value="false">错误</el-radio>
            </el-radio-group>
          </template>
          
          <template v-else>
            <el-input v-model="questionForm.answer" placeholder="请输入正确答案" />
          </template>
        </el-form-item>
        
        <el-form-item label="难度">
          <el-rate v-model="questionForm.difficulty" :max="5" />
        </el-form-item>
        
        <el-form-item label="解析">
          <el-input 
            v-model="questionForm.explanation" 
            type="textarea" 
            :rows="2"
            placeholder="请输入答案解析（可选）" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitQuestion" :loading="submitting">
          {{ isEditing ? '保存' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Delete, Plus, Star, Search } from '@element-plus/icons-vue'
import { bankApi, favoriteApi } from '@/api'

const route = useRoute()
const bankId = route.params.id

const loading = ref(false)
const bank = ref(null)
const questions = ref([])
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const questionFormRef = ref(null)

const filterType = ref('')
const filterDifficulty = ref('')
const searchKeyword = ref('')
const favoriteStatus = ref({})

const questionForm = ref({
  type: 'single',
  question: '',
  options: ['', '', '', ''],
  answer: '',
  answerArray: [],
  answerBool: true,
  difficulty: 3,
  explanation: ''
})

const questionRules = {
  question: [{ required: true, message: '请输入题目内容', trigger: 'blur' }]
}

const singleCount = computed(() => questions.value.filter(q => q.type === 'single').length)
const multipleCount = computed(() => questions.value.filter(q => q.type === 'multiple').length)
const judgeCount = computed(() => questions.value.filter(q => q.type === 'judge').length)

const filteredQuestions = computed(() => {
  return questions.value.filter(q => {
    if (filterType.value && q.type !== filterType.value) return false
    if (filterDifficulty.value && q.difficulty !== filterDifficulty.value) return false
    if (searchKeyword.value && !q.question.includes(searchKeyword.value)) return false
    return true
  })
})

const getTypeLabel = (type) => {
  const labels = { single: '单选题', multiple: '多选题', judge: '判断题', fill: '填空题' }
  return labels[type] || type
}

const formatAnswer = (question) => {
  if (question.type === 'judge') return question.answer ? '正确' : '错误'
  if (Array.isArray(question.answer)) return question.answer.join('、')
  return question.answer
}

const isCorrectOption = (question, option) => {
  const letter = option.charAt(0)
  if (question.type === 'single') return question.answer === letter
  if (question.type === 'multiple' && Array.isArray(question.answer)) {
    return question.answer.includes(letter)
  }
  return false
}

const fetchBank = async () => {
  loading.value = true
  try {
    bank.value = await bankApi.get(bankId)
    questions.value = await bankApi.getQuestions(bankId)
    // 检查收藏状态
    await checkFavoriteStatus()
  } catch (error) {
    console.error('获取题库失败:', error)
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
      await favoriteApi.add(bankId, question.id)
      favoriteStatus.value[question.id] = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    console.error('收藏操作失败:', error)
  }
}

const showAddDialog = () => {
  isEditing.value = false
  editingId.value = null
  questionForm.value = {
    type: 'single',
    question: '',
    options: ['', '', '', ''],
    answer: '',
    answerArray: [],
    answerBool: true,
    difficulty: 3,
    explanation: ''
  }
  dialogVisible.value = true
}

const showEditDialog = (question) => {
  isEditing.value = true
  editingId.value = question.id
  questionForm.value = {
    type: question.type,
    question: question.question,
    options: question.options?.length ? [...question.options] : ['', '', '', ''],
    answer: typeof question.answer === 'string' ? question.answer : '',
    answerArray: Array.isArray(question.answer) ? [...question.answer] : [],
    answerBool: typeof question.answer === 'boolean' ? question.answer : true,
    difficulty: question.difficulty,
    explanation: question.explanation || ''
  }
  dialogVisible.value = true
}

const addOption = () => {
  if (questionForm.value.options.length < 6) {
    questionForm.value.options.push('')
  }
}

const removeOption = (index) => {
  if (questionForm.value.options.length > 2) {
    questionForm.value.options.splice(index, 1)
  }
}

const submitQuestion = async () => {
  if (!questionFormRef.value) return
  
  await questionFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    // 构建提交数据
    const data = {
      type: questionForm.value.type,
      question: questionForm.value.question,
      options: ['single', 'multiple'].includes(questionForm.value.type) 
        ? questionForm.value.options.filter(o => o.trim())
        : [],
      difficulty: questionForm.value.difficulty,
      explanation: questionForm.value.explanation
    }
    
    // 处理答案
    if (questionForm.value.type === 'single') {
      data.answer = questionForm.value.answer
    } else if (questionForm.value.type === 'multiple') {
      data.answer = questionForm.value.answerArray
    } else if (questionForm.value.type === 'judge') {
      data.answer = questionForm.value.answerBool
    } else {
      data.answer = questionForm.value.answer
    }
    
    submitting.value = true
    try {
      if (isEditing.value) {
        await bankApi.updateQuestion(bankId, editingId.value, data)
        ElMessage.success('更新成功')
      } else {
        await bankApi.addQuestion(bankId, data)
        ElMessage.success('添加成功')
      }
      dialogVisible.value = false
      fetchBank()
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteQuestion = async (questionId) => {
  try {
    await bankApi.deleteQuestion(bankId, questionId)
    ElMessage.success('删除成功')
    fetchBank()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

onMounted(() => {
  fetchBank()
})
</script>

<style lang="scss" scoped>
.bank-detail-view {
  .header-left {
    display: flex;
    align-items: center;
    gap: 10px;
    
    h1 {
      margin: 0;
    }
  }
  
  .stats-row {
    margin-bottom: 20px;
  }
  
  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #ebeef5;
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
  
  .options-editor {
    width: 100%;
    
    .option-row {
      display: flex;
      gap: 10px;
      margin-bottom: 10px;
      
      .el-input {
        flex: 1;
      }
    }
  }
}
</style>
