#!/usr/bin/env python3
"""
AIPKG 打包命令行工具

使用方法:
    python scripts/build_aipkg.py <source_dir> <output_file> [options]

示例:
    python scripts/build_aipkg.py Data/EAIP2025-07.V1.4/Terminal packages/eaip-2507.aipkg
"""

import sys
import argparse
import getpass
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.aipkg_builder import AIPKGBuilder
from src.utils.logger import setup_logger, logger


def progress_callback(current: int, total: int, message: str):
    """进度回调函数"""
    if total > 0:
        percentage = int(current / total * 100)
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = '=' * filled + '-' * (bar_length - filled)
        print(f'\r[{bar}] {percentage}% - {message}', end='', flush=True)
    else:
        print(f'\r{message}', end='', flush=True)


def main():
    parser = argparse.ArgumentParser(
        description='AIPKG 打包工具 - 将航图目录打包成加密的 .aipkg 文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 基本用法
  python scripts/build_aipkg.py Data/EAIP2025-07.V1.4/Terminal packages/eaip-2507.aipkg

  # 指定版本和压缩级别
  python scripts/build_aipkg.py Data/EAIP2025-07.V1.4/Terminal packages/eaip-2507.aipkg \\
      --version EAIP2025-07.V1.4 \\
      --compression gzip \\
      --level 9

  # 禁用压缩
  python scripts/build_aipkg.py Data/EAIP2025-07.V1.4/Terminal packages/eaip-2507.aipkg \\
      --compression none
        '''
    )

    parser.add_argument(
        'source',
        help='源目录路径（Terminal 目录）'
    )

    parser.add_argument(
        'output',
        help='输出的 .aipkg 文件路径'
    )

    parser.add_argument(
        '-v', '--version',
        help='EAIP 版本（如 EAIP2025-07.V1.4），不指定则自动检测',
        default=None
    )

    parser.add_argument(
        '-p', '--password',
        help='加密密码（不指定则提示输入）',
        default=None
    )

    parser.add_argument(
        '-c', '--compression',
        choices=['gzip', 'none'],
        default='gzip',
        help='压缩算法（默认: gzip）'
    )

    parser.add_argument(
        '-l', '--level',
        type=int,
        choices=range(1, 10),
        default=6,
        help='压缩级别 1-9（默认: 6）'
    )

    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='不显示进度条'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日志级别（默认: INFO）'
    )

    args = parser.parse_args()

    # 设置日志
    setup_logger(level=args.log_level)

    # 验证源目录
    source_path = Path(args.source)
    if not source_path.exists():
        print(f'错误: 源目录不存在: {args.source}')
        return 1

    if not source_path.is_dir():
        print(f'错误: 源路径不是目录: {args.source}')
        return 1

    # 获取密码
    password = args.password
    if not password:
        print('请输入加密密码（至少 8 个字符，建议 12+ 字符）')
        password = getpass.getpass('密码: ')
        password_confirm = getpass.getpass('确认密码: ')

        if password != password_confirm:
            print('错误: 两次输入的密码不一致')
            return 1

        if len(password) < 8:
            print('错误: 密码长度至少 8 个字符')
            return 1

    # 确认输出路径
    output_path = Path(args.output)
    if output_path.exists():
        response = input(f'文件已存在: {args.output}\n是否覆盖? [y/N]: ')
        if response.lower() not in ['y', 'yes']:
            print('取消操作')
            return 0

    # 创建打包器
    builder = AIPKGBuilder()

    # 执行打包
    print('\n' + '=' * 60)
    print('开始打包 AIPKG')
    print('=' * 60)
    print(f'源目录: {args.source}')
    print(f'输出文件: {args.output}')
    print(f'压缩: {args.compression}')
    if args.compression != 'none':
        print(f'压缩级别: {args.level}')
    print('=' * 60)
    print()

    try:
        result = builder.create_package(
            source_dir=str(source_path),
            output_path=str(output_path),
            password=password,
            eaip_version=args.version,
            compression=args.compression,
            compression_level=args.level,
            progress_callback=None if args.no_progress else progress_callback
        )

        print()  # 换行
        print('\n' + '=' * 60)
        print('打包完成！')
        print('=' * 60)
        print(f'输出文件: {result["output_path"]}')
        print(f'EAIP 版本: {result["eaip_version"]}')
        print(f'文件总数: {result["total_files"]}')
        print(f'机场数量: {result["airports_count"]}')
        print(f'原始大小: {result["original_size"] / 1024 / 1024:.2f} MB')
        print(f'压缩后: {result["compressed_size"] / 1024 / 1024:.2f} MB')
        print(f'最终大小: {result["final_size"] / 1024 / 1024:.2f} MB')
        print(f'压缩率: {result["compression_ratio"] * 100:.1f}%')
        print(f'总压缩率: {result["final_size"] / result["original_size"] * 100:.1f}%')
        print('=' * 60)

        return 0

    except KeyboardInterrupt:
        print('\n\n操作被用户中断')
        return 130

    except Exception as e:
        logger.error(f'打包失败: {e}', exc_info=True)
        print(f'\n\n错误: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
