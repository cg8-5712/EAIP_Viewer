# EAIP Viewer - 电子航空情报资料查看器

## 项目简介

EAIP Viewer 是一款跨平台桌面应用程序，专为航空专业人员和航空爱好者设计，用于查看和管理电子航空情报资料（Electronic Aeronautical Information Publication）中的机场航图。本应用支持 Windows、macOS 和 Linux 操作系统，提供安全、高效的航图浏览体验。

## 核心功能

### 1. 用户认证系统
- **游客模式**：无需注册即可浏览部分航图资料
- **用户注册/登录**：完整功能访问权限
- 用户数据本地加密存储
- 会话管理与自动登录

### 2. 机场列表管理
- **多语言显示**：
  - 机场中文名称
  - 机场英文名称
  - ICAO 四字代码
  - 关联航图数量统计
- **智能搜索**：
  - 支持 ICAO 代码搜索
  - 支持机场名称（中/英文）搜索
  - 支持航图类别筛选
  - 支持航图文件名/关键词搜索
  - 实时搜索结果过滤
- **列表功能**：
  - 按字母/地区排序
  - 收藏机场快速访问
  - 最近访问记录

### 3. 航图分类浏览
支持以下 14 种标准航图类型：
- **ADC** (Aerodrome Chart) - 机场图
- **APDC** (Aircraft Parking/Docking Chart) - 机位/停机图
- **GMC** (Ground Movement Chart) - 地面活动图
- **DGS** (Docking Guidance System) - 停靠引导系统图
- **AOC** (Aircraft Operating Chart) - 航空器运行图
- **PATC** (Precision Approach Terrain Chart) - 精密进近地形图
- **FDA** (Final Descent Area) - 燃油排放区域图
- **ATCMAS** (ATC Minimum Altitude Sector) - 空管最低高度扇区图
- **SID** (Standard Instrument Departure) - 标准仪表离场程序图
- **STAR** (Standard Terminal Arrival Route) - 标准进场程序图
- **WAYPOINT LIST** - 航路点列表
- **DATABASE CODING TABLE** - 数据库编码表
- **IAC** (Instrument Approach Chart) - 仪表进近图
- **ATCSMAC** (ATC Surveillance Minimum Altitude Chart) - 空管监视最低高度图

### 4. 航图查看器
- **基础功能**：
  - 高质量 PDF/图片渲染
  - 鼠标滚轮缩放（无级缩放）
  - 拖拽平移浏览
  - 适应窗口/原始尺寸切换
  - 旋转视图（90°增量）
- **标注工具**：
  - 临时标注绘制
  - 文本注释
  - 测距工具
  - 高亮区域标记
  - 标注保存/清除（不修改原文件）
- **安全保护**：
  - 实时水印显示（用户名+时间戳）
  - 禁用文件下载/导出
  - 截图保护（窗口黑屏/选做功能）
  - 文件内容加密存储

### 5. OTA 自动更新系统
- **周期管理**：
  - 启动时自动检查更新
  - 手动检查更新选项
  - 服务器 Cycle 版本比对
  - 增量更新支持
- **数据同步**：
  - 后台下载最新航图数据包
  - 下载进度实时显示
  - 断点续传功能
  - 更新日志查看
  - 版本回滚机制

### 6. 数据安全保护
- **文件加密**：
  - AES-256 加密存储航图文件
  - 运行时内存解密浏览
  - 防止文件直接访问
- **访问控制**：
  - 用户权限验证
  - 水印追溯机制
  - 操作日志记录
- **防截图机制**（选做）：
  - Windows：SetWindowDisplayAffinity API
  - macOS：NSWindowSharingNone
  - Linux：X11 overlay protection

## 技术架构

### 架构设计理念

本项目采用 **PyQt6 + QML 混合架构**，结合两者优势：
- **QML 层**：负责 UI 界面、动画效果、用户交互（登录、列表、搜索、设置）
- **Python Widgets 层**：负责复杂业务逻辑（航图渲染、标注、加密、OTA）
- **核心逻辑层**：纯 Python 实现业务逻辑和数据处理

### 技术选型说明

#### 为什么选择 PyQt6 + QML？
1. **现代化 UI**：QML 提供声明式 UI 开发，支持 Material Design 风格
2. **开发效率**：UI 与逻辑分离，界面开发效率提升 50%+
3. **动画性能**：GPU 加速渲染，流畅的过渡动画和交互效果
4. **安全可控**：核心功能用 Python/C++ 实现，不影响加密和防护机制
5. **跨平台一致性**：QML 在 Windows/macOS/Linux 表现一致

#### 为什么不用 Web 技术（Electron/Tauri）？
- ❌ 无法实现真正的防截图功能
- ❌ 文件加密保护机制容易被绕过
- ❌ 打包体积大（150MB+ vs 30MB）
- ❌ 内存占用高（200MB+ vs 80MB）
- ❌ 水印和安全控制较弱

### 开发技术栈

#### 前端层（QML）
- **UI 框架**：Qt Quick / QML 6.x
- **UI 组件库**：Qt Quick Controls 2（Material / Universal 风格）
- **动画系统**：Qt Quick Animations & Transitions
- **布局系统**：Anchors / Layouts / StackView

#### 后端层（Python）
- **编程语言**：Python 3.9+（推荐 3.11 性能最佳）
- **GUI 框架**：PyQt6 6.4+
- **PDF 渲染**：PyMuPDF (fitz) - 性能最优的 Python PDF 库
- **图像处理**：Pillow 9.0+
- **数据加密**：cryptography (AES-256, PBKDF2)
- **网络请求**：aiohttp（异步）+ requests（同步）
- **数据存储**：SQLAlchemy 2.0 + SQLite
- **日志系统**：loguru
- **打包工具**：PyInstaller 5.0+

#### 混合桥接层
- **QML-Python 通信**：Qt Signals & Slots
- **自定义 QML 类型**：`qmlRegisterType` 注册 Python 类
- **图片提供器**：`QQuickImageProvider` 用于 PDF 图像传输
- **数据模型**：`QAbstractListModel` 用于列表数据绑定

### 项目结构
```
EAIP_Viewer/
├── src/
│   ├── main.py                      # 应用入口，初始化 QML Engine
│   ├── config.py                    # 全局配置管理
│   │
│   ├── qml/                         # QML 界面文件（前端）
│   │   ├── main.qml                 # 主窗口
│   │   ├── pages/                   # 页面组件
│   │   │   ├── LoginPage.qml        # 登录/注册界面
│   │   │   ├── AirportListPage.qml  # 机场列表页
│   │   │   ├── ChartGridPage.qml    # 航图分类网格
│   │   │   ├── SearchPage.qml       # 搜索界面
│   │   │   └── SettingsPage.qml     # 设置页面
│   │   ├── components/              # 可复用组件
│   │   │   ├── AirportCard.qml      # 机场卡片组件
│   │   │   ├── ChartTypeButton.qml  # 航图类型按钮
│   │   │   ├── SearchBar.qml        # 搜索栏
│   │   │   └── LoadingIndicator.qml # 加载动画
│   │   └── styles/                  # 样式主题
│   │       ├── Theme.qml            # 主题配置
│   │       └── Colors.qml           # 色彩方案
│   │
│   ├── ui/                          # Python Widgets（后端UI）
│   │   ├── chart_viewer_widget.py   # 航图查看器核心（QGraphicsView）
│   │   ├── annotation_tools.py      # 标注工具栏
│   │   └── watermark_overlay.py     # 水印叠加层
│   │
│   ├── controllers/                 # QML 后端控制器
│   │   ├── auth_controller.py       # 用户认证控制器（暴露给QML）
│   │   ├── airport_model.py         # 机场列表模型（QAbstractListModel）
│   │   ├── chart_provider.py        # 航图图片提供器（QQuickImageProvider）
│   │   └── update_controller.py     # OTA 更新控制器
│   │
│   ├── core/                        # 核心业务逻辑
│   │   ├── auth.py                  # 用户认证逻辑
│   │   ├── database.py              # 数据库操作
│   │   ├── encryption.py            # 文件加密/解密
│   │   ├── updater.py               # OTA 更新引擎
│   │   ├── search_engine.py         # 全文搜索引擎
│   │   └── pdf_renderer.py          # PDF 渲染器（PyMuPDF 封装）
│   │
│   ├── models/                      # 数据模型（SQLAlchemy）
│   │   ├── user.py                  # 用户模型
│   │   ├── airport.py               # 机场模型
│   │   ├── chart.py                 # 航图模型
│   │   └── update_cycle.py          # AIRAC Cycle 模型
│   │
│   └── utils/                       # 工具函数
│       ├── watermark.py             # 水印生成
│       ├── screenshot_protect.py    # 截图保护（平台相关）
│       ├── crypto_helper.py         # 加密辅助函数
│       ├── logger.py                # 日志配置
│       └── platform_utils.py        # 平台检测工具
│
├── resources/                       # 资源文件
│   ├── icons/                       # 应用图标
│   ├── fonts/                       # 自定义字体
│   └── qml.qrc                      # QML 资源文件（编译用）
│
├── data/                            # 运行时数据目录
│   ├── database.db                  # SQLite 数据库（加密）
│   ├── charts/                      # 航图文件（加密存储）
│   └── cache/                       # 缓存目录
│
├── tests/                           # 测试文件
│   ├── test_encryption.py
│   ├── test_pdf_renderer.py
│   └── test_search_engine.py
│
├── requirements.txt                 # Python 依赖
├── requirements-dev.txt             # 开发依赖
├── pyproject.toml                   # 项目配置（推荐）
├── setup.py                         # 安装脚本
├── .gitignore
├── LICENSE
└── README.md
```

### 架构分层说明

```
┌─────────────────────────────────────────────┐
│          QML UI 层（前端）                   │
│  登录界面 / 机场列表 / 搜索 / 设置            │  
│  Material Design 风格 + 动画效果             │
└────────────────┬────────────────────────────┘
                 │ Signals & Slots
                 ↓
┌─────────────────────────────────────────────┐
│       QML Controllers（桥接层）              │
│  暴露 Python 方法和属性给 QML 调用            │
│  QAbstractListModel / QObject               │
└────────────────┬────────────────────────────┘
                 │
┌────────────────┴──────────┬─────────────────┐
│  Python Widgets（复杂UI） │  Core 业务逻辑   │
│  航图查看器 / 标注工具    │  加密 / OTA       │
│  QGraphicsView / QPainter │  数据库 / 搜索   │
└───────────────────────────┴─────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────┐
│          SQLAlchemy ORM + SQLite            │
│          加密文件系统 + 日志系统              │
└─────────────────────────────────────────────┘
```

## 安装与部署

### 环境要求
- **Python**：3.9+ (推荐 3.11，性能提升 25%)
- **内存**：4GB RAM（推荐 8GB，QML 渲染需要更多内存）
- **磁盘空间**：1GB 可用空间（数据包另计，完整安装约 2GB）
- **显卡**：支持 OpenGL 2.0+（QML 硬件加速需要）
- **操作系统**：
  - Windows 10/11 (x64)
  - macOS 10.15+ (Intel / Apple Silicon)
  - Linux (Ubuntu 20.04+, Fedora 35+)
- **网络连接**：用于 OTA 更新和首次数据同步

### 快速开始

#### 1. 克隆仓库
```bash
git clone https://github.com/cg8-5712/EAIP_Viewer.git
cd EAIP_Viewer
```

#### 2. 创建虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖
```bash
# 生产环境依赖
pip install -r requirements.txt

# 开发环境依赖（包含测试工具、代码检查等）
pip install -r requirements-dev.txt
```

### 主要依赖包

#### 核心依赖 (requirements.txt)
```
# GUI 框架
PyQt6>=6.4.0
PyQt6-Qt6>=6.4.0

# PDF 处理
PyMuPDF>=1.23.0          # PDF 渲染引擎

# 图像处理
Pillow>=10.0.0

# 加密
cryptography>=41.0.0     # AES-256 + PBKDF2

# 数据库
SQLAlchemy>=2.0.0
alembic>=1.12.0          # 数据库迁移工具

# 网络请求
aiohttp>=3.9.0           # 异步 HTTP 客户端
requests>=2.31.0         # 同步 HTTP 客户端

# 日志
loguru>=0.7.0            # 更优雅的日志系统

# 配置管理
pydantic>=2.0.0          # 配置验证
python-dotenv>=1.0.0     # 环境变量管理

# 工具库
tqdm>=4.66.0             # 进度条（用于下载）
platformdirs>=3.10.0     # 跨平台目录管理
```

#### 开发依赖 (requirements-dev.txt)
```
# 测试框架
pytest>=7.4.0
pytest-qt>=4.2.0         # PyQt 测试插件
pytest-cov>=4.1.0        # 代码覆盖率

# 代码质量
black>=23.7.0            # 代码格式化
flake8>=6.1.0            # 代码检查
mypy>=1.5.0              # 类型检查

# 打包工具
pyinstaller>=5.13.0

# 文档生成
sphinx>=7.0.0
```

### 开发运行

#### 方式一：直接运行
```bash
python src/main.py
```

#### 方式二：使用模块方式运行（推荐）
```bash
python -m src.main
```

#### 调试模式（启用详细日志）
```bash
python src/main.py --debug
```

#### QML 实时热重载（开发 QML 界面时使用）
```bash
# 需要安装 qml-hot-reload 工具
python src/main.py --hot-reload
```

### 测试

#### 运行所有测试
```bash
pytest tests/
```

#### 运行特定测试文件
```bash
pytest tests/test_encryption.py -v
```

#### 生成覆盖率报告
```bash
pytest --cov=src --cov-report=html
# 报告生成在 htmlcov/index.html
```

### 打包发布

#### Windows 打包
```bash
# 单文件模式（推荐分发）
pyinstaller build_scripts/windows.spec

# 目录模式（开发调试）
pyinstaller --windowed --name EAIP_Viewer \
  --icon=resources/icons/app.ico \
  --add-data "src/qml;qml" \
  --add-data "resources;resources" \
  --hidden-import=PyQt6.QtQml \
  src/main.py

# 输出在 dist/EAIP_Viewer/
```

#### macOS 打包
```bash
# 创建 .app 应用包
pyinstaller build_scripts/macos.spec

# 签名（需要开发者证书）
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist/EAIP_Viewer.app

# 创建 DMG 安装包
hdiutil create -volname "EAIP Viewer" -srcfolder dist/EAIP_Viewer.app \
  -ov -format UDZO dist/EAIP_Viewer.dmg
```

#### Linux 打包
```bash
# AppImage 格式（推荐）
pyinstaller build_scripts/linux.spec
appimagetool dist/EAIP_Viewer/ EAIP_Viewer-x86_64.AppImage

# DEB 包（Debian/Ubuntu）
fpm -s dir -t deb -n eaip-viewer -v 1.0.0 \
  --prefix /opt/eaip-viewer \
  dist/EAIP_Viewer

# RPM 包（Fedora/RHEL）
fpm -s dir -t rpm -n eaip-viewer -v 1.0.0 \
  --prefix /opt/eaip-viewer \
  dist/EAIP_Viewer
```

### PyInstaller 配置文件示例

#### windows.spec
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/qml', 'qml'),
        ('resources', 'resources'),
    ],
    hiddenimports=[
        'PyQt6.QtQml',
        'PyQt6.QtQuick',
        'PyQt6.QtQuickControls2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EAIP_Viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app.ico',
)
```

## 使用指南

### 首次启动
1. 运行应用程序
2. 选择"游客模式"或"注册账户"
3. 等待初始数据同步（如有）
4. 开始浏览航图

### 搜索技巧
- **按 ICAO 搜索**：输入 `ZBAA` 查找北京首都机场
- **按名称搜索**：输入 `北京` 或 `Beijing`
- **按类别搜索**：输入 `ZBAA SID` 查找离场程序
- **按文件名搜索**：输入关键词快速定位航图

### 航图操作
- **缩放**：鼠标滚轮 或 Ctrl + +/-
- **平移**：鼠标左键拖拽
- **标注**：点击工具栏标注按钮
- **适应窗口**：双击图像 或 按 F 键

## 安全说明

### 数据保护
- 所有航图文件采用 AES-256 加密存储
- 用户密码使用 PBKDF2 哈希加密
- 不存储明文敏感信息

### 水印机制
查看航图时会自动添加半透明水印，包含：
- 用户名
- 查看时间戳
- 设备标识（可选）

### 防导出措施
- 禁用右键菜单
- 禁用打印功能
- 禁用文件另存为
- 截图保护（平台支持情况下）

## 更新日志

### Version 1.0.0 (计划中)
- [x] 基础用户认证系统
- [x] 机场列表浏览
- [x] 14类航图分类展示
- [x] 航图查看器核心功能
- [x] 智能搜索引擎
- [x] 文件加密系统
- [x] 水印保护
- [ ] OTA 自动更新
- [ ] 标注功能
- [ ] 截图保护（Windows）

## 常见问题

**Q: 支持哪些航图文件格式？**
A: 主要支持 PDF 格式，同时兼容 PNG、JPG 等图片格式。

**Q: 游客模式有什么限制？**
A: 游客模式可查看部分公开航图，但无法使用标注、收藏等高级功能。

**Q: 数据更新频率是多久？**
A: 跟随 AIRAC Cycle，通常为 28 天一个周期。

**Q: 能否导出航图？**
A: 出于版权保护，应用不支持导出功能。

**Q: 为什么选择 PyQt6 + QML 而不是纯 Widgets？**
A: QML 提供更现代的 UI 和更高的开发效率，同时保留 Widgets 处理复杂业务逻辑的能力。两者结合可以兼顾美观性和功能性。

**Q: QML 会影响应用安全性吗？**
A: 不会。核心的加密、防截图等安全功能都在 Python 层实现，QML 只负责 UI 展示，不影响安全机制。

**Q: 应用的内存占用大约是多少？**
A: 空闲状态约 80-100MB，查看航图时根据文件大小会增加到 150-300MB，相比 Electron 应用（200MB+）仍有优势。

## 开发计划

### 近期计划 (v1.1)
- [ ] 离线模式优化
- [ ] 多标签页浏览
- [ ] 航图版本对比功能
- [ ] 自定义快捷键

### 中期计划 (v1.2)
- [ ] 团队共享标注
- [ ] 航图套打功能
- [ ] 移动端同步（Android/iOS）
- [ ] 云端数据备份

### 远期计划 (v2.0)
- [ ] AI 航图识别
- [ ] 3D 机场模型
- [ ] 实时 NOTAM 集成
- [ ] 飞行计划集成

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎提交问题和拉取请求！请遵循以下规范：
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 联系方式

- **项目主页**: [GitHub Repository](https://github.com/cg8-5712/EAIP_Viewer)
- **问题反馈**: [Issues](https://github.com/cg8-5712/EAIP_Viewer/issues)
- **电子邮件**: [Cg8-5712](mailto:5712.cg8@gmail.com) or [HTony03](mailto:HTony03@foxmail.com)

## 致谢

感谢所有为航空安全和信息化做出贡献的开发者和组织。

---

**免责声明**：本软件仅供学习和研究使用，不得用于实际飞行导航。使用者应遵守当地航空法规，并使用官方授权的航空资料。