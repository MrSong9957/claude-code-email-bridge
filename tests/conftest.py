"""
pytest 配置文件
定义通用 fixtures
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_email_raw():
    """示例原始邮件"""
    return b"""From: test@example.com
To: claude@bridge.com
Subject: Test Command
Message-ID: <test123@example.com>

This is a test command.
"""


@pytest.fixture
def temp_db(tmp_path):
    """临时数据库路径"""
    return str(tmp_path / "test_commands.db")
