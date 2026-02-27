"""
PyWebView JS Bridge API
极简 API - 智能配置
"""

import logging
import threading
from typing import Dict, Any, Optional
from config.settings import get_settings
from mail.receiver import EmailReceiver
from mail.sender import EmailSender
from gui.mail_providers import detect_provider

logger = logging.getLogger(__name__)


class BridgeAPI:
    """PyWebView Bridge API - 极简配置"""

    def __init__(self):
        self.settings = get_settings()
        self.running = False
        self.app = None

    # 1. 获取/保存配置
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        email = self.settings.get('EMAIL_ACCOUNT', '')

        # 自动识别邮箱服务商
        provider = detect_provider(email)

        return {
            'email_account': email,
            'email_password': self.settings.get('EMAIL_PASSWORD', ''),
            'provider': provider,
            'whitelist': self.settings.get_whitelist()
        }

    def save_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """保存配置（自动识别服务商）"""
        email = config['email_account']
        password = config['email_password']

        # 自动识别邮箱服务商
        provider = detect_provider(email)

        # 写入 .env 文件
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"EMAIL_IMAP_SERVER={provider['imap_server']}\n")
            f.write(f"EMAIL_IMAP_PORT={provider['imap_port']}\n")
            f.write(f"EMAIL_SMTP_SERVER={provider['smtp_server']}\n")
            f.write(f"EMAIL_SMTP_PORT={provider['smtp_port']}\n")
            f.write(f"EMAIL_ACCOUNT={email}\n")
            f.write(f"EMAIL_PASSWORD={password}\n")
            f.write(f"EMAIL_WHITELIST={','.join(config.get('whitelist', []))}\n")

        # 重新加载配置
        self.settings = get_settings()
        return {
            'success': True,
            'provider': provider
        }

    # 2. 自动识别邮箱服务商
    def detect_email_provider(self, email):
        """根据邮箱地址自动识别服务商"""
        return detect_provider(email)

    # 3. 测试连接
    def test_connection(self):
        """测试 IMAP/SMTP 连接"""
        try:
            # 测试 IMAP
            imap_config = self.settings.get_imap_config()
            receiver = EmailReceiver(
                server=imap_config['server'],
                port=imap_config['port'],
                username=imap_config['username'],
                password=imap_config['password']
            )
            if not receiver.connect():
                return {'success': False, 'error': 'IMAP 连接失败'}
            if not receiver.login():
                return {'success': False, 'error': 'IMAP 登录失败'}

            # 测试 SMTP
            smtp_config = self.settings.get_smtp_config()
            sender = EmailSender(
                server=smtp_config['server'],
                port=smtp_config['port'],
                username=smtp_config['username'],
                password=smtp_config['password']
            )
            if not sender.connect():
                return {'success': False, 'error': 'SMTP 连接失败'}
            if not sender.login():
                return {'success': False, 'error': 'SMTP 登录失败'}

            return {'success': True, 'message': '✅ 连接成功'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # 4. 启动/停止服务
    def start_service(self):
        """启动邮件监听服务"""
        if self.running:
            return {'success': False, 'error': '服务已在运行'}

        try:
            # 在后台线程启动 main.py
            from main import EmailCommandApp

            self.app = EmailCommandApp()

            def run_service():
                try:
                    self.app.start()
                except Exception as e:
                    logger.error(f"服务运行错误: {e}", exc_info=True)
                    self.running = False

            thread = threading.Thread(target=run_service, daemon=True)
            thread.start()
            self.running = True

            return {'success': True, 'message': '服务已启动'}
        except Exception as e:
            return {'success': False, 'error': f'启动失败: {str(e)}'}

    def stop_service(self):
        """停止服务"""
        if not self.running:
            return {'success': False, 'error': '服务未运行'}

        try:
            if self.app:
                self.app.shutdown_requested = True
            self.running = False
            return {'success': True, 'message': '服务已停止'}
        except Exception as e:
            return {'success': False, 'error': f'停止失败: {str(e)}'}

    def get_status(self):
        """获取服务状态"""
        return {
            'running': self.running,
            'status': '运行中' if self.running else '已停止'
        }
