#!/usr/bin/env python3
"""
项目清理脚本
清理缓存文件和临时文件
"""

import os
import shutil
import sys
from pathlib import Path

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def cleanup():
    """执行清理"""
    root = Path(".")
    deleted = []

    print("开始清理项目目录...")
    print("=" * 50)

    # 1. 清理 __pycache__
    print("\n1. 清理 Python 字节码缓存...")
    count = 0
    for pycache in root.rglob("__pycache__"):
        if pycache.is_dir():
            try:
                shutil.rmtree(pycache)
                deleted.append(str(pycache))
                count += 1
                print(f"   [OK] 删除: {pycache}")
            except Exception as e:
                print(f"   [FAIL] 失败: {pycache} ({e})")

    if count > 0:
        print(f"   共删除 {count} 个 __pycache__ 目录")
    else:
        print("   没有 __pycache__ 目录需要清理")

    # 2. 清理 .pytest_cache
    print("\n2. 清理 pytest 缓存...")
    pytest_cache = root / ".pytest_cache"
    if pytest_cache.exists():
        try:
            shutil.rmtree(pytest_cache)
            deleted.append(str(pytest_cache))
            print(f"   [OK] 删除: {pytest_cache}")
        except Exception as e:
            print(f"   [FAIL] 失败: {e}")
    else:
        print("   .pytest_cache 目录不存在")

    # 3. 清理临时文件
    print("\n3. 清理运行时临时文件...")
    temp_files = [
        ".coverage",
        "commands.db.lock",
        "email_bridge.log",
        "claude_output.txt"
    ]

    for temp_file in temp_files:
        path = root / temp_file
        if path.exists():
            try:
                path.unlink()
                deleted.append(str(path))
                print(f"   [OK] 删除: {temp_file}")
            except Exception as e:
                print(f"   [FAIL] 失败: {temp_file} ({e})")
        else:
            print(f"   [SKIP] 跳过: {temp_file} (不存在)")

    # 输出结果
    print("\n" + "=" * 50)
    if deleted:
        print(f"\n[SUCCESS] 清理完成! 共删除 {len(deleted)} 项")
    else:
        print("\n[INFO] 项目已经很干净，无需清理")

    # 显示保留的核心文件
    print("\n" + "=" * 50)
    print("保留的核心文件和目录:")
    core_files = [
        ("main.py", "主程序入口"),
        ("config/", "配置模块"),
        ("core/", "核心执行模块"),
        ("mail/", "邮件处理模块"),
        ("queue/", "队列管理模块"),
        ("gui/", "GUI界面模块"),
        ("tests/", "测试目录"),
        ("docs/", "文档目录"),
        ("requirements.txt", "依赖清单"),
        ("requirements-test.txt", "测试依赖"),
        ("pyproject.toml", "项目配置"),
        ("README.md", "项目说明"),
        (".env.example", "环境变量模板"),
    ]

    for f, desc in core_files:
        path = Path(f)
        if path.exists():
            print(f"   [OK] {f:<25} {desc}")

    print("\n提示:")
    print("   - 删除的缓存文件会在下次运行时自动重新生成")
    print("   - 如需重新生成测试覆盖率，运行: pytest --cov")
    print("   - 可以定期运行此脚本保持项目整洁")

if __name__ == "__main__":
    cleanup()
