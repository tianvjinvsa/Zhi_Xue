<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <!-- 侧边栏 -->
        <el-aside width="220px" class="sidebar">
          <div class="logo">
            <el-icon :size="28" color="#409EFF"><Document /></el-icon>
            <span>智题坊</span>
          </div>
          <el-menu
            :default-active="activeMenu"
            router
            background-color="#304156"
            text-color="#bfcbd9"
            active-text-color="#409EFF"
          >
            <el-menu-item index="/banks">
              <el-icon><Folder /></el-icon>
              <span>题库管理</span>
            </el-menu-item>
            <el-menu-item index="/papers">
              <el-icon><Document /></el-icon>
              <span>试卷管理</span>
            </el-menu-item>
            <el-menu-item index="/exam">
              <el-icon><Edit /></el-icon>
              <span>开始答题</span>
            </el-menu-item>
            <el-menu-item index="/results">
              <el-icon><DataAnalysis /></el-icon>
              <span>成绩查看</span>
            </el-menu-item>
            <el-menu-item index="/favorites">
              <el-icon><Star /></el-icon>
              <span>我的收藏</span>
            </el-menu-item>
            <el-menu-item index="/ai-import">
              <el-icon><MagicStick /></el-icon>
              <span>AI导入</span>
            </el-menu-item>
            <el-menu-item index="/settings">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </el-menu-item>
            <el-menu-item index="/about">
              <el-icon><InfoFilled /></el-icon>
              <span>了解更多</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主内容区 -->
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style lang="scss">
.app-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.el-container {
  min-height: 100vh;
}

.sidebar {
  background: #304156;
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.1);
  overflow-x: hidden;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: #fff;
    font-size: 18px;
    font-weight: 600;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .el-menu {
    border-right: none;
    
    .el-menu-item {
      &:hover {
        background-color: rgba(64, 158, 255, 0.1) !important;
      }
      
      &.is-active {
        background-color: rgba(64, 158, 255, 0.2) !important;
        border-right: 3px solid #409EFF;
      }
    }
  }
}

.main-content {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 40px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
