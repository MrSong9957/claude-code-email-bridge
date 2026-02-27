#!/usr/bin/env python3
"""
RateLimiter 单元测试
测试速率限制功能
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from mail.parser import RateLimiter


class TestRateLimiter:
    """RateLimiter 测试类"""

    # ========== 基本功能测试 ==========

    def test_is_allowed_first_request(self):
        """测试首次请求允许"""
        limiter = RateLimiter()
        assert limiter.is_allowed("user@example.com") == True

    def test_is_allowed_within_limit(self):
        """测试30次内都允许"""
        limiter = RateLimiter()
        sender = "user@example.com"

        # 30次都应该允许
        for i in range(30):
            assert limiter.is_allowed(sender) == True, f"第{i+1}次请求应该被允许"

    def test_is_allowed_exceeds_limit(self):
        """测试超过30次后拒绝"""
        limiter = RateLimiter()
        sender = "user@example.com"

        # 发送30次请求
        for i in range(30):
            limiter.is_allowed(sender)

        # 第31次应该被拒绝
        assert limiter.is_allowed(sender) == False

    def test_get_remaining_initial(self):
        """测试初始剩余次数为30"""
        limiter = RateLimiter()
        assert limiter.get_remaining("user@example.com") == 30

    def test_get_remaining_after_requests(self):
        """测试请求后剩余次数减少"""
        limiter = RateLimiter()
        sender = "user@example.com"

        # 发送5次请求
        for i in range(5):
            limiter.is_allowed(sender)

        # 应该剩余25次
        assert limiter.get_remaining(sender) == 25

    # ========== 时间窗口测试 ==========

    def test_window_expiry(self):
        """测试时间窗口过期后计数重置"""
        limiter = RateLimiter(max_requests=2)
        sender = "user@example.com"

        # 发送2次请求耗尽配额
        limiter.is_allowed(sender)
        limiter.is_allowed(sender)

        # 应该被拒绝
        assert limiter.is_allowed(sender) == False

        # 模拟时间前进1小时后
        with patch('mail.parser.datetime') as mock_datetime:
            future_time = datetime.now() + timedelta(hours=1, seconds=1)
            mock_datetime.now.return_value = future_time

            # 应该重新允许
            assert limiter.is_allowed(sender) == True
            assert limiter.get_remaining(sender) == 1

    def test_different_senders_independent(self):
        """测试不同发件人独立计数"""
        limiter = RateLimiter(max_requests=2)

        # user1发送2次请求
        limiter.is_allowed("user1@example.com")
        limiter.is_allowed("user1@example.com")

        # user1应该被拒绝
        assert limiter.is_allowed("user1@example.com") == False

        # user2应该仍然允许
        assert limiter.is_allowed("user2@example.com") == True
        # user2只用了1次,所以剩余 2-1=1 次
        assert limiter.get_remaining("user2@example.com") == 1

    # ========== 自定义参数测试 ==========

    def test_custom_max_requests(self):
        """测试自定义max_requests参数"""
        limiter = RateLimiter(max_requests=5)
        sender = "user@example.com"

        # 5次都应该允许
        for i in range(5):
            assert limiter.is_allowed(sender) == True

        # 第6次应该被拒绝
        assert limiter.is_allowed(sender) == False

    def test_custom_window_hours(self):
        """测试自定义window_hours参数"""
        limiter = RateLimiter(max_requests=2, window_hours=2)
        sender = "user@example.com"

        # 发送2次请求耗尽配额
        limiter.is_allowed(sender)
        limiter.is_allowed(sender)

        # 应该被拒绝
        assert limiter.is_allowed(sender) == False

        # 模拟时间前进2小时后
        with patch('mail.parser.datetime') as mock_datetime:
            future_time = datetime.now() + timedelta(hours=2, seconds=1)
            mock_datetime.now.return_value = future_time

            # 应该重新允许
            assert limiter.is_allowed(sender) == True

    # ========== 边界条件测试 ==========

    def test_get_remaining_exhausted(self):
        """测试配额耗尽后剩余为0"""
        limiter = RateLimiter(max_requests=3)
        sender = "user@example.com"

        # 发送3次请求耗尽配额
        for i in range(3):
            limiter.is_allowed(sender)

        # 剩余应该为0
        assert limiter.get_remaining(sender) == 0
