"""
AIPKG 打包工具测试脚本

用于测试打包功能的基本用例
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.aipkg_builder import AIPKGBuilder
from src.core.aipkg_format import AIPKGHeader
from src.utils.logger import setup_logger, logger


def create_test_data(temp_dir: Path) -> Path:
    """创建测试数据"""
    terminal_dir = temp_dir / "Terminal"
    terminal_dir.mkdir(parents=True, exist_ok=True)

    # 创建测试机场
    zbaa_dir = terminal_dir / "ZBAA"
    zbaa_dir.mkdir(exist_ok=True)

    # 创建测试分类
    sid_dir = zbaa_dir / "SID"
    sid_dir.mkdir(exist_ok=True)

    # 创建测试 PDF 文件（模拟）
    test_files = [
        "ZBAA-7A01-SID RNAV RWY01-36L-36R(IDKEX).pdf",
        "ZBAA-7A02-SID RNAV RWY01-36L-36R(DOTRA).pdf",
        "ZBAA-7A03-SID RNAV RWY01-36R(LULTA).pdf",
    ]

    for file_name in test_files:
        file_path = sid_dir / file_name
        # 写入一些测试内容（模拟 PDF）
        with open(file_path, 'wb') as f:
            # PDF 魔数
            f.write(b'%PDF-1.4\n')
            # 写入一些内容
            test_content = f"Test content for {file_name}\n" * 1000
            f.write(test_content.encode('utf-8'))
            # PDF 结束标记
            f.write(b'%%EOF\n')

    logger.info(f"Created test data in {terminal_dir}")
    return terminal_dir


def test_basic_packaging():
    """测试基本打包功能"""
    logger.info("=" * 60)
    logger.info("Test 1: Basic Packaging")
    logger.info("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 创建测试数据
        terminal_dir = create_test_data(temp_path)

        # 输出路径
        output_path = temp_path / "test.aipkg"

        # 创建打包器
        builder = AIPKGBuilder()

        # 执行打包
        result = builder.create_package(
            source_dir=str(terminal_dir),
            output_path=str(output_path),
            password="TestPassword123!",
            eaip_version="EAIP2025-07.V1.4",
            compression="gzip",
            compression_level=6
        )

        # 验证结果
        assert result['success'], "Packaging failed"
        assert output_path.exists(), "Output file not created"
        assert result['total_files'] == 3, f"Expected 3 files, got {result['total_files']}"
        assert result['airports_count'] == 1, f"Expected 1 airport, got {result['airports_count']}"

        # 验证文件大小
        file_size = output_path.stat().st_size
        assert file_size > 0, "Output file is empty"

        # 验证 Header
        with open(output_path, 'rb') as f:
            header_bytes = f.read(512)
            header = AIPKGHeader.from_byte  s(header_bytes)
            assert header.magic == b'AIPK', f"Invalid magic: {header.magic}"
            assert header.total_files == 3, f"Header file count mismatch"

        logger.info("✅ Test 1 PASSED")
        logger.info(f"  - Files: {result['total_files']}")
        logger.info(f"  - Size: {file_size} bytes")
        logger.info(f"  - Compression: {result['compression_ratio'] * 100:.1f}%")


def test_no_compression():
    """测试无压缩打包"""
    logger.info("=" * 60)
    logger.info("Test 2: No Compression")
    logger.info("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 创建测试数据
        terminal_dir = create_test_data(temp_path)

        # 输出路径
        output_path = temp_path / "test_no_compress.aipkg"

        # 创建打包器
        builder = AIPKGBuilder()

        # 执行打包（无压缩）
        result = builder.create_package(
            source_dir=str(terminal_dir),
            output_path=str(output_path),
            password="TestPassword123!",
            compression="none"
        )

        # 验证
        assert result['success'], "Packaging failed"
        assert output_path.exists(), "Output file not created"

        # 无压缩时，压缩率应该接近 1.0
        assert result['compression_ratio'] > 0.95, "Compression ratio too low for 'none'"

        logger.info("✅ Test 2 PASSED")
        logger.info(f"  - Compression ratio: {result['compression_ratio'] * 100:.1f}%")


def test_invalid_password():
    """测试弱密码拒绝"""
    logger.info("=" * 60)
    logger.info("Test 3: Invalid Password")
    logger.info("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 创建测试数据
        terminal_dir = create_test_data(temp_path)

        # 输出路径
        output_path = temp_path / "test_weak_pass.aipkg"

        # 创建打包器
        builder = AIPKGBuilder()

        # 尝试使用弱密码
        try:
            builder.create_package(
                source_dir=str(terminal_dir),
                output_path=str(output_path),
                password="123",  # 太短
                eaip_version="EAIP2025-07.V1.4"
            )
            assert False, "Should have rejected weak password"
        except ValueError as e:
            logger.info(f"✅ Test 3 PASSED - Correctly rejected weak password: {e}")


def test_empty_directory():
    """测试空目录"""
    logger.info("=" * 60)
    logger.info("Test 4: Empty Directory")
    logger.info("=" * 60)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 创建空的 Terminal 目录
        terminal_dir = temp_path / "Terminal"
        terminal_dir.mkdir(parents=True, exist_ok=True)

        # 输出路径
        output_path = temp_path / "test_empty.aipkg"

        # 创建打包器
        builder = AIPKGBuilder()

        # 执行打包
        result = builder.create_package(
            source_dir=str(terminal_dir),
            output_path=str(output_path),
            password="TestPassword123!",
            eaip_version="EAIP2025-07.V1.4"
        )

        # 验证
        assert result['success'], "Packaging failed"
        assert result['total_files'] == 0, "Should have 0 files"
        assert result['airports_count'] == 0, "Should have 0 airports"

        logger.info("✅ Test 4 PASSED")


def main():
    """运行所有测试"""
    setup_logger(level="INFO")

    logger.info("")
    logger.info("=" * 60)
    logger.info("AIPKG Builder Test Suite")
    logger.info("=" * 60)
    logger.info("")

    tests = [
        ("基本打包功能", test_basic_packaging),
        ("无压缩打包", test_no_compression),
        ("弱密码拒绝", test_invalid_password),
        ("空目录处理", test_empty_directory),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            logger.info(f"\n开始测试: {test_name}")
            test_func()
            passed += 1
        except Exception as e:
            logger.error(f"❌ Test FAILED: {test_name}")
            logger.error(f"  Error: {e}", exc_info=True)
            failed += 1

    logger.info("")
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    logger.info(f"Total: {len(tests)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
