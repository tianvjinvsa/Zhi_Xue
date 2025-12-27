<template>
  <div class="ai-import-view">
    <div class="page-header">
      <h1><el-icon><MagicStick /></el-icon>AI智能导入</h1>
    </div>

    <el-row :gutter="20">
      <!-- 文件导入 -->
      <el-col :span="24" style="margin-bottom: 20px;">
        <div class="card-container">
          <h3>📁 文件导入</h3>
          <p class="hint">支持导入 Word、Excel、TXT、图片格式的题目文件，AI将自动识别并解析</p>
          
          <el-upload
            ref="uploadRef"
            class="file-upload-area"
            drag
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
            accept=".txt,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.gif,.webp"
          >
            <div v-if="!selectedFile" class="upload-placeholder">
              <el-icon class="upload-icon"><Upload /></el-icon>
              <div class="upload-text">将文件拖到此处，或<em>点击上传</em></div>
              <div class="upload-hint">支持 Word(.docx) / Excel(.xlsx) / 文本(.txt) / 图片(.png/.jpg)</div>
            </div>
            <div v-else class="selected-file-info">
              <el-icon class="file-icon" :class="getFileIconClass(selectedFile.name)">
                <component :is="getFileIcon(selectedFile.name)" />
              </el-icon>
              <div class="file-details">
                <div class="file-name">{{ selectedFile.name }}</div>
                <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
              </div>
              <el-button type="danger" text @click.stop="clearSelectedFile">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </el-upload>
          
          <el-button 
            type="primary" 
            style="width: 100%; margin-top: 15px"
            @click="parseFile"
            :loading="parsingFile"
            :disabled="!selectedFile"
          >
            <el-icon><MagicStick /></el-icon>
            AI解析文件
          </el-button>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="card-container">
          <h3>📝 文本导入</h3>
          <p class="hint">粘贴题目文本，AI将自动识别并解析为标准格式</p>
          
          <el-input 
            v-model="textContent"
            type="textarea"
            :rows="15"
            placeholder="请粘贴题目内容，支持多道题目批量导入...

示例格式：
1. 以下哪项是正确的？
A. 选项一
B. 选项二
C. 选项三
D. 选项四
答案：A

2. 判断题：地球是圆的。（✓）"
          />
          
          <el-button 
            type="primary" 
            style="width: 100%; margin-top: 15px"
            @click="parseText"
            :loading="parsing"
            :disabled="!textContent.trim()"
          >
            <el-icon><MagicStick /></el-icon>
            AI解析
          </el-button>
        </div>
      </el-col>
      
      <el-col :span="12">
        <div class="card-container">
          <h3>🤖 AI生成题目</h3>
          <p class="hint">输入知识点或主题，AI将自动生成题目</p>
          
          <el-form :model="generateForm" label-width="100px">
            <el-form-item label="知识点/主题">
              <el-input 
                v-model="generateForm.topic"
                type="textarea"
                :rows="3"
                placeholder="例如：Python基础语法、中国近代史、高中数学函数..."
              />
            </el-form-item>
            
            <el-form-item label="生成数量">
              <el-input-number v-model="generateForm.count" :min="1" :max="20" />
            </el-form-item>
            
            <el-form-item label="难度范围">
              <el-slider 
                v-model="generateForm.difficultyRange" 
                range 
                :min="1" 
                :max="5"
                :marks="{ 1: '简单', 3: '中等', 5: '困难' }"
              />
            </el-form-item>
            
            <el-form-item label="题目类型">
              <el-checkbox-group v-model="generateForm.types">
                <el-checkbox value="single">单选题</el-checkbox>
                <el-checkbox value="multiple">多选题</el-checkbox>
                <el-checkbox value="judge">判断题</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-form>
          
          <el-button 
            type="success" 
            style="width: 100%"
            @click="generateQuestions"
            :loading="generating"
            :disabled="!generateForm.topic.trim()"
          >
            <el-icon><MagicStick /></el-icon>
            AI生成
          </el-button>
        </div>
      </el-col>
    </el-row>

    <!-- 解析结果 -->
    <div v-if="parsedQuestions.length > 0" class="card-container result-section">
      <div class="result-header">
        <h3>🎉 解析结果（{{ parsedQuestions.length }} 道题目）</h3>
        <div class="actions">
          <el-select v-model="targetBankId" placeholder="选择目标题库" style="width: 200px">
            <el-option 
              v-for="bank in banks" 
              :key="bank.id" 
              :label="bank.name" 
              :value="bank.id" 
            />
          </el-select>
          <el-button type="primary" @click="importToBank" :disabled="!targetBankId" :loading="importing">
            导入到题库
          </el-button>
        </div>
      </div>
      
      <div class="parsed-questions">
        <div 
          v-for="(question, index) in parsedQuestions" 
          :key="index"
          class="question-card"
        >
          <div class="question-header">
            <div class="question-info">
              <span class="question-number">{{ index + 1 }}</span>
              <el-tag :class="['question-type-tag', question.type]" size="small">
                {{ getTypeLabel(question.type) }}
              </el-tag>
              <div class="difficulty-stars">
                <el-rate v-model="question.difficulty" :max="5" size="small" />
              </div>
            </div>
            <el-button type="danger" text size="small" @click="removeQuestion(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          
          <div class="question-content">{{ question.question }}</div>
          
          <div v-if="question.options?.length" class="question-options">
            <div v-for="option in question.options" :key="option" class="option-item">
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { aiApi, bankApi } from '@/api'
import { Upload, Delete, Document, Picture } from '@element-plus/icons-vue'

const textContent = ref('')
const parsing = ref(false)
const parsingFile = ref(false)
const generating = ref(false)
const importing = ref(false)
const parsedQuestions = ref([])
const banks = ref([])
const targetBankId = ref('')
const selectedFile = ref(null)
const uploadRef = ref(null)

const generateForm = ref({
  topic: '',
  count: 5,
  difficultyRange: [2, 4],
  types: ['single', 'multiple', 'judge']
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

const formatFileSize = (size) => {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

const getFileIcon = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext)) return Picture
  return Document
}

const getFileIconClass = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  if (['doc', 'docx'].includes(ext)) return 'word-icon'
  if (['xls', 'xlsx'].includes(ext)) return 'excel-icon'
  if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext)) return 'image-icon'
  return 'text-icon'
}

const handleFileChange = (uploadFile) => {
  selectedFile.value = uploadFile.raw
}

const clearSelectedFile = () => {
  selectedFile.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const parseFile = async () => {
  if (!selectedFile.value) return
  
  parsingFile.value = true
  try {
    const result = await aiApi.parseFile(selectedFile.value)
    parsedQuestions.value = result.questions || []
    if (parsedQuestions.value.length === 0) {
      ElMessage.warning('未能从文件中解析出题目')
    } else {
      ElMessage.success(`成功解析 ${parsedQuestions.value.length} 道题目`)
      clearSelectedFile()
    }
  } catch (error) {
    console.error('文件解析失败:', error)
  } finally {
    parsingFile.value = false
  }
}

const fetchBanks = async () => {
  try {
    banks.value = await bankApi.getAll()
  } catch (error) {
    console.error('获取题库列表失败:', error)
  }
}

const parseText = async () => {
  parsing.value = true
  try {
    const result = await aiApi.parse(textContent.value)
    parsedQuestions.value = result.questions || []
    if (parsedQuestions.value.length === 0) {
      ElMessage.warning('未能解析出题目，请检查格式')
    } else {
      ElMessage.success(`成功解析 ${parsedQuestions.value.length} 道题目`)
    }
  } catch (error) {
    console.error('解析失败:', error)
  } finally {
    parsing.value = false
  }
}

const generateQuestions = async () => {
  generating.value = true
  try {
    const typeLabels = generateForm.value.types.map(t => getTypeLabel(t)).join('、')
    const result = await aiApi.generate({
      topic: generateForm.value.topic,
      count: generateForm.value.count,
      type_distribution: `题型包括：${typeLabels}`,
      difficulty_min: generateForm.value.difficultyRange[0],
      difficulty_max: generateForm.value.difficultyRange[1]
    })
    parsedQuestions.value = result.questions || []
    if (parsedQuestions.value.length === 0) {
      ElMessage.warning('生成失败，请重试')
    } else {
      ElMessage.success(`成功生成 ${parsedQuestions.value.length} 道题目`)
    }
  } catch (error) {
    console.error('生成失败:', error)
  } finally {
    generating.value = false
  }
}

const removeQuestion = (index) => {
  parsedQuestions.value.splice(index, 1)
}

const importToBank = async () => {
  if (!targetBankId.value || parsedQuestions.value.length === 0) return
  
  importing.value = true
  let successCount = 0
  
  try {
    for (const question of parsedQuestions.value) {
      try {
        await bankApi.addQuestion(targetBankId.value, question)
        successCount++
      } catch (e) {
        console.error('导入单题失败:', e)
      }
    }
    
    if (successCount > 0) {
      ElMessage.success(`成功导入 ${successCount} 道题目`)
      parsedQuestions.value = []
    } else {
      ElMessage.error('导入失败')
    }
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  fetchBanks()
})
</script>

<style lang="scss" scoped>
.ai-import-view {
  .hint {
    color: #909399;
    font-size: 14px;
    margin-bottom: 15px;
  }
  
  h3 {
    margin: 0 0 10px;
    color: #303133;
  }
  
  .file-upload-area {
    width: 100%;
    
    :deep(.el-upload) {
      width: 100%;
    }
    
    :deep(.el-upload-dragger) {
      width: 100%;
      height: auto;
      min-height: 120px;
      padding: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
  
  .upload-placeholder {
    text-align: center;
    
    .upload-icon {
      font-size: 48px;
      color: #c0c4cc;
      margin-bottom: 10px;
    }
    
    .upload-text {
      color: #606266;
      font-size: 14px;
      
      em {
        color: #409eff;
        font-style: normal;
      }
    }
    
    .upload-hint {
      color: #909399;
      font-size: 12px;
      margin-top: 8px;
    }
  }
  
  .selected-file-info {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 10px;
    
    .file-icon {
      font-size: 40px;
      
      &.word-icon { color: #2b579a; }
      &.excel-icon { color: #217346; }
      &.image-icon { color: #ff9800; }
      &.text-icon { color: #607d8b; }
    }
    
    .file-details {
      flex: 1;
      text-align: left;
      
      .file-name {
        font-size: 14px;
        font-weight: 600;
        color: #303133;
        word-break: break-all;
      }
      
      .file-size {
        font-size: 12px;
        color: #909399;
        margin-top: 4px;
      }
    }
  }
  
  .result-section {
    margin-top: 20px;
    
    .result-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 1px solid #ebeef5;
      
      h3 {
        margin: 0;
      }
      
      .actions {
        display: flex;
        gap: 10px;
      }
    }
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
}
</style>
