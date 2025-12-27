<template>
  <div class="volcano-help">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <el-button 
        type="primary" 
        :icon="ArrowLeft" 
        @click="goBack"
        class="back-btn"
      >
        返回设置
      </el-button>
      <h2 class="nav-title">火山引擎配置指南</h2>
    </div>
    
    <!-- 主要内容 -->
    <div class="help-content">
      <el-scrollbar height="calc(100vh - 120px)">
        <div class="content-wrapper">
          <!-- 视频教程 -->
          <section class="section video-section">
            <h3>
              <el-icon><VideoPlay /></el-icon>
              配置视频教程
            </h3>
            <div class="video-container">
              <video controls width="100%">
                <source src="/video/教学视频.mp4" type="video/mp4">
                您的浏览器不支持视频播放。
              </video>
            </div>
          </section>

          <!-- 简介 -->
          <section class="section intro">
            <h3>
              <el-icon><InfoFilled /></el-icon>
              什么是火山引擎？
            </h3>
            <p>
              火山引擎是字节跳动旗下的企业级云服务平台，提供丰富的AI能力，包括大语言模型（豆包大模型）。
              通过火山引擎，您可以获取与 OpenAI 兼容的 API 接口，为智题坊提供 AI 识别和题目生成功能。
            </p>
            <el-alert type="info" :closable="false" show-icon>
              <template #title>
                火山引擎提供一定的免费额度，适合个人学习和小规模使用。
              </template>
            </el-alert>
          </section>

          <!-- 步骤一 -->
          <section class="section">
            <h3>
              <span class="step-number">1</span>
              注册火山引擎账号
            </h3>
            <div class="step-content">
              <ol>
                <li>
                  访问火山引擎官网：
                  <el-link type="primary" href="https://www.volcengine.com/" target="_blank">
                    https://www.volcengine.com/
                  </el-link>
                </li>
                <li>点击右上角【注册】按钮</li>
                <li>可选择手机号或邮箱注册</li>
                <li>完成实名认证（必须步骤，否则无法使用AI服务）</li>
              </ol>
              <el-alert type="warning" :closable="false" show-icon>
                <template #title>
                  实名认证可能需要 1-2 个工作日审核，请提前准备。
                </template>
              </el-alert>
            </div>
          </section>

          <!-- 步骤二 -->
          <section class="section">
            <h3>
              <span class="step-number">2</span>
              开通豆包大模型服务
            </h3>
            <div class="step-content">
              <ol>
                <li>登录火山引擎控制台</li>
                <li>
                  在搜索框中搜索【豆包大模型】或访问：
                  <el-link type="primary" href="https://console.volcengine.com/ark" target="_blank">
                    https://console.volcengine.com/ark
                  </el-link>
                </li>
                <li>点击【立即开通】或【免费试用】</li>
                <li>阅读并同意服务协议</li>
              </ol>
              <div class="tip-box">
                <el-icon><Promotion /></el-icon>
                <span>新用户通常有免费额度赠送，可以先体验再决定是否付费。</span>
              </div>
            </div>
          </section>

          <!-- 步骤三 -->
          <section class="section">
            <h3>
              <span class="step-number">3</span>
              创建模型推理接入点
            </h3>
            <div class="step-content">
              <ol>
                <li>在豆包大模型控制台，点击左侧【模型推理】</li>
                <li>选择【创建推理接入点】</li>
                <li>
                  选择需要的模型（推荐选择）：
                  <ul class="model-list">
                    <li>
                      <el-tag type="success">推荐</el-tag>
                      <strong>Doubao-pro-32k</strong> - 性价比高，适合日常使用
                    </li>
                    <li>
                      <el-tag type="primary">高级</el-tag>
                      <strong>Doubao-pro-128k</strong> - 支持更长上下文
                    </li>
                    <li>
                      <el-tag type="warning">视觉</el-tag>
                      <strong>Doubao-vision-pro-32k</strong> - 支持图片识别（用于题目识别）
                    </li>
                  </ul>
                </li>
                <li>填写接入点名称（如：my-doubao-pro）</li>
                <li>点击【确认创建】</li>
              </ol>
              <el-alert type="success" :closable="false" show-icon>
                <template #title>
                  创建完成后，记录下「接入点ID」，格式类似：ep-xxxxxxxxxxxx-xxxxx
                </template>
              </el-alert>
            </div>
          </section>

          <!-- 步骤四 -->
          <section class="section">
            <h3>
              <span class="step-number">4</span>
              获取 API Key
            </h3>
            <div class="step-content">
              <ol>
                <li>点击左侧菜单【API Key管理】</li>
                <li>点击【创建API Key】</li>
                <li>填写名称和描述（可选）</li>
                <li>点击【确认】创建</li>
                <li>
                  <strong style="color: #e74c3c;">重要：</strong>
                  创建成功后，立即复制保存 API Key，它只显示一次！
                </li>
              </ol>
              <div class="warning-box">
                <el-icon><Warning /></el-icon>
                <div>
                  <strong>安全提示</strong>
                  <p>API Key 是您账户的凭证，请妥善保管：</p>
                  <ul>
                    <li>不要分享给他人</li>
                    <li>不要提交到公开代码仓库</li>
                    <li>定期更换 API Key</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          <!-- 步骤五 -->
          <section class="section">
            <h3>
              <span class="step-number">5</span>
              在智题坊中配置
            </h3>
            <div class="step-content">
              <p>回到智题坊的【系统设置】页面，填写以下信息：</p>
              <div class="config-table">
                <div class="config-row">
                  <div class="config-label">API 地址</div>
                  <div class="config-value">
                    <code>https://ark.cn-beijing.volces.com/api/v3</code>
                    <el-button size="small" @click="copyText('https://ark.cn-beijing.volces.com/api/v3')">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </div>
                </div>
                <div class="config-row">
                  <div class="config-label">API Key</div>
                  <div class="config-value">
                    <code>您在步骤4获取的 API Key</code>
                  </div>
                </div>
                <div class="config-row">
                  <div class="config-label">文字模型</div>
                  <div class="config-value">
                    <code>文字模型的接入点ID（如：ep-xxxx-xxxxx）</code>
                    <p class="config-tip">用于AI生成题目、解析文本等功能</p>
                  </div>
                </div>
                <div class="config-row">
                  <div class="config-label">视觉模型</div>
                  <div class="config-value">
                    <code>视觉模型的接入点ID（如：ep-xxxx-xxxxx）</code>
                    <p class="config-tip">用于图片识别，需选择带有"vision"的模型</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- 常见问题 -->
          <section class="section faq">
            <h3>
              <el-icon><QuestionFilled /></el-icon>
              常见问题
            </h3>
            <el-collapse>
              <el-collapse-item title="Q1: 为什么提示「认证失败」？">
                <ul>
                  <li>检查 API Key 是否正确复制，没有多余空格</li>
                  <li>确认 API Key 状态是「已启用」</li>
                  <li>检查账户是否已完成实名认证</li>
                </ul>
              </el-collapse-item>
              <el-collapse-item title="Q2: 为什么提示「模型不存在」？">
                <ul>
                  <li>模型名称应该填写「接入点ID」，不是模型的显示名称</li>
                  <li>接入点ID 格式为：ep-xxxxxxxxxx-xxxxx</li>
                  <li>确认接入点状态是「已启用」</li>
                </ul>
              </el-collapse-item>
              <el-collapse-item title="Q3: 费用是如何计算的？">
                <ul>
                  <li>按照实际调用的 Token 数量计费</li>
                  <li>不同模型价格不同，详见官网定价页面</li>
                  <li>新用户通常有免费额度</li>
                  <li>可在控制台设置用量告警，避免超支</li>
                </ul>
              </el-collapse-item>
              <el-collapse-item title="Q4: 如何提高识别准确率？">
                <ul>
                  <li>拍照时确保光线充足、文字清晰</li>
                  <li>避免图片过于倾斜或模糊</li>
                  <li>选择更高级的模型可以提高准确率</li>
                </ul>
              </el-collapse-item>
            </el-collapse>
          </section>

          <!-- 相关链接 -->
          <section class="section links">
            <h3>
              <el-icon><Link /></el-icon>
              相关链接
            </h3>
            <div class="link-grid">
              <el-card shadow="hover" @click="openLink('https://www.volcengine.com/')">
                <template #header>火山引擎官网</template>
                <p>注册账号、了解更多产品</p>
              </el-card>
              <el-card shadow="hover" @click="openLink('https://console.volcengine.com/ark')">
                <template #header>豆包大模型控制台</template>
                <p>管理模型接入点、API Key</p>
              </el-card>
              <el-card shadow="hover" @click="openLink('https://www.volcengine.com/docs/82379')">
                <template #header>官方文档</template>
                <p>详细的 API 文档和示例</p>
              </el-card>
              <el-card shadow="hover" @click="openLink('https://www.volcengine.com/pricing?product=doubao')">
                <template #header>定价说明</template>
                <p>了解各模型的定价策略</p>
              </el-card>
            </div>
          </section>
        </div>
      </el-scrollbar>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, 
  InfoFilled, 
  Promotion, 
  Warning, 
  CopyDocument,
  QuestionFilled,
  Link
} from '@element-plus/icons-vue'

const router = useRouter()

const goBack = () => {
  router.push('/settings')
}

const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

const openLink = (url) => {
  window.open(url, '_blank')
}
</script>

<style scoped>
.volcano-help {
  height: 100%;
  background: #f5f7fa;
}

.top-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.back-btn {
  flex-shrink: 0;
}

.nav-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.help-content {
  padding: 24px;
}

.content-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

.section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.section h3 {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #303133;
  padding-bottom: 12px;
  border-bottom: 2px solid #409eff;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
  border-radius: 50%;
  font-size: 14px;
  font-weight: bold;
}

.step-content {
  padding-left: 40px;
}

.step-content ol {
  margin: 0;
  padding-left: 20px;
  line-height: 2;
}

.step-content ol li {
  margin-bottom: 8px;
}

.model-list {
  margin-top: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  list-style: none;
}

.model-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px dashed #e4e7ed;
}

.model-list li:last-child {
  border-bottom: none;
}

.tip-box {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #e8f4fd, #d9ecff);
  border-radius: 8px;
  color: #409eff;
  font-size: 14px;
}

.warning-box {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding: 16px;
  background: #fef0f0;
  border-radius: 8px;
  border-left: 4px solid #f56c6c;
}

.warning-box .el-icon {
  color: #f56c6c;
  font-size: 24px;
  flex-shrink: 0;
}

.warning-box strong {
  color: #f56c6c;
  display: block;
  margin-bottom: 8px;
}

.warning-box ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
  font-size: 13px;
  color: #606266;
}

.config-table {
  margin-top: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.config-row {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
}

.config-row:last-child {
  border-bottom: none;
}

.config-label {
  width: 120px;
  padding: 12px 16px;
  background: #f5f7fa;
  font-weight: 500;
  color: #606266;
  flex-shrink: 0;
}

.config-value {
  flex: 1;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.config-value code {
  padding: 4px 8px;
  background: #f0f2f5;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
  color: #e74c3c;
  word-break: break-all;
}

.config-tip {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.faq :deep(.el-collapse-item__header) {
  font-size: 15px;
  font-weight: 500;
}

.faq ul {
  margin: 0;
  padding-left: 20px;
  line-height: 1.8;
  color: #606266;
}

.links .link-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.links .el-card {
  cursor: pointer;
  transition: all 0.3s;
}

.links .el-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.links :deep(.el-card__header) {
  padding: 12px 16px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
  font-weight: 600;
}

.links .el-card p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.intro p {
  line-height: 1.8;
  color: #606266;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .links .link-grid {
    grid-template-columns: 1fr;
  }
  
  .config-row {
    flex-direction: column;
  }
  
  .config-label {
    width: 100%;
  }
}
</style>
