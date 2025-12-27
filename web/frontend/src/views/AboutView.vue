<template>
  <div class="about-view">
    <div class="page-header">
      <h1><el-icon><InfoFilled /></el-icon>了解更多</h1>
    </div>

    <!-- 作者信息卡片 -->
    <div class="author-card card-container">
      <div class="author-info">
        <img src="/images/头像.jpg" alt="作者头像" class="avatar" />
        <div class="author-detail">
          <h2>智题坊</h2>
          <p class="desc">功能完善的智能答题系统，助力高效学习</p>
          <div class="contact-links">
            <el-button type="primary" plain @click="openLink('https://qm.qq.com/q/HruBrdOukc')">
              <el-icon><ChatDotRound /></el-icon>
              &nbsp; QQ: 1727369245
            </el-button>
            <el-button plain @click="openLink('https://github.com/K-zhaochao')">
              <el-icon><Link /></el-icon>
              GitHub
            </el-button>
            <el-button type="warning" @click="openLink('https://afdian.com/a/draven323')">
              ☕ 请我喝杯咖啡
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能介绍 -->
    <div class="card-container">
      <h3>📚 功能介绍</h3>
      <el-row :gutter="16">
        <el-col :span="6" v-for="feature in features" :key="feature.title">
          <div class="feature-item">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h4>{{ feature.title }}</h4>
            <ul>
              <li v-for="item in feature.items" :key="item">{{ item }}</li>
            </ul>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 技术栈和版本信息 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <div class="card-container">
          <h3>🛠️ 技术栈</h3>
          <div class="tech-grid">
            <div class="tech-item" v-for="tech in techStack" :key="tech.name">
              <span class="tech-icon">{{ tech.icon }}</span>
              <span class="tech-name">{{ tech.name }}</span>
              <span class="tech-desc">{{ tech.desc }}</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="card-container">
          <h3>📋 版本信息</h3>
          <div class="version-info">
            <div class="version-row">
              <span>当前版本</span>
              <el-tag type="primary">v1.0.0</el-tag>
            </div>
            <div class="version-row">
              <span>发布日期</span>
              <span class="date">2025-12</span>
            </div>
            <div class="version-row">
              <span>开源协议</span>
              <span class="license">GPL</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const features = ref([
  {
    icon: '📖',
    title: '题库管理',
    items: ['创建与编辑题库', '支持单选/多选/判断/填空题', 'AI智能识别导入', '难度标签分类管理']
  },
  {
    icon: '📝',
    title: '智能组卷',
    items: ['从多个题库随机抽题', '按难度范围智能筛选', '自定义各题型分值', '灵活设置时间限制']
  },
  {
    icon: '✏️',
    title: '在线答题',
    items: ['实时倒计时提醒', '答题进度自动保存', '答题卡快速导航', '随时收藏重点题目']
  },
  {
    icon: '📊',
    title: '成绩分析',
    items: ['自动评分与统计', '详细答案解析', '错题分布分析', '完整历史记录']
  },
  {
    icon: '⭐',
    title: '收藏复习',
    items: ['一键收藏难题', '按来源分类管理', '快速复习模式', '支持导出整理']
  },
  {
    icon: '🤖',
    title: 'AI 功能',
    items: ['文本智能解析', '图片OCR识别', '一键智能出题', '支持多种AI服务']
  },
  {
    icon: '💾',
    title: '数据管理',
    items: ['灵活的数据存储路径', '选择性导出备份', '智能识别导入', '完整数据迁移']
  },
  {
    icon: '⚙️',
    title: '系统设置',
    items: ['AI服务自由配置', '支持火山引擎/OpenAI', '自动检测版本更新', '个性化路径设置']
  }
])

const techStack = ref([
  { icon: '🌐', name: '前端', desc: 'Vue 3 + Element Plus' },
  { icon: '⚡', name: '后端', desc: 'FastAPI + Python' },
  { icon: '📦', name: '打包', desc: 'PyInstaller' },
  { icon: '🤖', name: 'AI', desc: 'OpenAI / 火山引擎' }
])

const openLink = (url) => {
  window.open(url, '_blank')
}
</script>

<style lang="scss" scoped>
.about-view {
  .page-header {
    margin-bottom: 24px;
    h1 {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }

  .card-container {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 20px;
    
    h3 {
      margin: 0 0 20px;
      color: #303133;
      font-size: 16px;
    }
  }

  .author-card {
    .author-info {
      display: flex;
      align-items: center;
      gap: 24px;
      
      .avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #ecf5ff;
      }
      
      .author-detail {
        h2 {
          margin: 0 0 8px;
          font-size: 22px;
          color: #303133;
        }
        
        .desc {
          color: #909399;
          margin: 0 0 16px;
        }
        
        .contact-links {
          display: flex;
          gap: 12px;
        }
      }
    }
  }

  .feature-item {
    background: #f8fafc;
    border-radius: 8px;
    padding: 16px;
    height: 100%;
    margin-bottom: 16px;
    
    .feature-icon {
      font-size: 24px;
      margin-bottom: 8px;
    }
    
    h4 {
      margin: 0 0 10px;
      color: #303133;
      font-size: 14px;
    }
    
    ul {
      margin: 0;
      padding-left: 16px;
      color: #606266;
      font-size: 12px;
      
      li {
        margin-bottom: 4px;
        line-height: 1.4;
      }
    }
  }

  .tech-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    
    .tech-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px;
      background: #f8fafc;
      border-radius: 8px;
      text-align: center;
      
      .tech-icon {
        font-size: 24px;
        margin-bottom: 8px;
      }
      
      .tech-name {
        font-weight: 500;
        color: #303133;
        margin-bottom: 4px;
      }
      
      .tech-desc {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .version-info {
    .version-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px dashed #ebeef5;
      
      &:last-child {
        border-bottom: none;
      }
      
      span:first-child {
        color: #909399;
      }
      
      .date, .license {
        color: #303133;
        font-weight: 500;
      }
    }
  }
}
</style>
