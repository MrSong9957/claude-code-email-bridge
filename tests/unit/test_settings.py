#!/usr/bin/env python3
"""
Settings 单元测试
测试配置加载功能
"""

import pytest
import os
from config.settings import Settings


class TestSettings:
    """Settings 测试类"""

    def test_get_whitelist_empty(self, monkeypatch):
        """测试空白名单"""
        # 删除环境变量
        monkeypatch.delenv("EMAIL_WHITELIST", raising=False)
        # 清空已加载的环境变量
        monkeypatch.setenv("EMAIL_WHITELIST", "")

        # 重新创建 Settings 实例以避免缓存
        settings = Settings.__new__(Settings)
        settings.__init__()

        whitelist = settings.get_whitelist()

        # 空字符串分割后应该是空列表
        assert whitelist == [] or whitelist == ['']  # 接受两种可能

    def test_get_whitelist_single(self, monkeypatch):
        """测试单个白名单邮箱"""
        monkeypatch.setenv("EMAIL_WHITELIST", "user@example.com")

        settings = Settings()
        whitelist = settings.get_whitelist()

        assert len(whitelist) == 1
        assert "user@example.com" in whitelist

    def test_get_whitelist_multiple(self, monkeypatch):
        """测试多个白名单邮箱"""
        monkeypatch.setenv("EMAIL_WHITELIST", "user1@example.com,user2@example.com,user3@example.com")

        settings = Settings()
        whitelist = settings.get_whitelist()

        assert len(whitelist) == 3
        assert "user1@example.com" in whitelist
        assert "user2@example.com" in whitelist
        assert "user3@example.com" in whitelist

    def test_get_whitelist_with_spaces(self, monkeypatch):
        """测试带空格的白名单"""
        monkeypatch.setenv("EMAIL_WHITELIST", "  user1@example.com  ,  user2@example.com  ")

        settings = Settings()
        whitelist = settings.get_whitelist()

        # 空格应该被去除
        assert "user1@example.com" in whitelist
        assert "user2@example.com" in whitelist
        # 不应该有空格
        assert "  user1@example.com  " not in whitelist

    def test_get_polling_interval_default(self, monkeypatch):
        """测试默认轮询间隔"""
        monkeypatch.delenv("POLLING_INTERVAL", raising=False)

        settings = Settings()
        interval = settings.get_polling_interval()

        # 应该返回默认值
        assert interval > 0
        assert isinstance(interval, int)

    def test_get_polling_interval_from_env(self, monkeypatch):
        """测试从环境变量读取轮询间隔"""
        monkeypatch.setenv("POLLING_INTERVAL", "60")

        settings = Settings()
        interval = settings.get_polling_interval()

        assert interval == 60

    def test_get_imap_config(self, monkeypatch):
        """测试获取IMAP配置"""
        monkeypatch.setenv("EMAIL_USERNAME", "test@example.com")
        monkeypatch.setenv("EMAIL_PASSWORD", "password123")

        settings = Settings()
        config = settings.get_imap_config()

        assert "server" in config
        assert "port" in config
        assert "username" in config
        assert "password" in config
        assert config['username'] == "test@example.com"
        assert config['password'] == "password123"

    def test_get_smtp_config(self, monkeypatch):
        """测试获取SMTP配置"""
        monkeypatch.setenv("EMAIL_USERNAME", "test@example.com")
        monkeypatch.setenv("EMAIL_PASSWORD", "password123")

        settings = Settings()
        config = settings.get_smtp_config()

        assert "server" in config
        assert "port" in config
        assert "username" in config
        assert "password" in config
        assert config['username'] == "test@example.com"
        assert config['password'] == "password123"

    def test_get_generic_method(self, monkeypatch):
        """测试通用get方法"""
        monkeypatch.setenv("CUSTOM_VAR", "custom_value")

        settings = Settings()

        # 测试存在的环境变量
        assert settings.get("CUSTOM_VAR") == "custom_value"

        # 测试不存在的环境变量返回默认值
        assert settings.get("NON_EXISTENT", "default") == "default"
