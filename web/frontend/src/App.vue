<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <!-- 侧边栏 -->
        <el-aside width="240px" class="sidebar">
          <div class="logo">
            <div class="logo-icon">
              <el-icon :size="24"><Document /></el-icon>
            </div>
            <span>智题坊</span>
          </div>
          
          <div class="menu-wrapper">
            <el-menu
              :default-active="activeMenu"
              router
              class="modern-menu"
            >
              <div class="menu-group">
                <div class="group-title">核心功能</div>
                <el-menu-item index="/banks">
                  <el-icon><Folder /></el-icon>
                  <span>题库管理</span>
                </el-menu-item>
                <el-menu-item index="/papers">
                  <el-icon><Files /></el-icon>
                  <span>试卷管理</span>
                </el-menu-item>
                <el-menu-item index="/exam">
                  <el-icon><EditPen /></el-icon>
                  <span>开始答题</span>
                </el-menu-item>
              </div>

              <div class="menu-group">
                <div class="group-title">学习记录</div>
                <el-menu-item index="/results">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>成绩查看</span>
                </el-menu-item>
                <el-menu-item index="/favorites">
                  <el-icon><Star /></el-icon>
                  <span>我的收藏</span>
                </el-menu-item>
              </div>

              <div class="menu-group">
                <div class="group-title">工具与设置</div>
                <el-menu-item index="/ai-import">
                  <el-icon><MagicStick /></el-icon>
                  <span>AI 智能导入</span>
                </el-menu-item>
                <el-menu-item index="/settings">
                  <el-icon><Setting /></el-icon>
                  <span>系统设置</span>
                </el-menu-item>
              </div>
            </el-menu>
          </div>

          <div class="sidebar-footer">
            <el-menu 
              :default-active="activeMenu"
              router 
              class="modern-menu"
            >
              <el-menu-item index="/about">
                <el-icon><InfoFilled /></el-icon>
                <span>关于系统</span>
              </el-menu-item>
            </el-menu>
          </div>
        </el-aside>

        <!-- 主内容区 -->
        <el-main class="main-content">
          <div class="content-wrapper">
            <router-view v-slot="{ Component }">
              <transition name="page-fade" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </div>
        </el-main>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import { 
  Document, Folder, Files, EditPen, DataAnalysis, 
  Star, MagicStick, Setting, InfoFilled 
} from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/banks/')) return '/banks'
  if (path.startsWith('/papers/')) return '/papers'
  if (path.startsWith('/exam/')) return '/exam'
  if (path.startsWith('/results/')) return '/results'
  return path
})
</script>

<style lang="scss">
:root {
  --sidebar-bg: #ffffff;
  --sidebar-active-bg: #ecf5ff;
  --sidebar-text: #606266;
  --sidebar-active-text: #409eff;
  --main-bg: #f5f7fa;
}

body {
  margin: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.app-container {
  min-height: 100vh;
  background: var(--main-bg);
}

.sidebar {
  background: var(--sidebar-bg);
  border-right: 1px solid #e6e8eb;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: sticky;
  top: 0;
  z-index: 100;
  
  .logo {
    height: 72px;
    padding: 0 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    
    .logo-icon {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #409eff, #3a8ee6);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      box-shadow: 0 4px 10px rgba(64, 158, 255, 0.3);
    }

    span {
      font-size: 20px;
      font-weight: 700;
      color: #1a1a1a;
      letter-spacing: 1px;
    }
  }

  .menu-wrapper {
    flex: 1;
    padding: 12px;
    overflow-y: auto;
  }

  .modern-menu {
    border: none !important;
    background: transparent !important;

    .menu-group {
      margin-bottom: 20px;
      
      .group-title {
        padding: 0 16px;
        margin-bottom: 8px;
        font-size: 12px;
        font-weight: 600;
        color: #909399;
        text-transform: uppercase;
        letter-spacing: 1px;
      }
    }

    .el-menu-item {
      height: 48px;
      line-height: 48px;
      margin: 4px 0;
      border-radius: 10px;
      color: var(--sidebar-text);
      transition: all 0.3s;

      &:hover {
        background-color: #f5f7fa !important;
        color: #303133;
      }

      &.is-active {
        background-color: var(--sidebar-active-bg) !important;
        color: var(--sidebar-active-text);
        font-weight: 600;
        
        &::after {
          content: '';
          position: absolute;
          right: 12px;
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--sidebar-active-text);
        }
      }

      .el-icon {
        font-size: 18px;
        margin-right: 12px;
      }
    }
  }

  .sidebar-footer {
    padding: 12px;
    border-top: 1px solid #f0f2f5;
  }
}

.main-content {
  padding: 0 !important;
  height: 100vh;
  overflow-y: auto;

  .content-wrapper {
    max-width: 1280px;
    margin: 0 auto;
    padding: 32px;
  }
}

/* 页面切换动画 */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.3s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 全局卡片容器样式 */
.card-container {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
  border: 1px solid #f0f2f5;
}

/* 全局标题样式 */
.page-header {
  margin-bottom: 32px;
  h1 {
    margin: 0;
    font-size: 28px;
    font-weight: 700;
    color: #1a1a1a;
  }
}
</style>
