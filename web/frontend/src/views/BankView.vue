<template>
  <div class="bank-view">
    <div class="page-header">
      <h1><el-icon><Folder /></el-icon>题库管理</h1>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>新建题库
      </el-button>
    </div>

    <div v-loading="loading">
      <div v-if="banks.length > 0" class="banks-grid">
        <el-card 
          v-for="bank in banks" 
          :key="bank.id" 
          class="bank-card" 
          shadow="hover"
        >
          <div class="bank-card-header">
            <div class="bank-icon">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="bank-title">
              <h3>{{ bank.name }}</h3>
              <el-tag size="small" type="info">{{ bank.subject || '未分类' }}</el-tag>
            </div>
          </div>
          
          <div class="bank-desc">
            {{ bank.description || '暂无描述信息' }}
          </div>
          
          <div class="bank-stats">
            <div class="stat-item">
              <span class="stat-value">{{ bank.question_count || 0 }}</span>
              <span class="stat-label">题目数量</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ formatDate(bank.created_at) }}</span>
              <span class="stat-label">创建时间</span>
            </div>
          </div>
          
          <div class="bank-actions">
            <el-button type="primary" @click="goToBank(bank.id)">管理题目</el-button>
            <el-dropdown trigger="click">
              <el-button icon="MoreFilled" />
              <template #footer>
                <el-dropdown-menu>
                  <el-dropdown-item @click="showEditDialog(bank)">
                    <el-icon><Edit /></el-icon>编辑信息
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="deleteBank(bank.id)" style="color: #f56c6c">
                    <el-icon><Delete /></el-icon>删除题库
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="showEditDialog(bank)">
                    <el-icon><Edit /></el-icon>编辑信息
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="confirmDelete(bank.id)" style="color: #f56c6c">
                    <el-icon><Delete /></el-icon>删除题库
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-card>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <el-icon><FolderOpened /></el-icon>
        <p>暂无题库，点击上方按钮创建第一个题库</p>
        <el-button type="primary" @click="showCreateDialog">立即创建</el-button>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑题库' : '新建题库'"
      width="500px"
    >
      <el-form :model="form" label-width="80px" :rules="rules" ref="formRef">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入题库名称" />
        </el-form-item>
        <el-form-item label="科目" prop="subject">
          <el-input v-model="form.subject" placeholder="请输入所属科目" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入描述信息" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ isEditing ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { bankApi } from '@/api'
import { Folder, Plus, FolderOpened, Edit, Delete, MoreFilled } from '@element-plus/icons-vue'

const router = useRouter()

const loading = ref(false)
const banks = ref([])
const dialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const form = ref({
  name: '',
  subject: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入题库名称', trigger: 'blur' }]
}

const fetchBanks = async () => {
  loading.value = true
  try {
    banks.value = await bankApi.getAll()
  } catch (error) {
    console.error('获取题库列表失败:', error)
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  isEditing.value = false
  editingId.value = null
  form.value = { name: '', subject: '', description: '' }
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEditing.value = true
  editingId.value = row.id
  form.value = {
    name: row.name,
    subject: row.subject || '',
    description: row.description || ''
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEditing.value) {
        await bankApi.update(editingId.value, form.value)
        ElMessage.success('更新成功')
      } else {
        await bankApi.create(form.value)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchBanks()
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const deleteBank = async (id) => {
  try {
    await bankApi.delete(id)
    ElMessage.success('删除成功')
    fetchBanks()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

const goToBank = (id) => {
  router.push(`/banks/${id}`)
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const confirmDelete = (id) => {
  ElMessageBox.confirm('确定要删除这个题库吗？此操作不可撤销！', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteBank(id)
  }).catch(() => {})
}

onMounted(() => {
  fetchBanks()
})
</script>

<style lang="scss" scoped>
.bank-view {
  .banks-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 10px;
  }

  .bank-card {
    border-radius: 12px;
    transition: all 0.3s;
    border: 1px solid #ebeef5;

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1) !important;
    }

    .bank-card-header {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 15px;

      .bank-icon {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        background: linear-gradient(135deg, #409eff, #79bbff);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        font-size: 24px;
      }

      .bank-title {
        flex: 1;
        h3 {
          margin: 0 0 4px;
          font-size: 18px;
          color: #303133;
        }
      }
    }

    .bank-desc {
      color: #606266;
      font-size: 14px;
      line-height: 1.6;
      height: 44px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      margin-bottom: 20px;
    }

    .bank-stats {
      display: flex;
      background: #f8f9fa;
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 20px;

      .stat-item {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        
        &:first-child {
          border-right: 1px solid #e4e7ed;
        }

        .stat-value {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
        }

        .stat-label {
          font-size: 12px;
          color: #909399;
          margin-top: 2px;
        }
      }
    }

    .bank-actions {
      display: flex;
      gap: 10px;

      .el-button:first-child {
        flex: 1;
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 60px 0;
    background: #fff;
    border-radius: 12px;
    
    .el-icon {
      font-size: 64px;
      color: #dcdfe6;
      margin-bottom: 16px;
    }

    p {
      color: #909399;
      margin-bottom: 20px;
    }
  }
}
</style>
