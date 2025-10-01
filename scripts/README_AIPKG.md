# AIPKG 打包工具使用说明

## 简介

AIPKG 打包工具用于将原始航图目录打包成加密的 `.aipkg` 文件，用于分发和更新。

## 快速开始

### 1. 基本用法

```bash
python scripts/build_aipkg.py <源目录> <输出文件>
```

**示例：**

```bash
# 打包 EAIP 2025-07 版本
python scripts/build_aipkg.py Data/EAIP2025-07.V1.4/Terminal packages/eaip-2507.aipkg
```

运行后会提示输入加密密码。

### 2. 命令行参数

```bash
python scripts/build_aipkg.py [-h] [-v VERSION] [-p PASSWORD]
                               [-c {gzip,none}] [-l {1-9}]
                               [--no-progress] [--log-level {DEBUG,INFO,WARNING,ERROR}]
                               source output
```

#### 必需参数

- `source`: 源目录路径（Terminal 目录）
- `output`: 输出的 .aipkg 文件路径

#### 可选参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-v, --version` | EAIP 版本（如 EAIP2025-07.V1.4） | 自动检测 |
| `-p, --password` | 加密密码 | 提示输入 |
| `-c, --compression` | 压缩算法（gzip, none） | gzip |
| `-l, --level` | 压缩级别（1-9） | 6 |
| `--no-progress` | 不显示进度条 | False |
| `--log-level` | 日志级别 | INFO |

### 3. 使用示例

#### 示例 1：基本打包（交互式输入密码）

```bash
python scripts/build_aipkg.py Data/EAIP2025-07.V1.4/Terminal packages/eaip-2507.aipkg
```

#### 示例 2：指定版本和密码

```bash
python scripts/build_aipkg.py \
    Data/EAIP2025-07.V1.4/Terminal \
    packages/eaip-2507.aipkg \
    --version EAIP2025-07.V1.4 \
    --password "MySecurePassword123!"
```

#### 示例 3：最高压缩率

```bash
python scripts/build_aipkg.py \
    Data/EAIP2025-07.V1.4/Terminal \
    packages/eaip-2507.aipkg \
    --compression gzip \
    --level 9
```

#### 示例 4：禁用压缩（最快速度）

```bash
python scripts/build_aipkg.py \
    Data/EAIP2025-07.V1.4/Terminal \
    packages/eaip-2507.aipkg \
    --compression none
```

#### 示例 5：调试模式

```bash
python scripts/build_aipkg.py \
    Data/EAIP2025-07.V1.4/Terminal \
    packages/eaip-2507.aipkg \
    --log-level DEBUG
```

## 目录结构要求

源目录必须是 EAIP 的 `Terminal` 目录，结构如下：

```
Terminal/
├─ ZBAA/                    # 机场 ICAO 代码
│  ├─ ADC/                  # 机场图
│  │  └─ ZBAA-1A-ADC.pdf
│  ├─ SID/                  # 离场程序
│  │  ├─ ZBAA-7A01-SID RNAV RWY01-36L-36R(IDKEX).pdf
│  │  └─ ...
│  ├─ STAR/                 # 进场程序
│  └─ ...
├─ ZBAD/
└─ ...
```

## 密码要求

为了保证安全性，密码必须满足以下要求：

- ✅ 最小长度：8 个字符（建议 12+ 字符）
- ✅ 包含大写字母
- ✅ 包含小写字母
- ✅ 包含数字
- ✅ 建议包含特殊字符
- ❌ 不能使用常见弱密码（如 password123）

**密码示例（强密码）：**
- `MyEAIP@2025!Secure`
- `Aviat10n#Chart$2025`
- `Fly!ng@Secur3Pass`

## 输出信息

打包完成后会显示以下信息：

```
============================================================
打包完成！
============================================================
输出文件: packages/eaip-2507.aipkg
EAIP 版本: EAIP2025-07.V1.4
文件总数: 3421
机场数量: 156
原始大小: 1024.00 MB
压缩后: 512.00 MB
最终大小: 520.00 MB
压缩率: 50.0%
总压缩率: 50.8%
============================================================
```

## 性能参数

### 压缩级别对比

| 级别 | 压缩率 | 速度 | 推荐场景 |
|------|--------|------|----------|
| 1 | ~30% | 最快 | 快速测试 |
| 6 | ~50% | 平衡 | **推荐默认** |
| 9 | ~55% | 最慢 | 最终分发 |
| none | 0% | 极快 | 仅加密 |

### 预估时间

以 3000 个文件（总计 1GB）为例：

| 配置 | 预估时间 |
|------|----------|
| 级别 1 | ~2 分钟 |
| 级别 6 | ~5 分钟 |
| 级别 9 | ~10 分钟 |
| 无压缩 | ~1 分钟 |

## 常见问题

### Q1: 提示"密码过于简单"

**A**: 请使用更强的密码，包含大小写字母、数字和特殊字符。

### Q2: 打包过程中断了怎么办？

**A**: 重新运行命令即可，临时文件会自动清理。

### Q3: 如何验证打包的文件是否正确？

**A**: 使用读取工具验证：

```bash
python scripts/verify_aipkg.py packages/eaip-2507.aipkg
```

### Q4: 可以修改已经打包的文件吗？

**A**: 不可以，需要重新打包。AIPKG 格式包含完整性校验，任何修改都会被检测到。

### Q5: 忘记密码怎么办？

**A**: 无法恢复，这是加密系统的安全特性。请妥善保管密码。

## 安全注意事项

1. **密码管理**
   - 使用强密码
   - 不要在命令行中明文指定密码（会留在 shell 历史中）
   - 建议使用交互式输入密码

2. **文件保护**
   - 打包后的 .aipkg 文件包含加密数据
   - 原始 Terminal 目录可以删除（建议保留备份）
   - .aipkg 文件可以安全分发

3. **密钥安全**
   - 用户密码不会存储在任何地方
   - 加密密钥只在打包过程中存在于内存
   - 进程结束后自动清除

## 高级用法

### 批量打包多个版本

```bash
#!/bin/bash

versions=(
    "EAIP2025-07.V1.4"
    "EAIP2025-08.V1.0"
    "EAIP2025-09.V1.0"
)

for version in "${versions[@]}"; do
    echo "打包 $version..."
    python scripts/build_aipkg.py \
        "Data/$version/Terminal" \
        "packages/${version,,}.aipkg" \
        --version "$version" \
        --password "YourSecurePassword123!" \
        --level 6
done
```

### 使用环境变量传递密码

```bash
export AIPKG_PASSWORD="YourSecurePassword123!"

python scripts/build_aipkg.py \
    Data/EAIP2025-07.V1.4/Terminal \
    packages/eaip-2507.aipkg \
    --password "$AIPKG_PASSWORD"
```

## 技术规格

- **加密算法**: AES-256-GCM
- **密钥派生**: PBKDF2-HMAC-SHA256（100,000 迭代）
- **压缩算法**: gzip
- **哈希算法**: SHA-256
- **文件格式**: 自定义二进制格式（详见文档）

## 相关文档

- [航图加密方案详细设计](../docs/07-航图加密方案.md)
- [AIPKG 文件格式规范](../docs/aipkg-format-spec.md)
- [开发指南](../docs/03-开发指南.md)

## 支持与反馈

如有问题，请查看：
- 项目 README
- 开发文档
- GitHub Issues

---

**版本**: 1.0
**最后更新**: 2025-10-01
