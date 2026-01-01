<template>
  <div class="native-market-container">
    <!-- 顶部搜索和筛选 -->
    <div class="market-header">
      <div class="header-left">
        <el-icon class="title-icon"><Shop /></el-icon>
        <h2>题库商城</h2>
        <el-tag size="small" type="info">云端题库资源</el-tag>
      </div>
      <div class="header-right">
        <el-button @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索题库名称、科目、关键词..."
        clearable
        size="large"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-bar">
      <div class="filter-item">
        <span class="filter-label">分类：</span>
        <el-radio-group v-model="selectedCategory" size="small" @change="handleFilter">
          <el-radio-button label="">全部</el-radio-button>
          <el-radio-button 
            v-for="cat in categories" 
            :key="cat.id" 
            :label="cat.id"
          >
            {{ cat.name }}
          </el-radio-button>
        </el-radio-group>
      </div>
      <div class="filter-item">
        <span class="filter-label">排序：</span>
        <el-select v-model="sortBy" size="small" @change="handleFilter">
          <el-option label="最新上传" value="latest" />
          <el-option label="下载最多" value="popular" />
          <el-option label="题目最多" value="questions" />
        </el-select>
      </div>
    </div>

    <!-- 题库列表 -->
    <div class="bank-list" v-loading="loading">
      <el-empty v-if="!loading && banks.length === 0" description="暂无题库数据" />
      
      <el-row :gutter="20" v-else>
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="bank in banks" :key="bank.id">
          <el-card class="bank-card" shadow="hover" @click="showBankDetail(bank)">
            <template #header>
              <div class="card-header">
                <el-icon class="bank-icon"><Collection /></el-icon>
                <span class="bank-name">{{ bank.name }}</span>
              </div>
            </template>
            
            <div class="bank-info">
              <div class="info-row">
                <el-tag size="small" type="success">{{ bank.subject || '通用' }}</el-tag>
                <el-tag size="small" type="info">{{ bank.question_count }} 题</el-tag>
              </div>
              <p class="bank-desc">{{ bank.description || '暂无描述' }}</p>
              <div class="bank-meta">
                <span><el-icon><Download /></el-icon> {{ bank.download_count || 0 }}</span>
                <span><el-icon><Clock /></el-icon> {{ formatDate(bank.created_at) }}</span>
              </div>
            </div>
            
            <template #footer>
              <el-button type="primary" size="small" @click.stop="handleDownload(bank)">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
              <el-button size="small" @click.stop="previewBank(bank)">
                <el-icon><View /></el-icon>
                预览
              </el-button>
            </template>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleFilter"
        @current-change="handleFilter"
      />
    </div>

    <!-- 题库详情对话框 -->
    <el-dialog 
      v-model="detailVisible" 
      :title="currentBank?.name || '题库详情'"
      width="600px"
    >
      <div class="bank-detail" v-if="currentBank">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="题库名称" :span="2">
            {{ currentBank.name }}
          </el-descriptions-item>
          <el-descriptions-item label="科目">
            {{ currentBank.subject || '通用' }}
          </el-descriptions-item>
          <el-descriptions-item label="题目数量">
            {{ currentBank.question_count }}
          </el-descriptions-item>
          <el-descriptions-item label="下载次数">
            {{ currentBank.download_count || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">
            {{ formatDate(currentBank.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ currentBank.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 题目预览 -->
        <div class="preview-section" v-if="previewQuestions.length > 0">
          <h4>题目预览</h4>
          <div class="preview-question" v-for="(q, idx) in previewQuestions" :key="idx">
            <p class="q-content">{{ idx + 1 }}. {{ q.content }}</p>
            <div class="q-options" v-if="q.options?.length">
              <p v-for="(opt, i) in q.options" :key="i" class="q-option">
                {{ String.fromCharCode(65 + i) }}. {{ opt }}
              </p>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleDownload(currentBank)">
          <el-icon><Download /></el-icon>
          下载此题库
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Shop, Search, Refresh, Collection, Download, 
  Clock, View 
} from '@element-plus/icons-vue'
import { marketApi } from '@/api'
import { bankApi } from '@/api'

// 状态
const loading = ref(false)
const banks = ref([])
const categories = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchQuery = ref('')
const selectedCategory = ref('')
const sortBy = ref('latest')

// 详情对话框
const detailVisible = ref(false)
const currentBank = ref(null)
const previewQuestions = ref([])

// 加载题库列表
const loadBanks = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      limit: pageSize.value,
      category: selectedCategory.value || undefined,
      sort: sortBy.value,
    }
    const result = await marketApi.getBanks(params)
    banks.value = result.banks || []
    total.value = result.total || 0
  } catch (error) {
    console.error('加载题库失败:', error)
    ElMessage.error('无法连接到题库商城服务器，请检查网络')
    banks.value = []
  } finally {
    loading.value = false
  }
}

// 加载分类
const loadCategories = async () => {
  try {
    const result = await marketApi.getCategories()
    categories.value = result.categories || []
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

// 搜索
const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    loadBanks()
    return
  }
  
  loading.value = true
  try {
    const result = await marketApi.search(searchQuery.value, {
      page: currentPage.value,
      limit: pageSize.value,
    })
    banks.value = result.banks || []
    total.value = result.total || 0
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 筛选
const handleFilter = () => {
  loadBanks()
}

// 刷新
const refreshData = () => {
  currentPage.value = 1
  loadBanks()
  loadCategories()
}

// 显示详情
const showBankDetail = async (bank) => {
  currentBank.value = bank
  detailVisible.value = true
  previewQuestions.value = []
  
  try {
    const result = await marketApi.previewBank(bank.id, 5)
    previewQuestions.value = result.questions || []
  } catch (error) {
    console.error('加载预览失败:', error)
  }
}

// 预览
const previewBank = async (bank) => {
  showBankDetail(bank)
}

// 下载题库
const handleDownload = async (bank) => {
  try {
    await ElMessageBox.confirm(
      `确定要下载题库「${bank.name}」吗？下载后将自动导入到本地题库。`,
      '下载确认',
      { confirmButtonText: '下载', cancelButtonText: '取消', type: 'info' }
    )
    
    ElMessage.info('开始下载...')
    
    // 下载题库文件
    const blob = await marketApi.downloadBank(bank.id)
    
    // 解析 JSON 内容
    const text = await blob.text()
    const bankData = JSON.parse(text)
    
    // 导入到本地
    await bankApi.create({
      name: bankData.name || bank.name,
      subject: bankData.subject || bank.subject,
      description: bankData.description || bank.description,
      chapters: bankData.chapters || [],
      questions: bankData.questions || [],
    })
    
    ElMessage.success(`题库「${bank.name}」下载并导入成功！`)
    detailVisible.value = false
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('下载失败:', error)
      ElMessage.error('下载失败: ' + (error.message || '未知错误'))
    }
  }
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 初始化
onMounted(() => {
  loadBanks()
  loadCategories()
})
</script>

<style scoped>
.native-market-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.market-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 28px;
  color: var(--el-color-primary);
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
}

.search-bar {
  margin-bottom: 20px;
}

.search-bar .el-input {
  max-width: 600px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 24px;
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.bank-list {
  min-height: 400px;
}

.bank-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.2s;
}

.bank-card:hover {
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bank-icon {
  font-size: 20px;
  color: var(--el-color-primary);
}

.bank-name {
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bank-info {
  min-height: 100px;
}

.info-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.bank-desc {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 12px;
}

.bank-meta {
  display: flex;
  gap: 16px;
  color: var(--el-text-color-placeholder);
  font-size: 12px;
}

.bank-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 详情对话框 */
.preview-section {
  margin-top: 20px;
}

.preview-section h4 {
  margin-bottom: 12px;
  color: var(--el-text-color-primary);
}

.preview-question {
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  margin-bottom: 12px;
}

.q-content {
  font-weight: 500;
  margin-bottom: 8px;
}

.q-options {
  padding-left: 16px;
}

.q-option {
  margin: 4px 0;
  color: var(--el-text-color-secondary);
}
</style>
