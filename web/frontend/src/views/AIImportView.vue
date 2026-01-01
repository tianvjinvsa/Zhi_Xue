<template>
  <div class="ai-import-view">
    <div class="page-header">
      <div class="title-section">
        <h1><el-icon><MagicStick /></el-icon>AI 智能导入</h1>
        <p class="subtitle">利用大模型能力，快速将各种格式的题目转化为系统题库</p>
      </div>
    </div>

    <div class="import-methods-card">
      <el-tabs v-model="activeTab" class="import-tabs">
        <!-- 文件导入 -->
        <el-tab-pane name="file">
          <template #label>
            <span class="tab-label">
              <el-icon><Files /></el-icon>文件解析
            </span>
          </template>
          <div class="tab-content">
            <div class="method-intro">
              <h3>📁 智能文件解析</h3>
              <p>支持 Word、Excel、TXT 及图片格式，AI 将自动识别题目、选项及答案</p>
            </div>
            
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
                <el-icon class="upload-icon"><UploadFilled /></el-icon>
                <div class="upload-text">将文件拖到此处，或<em>点击上传</em></div>
                <div class="upload-hint">支持 Word / Excel / TXT / 图片 (最大 10MB)</div>
              </div>
              <div v-else class="selected-file-info">
                <div class="file-card">
                  <el-icon class="file-icon" :class="getFileIconClass(selectedFile.name)">
                    <component :is="getFileIcon(selectedFile.name)" />
                  </el-icon>
                  <div class="file-details">
                    <div class="file-name">{{ selectedFile.name }}</div>
                    <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
                  </div>
                  <el-button type="danger" circle @click.stop="clearSelectedFile">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </el-upload>
            
            <div class="action-bar">
              <el-button 
                type="primary" 
                size="large"
                @click="parseFile"
                :loading="parsingFile"
                :disabled="!selectedFile"
                class="main-action-btn"
              >
                <el-icon><MagicStick /></el-icon>开始 AI 解析
              </el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- 文本导入 -->
        <el-tab-pane name="text">
          <template #label>
            <span class="tab-label">
              <el-icon><EditPen /></el-icon>文本解析
            </span>
          </template>
          <div class="tab-content">
            <div class="method-intro">
              <h3>📝 文本内容解析</h3>
              <p>直接粘贴题目文本，AI 将自动识别并解析为标准格式</p>
            </div>
            
            <el-input 
              v-model="textContent"
              type="textarea"
              :rows="12"
              placeholder="请粘贴题目内容，支持多道题目批量导入...

示例格式：
1. 以下哪项是正确的？
A. 选项一
B. 选项二
答案：A"
              class="text-import-input"
            />
            
            <div class="action-bar">
              <el-button 
                type="primary" 
                size="large"
                @click="parseText"
                :loading="parsing"
                :disabled="!textContent.trim()"
                class="main-action-btn"
              >
                <el-icon><MagicStick /></el-icon>开始 AI 解析
              </el-button>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- AI 生成 -->
        <el-tab-pane name="generate">
          <template #label>
            <span class="tab-label">
              <el-icon><Cpu /></el-icon>AI 自动生成
            </span>
          </template>
          <div class="tab-content">
            <div class="method-intro">
              <h3>🤖 知识点自动出题</h3>
              <p>输入知识点或主题，AI 将根据您的要求自动生成高质量题目</p>
            </div>
            
            <div class="generate-form-container">
              <el-form :model="generateForm" label-position="top">
                <el-row :gutter="40">
                  <el-col :span="14">
                    <el-form-item label="知识点/主题">
                      <el-input 
                        v-model="generateForm.topic"
                        type="textarea"
                        :rows="6"
                        placeholder="例如：Python 基础语法、中国近代史、高中数学函数..."
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="10">
                    <el-form-item label="题目类型">
                      <el-checkbox-group v-model="generateForm.types" class="type-checkbox-group">
                        <el-checkbox value="single">单选题</el-checkbox>
                        <el-checkbox value="multiple">多选题</el-checkbox>
                        <el-checkbox value="judge">判断题</el-checkbox>
                      </el-checkbox-group>
                    </el-form-item>
                    
                    <div class="form-row">
                      <el-form-item label="生成数量" style="flex: 1">
                        <el-input-number v-model="generateForm.count" :min="1" :max="20" style="width: 100%" />
                      </el-form-item>
                      <el-form-item label="难度" style="flex: 1">
                        <el-select v-model="generateForm.difficulty" style="width: 100%">
                          <el-option label="简单" :value="1" />
                          <el-option label="中等" :value="3" />
                          <el-option label="困难" :value="5" />
                        </el-select>
                      </el-form-item>
                    </div>
                  </el-col>
                </el-row>
              </el-form>
            </div>
            
            <div class="action-bar">
              <el-button 
                type="success" 
                size="large"
                @click="generateQuestions"
                :loading="generating"
                :disabled="!generateForm.topic.trim()"
                class="main-action-btn"
              >
                <el-icon><MagicStick /></el-icon>开始 AI 生成
              </el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 解析结果 -->
    <div v-if="parsedQuestions.length > 0" class="result-section">
      <div class="result-header">
        <div class="header-left">
          <span class="result-count">
            已解析 <strong>{{ parsedQuestions.length }}</strong> 道题目
          </span>
          <el-checkbox 
            v-model="isAllSelected" 
            :indeterminate="isIndeterminate"
            @change="handleSelectAll"
            class="select-all-checkbox"
          >
            全选
          </el-checkbox>
        </div>
        <div class="header-right">
          <el-button type="danger" plain @click="batchDelete" :disabled="selectedCount === 0">
            批量删除 ({{ selectedCount }})
          </el-button>
          <el-button type="primary" @click="showImportDialog" :disabled="selectedCount === 0">
            导入到题库 ({{ selectedCount }})
          </el-button>
        </div>
      </div>

      <div class="questions-list">
        <div 
          v-for="(question, index) in parsedQuestions" 
          :key="index" 
          class="question-item-card"
          :class="{ selected: question.selected }"
        >
          <div class="q-checkbox">
            <el-checkbox v-model="question.selected" @change="updateSelectState" />
          </div>
          <div class="q-content">
            <div class="q-header">
              <el-tag size="small" :type="getTypeTag(question.type)">{{ getTypeLabel(question.type) }}</el-tag>
              <el-rate v-model="question.difficulty" disabled />
              <div class="q-actions">
                <el-button link type="primary" @click="editQuestion(index)">编辑</el-button>
                <el-button link type="danger" @click="removeQuestion(index)">删除</el-button>
              </div>
            </div>
            <div class="q-text">{{ question.question }}</div>
            <div v-if="question.options?.length" class="q-options">
              <div 
                v-for="(opt, optIdx) in question.options" 
                :key="optIdx"
                class="q-option"
                :class="{ 'is-answer': isCorrectOption(question, optIdx) }"
              >
                <span class="opt-label">{{ String.fromCharCode(65 + optIdx) }}</span>
                <span class="opt-text">{{ opt }}</span>
              </div>
            </div>
            <div class="q-footer">
              <div class="q-answer">
                <strong>正确答案：</strong>
                <span class="answer-text">{{ formatAnswer(question) }}</span>
              </div>
              <div v-if="question.explanation" class="q-analysis">
                <strong>解析：</strong>{{ question.explanation }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入到题库" width="500px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="选择目标题库" required>
          <el-select 
            v-model="targetBankId" 
            placeholder="请选择题库" 
            style="width: 100%"
            @change="loadTargetBankChapters"
          >
            <el-option 
              v-for="bank in banks" 
              :key="bank.id" 
              :label="bank.name" 
              :value="bank.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择章节（可选）">
          <el-select 
            v-model="targetChapter" 
            placeholder="可选择已有章节或留空" 
            style="width: 100%"
            clearable
            filterable
            allow-create
            :disabled="!targetBankId"
          >
            <el-option 
              v-for="chapter in targetBankChapters" 
              :key="chapter" 
              :label="chapter" 
              :value="chapter" 
            />
          </el-select>
          <div class="form-tip">可从已有章节中选择，或输入新章节名称</div>
        </el-form-item>
        <div class="import-summary">
          将导入 <strong>{{ selectedCount }}</strong> 道题目到所选题库。
        </div>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport" :loading="importing" :disabled="!targetBankId">
          确认导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑题目" width="650px" destroy-on-close>
      <el-form v-if="editingQuestion" :model="editingQuestion" label-width="80px">
        <el-form-item label="题目类型">
          <el-select v-model="editingQuestion.type" style="width: 100%">
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="判断题" value="judge" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目内容">
          <el-input v-model="editingQuestion.question" type="textarea" :rows="3" />
        </el-form-item>
        
        <template v-if="editingQuestion.type !== 'judge'">
          <el-form-item 
            v-for="(opt, idx) in editingQuestion.options" 
            :key="idx" 
            :label="'选项 ' + String.fromCharCode(65 + idx)"
          >
            <div class="option-edit-row">
              <el-input v-model="editingQuestion.options[idx]" />
              <el-checkbox 
                v-if="editingQuestion.type === 'multiple'"
                v-model="editingQuestion.answer"
                :label="String.fromCharCode(65 + idx)"
              >正确</el-checkbox>
              <el-radio 
                v-else
                v-model="editingQuestion.answer"
                :label="String.fromCharCode(65 + idx)"
              >正确</el-radio>
              <el-button type="danger" link @click="editingQuestion.options.splice(idx, 1)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </el-form-item>
          <el-button type="primary" link @click="editingQuestion.options.push('')" style="margin-left: 80px">
            <el-icon><Plus /></el-icon>添加选项
          </el-button>
        </template>
        
        <el-form-item v-else label="正确答案">
          <el-radio-group v-model="editingQuestion.answer">
            <el-radio label="正确">正确</el-radio>
            <el-radio label="错误">错误</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="题目解析">
          <el-input v-model="editingQuestion.explanation" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="难度">
          <el-rate v-model="editingQuestion.difficulty" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  MagicStick, UploadFilled, Files, EditPen, Cpu, 
  Delete, Plus, Document, Notebook, Picture 
} from '@element-plus/icons-vue'
import { aiApi, bankApi } from '@/api'

const activeTab = ref('file')
const textContent = ref('')
const selectedFile = ref(null)
const uploadRef = ref(null)
const parsing = ref(false)
const parsingFile = ref(false)
const generating = ref(false)
const parsedQuestions = ref([])
const banks = ref([])
const importDialogVisible = ref(false)
const targetBankId = ref('')
const targetChapter = ref('')
const importing = ref(false)

// 编辑相关
const editDialogVisible = ref(false)
const editingQuestion = ref(null)
const editingIndex = ref(-1)

// 目标题库的章节列表
const targetBankChapters = ref([])

const generateForm = reactive({
  topic: '',
  count: 5,
  difficulty: 3,
  types: ['single']
})

// 会话存储的key
const STORAGE_KEY = 'ai_import_parsed_questions'

// 从sessionStorage恢复数据
const restoreFromStorage = () => {
  try {
    const saved = sessionStorage.getItem(STORAGE_KEY)
    if (saved) {
      const data = JSON.parse(saved)
      if (Array.isArray(data) && data.length > 0) {
        parsedQuestions.value = data
        ElMessage.success(`已恢复 ${data.length} 道未导入的题目`)
      }
    }
  } catch (error) {
    console.error('恢复数据失败:', error)
  }
}

// 保存到sessionStorage
const saveToStorage = () => {
  try {
    if (parsedQuestions.value.length > 0) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(parsedQuestions.value))
    } else {
      sessionStorage.removeItem(STORAGE_KEY)
    }
  } catch (error) {
    console.error('保存数据失败:', error)
  }
}

// 监听解析结果变化并保存
watch(parsedQuestions, () => {
  saveToStorage()
}, { deep: true })

// 选择逻辑
const isAllSelected = ref(false)
const selectedCount = computed(() => parsedQuestions.value.filter(q => q.selected).length)
const isIndeterminate = computed(() => {
  return selectedCount.value > 0 && selectedCount.value < parsedQuestions.value.length
})

const handleSelectAll = (val) => {
  parsedQuestions.value.forEach(q => q.selected = val)
}

const updateSelectState = () => {
  isAllSelected.value = selectedCount.value === parsedQuestions.value.length
}

const getTypeLabel = (type) => {
  const labels = { single: '单选题', multiple: '多选题', judge: '判断题' }
  return labels[type] || type
}

const getTypeTag = (type) => {
  const tags = { single: '', multiple: 'success', judge: 'warning' }
  return tags[type] || ''
}

const isCorrectOption = (question, idx) => {
  const label = String.fromCharCode(65 + idx)
  if (Array.isArray(question.answer)) {
    return question.answer.includes(label)
  }
  return question.answer === label
}

const formatAnswer = (question) => {
  if (Array.isArray(question.answer)) return question.answer.join(', ')
  return question.answer
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const clearSelectedFile = () => {
  selectedFile.value = null
  if (uploadRef.value) uploadRef.value.clearFiles()
}

const getFileIcon = (name) => {
  if (name.match(/\.(docx?)$/i)) return Document
  if (name.match(/\.(xlsx?)$/i)) return Notebook
  if (name.match(/\.(png|jpe?g|gif|webp)$/i)) return Picture
  return Document
}

const getFileIconClass = (name) => {
  if (name.match(/\.(docx?)$/i)) return 'icon-word'
  if (name.match(/\.(xlsx?)$/i)) return 'icon-excel'
  if (name.match(/\.(png|jpe?g|gif|webp)$/i)) return 'icon-image'
  return ''
}

const formatFileSize = (size) => {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

const parseText = async () => {
  parsing.value = true
  try {
    const result = await aiApi.parse(textContent.value)
    const questions = result.questions || []
    addParsedQuestions(questions)
    ElMessage.success(`成功解析 ${questions.length} 道题目`)
  } catch (error) {
    ElMessage.error('解析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    parsing.value = false
  }
}

const parseFile = async () => {
  if (!selectedFile.value) return
  parsingFile.value = true
  try {
    const result = await aiApi.parseFile(selectedFile.value)
    const questions = result.questions || []
    addParsedQuestions(questions)
    ElMessage.success(`成功解析 ${questions.length} 道题目`)
  } catch (error) {
    ElMessage.error('解析失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    parsingFile.value = false
  }
}

const generateQuestions = async () => {
  generating.value = true
  try {
    const result = await aiApi.generate({
      topic: generateForm.topic,
      count: generateForm.count,
      difficulty_min: Math.max(1, generateForm.difficulty - 1),
      difficulty_max: Math.min(5, generateForm.difficulty + 1),
      type_distribution: generateForm.types.join(',')
    })
    const questions = result.questions || []
    addParsedQuestions(questions)
    ElMessage.success(`成功生成 ${questions.length} 道题目`)
  } catch (error) {
    ElMessage.error('生成失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    generating.value = false
  }
}

const addParsedQuestions = (questions) => {
  if (!Array.isArray(questions)) return
  const newQuestions = questions.map(q => ({
    ...q,
    selected: true,
    difficulty: q.difficulty || 3
  }))
  parsedQuestions.value = [...newQuestions, ...parsedQuestions.value]
  updateSelectState()
}

const removeQuestion = (index) => {
  parsedQuestions.value.splice(index, 1)
  updateSelectState()
}

const batchDelete = () => {
  ElMessageBox.confirm(`确定删除选中的 ${selectedCount.value} 道题目吗？`, '提示', {
    type: 'warning'
  }).then(() => {
    parsedQuestions.value = parsedQuestions.value.filter(q => !q.selected)
    updateSelectState()
  })
}

const editQuestion = (index) => {
  editingIndex.value = index
  editingQuestion.value = JSON.parse(JSON.stringify(parsedQuestions.value[index]))
  editDialogVisible.value = true
}

const saveEdit = () => {
  parsedQuestions.value[editingIndex.value] = editingQuestion.value
  editDialogVisible.value = false
  ElMessage.success('修改已保存')
}

const showImportDialog = async () => {
  importDialogVisible.value = true
  targetBankId.value = ''
  targetChapter.value = ''
  targetBankChapters.value = []
  try {
    banks.value = await bankApi.getAll()
  } catch (error) {
    console.error('获取题库失败:', error)
  }
}

// 监听目标题库变化，加载章节
const loadTargetBankChapters = async () => {
  if (!targetBankId.value) {
    targetBankChapters.value = []
    return
  }
  try {
    const result = await bankApi.getChapters(targetBankId.value)
    targetBankChapters.value = result.chapters || []
  } catch (error) {
    targetBankChapters.value = []
  }
}

const confirmImport = async () => {
  importing.value = true
  try {
    const selectedQuestions = parsedQuestions.value
      .filter(q => q.selected)
      .map(q => ({
        ...q,
        chapter: targetChapter.value || q.chapter || ''
      }))
    await bankApi.batchAddQuestions(targetBankId.value, selectedQuestions)
    ElMessage.success('导入成功')
    parsedQuestions.value = parsedQuestions.value.filter(q => !q.selected)
    importDialogVisible.value = false
    targetBankId.value = ''
    targetChapter.value = ''
    updateSelectState()
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  // 恢复之前未导入的题目
  restoreFromStorage()
  try {
    banks.value = await bankApi.getAll()
  } catch (error) {}
})
</script>

<style lang="scss" scoped>
.ai-import-view {
  .page-header {
    margin-bottom: 32px;
    .title-section {
      h1 {
        margin: 0;
        font-size: 28px;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #1a1a1a;
        .el-icon { color: #409eff; }
      }
      .subtitle {
        margin: 8px 0 0;
        color: #909399;
        font-size: 14px;
      }
    }
  }

  .import-methods-card {
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    margin-bottom: 32px;

    .import-tabs {
      :deep(.el-tabs__header) {
        margin-bottom: 32px;
      }
      :deep(.el-tabs__nav-wrap::after) {
        height: 1px;
      }
      .tab-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        padding: 0 8px;
      }
    }

    .tab-content {
      max-width: 900px;
      margin: 0 auto;

      .method-intro {
        text-align: center;
        margin-bottom: 32px;
        h3 { margin: 0 0 8px; font-size: 20px; color: #303133; }
        p { margin: 0; color: #909399; font-size: 14px; }
      }
    }
  }

  .file-upload-area {
    :deep(.el-upload-dragger) {
      border-radius: 12px;
      padding: 40px;
      background: #fcfdfe;
      border: 2px dashed #dcdfe6;
      &:hover {
        border-color: #409eff;
        background: #f5f9ff;
      }
    }

    .upload-placeholder {
      .upload-icon {
        font-size: 48px;
        color: #c0c4cc;
        margin-bottom: 16px;
      }
      .upload-text {
        font-size: 16px;
        color: #606266;
        em { color: #409eff; font-style: normal; font-weight: 600; }
      }
      .upload-hint {
        margin-top: 12px;
        font-size: 13px;
        color: #909399;
      }
    }

    .selected-file-info {
      .file-card {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        background: #fff;
        border: 1px solid #ebeef5;
        border-radius: 8px;
        text-align: left;

        .file-icon {
          font-size: 32px;
          &.icon-word { color: #2b579a; }
          &.icon-excel { color: #217346; }
          &.icon-image { color: #e6a23c; }
        }

        .file-details {
          flex: 1;
          .file-name { font-weight: 600; color: #303133; margin-bottom: 4px; }
          .file-size { font-size: 12px; color: #909399; }
        }
      }
    }
  }

  .text-import-input {
    :deep(.el-textarea__inner) {
      border-radius: 12px;
      padding: 16px;
      background: #fcfdfe;
      font-family: monospace;
    }
  }

  .generate-form-container {
    background: #f8f9fa;
    padding: 24px;
    border-radius: 12px;
    
    .type-checkbox-group {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-top: 8px;
    }

    .form-row {
      display: flex;
      gap: 20px;
      margin-top: 20px;
    }
  }

  .action-bar {
    margin-top: 32px;
    display: flex;
    justify-content: center;
    .main-action-btn {
      padding: 12px 48px;
      font-weight: 600;
      border-radius: 8px;
      height: auto;
    }
  }

  .result-section {
    .result-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding: 0 4px;

      .header-left {
        display: flex;
        align-items: center;
        gap: 24px;
        .result-count {
          font-size: 16px;
          color: #606266;
          strong { color: #409eff; font-size: 20px; }
        }
      }
    }

    .questions-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .question-item-card {
      display: flex;
      gap: 16px;
      padding: 20px;
      background: #fff;
      border: 1px solid #ebeef5;
      border-radius: 12px;
      transition: all 0.2s;

      &:hover {
        border-color: #409eff;
        box-shadow: 0 4px 12px rgba(64,158,255,0.08);
      }

      &.selected {
        background: #f0f7ff;
        border-color: #409eff;
      }

      .q-checkbox {
        padding-top: 4px;
      }

      .q-content {
        flex: 1;
        .q-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
          .q-actions {
            margin-left: auto;
          }
        }
        .q-text {
          font-size: 16px;
          font-weight: 500;
          color: #303133;
          line-height: 1.6;
          margin-bottom: 16px;
        }
        .q-options {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
          gap: 12px;
          margin-bottom: 16px;

          .q-option {
            display: flex;
            gap: 8px;
            padding: 10px 16px;
            background: #f8f9fa;
            border-radius: 6px;
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
            }
          }
        }
        .q-footer {
          padding-top: 16px;
          border-top: 1px dashed #ebeef5;
          font-size: 14px;
          .q-answer {
            margin-bottom: 8px;
            .answer-text { color: #67c23a; font-weight: 600; }
          }
          .q-analysis {
            color: #909399;
            line-height: 1.5;
          }
        }
      }
    }
  }
}

.option-edit-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.import-summary {
  margin-top: 16px;
  padding: 12px;
  background: #f0f7ff;
  border-radius: 6px;
  color: #409eff;
  font-size: 14px;
}
</style>
