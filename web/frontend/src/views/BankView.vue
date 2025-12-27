<template>
  <div class="bank-view">
    <div class="page-header">
      <h1><el-icon><Folder /></el-icon>题库管理</h1>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>新建题库
      </el-button>
    </div>

    <div class="card-container">
      <el-table :data="banks" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="名称" min-width="180">
          <template #default="{ row }">
            <router-link :to="`/banks/${row.id}`" class="bank-link">
              {{ row.name }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="科目" width="120" />
        <el-table-column prop="question_count" label="题目数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.question_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="goToBank(row.id)">
                管理
              </el-button>
              <el-button type="info" size="small" @click="showEditDialog(row)">
                编辑
              </el-button>
              <el-popconfirm 
                title="确定要删除这个题库吗？" 
                @confirm="deleteBank(row.id)"
              >
                <template #reference>
                  <el-button type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="banks.length === 0 && !loading" class="empty-state">
        <el-icon><FolderOpened /></el-icon>
        <p>暂无题库，点击上方按钮创建第一个题库</p>
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
import { ElMessage } from 'element-plus'
import { bankApi } from '@/api'

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

onMounted(() => {
  fetchBanks()
})
</script>

<style lang="scss" scoped>
.bank-view {
  .bank-link {
    color: #409eff;
    text-decoration: none;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
  
  .action-buttons {
    justify-content: center;
  }
}
</style>
