# 智题坊

一个功能完善的智能答题系统，采用 **Vue 3 + Element Plus + FastAPI** 技术栈构建，通过 **PyInstaller** 打包为桌面应用程序。支持题库管理、智能组卷、在线答题、自动评分和 AI 辅助功能。

## ✨ 功能特性

### 🎯 核心功能

- **题库管理**：创建、编辑、删除题库，支持多种题型（单选、多选、判断、填空）
- **智能组卷**：根据配置自动生成试卷，支持按难度、标签筛选
- **在线答题**：计时答题、进度保存、答题卡快速跳转
- **自动评分**：客观题自动评分，详细的答题结果分析
- **收藏功能**：收藏重要或易错题目，方便复习

### 🤖 AI 功能

- **文本解析**：从文本中自动识别和解析题目
- **图片识别**：OCR 识别图片中的题目内容
- **智能出题**：根据知识点和难度自动生成新题目
- **支持多种 AI 服务**：OpenAI、火山引擎、Azure 等兼容接口

### 📦 其他特性

- 支持 Excel、CSV、Word、JSON 格式导入导出
- 答题进度自动保存
- 详细的统计分析
- 可配置数据存储路径
- 自动检测更新

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| **前端框架** | Vue 3 + Element Plus |
| **构建工具** | Vite |
| **后端框架** | FastAPI (Python) |
| **数据存储** | 本地 JSON 文件 |
| **桌面打包** | PyInstaller |
| **AI 接口** | OpenAI / 火山引擎 兼容 API |

## 📁 项目结构

```
AnswerSystem/
├── main.py              # 程序入口
├── config.py            # 配置管理
├── requirements.txt     # Python 依赖列表
├── build.spec           # PyInstaller 打包配置
├── models/              # 数据模型
│   ├── question.py      # 题目模型
│   ├── bank.py          # 题库模型
│   ├── paper.py         # 试卷模型
│   ├── result.py        # 答题结果模型
│   └── favorite.py      # 收藏模型
├── services/            # 业务服务
│   ├── bank_service.py  # 题库服务
│   ├── paper_service.py # 组卷服务
│   ├── exam_service.py  # 答题服务
│   ├── ai_service.py    # AI 服务
│   ├── favorite_service.py # 收藏服务
│   └── import_service.py # 导入服务
├── utils/               # 工具函数
│   ├── file_handler.py  # 文件处理
│   ├── validators.py    # 数据验证
│   └── helpers.py       # 辅助函数
├── resources/           # 资源文件
│   ├── icons/           # 图标
│   ├── styles/          # 样式表
│   └── 火山引擎配置指南.md # AI 配置文档
├── web/                 # Web 应用
│   ├── start.py         # 服务启动脚本
│   ├── start.bat        # Windows 启动脚本
│   ├── backend/         # 后端 API
│   │   └── main.py      # FastAPI 服务
│   └── frontend/        # 前端项目
│       ├── src/
│       │   ├── views/   # 页面组件
│       │   ├── api/     # API 封装
│       │   ├── router/  # 路由配置
│       │   └── styles/  # 样式文件
│       ├── images/      # 图片资源
│       └── dist/        # 前端构建产物
└── data/                # 数据目录
    ├── banks/           # 题库数据
    ├── papers/          # 试卷数据
    ├── results/         # 答题记录
    └── favorites.json   # 收藏数据
```

## 🚀 快速开始

### 开发环境运行

#### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

#### 2. 安装前端依赖

```bash
cd web/frontend
npm install
```

#### 3. 构建前端

```bash
npm run build
```

#### 4. 启动服务

```bash
# 回到项目根目录
cd ../..
# 使用启动脚本
cd web
python start.py
```

或直接双击 `web/start.bat`（Windows）

#### 5. 访问系统

打开浏览器访问 `http://localhost:5173`

### 打包为可执行文件

#### 1. 确保前端已构建

```bash
cd web/frontend
npm run build
```

#### 2. 执行打包

```bash
cd ../..
pyinstaller build.spec
```

打包后的文件位于 `dist/智题坊/` 目录。

## 📖 使用说明

### 题库管理

1. 点击"题库管理"进入题库列表
2. 可以创建新题库、编辑或删除现有题库
3. 在题库详情中添加、编辑、删除题目
4. 支持从 Excel/CSV/Word/JSON 批量导入题目

### 智能组卷

1. 点击"试卷管理" → "生成试卷"
2. 选择来源题库
3. 配置各题型数量、难度范围、分值
4. 点击生成即可创建试卷

### 在线答题

1. 点击"开始答题"选择试卷
2. 答题过程中可使用答题卡快速跳转
3. 完成后点击"交卷"查看成绩

### AI 功能配置

1. 进入"系统设置"
2. 配置 AI 服务地址和 API Key
3. 点击"火山引擎配置帮助"查看详细指南
4. 测试连接确认配置正确

### 数据路径配置

1. 在"系统设置"中可自定义数据存储路径
2. 支持配置：题库、试卷、成绩、收藏数据的存储位置
3. 修改路径后需重启服务生效

## 🔄 更新检测

系统支持自动检测 GitHub 上的新版本：

1. 在"系统设置"中点击"检测更新"
2. 如有新版本会显示更新说明
3. 点击"前往下载"可跳转到下载页面

发布地址：<https://github.com/K-zhaochao/AnswerSystem/releases>

## ⚙️ 配置说明

### AI 服务配置

在"系统设置"页面配置 AI 服务：

| 配置项 | 说明 |
|--------|------|
| API Base URL | API 端点地址 |
| API Key | 您的 API 密钥（加密存储） |
| 模型名称 | 使用的模型（如 gpt-4o-mini） |
| 视觉模型 | 图片识别模型（如 gpt-4o） |
| Temperature | 生成随机性（0-2） |
| Max Tokens | 最大输出长度 |

### 支持的 AI 提供商

- **OpenAI**：GPT-4、GPT-3.5
- **火山引擎**：Doubao 系列（[配置指南](resources/火山引擎配置指南.md)）
- **Azure OpenAI Service**
- 其他兼容 OpenAI API 的服务

## 📄 开源协议

本项目采用 GPL 协议开源。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

- **QQ**：[1727369245](https://qm.qq.com/q/HruBrdOukc)
- **GitHub**：[K-zhaochao](https://github.com/K-zhaochao)
- **赞助支持**：[爱发电](https://afdian.com/a/draven323)
