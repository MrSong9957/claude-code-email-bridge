#!/usr/bin/env python3
"""
EmailParser 单元测试
测试邮件解析和白名单验证功能
"""

import pytest
import email
from email.message import Message
from mail.parser import EmailParser


class TestEmailParserWhitelist:
    """白名单验证测试"""

    def test_whitelist_empty_accepts_all(self):
        """测试空白名单接受所有发件人"""
        parser = EmailParser(whitelist=[])
        assert parser.is_sender_whitelisted("anyone@example.com") == True
        assert parser.is_sender_whitelisted("other@domain.com") == True

    def test_whitelist_exact_match(self):
        """测试精确匹配白名单邮箱"""
        parser = EmailParser(whitelist=["user@example.com", "admin@example.com"])

        # 在白名单中
        assert parser.is_sender_whitelisted("user@example.com") == True
        assert parser.is_sender_whitelisted("admin@example.com") == True

        # 不在白名单中
        assert parser.is_sender_whitelisted("other@example.com") == False
        assert parser.is_sender_whitelisted("user@other.com") == False

    def test_whitelist_case_insensitive(self):
        """测试大小写不敏感匹配"""
        parser = EmailParser(whitelist=["User@Example.Com"])

        # 不同大小写都应该匹配
        assert parser.is_sender_whitelisted("user@example.com") == True
        assert parser.is_sender_whitelisted("USER@EXAMPLE.COM") == True
        assert parser.is_sender_whitelisted("User@Example.Com") == True

    def test_whitelist_with_spaces(self):
        """测试带空格的邮箱处理"""
        parser = EmailParser(whitelist=["  user@example.com  "])

        # 去除空格后匹配
        assert parser.is_sender_whitelisted("user@example.com") == True

    def test_whitelist_not_in_list(self):
        """测试不在白名单中的邮箱被拒绝"""
        parser = EmailParser(whitelist=["allowed@example.com"])

        assert parser.is_sender_whitelisted("blocked@example.com") == False
        assert parser.is_sender_whitelisted("allowed@other.com") == False

    def test_set_whitelist_updates(self):
        """测试动态更新白名单"""
        parser = EmailParser(whitelist=["old@example.com"])

        # 初始在白名单中
        assert parser.is_sender_whitelisted("old@example.com") == True
        assert parser.is_sender_whitelisted("new@example.com") == False

        # 更新白名单
        parser.set_whitelist(["new@example.com"])

        # 现在新的在白名单中
        assert parser.is_sender_whitelisted("old@example.com") == False
        assert parser.is_sender_whitelisted("new@example.com") == True

    def test_whitelist_security_bypass(self):
        """测试防止子字符串绕过攻击"""
        parser = EmailParser(whitelist=["admin@example.com"])

        # 之前使用 'in' 会被这些绕过
        assert parser.is_sender_whitelisted("fakeadmin@example.com.evil.com") == False
        assert parser.is_sender_whitelisted("admin@example.com.attacker.com") == False
        assert parser.is_sender_whitelisted("xadmin@example.com") == False

        # 正确的邮箱应该通过
        assert parser.is_sender_whitelisted("admin@example.com") == True


class TestEmailParserSender:
    """发件人提取测试"""

    def test_extract_sender_simple(self):
        """测试简单邮箱格式"""
        msg = Message()
        msg["From"] = "user@example.com"

        parser = EmailParser()
        assert parser.extract_sender(msg) == "user@example.com"

    def test_extract_sender_with_angle_brackets(self):
        """测试带名称和尖括号的格式"""
        msg = Message()
        msg["From"] = "John Doe <john@example.com>"

        parser = EmailParser()
        assert parser.extract_sender(msg) == "john@example.com"

    def test_extract_sender_empty(self):
        """测试空From头"""
        msg = Message()
        msg["From"] = ""

        parser = EmailParser()
        assert parser.extract_sender(msg) == ""

    def test_extract_sender_unicode(self):
        """测试Unicode字符"""
        msg = Message()
        msg["From"] = "张三 <zhang@example.com>"

        parser = EmailParser()
        assert parser.extract_sender(msg) == "zhang@example.com"


class TestEmailParserCommand:
    """命令提取测试"""

    def test_extract_command_plain_text(self):
        """测试纯文本正文提取"""
        msg = Message()
        msg.set_payload("This is a test command")

        parser = EmailParser()
        assert parser.extract_command(msg) == "This is a test command"

    def test_strip_replies_removes_quotes(self):
        """测试去除引用行"""
        text = """This is my command

> This is a quote
> from the previous email
> more quotes"""

        parser = EmailParser()
        result = parser._strip_replies(text)

        # 引用行应该被去除
        assert ">" not in result
        assert "This is my command" in result

    def test_strip_replies_removes_separator(self):
        """测试去除回复分隔符"""
        text = """This is my command

On someone@example.com wrote:
Previous message here"""

        parser = EmailParser()
        result = parser._strip_replies(text)

        # 分隔符之后的内容应该被去除
        assert "On someone@example.com wrote:" not in result
        assert "Previous message here" not in result
        assert "This is my command" in result


class TestEmailParserComplete:
    """完整解析测试"""

    def test_parse_email_complete(self, sample_email_raw):
        """测试完整邮件解析"""
        parser = EmailParser(whitelist=["test@example.com"])

        result = parser.parse_email(sample_email_raw)

        # 验证解析结果
        assert result["sender"] == "test@example.com"
        assert result["is_whitelisted"] == True
        assert "Test Command" in result["subject"]
        assert "test command" in result["command"].lower()

    def test_decode_header_utf8(self):
        """测试UTF-8编码主题"""
        parser = EmailParser()

        # MIME编码的UTF-8主题
        encoded = "=?utf-8?b?5rWL6K+V6YKu5Lu2?="  # "测试主题"
        result = parser._decode_header(encoded)

        assert len(result) > 0
        # 应该成功解码

    def test_html_to_text(self):
        """测试HTML转纯文本"""
        html = "<html><body><h1>Title</h1><p>This is a paragraph</p></body></html>"

        parser = EmailParser()
        result = parser._html_to_text(html)

        # HTML标签应该被移除
        assert "<html>" not in result
        assert "<h1>" not in result
        assert "Title" in result
        assert "This is a paragraph" in result
