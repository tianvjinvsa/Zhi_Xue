"""
系统设置界面
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QGroupBox, QFormLayout, QMessageBox,
    QCheckBox, QSpinBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from config import config, ConfigManager
from services import AIService


class SettingsView(QWidget):
    """系统设置视图"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_service = AIService()
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("⚙️ 系统设置")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        layout.addWidget(title_label)
        
        # AI设置
        ai_group = QGroupBox("AI服务配置")
        ai_layout = QFormLayout(ai_group)
        
        # API提供商
        self.provider_combo = QComboBox()
        self.provider_combo.addItem("OpenAI", "openai")
        self.provider_combo.addItem("Azure OpenAI", "azure")
        self.provider_combo.addItem("通义千问", "qwen")
        self.provider_combo.addItem("智谱AI", "zhipu")
        self.provider_combo.addItem("其他（自定义）", "custom")
        ai_layout.addRow("API提供商:", self.provider_combo)
        
        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("请输入API密钥")
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.api_key_input)
        
        show_key_btn = QPushButton("👁")
        show_key_btn.setFixedSize(32, 32)
        show_key_btn.setCheckable(True)
        show_key_btn.toggled.connect(
            lambda checked: self.api_key_input.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )
        key_layout.addWidget(show_key_btn)
        
        ai_layout.addRow("API密钥:", key_layout)
        
        # Base URL
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("留空使用默认地址，自定义时填写完整API地址")
        ai_layout.addRow("API地址:", self.base_url_input)
        
        # 模型选择
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("如: gpt-4o-mini, gpt-4o")
        ai_layout.addRow("文本模型:", self.model_input)
        
        self.vision_model_input = QLineEdit()
        self.vision_model_input.setPlaceholderText("如: gpt-4o（需要支持图片的模型）")
        ai_layout.addRow("视觉模型:", self.vision_model_input)
        
        # Max Tokens设置
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(0, 128000)
        self.max_tokens_spin.setValue(0)
        self.max_tokens_spin.setSpecialValueText("不限制")
        self.max_tokens_spin.setToolTip("设置为0表示不限制输出长度")
        ai_layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        # 思考时间设置
        self.thinking_time_spin = QSpinBox()
        self.thinking_time_spin.setRange(0, 600)
        self.thinking_time_spin.setValue(0)
        self.thinking_time_spin.setSuffix(" 秒")
        self.thinking_time_spin.setSpecialValueText("不限制")
        self.thinking_time_spin.setToolTip("模型思考时间限制，0表示不限制")
        ai_layout.addRow("思考时间:", self.thinking_time_spin)
        
        # 测试连接
        test_btn = QPushButton("🔗 测试连接")
        test_btn.setObjectName("secondaryButton")
        test_btn.clicked.connect(self._test_connection)
        ai_layout.addRow("", test_btn)
        
        layout.addWidget(ai_group)
        
        # 应用设置
        app_group = QGroupBox("应用设置")
        app_layout = QFormLayout(app_group)
        
        # 自动保存
        self.auto_save_check = QCheckBox("启用自动保存")
        self.auto_save_check.setToolTip("答题时自动保存答案")
        app_layout.addRow("自动保存:", self.auto_save_check)
        
        # 多选题部分得分
        self.partial_score_check = QCheckBox("多选题部分正确时给部分分")
        app_layout.addRow("部分得分:", self.partial_score_check)
        
        # 默认时间
        self.default_time_spin = QSpinBox()
        self.default_time_spin.setRange(0, 300)
        self.default_time_spin.setSuffix(" 分钟")
        self.default_time_spin.setSpecialValueText("不限时")
        app_layout.addRow("默认答题时间:", self.default_time_spin)
        
        layout.addWidget(app_group)
        
        layout.addStretch()
        
        # 保存按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        reset_btn = QPushButton("恢复默认")
        reset_btn.setObjectName("secondaryButton")
        reset_btn.clicked.connect(self._reset_defaults)
        btn_layout.addWidget(reset_btn)
        
        save_btn = QPushButton("💾 保存设置")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_settings(self):
        """加载设置"""
        # AI设置
        ai_config = config.ai_config
        
        index = self.provider_combo.findData(ai_config.api_provider)
        if index >= 0:
            self.provider_combo.setCurrentIndex(index)
        
        self.api_key_input.setText(ai_config.api_key)
        self.base_url_input.setText(ai_config.api_base_url)
        self.model_input.setText(ai_config.model)
        self.vision_model_input.setText(ai_config.vision_model)
        self.max_tokens_spin.setValue(ai_config.max_tokens)
        self.thinking_time_spin.setValue(ai_config.thinking_time)
        
        # 应用设置
        app_config = config.app_config
        
        self.auto_save_check.setChecked(app_config.auto_save)
        self.partial_score_check.setChecked(app_config.multiple_partial_score)
        self.default_time_spin.setValue(app_config.default_time_limit)
    
    def _save_settings(self):
        """保存设置"""
        # AI设置
        config.ai_config.api_provider = self.provider_combo.currentData()
        config.ai_config.api_key = self.api_key_input.text().strip()
        config.ai_config.api_base_url = self.base_url_input.text().strip()
        config.ai_config.model = self.model_input.text().strip() or "gpt-4o-mini"
        config.ai_config.vision_model = self.vision_model_input.text().strip() or "gpt-4o"
        config.ai_config.max_tokens = self.max_tokens_spin.value()
        config.ai_config.thinking_time = self.thinking_time_spin.value()
        
        # 应用设置
        config.app_config.auto_save = self.auto_save_check.isChecked()
        config.app_config.multiple_partial_score = self.partial_score_check.isChecked()
        config.app_config.default_time_limit = self.default_time_spin.value()
        
        # 保存到文件
        config.save()
        
        # 重置AI服务客户端
        self.ai_service._reset_client()
        
        QMessageBox.information(self, "成功", "设置已保存！")
    
    def _test_connection(self):
        """测试AI连接"""
        # 临时更新配置
        old_key = config.ai_config.api_key
        old_url = config.ai_config.api_base_url
        old_model = config.ai_config.model
        
        config.ai_config.api_key = self.api_key_input.text().strip()
        config.ai_config.api_base_url = self.base_url_input.text().strip()
        config.ai_config.model = self.model_input.text().strip() or "gpt-4o-mini"
        
        self.ai_service._reset_client()
        
        success, message = self.ai_service.check_connection()
        
        # 恢复配置
        config.ai_config.api_key = old_key
        config.ai_config.api_base_url = old_url
        config.ai_config.model = old_model
        self.ai_service._reset_client()
        
        if success:
            QMessageBox.information(self, "连接成功", "✅ AI服务连接正常！")
        else:
            QMessageBox.warning(self, "连接失败", f"❌ 连接失败: {message}")
    
    def _reset_defaults(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self, "确认", "确定要恢复默认设置吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.provider_combo.setCurrentIndex(0)
            self.api_key_input.clear()
            self.base_url_input.clear()
            self.model_input.setText("gpt-4o-mini")
            self.vision_model_input.setText("gpt-4o")
            self.max_tokens_spin.setValue(0)
            self.thinking_time_spin.setValue(0)
            self.auto_save_check.setChecked(True)
            self.partial_score_check.setChecked(True)
            self.default_time_spin.setValue(60)
