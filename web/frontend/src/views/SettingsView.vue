<template>
  <div class="settings-view">
    <div class="page-header">
      <h1><el-icon><Setting /></el-icon>系统设置</h1>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <div class="card-container">
          <div class="card-header-with-link">
            <h3>🤖 AI服务配置</h3>
            <el-link 
              type="primary" 
              :underline="false"
              @click="router.push('/volcano-help')"
            >
              <el-icon><QuestionFilled /></el-icon>
              火山引擎配置帮助
            </el-link>
          </div>
          
          <el-form :model="aiConfig" label-width="120px">
            <el-form-item label="API Base URL">
              <el-input v-model="aiConfig.apiBaseUrl" placeholder="https://api.openai.com/v1" />
            </el-form-item>
            
            <el-form-item label="API Key">
              <el-input 
                v-model="aiConfig.apiKey" 
                type="password" 
                show-password
                placeholder="留空则使用已保存的密钥，输入新值则更新" 
              />
            </el-form-item>
            
            <el-form-item label="文字模型">
              <el-input v-model="aiConfig.model" placeholder="gpt-4o-mini" />
            </el-form-item>
            
            <el-form-item label="视觉模型">
                  <el-input v-model="aiConfig.visionModel" placeholder="gpt-4-vision-preview" />
                  <div class="form-tip">用于解析图片题目的模型</div>
            </el-form-item>
            <!-- 高级设置折叠区域 -->
            <el-collapse v-model="advancedExpanded" class="advanced-settings">
              <el-collapse-item name="advanced">
                <template #title>
                  <span class="advanced-title">
                    <el-icon><Tools /></el-icon>
                    高级设置
                  </span>
                </template>
                
                <el-form-item label="Temperature">
                  <el-slider 
                    v-model="aiConfig.temperature" 
                    :min="0" 
                    :max="2" 
                    :step="0.1"
                    show-input
                  />
                  <div class="form-tip">控制生成内容的随机性，值越高越随机</div>
                </el-form-item>
                
                <el-form-item label="Max Tokens">
                  <el-input-number v-model="aiConfig.maxTokens" :min="100" :max="8000" />
                  <div class="form-tip">单次生成的最大Token数量</div>
                </el-form-item>
              </el-collapse-item>
            </el-collapse>
            
            <el-form-item style="margin-top: 16px;">
              <el-button type="primary" @click="saveAIConfig" :loading="saving">
                保存配置
              </el-button>
              <el-button @click="testConnection" :loading="testing">
                测试连接
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
      
      <el-col :span="12">
        <div class="card-container">
          <h3>📊 系统信息</h3>
          
          <div class="info-list">
            <div class="info-item">
              <span class="label">系统版本</span>
              <span class="value">
                {{ currentVersion || '2.0.0' }}
                <el-button 
                  size="small" 
                  type="primary" 
                  link 
                  :loading="checkingUpdate"
                  @click="checkForUpdate"
                  style="margin-left: 8px"
                >
                  检测更新
                </el-button>
              </span>
            </div>
            <div class="info-item">
              <span class="label">前端框架</span>
              <span class="value">Vue 3 + Element Plus</span>
            </div>
            <div class="info-item">
              <span class="label">后端框架</span>
              <span class="value">FastAPI + Python</span>
            </div>
            <div class="info-item">
              <span class="label">打包工具</span>
              <span class="value">PyInstaller</span>
            </div>
            <div class="info-item">
              <span class="label">AI连接状态</span>
              <span class="value">
                <el-tag :type="connectionStatus ? 'success' : 'danger'">
                  {{ connectionStatus ? '已连接' : '未连接' }}
                </el-tag>
              </span>
            </div>
          </div>
          
          <!-- 更新提示 -->
          <div v-if="updateInfo && updateInfo.has_update" class="update-alert">
            <el-alert 
              :title="`发现新版本 ${updateInfo.latest_version}`"
              type="success" 
              :closable="false"
              show-icon
            >
              <template #default>
                <div class="update-content">
                  <p v-if="updateInfo.release_name">{{ updateInfo.release_name }}</p>
                  <p v-if="updateInfo.release_notes" class="release-notes">
                    {{ updateInfo.release_notes.substring(0, 200) }}
                    {{ updateInfo.release_notes.length > 200 ? '...' : '' }}
                  </p>
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="openDownload"
                    style="margin-top: 8px"
                  >
                    前往下载
                  </el-button>
                </div>
              </template>
            </el-alert>
          </div>
        </div>
        
        <div class="card-container" style="margin-top: 20px">
          <h3>⚡ 快捷操作</h3>
          
          <div class="quick-actions">
            <el-button @click="clearCache">清除缓存</el-button>
            <el-button type="primary" @click="showExportDialog">导出数据</el-button>
            <el-button type="success" @click="showImportDialog">导入数据</el-button>
            <el-button type="danger" @click="resetSystem">重置系统</el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 导出数据对话框 -->
    <el-dialog v-model="exportDialogVisible" title="导出数据" width="500px">
      <el-form label-width="100px">
        <el-form-item label="导出路径">
          <div class="path-input-row">
            <el-input v-model="exportConfig.path" placeholder="请输入导出文件夹的绝对路径，例如 D:\backup\智题坊数据" />
            <el-button type="primary" @click="browseExportFolder" :loading="browsingFolder">
              浏览
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="选择数据">
          <el-checkbox-group v-model="exportConfig.types">
            <el-checkbox label="banks">题库数据</el-checkbox>
            <el-checkbox label="papers">试卷数据</el-checkbox>
            <el-checkbox label="results">成绩数据</el-checkbox>
            <el-checkbox label="favorites">我的收藏</el-checkbox>
            <el-checkbox label="ai_config">AI配置</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doExport" :loading="exporting">开始导出</el-button>
      </template>
    </el-dialog>

    <!-- 导入数据对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入数据" width="520px">
      <el-form label-width="100px">
        <el-form-item label="导入路径">
          <div class="path-input-row">
            <el-input v-model="importConfig.path" placeholder="请输入包含数据的文件夹绝对路径" />
            <el-button type="primary" @click="browseImportFolder" :loading="browsingFolder">
              浏览
            </el-button>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="small" @click="scanImportFolder" :loading="scanning">
            扫描文件夹
          </el-button>
        </el-form-item>
        
        <template v-if="importScanResult">
          <el-divider content-position="left">可导入的数据</el-divider>
          <el-form-item label="选择数据">
            <el-checkbox-group v-model="importConfig.types">
              <el-checkbox 
                label="banks" 
                :disabled="!importScanResult.banks"
              >
                题库数据 
                <el-tag v-if="importScanResult.banks" size="small" type="success">
                  {{ importScanResult.banks_count }} 个
                </el-tag>
                <el-tag v-else size="small" type="info">无</el-tag>
              </el-checkbox>
              <el-checkbox 
                label="papers" 
                :disabled="!importScanResult.papers"
              >
                试卷数据
                <el-tag v-if="importScanResult.papers" size="small" type="success">
                  {{ importScanResult.papers_count }} 份
                </el-tag>
                <el-tag v-else size="small" type="info">无</el-tag>
              </el-checkbox>
              <el-checkbox 
                label="results" 
                :disabled="!importScanResult.results"
              >
                成绩数据
                <el-tag v-if="importScanResult.results" size="small" type="success">
                  {{ importScanResult.results_count }} 条
                </el-tag>
                <el-tag v-else size="small" type="info">无</el-tag>
              </el-checkbox>
              <el-checkbox 
                label="favorites" 
                :disabled="!importScanResult.favorites"
              >
                我的收藏
                <el-tag v-if="importScanResult.favorites" size="small" type="success">
                  {{ importScanResult.favorites_count }} 条
                </el-tag>
                <el-tag v-else size="small" type="info">无</el-tag>
              </el-checkbox>
              <el-checkbox 
                label="ai_config" 
                :disabled="!importScanResult.ai_config"
              >
                AI配置
                <el-tag v-if="importScanResult.ai_config" size="small" type="success">有</el-tag>
                <el-tag v-else size="small" type="info">无</el-tag>
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item v-if="importScanResult.export_info">
            <el-alert 
              type="info" 
              :closable="false"
              :title="`导出时间: ${formatDate(importScanResult.export_info.export_time)} | 版本: ${importScanResult.export_info.version}`"
            />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="doImport" 
          :loading="importing"
          :disabled="!importScanResult || importConfig.types.length === 0"
        >
          开始导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 路径配置 -->
    <div class="card-container path-config-section">
      <h3>📁 数据存储路径配置</h3>
      <p class="path-config-desc">
        设置数据文件的存储位置。修改后需要重启后端服务才能生效。
        如果是打包后的可执行文件，建议将路径设置到程序外部目录以防止数据丢失。
      </p>
      
      <el-form :model="pathConfig" label-width="140px">
        <el-form-item label="题库数据目录">
          <el-input v-model="pathConfig.banksDir" placeholder="请输入题库数据存储的绝对路径" />
        </el-form-item>
        
        <el-form-item label="试卷数据目录">
          <el-input v-model="pathConfig.papersDir" placeholder="请输入试卷数据存储的绝对路径" />
        </el-form-item>
        
        <el-form-item label="成绩数据目录">
          <el-input v-model="pathConfig.resultsDir" placeholder="请输入成绩数据存储的绝对路径" />
        </el-form-item>
        
        <el-form-item label="收藏数据文件">
          <el-input v-model="pathConfig.favoritesFile" placeholder="请输入收藏数据文件的绝对路径" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="savePathConfig" :loading="savingPaths">
            保存路径配置
          </el-button>
          <el-button @click="resetPaths">恢复默认</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Tools } from '@element-plus/icons-vue'
import { aiApi, configApi, systemApi, dataApi } from '@/api'

const router = useRouter()
const saving = ref(false)
const testing = ref(false)
const savingPaths = ref(false)
const connectionStatus = ref(false)
const checkingUpdate = ref(false)
const currentVersion = ref('')
const updateInfo = ref(null)
const advancedExpanded = ref([])  // 高级设置折叠状态

// 导出相关
const exportDialogVisible = ref(false)
const exporting = ref(false)
const exportConfig = ref({
  path: '',
  types: ['banks', 'papers', 'results', 'ai_config']
})

// 导入相关
const importDialogVisible = ref(false)
const importing = ref(false)
const scanning = ref(false)
const browsingFolder = ref(false)
const importScanResult = ref(null)
const importConfig = ref({
  path: '',
  types: []
})

const aiConfig = ref({
  apiBaseUrl: '',
  apiKey: '',
  model: 'gpt-4o-mini',
  visionModel: 'gpt-4o',
  temperature: 0.3,
  maxTokens: 100000
})

const pathConfig = ref({
  banksDir: '',
  papersDir: '',
  resultsDir: '',
  favoritesFile: ''
})

const loadConfig = async () => {
  try {
    const config = await configApi.getAI()
    if (!config) return
    aiConfig.value.apiBaseUrl = config.api_base_url || ''
    aiConfig.value.apiKey = ''
    aiConfig.value.model = config.model || 'gpt-4o-mini'
    aiConfig.value.visionModel = config.vision_model || 'gpt-4o'
    aiConfig.value.temperature = config.temperature ?? 0.3
    aiConfig.value.maxTokens = config.max_tokens || 100000
  } catch (e) {
    console.error('加载配置失败:', e)
  }
}

const loadPathConfig = async () => {
  try {
    const config = await configApi.getPaths()
    if (!config) return
    pathConfig.value.banksDir = config.banks_dir || ''
    pathConfig.value.papersDir = config.papers_dir || ''
    pathConfig.value.resultsDir = config.results_dir || ''
    pathConfig.value.favoritesFile = config.favorites_file || ''
  } catch (e) {
    console.error('加载路径配置失败:', e)
  }
}

const saveAIConfig = async () => {
  saving.value = true
  try {
    const updateData = {
      api_base_url: aiConfig.value.apiBaseUrl,
      model: aiConfig.value.model,
      vision_model: aiConfig.value.visionModel,
      temperature: aiConfig.value.temperature,
      max_tokens: aiConfig.value.maxTokens
    }
    
    if (aiConfig.value.apiKey && aiConfig.value.apiKey.trim()) {
      updateData.api_key = aiConfig.value.apiKey
    }
    
    await configApi.updateAI(updateData)
    ElMessage.success('配置已保存到服务器')
    await loadConfig()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const savePathConfig = async () => {
  savingPaths.value = true
  try {
    const updateData = {
      banks_dir: pathConfig.value.banksDir,
      papers_dir: pathConfig.value.papersDir,
      results_dir: pathConfig.value.resultsDir,
      favorites_file: pathConfig.value.favoritesFile
    }
    
    await configApi.updatePaths(updateData)
    ElMessage.success('路径配置已保存，部分更改可能需要重启服务后生效')
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    savingPaths.value = false
  }
}

const resetPaths = async () => {
  try {
    await ElMessageBox.confirm('确定要恢复默认路径配置吗？', '提示', { type: 'warning' })
    await loadPathConfig()
    ElMessage.success('已恢复默认路径')
  } catch {
    // 用户取消
  }
}

const testConnection = async () => {
  testing.value = true
  try {
    const params = {
      api_base_url: aiConfig.value.apiBaseUrl,
      api_key: aiConfig.value.apiKey,
      model: aiConfig.value.model
    };
    
    const res = await aiApi.checkConnection(params)
    if (res.success) {
      ElMessage.success('连接成功')
      connectionStatus.value = true
    } else {
      ElMessage.error(res.message || '连接失败')
      connectionStatus.value = false
    }
  } catch (error) {
    ElMessage.error('连接测试失败')
    connectionStatus.value = false
  } finally {
    testing.value = false
  }
}

const loadVersion = async () => {
  try {
    const data = await systemApi.getVersion()
    if (data && data.version) {
      currentVersion.value = data.version
    } else {
      currentVersion.value = '2.0.0'
    }
  } catch {
    currentVersion.value = '2.0.0'
  }
}

const checkForUpdate = async () => {
  checkingUpdate.value = true
  try {
    const data = await systemApi.checkUpdate()
    updateInfo.value = data
    
    if (data.has_update) {
      ElMessage.success(`发现新版本 ${data.latest_version}`)
    } else {
      ElMessage.info('当前已是最新版本')
    }
  } catch (error) {
    ElMessage.error('检测更新失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    checkingUpdate.value = false
  }
}

const openDownload = () => {
  if (updateInfo.value?.html_url) {
    window.open(updateInfo.value.html_url, '_blank')
  }
}

const clearCache = () => {
  ElMessage.success('缓存已清除')
}

const showExportDialog = () => {
  exportConfig.value.path = ''
  exportConfig.value.types = ['banks', 'papers', 'results', 'favorites', 'ai_config']
  exportDialogVisible.value = true
}

// 浏览文件夹 - 导出
const browseExportFolder = async () => {
  browsingFolder.value = true
  try {
    const result = await systemApi.selectFolder()
    if (result.path) {
      exportConfig.value.path = result.path
    }
  } catch (error) {
    ElMessage.error('打开文件夹选择器失败')
  } finally {
    browsingFolder.value = false
  }
}

// 浏览文件夹 - 导入
const browseImportFolder = async () => {
  browsingFolder.value = true
  try {
    const result = await systemApi.selectFolder()
    if (result.path) {
      importConfig.value.path = result.path
    }
  } catch (error) {
    ElMessage.error('打开文件夹选择器失败')
  } finally {
    browsingFolder.value = false
  }
}

const doExport = async () => {
  if (!exportConfig.value.path) {
    ElMessage.warning('请输入导出路径')
    return
  }
  if (exportConfig.value.types.length === 0) {
    ElMessage.warning('请至少选择一项要导出的数据')
    return
  }
  
  exporting.value = true
  try {
    const result = await dataApi.export({
      export_path: exportConfig.value.path,
      include_banks: exportConfig.value.types.includes('banks'),
      include_papers: exportConfig.value.types.includes('papers'),
      include_results: exportConfig.value.types.includes('results'),
      include_favorites: exportConfig.value.types.includes('favorites'),
      include_ai_config: exportConfig.value.types.includes('ai_config')
    })
    ElMessage.success(`导出成功: ${result.exported.join(', ')}`)
    exportDialogVisible.value = false
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    exporting.value = false
  }
}

const showImportDialog = () => {
  importConfig.value.path = ''
  importConfig.value.types = []
  importScanResult.value = null
  importDialogVisible.value = true
}

const scanImportFolder = async () => {
  if (!importConfig.value.path) {
    ElMessage.warning('请输入导入路径')
    return
  }
  
  scanning.value = true
  try {
    const result = await dataApi.scanImport(importConfig.value.path)
    importScanResult.value = result
    
    // 自动选中可用的数据类型
    importConfig.value.types = []
    if (result.banks) importConfig.value.types.push('banks')
    if (result.papers) importConfig.value.types.push('papers')
    if (result.results) importConfig.value.types.push('results')
    if (result.favorites) importConfig.value.types.push('favorites')
    if (result.ai_config) importConfig.value.types.push('ai_config')
    
    if (importConfig.value.types.length === 0) {
      ElMessage.warning('该文件夹中没有可导入的数据')
    }
  } catch (error) {
    ElMessage.error('扫描失败: ' + (error.response?.data?.detail || error.message))
    importScanResult.value = null
  } finally {
    scanning.value = false
  }
}

const doImport = async () => {
  if (importConfig.value.types.length === 0) {
    ElMessage.warning('请选择要导入的数据')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      '导入数据会新增数据到系统中，是否继续？',
      '确认导入',
      { type: 'warning' }
    )
  } catch {
    return
  }
  
  importing.value = true
  try {
    const result = await dataApi.import({
      import_path: importConfig.value.path,
      include_banks: importConfig.value.types.includes('banks'),
      include_papers: importConfig.value.types.includes('papers'),
      include_results: importConfig.value.types.includes('results'),
      include_favorites: importConfig.value.types.includes('favorites'),
      include_ai_config: importConfig.value.types.includes('ai_config')
    })
    
    if (result.errors && result.errors.length > 0) {
      ElMessage.warning(`导入完成，但有部分错误: ${result.errors.join('; ')}`)
    } else {
      ElMessage.success(`导入成功: ${result.imported.join(', ')}`)
    }
    
    importDialogVisible.value = false
    
    // 如果导入了AI配置，重新加载配置
    if (importConfig.value.types.includes('ai_config')) {
      await loadConfig()
    }
  } catch (error) {
    ElMessage.error('导入失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    importing.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const resetSystem = async () => {
  try {
    await ElMessageBox.confirm('此操作将清除所有数据，是否继续？', '警告', { type: 'warning' })
    ElMessage.info('功能开发中...')
  } catch {
    // 用户取消
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      loadConfig(),
      loadPathConfig(),
      loadVersion()
    ])
    
    // 自动检查一次连接状态
    if (aiConfig.value.apiBaseUrl) {
      // 使用已保存的配置进行静默测试
      try {
        const res = await aiApi.checkConnection({
          api_base_url: aiConfig.value.apiBaseUrl,
          model: aiConfig.value.model
        })
        connectionStatus.value = res.success
      } catch (e) {
        connectionStatus.value = false
      }
    }
  } catch (error) {
    console.error('初始化设置页面失败:', error)
  }
})
</script>

<style lang="scss" scoped>
.settings-view {
  h3 {
    margin: 0 0 20px;
    color: #303133;
  }
  
  .card-header-with-link {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h3 {
      margin: 0;
    }
    
    .el-link {
      font-size: 14px;
      
      .el-icon {
        margin-right: 4px;
      }
    }
  }
  
  .advanced-settings {
    margin: 16px 0;
    border: none;
    
    :deep(.el-collapse-item__header) {
      background: #f5f7fa;
      border-radius: 4px;
      padding: 0 12px;
      height: 40px;
      line-height: 40px;
      border: none;
      
      &.is-active {
        border-bottom-left-radius: 0;
        border-bottom-right-radius: 0;
      }
    }
    
    :deep(.el-collapse-item__wrap) {
      border: 1px solid #e4e7ed;
      border-top: none;
      border-radius: 0 0 4px 4px;
    }
    
    :deep(.el-collapse-item__content) {
      padding: 16px;
    }
    
    .advanced-title {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #606266;
      font-size: 14px;
    }
    
    .form-tip {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
  }
  
  .info-list {
    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px dashed #ebeef5;
      
      &:last-child {
        border-bottom: none;
      }
      
      .label {
        color: #909399;
      }
      
      .value {
        color: #303133;
        font-weight: 500;
        display: flex;
        align-items: center;
      }
    }
  }
  
  .update-alert {
    margin-top: 16px;
    
    .update-content {
      p {
        margin: 0 0 4px;
        font-size: 13px;
        
        &.release-notes {
          color: #606266;
          white-space: pre-wrap;
          line-height: 1.5;
        }
      }
    }
  }
  
  .quick-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .path-input-row {
    display: flex;
    gap: 8px;
    width: 100%;
    
    .el-input {
      flex: 1;
    }
  }
  
  .path-config-section {
    margin-top: 20px;
    
    .path-config-desc {
      color: #909399;
      font-size: 14px;
      margin-bottom: 20px;
      line-height: 1.6;
    }
  }
}
</style>
