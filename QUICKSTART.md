# EAIP Viewer - 快速启动指南

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制环境变量配置文件
cp .env.example .env

# 编辑 .env 文件，修改必要的配置
```

### 3. 初始化数据库

```bash
python scripts/init_database.py
```

### 4. 运行应用

```bash
python src/main.py
```

## 📁 项目结构

```
EAIP_Viewer/
├── src/
│   ├── main.py              # 主程序入口
│   ├── config.py            # 配置管理
│   ├── qml/                 # QML 界面文件
│   │   ├── main.qml         # 主窗口
│   │   ├── pages/           # 页面组件
│   │   ├── components/      # 可复用组件
│   │   └── styles/          # 主题样式
│   ├── controllers/         # QML 控制器（桥接层）
│   ├── core/                # 核心业务逻辑
│   ├── models/              # 数据模型（ORM）
│   ├── ui/                  # Python Widgets
│   └── utils/               # 工具函数
├── docs/                    # 项目文档
├── tests/                   # 测试文件
├── resources/               # 资源文件
├── data/                    # 运行时数据
├── scripts/                 # 脚本工具
└── requirements.txt         # 依赖列表
```

## ✅ 已完成功能（基础框架）

- [x] 项目目录结构
- [x] 依赖管理配置
- [x] 主程序入口
- [x] QML 主题系统
- [x] 主窗口和导航框架
- [x] 数据库模型定义
- [x] 数据库管理器
- [x] 基础控制器类
- [x] 日志系统
- [x] 配置管理

## 📖 文档

详细文档请查看 `docs/` 目录：

- [安装部署指南](./docs/01-安装部署指南.md)
- [用户操作手册](./docs/02-用户操作手册.md)
- [开发指南](./docs/03-开发指南.md)
- [架构设计文档](./docs/04-架构设计文档.md)
- [项目阶段计划](./docs/05-项目阶段计划.md)
- [用户认证系统详细文档](./docs/06-用户认证系统详细文档.md)

## 🛠 开发工具

### 代码格式化

```bash
black src/
```

### 代码检查

```bash
flake8 src/
```

### 类型检查

```bash
mypy src/
```

### 运行测试

```bash
pytest
```

## 📝 后续开发计划

按照 [项目阶段计划](./docs/05-项目阶段计划.md)，下一步工作：

### Week 5-6: 用户认证系统
- 实现用户注册、登录功能
- 密码加密和验证
- 会话管理
- 游客模式

### Week 7-8: 机场列表功能
- 导入机场数据
- 实现列表模型
- 搜索和排序功能

### Week 9-10: 航图查看器
- PDF 渲染引擎
- 缩放、平移、旋转功能
- 工具栏实现

详见：[docs/05-项目阶段计划.md](./docs/05-项目阶段计划.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

- Email: 5712.cg8@gmail.com
- GitHub: https://github.com/cg8-5712/EAIP_Viewer
