<template>
  <div class="market-container">
    <div class="market-header">
      <div class="header-left">
        <div class="title">
          <el-icon><ShoppingCart /></el-icon>
          <span>题库商城</span>
        </div>
        <el-tag size="small" type="info" effect="plain">浏览并获取优质题库资源</el-tag>
      </div>
      <div class="header-right">
        <div class="iframe-controls">
          <div class="control-group">
            <el-tooltip content="缩小" placement="bottom">
              <el-button size="small" circle @click="zoomOut"><el-icon><Minus /></el-icon></el-button>
            </el-tooltip>
            <span class="zoom-text">{{ Math.round(scale * 100) }}%</span>
            <el-tooltip content="放大" placement="bottom">
              <el-button size="small" circle @click="zoomIn"><el-icon><Plus /></el-icon></el-button>
            </el-tooltip>
            <el-button size="small" link @click="resetZoom">重置</el-button>
          </div>
          <div class="control-divider"></div>
          <el-tooltip content="全屏查看" placement="bottom">
            <el-button size="small" circle @click="enterFullscreen">
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
        
        <el-divider direction="vertical" />
        
        <el-button type="danger" plain @click="openBilibili">
          <el-icon><VideoCamera /></el-icon>&nbsp;使用教程
        </el-button>
        <el-button type="primary" plain @click="refreshPage">
          <el-icon><Refresh /></el-icon>&nbsp;刷新
        </el-button>
        
      </div>
    </div>

    <div class="market-content">
      <div v-if="loading" class="loading-overlay">
        <el-icon class="loading-icon" is-loading><Loading /></el-icon>
        <p>正在加载题库商城...</p>
      </div>
      
      <div v-else-if="loadError" class="error-overlay">
        <el-icon class="error-icon"><Warning /></el-icon>
        <p>{{ loadError }}</p>
        <el-button type="primary" @click="loadIframe">重试加载</el-button>
      </div>

      <div class="iframe-wrapper" ref="iframeWrapper">
        <iframe
          ref="iframeRef"
          :src="marketUrl"
          @load="onIframeLoad"
          @error="onIframeError"
          sandbox="allow-scripts allow-same-origin allow-popups allow-forms allow-storage-access-by-user-activation"
          allowfullscreen
          allow="fullscreen; clipboard-read; clipboard-write"
        ></iframe>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  ShoppingCart, Refresh, Loading, Warning, 
  VideoCamera, Plus, Minus, FullScreen 
} from '@element-plus/icons-vue'

const marketUrl = 'http://pan.matehub.top/'
const bilibiliUrl = 'https://www.bilibili.com/video/BV1V7vXBsEhu/?vd_source=9f6dba46a25347083d8d2aa39d801b33'
const iframeRef = ref(null)
const iframeWrapper = ref(null)
const loading = ref(true)
const loadError = ref('')
const scale = ref(1)

const onIframeLoad = () => {
  loading.value = false
  loadError.value = ''
}

const onIframeError = () => {
  loading.value = false
  loadError.value = '无法加载题库商城页面，请检查网络连接'
}

const loadIframe = () => {
  loading.value = true
  loadError.value = ''
  if (iframeRef.value) {
    iframeRef.value.src = marketUrl
  }
}

const refreshPage = () => {
  loadIframe()
}

const openBilibili = () => {
  window.open(bilibiliUrl, '_blank')
}

onMounted(() => {
  // 设置超时检测
  setTimeout(() => {
    if (loading.value) {
      loading.value = false
      loadError.value = '加载超时，请检查网络连接或直接在浏览器中打开'
    }
  }, 15000)
})

// 缩放与全屏控制
const applyScale = () => {
  if (!iframeRef.value) return
  iframeRef.value.style.transform = `scale(${scale.value})`
  iframeRef.value.style.transformOrigin = '0 0'
}

const zoomIn = () => {
  scale.value = Math.min(3, +(scale.value + 0.1).toFixed(2))
  applyScale()
}

const zoomOut = () => {
  scale.value = Math.max(0.4, +(scale.value - 0.1).toFixed(2))
  applyScale()
}

const resetZoom = () => {
  scale.value = 1
  applyScale()
}

const enterFullscreen = async () => {
  try {
    const el = iframeWrapper.value || iframeRef.value
    if (el.requestFullscreen) await el.requestFullscreen()
    else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen()
  } catch (e) {
    // ignore
  }
}
</script>

<style scoped lang="scss">
.market-container {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  overflow: hidden;
  position: relative;

  .market-header {
    padding: 12px 20px;
    background: #fff;
    border-bottom: 1px solid #ebeef5;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    z-index: 10;

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;

      .title {
        font-size: 18px;
        font-weight: 600;
        color: #303133;
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 12px;

      .iframe-controls {
        display: flex;
        align-items: center;
        background: #f0f2f5;
        padding: 4px;
        border-radius: 8px;
        gap: 4px;

        .control-group {
          display: flex;
          align-items: center;
          gap: 2px;
        }

        .control-divider {
          width: 1px;
          height: 20px;
          background: #dcdfe6;
          margin: 0 4px;
        }

        .zoom-text {
          font-size: 12px;
          color: #606266;
          min-width: 45px;
          text-align: center;
          font-family: monospace;
        }
      }
    }
  }

  .market-content {
    flex: 1;
    position: relative;
    overflow: auto;
    background: #e4e7ed;
    display: flex;
    justify-content: center;

    .iframe-wrapper {
      width: 100%;
      height: 100%;
      position: relative;
      background: #fff;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;

      iframe {
        width: 100%;
        height: 100%;
        border: none;
        display: block;
        transition: transform 0.2s ease-out;
      }
    }

    .loading-overlay, .error-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      background: rgba(255, 255, 255, 0.9);
      z-index: 5;

      .loading-icon {
        font-size: 40px;
        color: var(--el-color-primary);
        margin-bottom: 16px;
      }

      .error-icon {
        font-size: 48px;
        color: var(--el-color-danger);
        margin-bottom: 16px;
      }

      p {
        color: #606266;
        font-size: 14px;
        margin-bottom: 20px;
      }
    }
  }
}

// 全屏状态下的样式微调
:fullscreen {
  .iframe-wrapper {
    width: 100vw !important;
    height: 100vh !important;
    
    iframe {
      width: 100% !important;
      height: 100% !important;
    }
  }
}
</style>
