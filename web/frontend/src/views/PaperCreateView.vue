<template>
  <div class="paper-create-view">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="$router.push('/papers')" text>
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
        <h1><el-icon><Document /></el-icon>生成试卷</h1>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧配置表单 -->
      <el-col :span="14">
        <div class="card-container">
          <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
            <el-divider content-position="left">
              <el-icon><Document /></el-icon> 基本信息
            </el-divider>
            
            <el-form-item label="试卷名称" prop="title">
              <el-input v-model="form.title" placeholder="请输入试卷名称" />
            </el-form-item>
            
            <el-form-item label="描述">
              <el-input 
                v-model="form.description" 
                type="textarea" 
                :rows="2"
                placeholder="请输入试卷描述（可选）" 
              />
            </el-form-item>
            
            <el-form-item label="答题时限">
              <el-input-number 
                v-model="form.time_limit" 
                :min="0" 
                :max="300"
                :step="10"
              />
              <span class="form-hint">分钟（0 表示不限时）</span>
            </el-form-item>
            
            <el-divider content-position="left">
              <el-icon><Folder /></el-icon> 选择题库
            </el-divider>
            
            <el-form-item label="来源题库" prop="bank_ids">
              <el-checkbox-group v-model="form.bank_ids">
                <el-checkbox 
                  v-for="bank in banks" 
                  :key="bank.id" 
                  :value="bank.id"
                  :disabled="bank.question_count === 0"
                >
                  {{ bank.name }}
                  <el-tag size="small" type="info">{{ bank.question_count || 0 }} 题</el-tag>
                </el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-divider content-position="left">
              <el-icon><List /></el-icon> 题目数量
            </el-divider>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="单选题">
                  <el-input-number v-model="form.single_count" :min="0" :max="50" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="多选题">
                  <el-input-number v-model="form.multiple_count" :min="0" :max="50" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="判断题">
                  <el-input-number v-model="form.judge_count" :min="0" :max="50" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="填空题">
                  <el-input-number v-model="form.fill_count" :min="0" :max="50" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-divider content-position="left">
              <el-icon><Star /></el-icon> 难度范围
            </el-divider>
            
            <el-form-item label="难度">
              <div class="difficulty-slider-wrapper">
                <el-slider 
                  v-model="difficultyRange" 
                  range 
                  :min="1" 
                  :max="5" 
                  :marks="difficultyMarks"
                  class="difficulty-slider"
                />
              </div>
            </el-form-item>
            
            <el-divider content-position="left">
              <el-icon><Coin /></el-icon> 分值设置
            </el-divider>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="单选题分值">
                  <el-input-number v-model="form.score_rules.single" :min="1" :max="20" :precision="1" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="多选题分值">
                  <el-input-number v-model="form.score_rules.multiple" :min="1" :max="20" :precision="1" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="判断题分值">
                  <el-input-number v-model="form.score_rules.judge" :min="1" :max="20" :precision="1" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="填空题分值">
                  <el-input-number v-model="form.score_rules.fill" :min="1" :max="20" :precision="1" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
      </el-col>
      
      <!-- 右侧预览 -->
      <el-col :span="10">
        <div class="card-container preview-panel">
          <h3><el-icon><View /></el-icon> 试卷预览</h3>
          
          <div class="preview-info">
            <div class="info-item">
              <span class="label">试卷名称</span>
              <span class="value">{{ form.title || '未命名试卷' }}</span>
            </div>
            <div class="info-item">
              <span class="label">答题时限</span>
              <span class="value">{{ form.time_limit ? `${form.time_limit} 分钟` : '不限时' }}</span>
            </div>
            <div class="info-item">
              <span class="label">题目总数</span>
              <span class="value highlight">{{ totalQuestions }} 道</span>
            </div>
            <div class="info-item">
              <span class="label">预计总分</span>
              <span class="value highlight">{{ totalScore }} 分</span>
            </div>
          </div>
          
          <el-divider />
          
          <h4>题型分布</h4>
          <div class="type-distribution">
            <div v-if="form.single_count > 0" class="type-item">
              <el-tag type="primary">单选题</el-tag>
              <span>{{ form.single_count }} 道 × {{ form.score_rules.single }} 分 = {{ form.single_count * form.score_rules.single }} 分</span>
            </div>
            <div v-if="form.multiple_count > 0" class="type-item">
              <el-tag type="success">多选题</el-tag>
              <span>{{ form.multiple_count }} 道 × {{ form.score_rules.multiple }} 分 = {{ form.multiple_count * form.score_rules.multiple }} 分</span>
            </div>
            <div v-if="form.judge_count > 0" class="type-item">
              <el-tag type="warning">判断题</el-tag>
              <span>{{ form.judge_count }} 道 × {{ form.score_rules.judge }} 分 = {{ form.judge_count * form.score_rules.judge }} 分</span>
            </div>
            <div v-if="form.fill_count > 0" class="type-item">
              <el-tag type="danger">填空题</el-tag>
              <span>{{ form.fill_count }} 道 × {{ form.score_rules.fill }} 分 = {{ form.fill_count * form.score_rules.fill }} 分</span>
            </div>
          </div>
          
          <el-divider />
          
          <el-button 
            type="primary" 
            size="large" 
            style="width: 100%"
            @click="generatePaper"
            :loading="generating"
            :disabled="form.bank_ids.length === 0 || totalQuestions === 0"
          >
            <el-icon><Document /></el-icon>
            生成试卷
          </el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { bankApi, paperApi } from '@/api'

const router = useRouter()

const banks = ref([])
const generating = ref(false)
const formRef = ref(null)
const difficultyRange = ref([1, 5])

const difficultyMarks = {
  1: '简单',
  2: '',
  3: '中等',
  4: '',
  5: '困难'
}

const form = ref({
  title: '',
  description: '',
  time_limit: 60,
  bank_ids: [],
  single_count: 10,
  multiple_count: 5,
  judge_count: 5,
  fill_count: 0,
  score_rules: {
    single: 5,
    multiple: 5,
    judge: 2,
    fill: 5
  }
})

const rules = {
  title: [{ required: true, message: '请输入试卷名称', trigger: 'blur' }],
  bank_ids: [{ required: true, message: '请至少选择一个题库', trigger: 'change' }]
}

const totalQuestions = computed(() => {
  return form.value.single_count + form.value.multiple_count + 
         form.value.judge_count + form.value.fill_count
})

const totalScore = computed(() => {
  const f = form.value
  return f.single_count * f.score_rules.single +
         f.multiple_count * f.score_rules.multiple +
         f.judge_count * f.score_rules.judge +
         f.fill_count * f.score_rules.fill
})

const fetchBanks = async () => {
  try {
    banks.value = await bankApi.getAll()
  } catch (error) {
    console.error('获取题库列表失败:', error)
  }
}

const generatePaper = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    generating.value = true
    try {
      const config = {
        ...form.value,
        min_difficulty: difficultyRange.value[0],
        max_difficulty: difficultyRange.value[1]
      }
      
      const result = await paperApi.generate(config)
      ElMessage.success('试卷生成成功！')
      router.push('/papers')
    } catch (error) {
      console.error('生成失败:', error)
    } finally {
      generating.value = false
    }
  })
}

onMounted(() => {
  fetchBanks()
})
</script>

<style lang="scss" scoped>
.paper-create-view {
  .header-left {
    display: flex;
    align-items: center;
    gap: 10px;
    
    h1 {
      margin: 0;
    }
  }
  
  .form-hint {
    margin-left: 10px;
    color: #909399;
    font-size: 13px;
  }
  
  .difficulty-slider-wrapper {
    width: 100%;
    padding: 0 30px 30px 30px;
    
    .difficulty-slider {
      width: 100%;
    }
  }
  
  .preview-panel {
    position: sticky;
    top: 20px;
    
    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 20px;
      color: #303133;
    }
    
    h4 {
      margin: 0 0 15px;
      color: #606266;
      font-size: 14px;
    }
    
    .preview-info {
      .info-item {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px dashed #ebeef5;
        
        .label {
          color: #909399;
        }
        
        .value {
          font-weight: 500;
          color: #303133;
          
          &.highlight {
            color: #409eff;
            font-size: 18px;
          }
        }
      }
    }
    
    .type-distribution {
      .type-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        font-size: 14px;
        color: #606266;
      }
    }
  }
}
</style>
