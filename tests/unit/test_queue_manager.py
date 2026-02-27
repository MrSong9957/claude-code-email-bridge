#!/usr/bin/env python3
"""
CommandQueue 单元测试
测试命令队列管理功能
"""

import pytest
import time
from queue.manager import CommandQueue


class TestCommandQueueEnqueueDequeue:
    """入队/出队测试"""

    @pytest.fixture
    def queue(self, temp_db):
        """每个测试使用独立的临时数据库"""
        return CommandQueue(db_path=temp_db, use_lock=False)

    def test_enqueue_success(self, queue):
        """测试成功入队返回ID"""
        cmd_id = queue.enqueue(
            sender="user@example.com",
            command="test command",
            message_id="<msg123@example.com>",
            subject="Test Subject"
        )

        assert cmd_id is not None
        assert cmd_id > 0

    def test_dequeue_success(self, queue):
        """测试成功出队"""
        # 先入队
        queue.enqueue(
            sender="user@example.com",
            command="test cmd",
            message_id="<msg123@example.com>"
        )

        # 再出队
        cmd = queue.dequeue()

        assert cmd is not None
        assert cmd['sender'] == "user@example.com"
        assert cmd['command'] == "test cmd"
        assert cmd['status'] == "processing"

    def test_dequeue_empty_queue(self, queue):
        """测试空队列出队返回None"""
        cmd = queue.dequeue()
        assert cmd is None

    def test_dequeue_updates_status(self, queue):
        """测试出队后状态更新为processing"""
        cmd_id = queue.enqueue("user@example.com", "test cmd")

        # 出队
        cmd = queue.dequeue()

        # 验证状态
        assert cmd['status'] == "processing"

    def test_fifo_order(self, queue):
        """测试先入先出顺序"""
        queue.enqueue("user1@example.com", "cmd1")
        queue.enqueue("user2@example.com", "cmd2")
        queue.enqueue("user3@example.com", "cmd3")

        cmd1 = queue.dequeue()
        cmd2 = queue.dequeue()
        cmd3 = queue.dequeue()

        assert cmd1['sender'] == "user1@example.com"
        assert cmd2['sender'] == "user2@example.com"
        assert cmd3['sender'] == "user3@example.com"


class TestCommandQueueStatus:
    """状态管理测试"""

    @pytest.fixture
    def queue(self, temp_db):
        return CommandQueue(db_path=temp_db, use_lock=False)

    def test_update_status_completed(self, queue):
        """测试更新为completed"""
        cmd_id = queue.enqueue("user@example.com", "test cmd")
        queue.dequeue()

        result = queue.update_status(cmd_id, "completed")

        assert result == True

        # 验证状态已更新
        cmd = queue.get_by_id(cmd_id)
        assert cmd['status'] == "completed"

    def test_update_status_failed(self, queue):
        """测试更新为failed"""
        cmd_id = queue.enqueue("user@example.com", "test cmd")
        queue.dequeue()

        result = queue.update_status(cmd_id, "failed")

        assert result == True

        cmd = queue.get_by_id(cmd_id)
        assert cmd['status'] == "failed"

    def test_update_status_with_result(self, queue):
        """测试带结果更新"""
        cmd_id = queue.enqueue("user@example.com", "test cmd")
        queue.dequeue()

        queue.update_status(cmd_id, "completed", result="Command output here")

        cmd = queue.get_by_id(cmd_id)
        assert cmd['result'] == "Command output here"

    def test_update_status_with_error(self, queue):
        """测试带错误更新"""
        cmd_id = queue.enqueue("user@example.com", "test cmd")
        queue.dequeue()

        queue.update_status(cmd_id, "failed", error="Command failed: timeout")

        cmd = queue.get_by_id(cmd_id)
        assert cmd['error'] == "Command failed: timeout"


class TestCommandQueueRetry:
    """重试机制测试"""

    @pytest.fixture
    def queue(self, temp_db):
        return CommandQueue(db_path=temp_db, use_lock=False)

    def test_increment_retry(self, queue):
        """测试重试计数增加"""
        cmd_id = queue.enqueue("user@example.com", "test cmd")

        # 初始重试次数
        cmd = queue.get_by_id(cmd_id)
        assert cmd['retry_count'] == 0

        # 增加重试
        new_count = queue.increment_retry(cmd_id)
        assert new_count == 1

        # 再次增加
        new_count = queue.increment_retry(cmd_id)
        assert new_count == 2

    def test_should_retry_under_limit(self, queue):
        """测试重试次数内允许"""
        cmd_id = queue.enqueue("user@example.com", "test cmd")

        # 重试2次,默认max_retries=3
        queue.increment_retry(cmd_id)
        queue.increment_retry(cmd_id)

        assert queue.should_retry(cmd_id, max_retries=3) == True

    def test_should_retry_exceeds_limit(self, queue):
        """测试超过max_retries拒绝"""
        cmd_id = queue.enqueue("user@example.com", "test cmd")

        # 重试3次,达到限制
        for _ in range(3):
            queue.increment_retry(cmd_id)

        assert queue.should_retry(cmd_id, max_retries=3) == False


class TestCommandQueueQuery:
    """查询方法测试"""

    @pytest.fixture
    def queue(self, temp_db):
        return CommandQueue(db_path=temp_db, use_lock=False)

    def test_get_stats(self, queue):
        """测试统计信息"""
        # 添加一些命令
        queue.enqueue("user1@example.com", "cmd1")
        queue.enqueue("user2@example.com", "cmd2")
        queue.dequeue()  # 变为processing

        stats = queue.get_stats()

        assert 'pending' in stats
        assert 'processing' in stats
        assert 'completed' in stats
        assert 'failed' in stats

        # 验证统计
        assert stats['pending'] >= 0
        assert stats['processing'] >= 1

    def test_get_pending_commands(self, queue):
        """测试获取待处理列表"""
        queue.enqueue("user1@example.com", "cmd1")
        queue.enqueue("user2@example.com", "cmd2")

        pending = queue.get_pending_commands(limit=10)

        assert len(pending) == 2
        assert all(cmd['status'] == 'pending' for cmd in pending)

    def test_get_by_id_exists(self, queue):
        """测试根据ID获取存在的命令"""
        cmd_id = queue.enqueue("user@example.com", "test cmd")

        cmd = queue.get_by_id(cmd_id)

        assert cmd is not None
        assert cmd['id'] == cmd_id
        assert cmd['sender'] == "user@example.com"

    def test_get_by_id_not_exists(self, queue):
        """测试根据ID获取不存在的命令"""
        cmd = queue.get_by_id(99999)
        assert cmd is None


class TestCommandQueueMaintenance:
    """维护操作测试"""

    @pytest.fixture
    def queue(self, temp_db):
        return CommandQueue(db_path=temp_db, use_lock=False)

    def test_close_releases_lock(self, temp_db):
        """测试关闭释放文件锁"""
        # 使用带锁的队列
        locked_queue = CommandQueue(db_path=temp_db, use_lock=True)

        # 关闭
        locked_queue.close()

        # 锁应该被释放
        assert locked_queue.lock_fd is None
