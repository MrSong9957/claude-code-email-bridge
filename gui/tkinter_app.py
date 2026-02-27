#!/usr/bin/env python3
"""
Claude Email Bridge - Tkinter GUI 应用
极简配置工具（零额外依赖）
"""

import sys
from pathlib import Path


def get_resource_path(relative_path):
    """获取资源文件的绝对路径（兼容 PyInstaller）"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        return Path(sys._MEIPASS) / relative_path
    # 开发环境
    return Path(__file__).parent / relative_path


def get_user_data_dir():
    """获取用户数据目录（用于日志和数据库）"""
    if sys.platform == 'win32':
        # Windows: C:\Users\<user>\AppData\Local\Claude Email Bridge\
        return Path.home() / 'AppData' / 'Local' / 'Claude Email Bridge'
    elif sys.platform == 'darwin':
        # macOS: ~/Library/Application Support/Claude Email Bridge/
        return Path.home() / 'Library' / 'Application Support' / 'Claude Email Bridge'
    else:
        # Linux: ~/.local/share/claude-email-bridge/
        return Path.home() / '.local' / 'share' / 'claude-email-bridge'


# 添加项目根目录到 sys.path
project_root = get_resource_path('..').resolve()
sys.path.insert(0, str(project_root))

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from config.settings import get_settings
from mail.receiver import EmailReceiver
from mail.sender import EmailSender
from gui.mail_providers import detect_provider

logger = logging.getLogger(__name__)


class EmailBridgeGUI:
    """极简配置 GUI"""

    def __init__(self):
        self.settings = get_settings()
        self.running = False
        self.app = None

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("Claude Email Bridge")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # 配置样式
        self.setup_styles()

        # 创建界面
        self.create_widgets()

        # 加载配置
        self.load_config()

    def setup_styles(self):
        """配置样式"""
        style = ttk.Style()
        style.theme_use('clam')  # 使用 clam 主题（更现代）

        # 配置按钮样式
        style.configure('Primary.TButton',
                       font=('Inter', 10),
                       padding=(20, 10))

        style.configure('Secondary.TButton',
                       font=('Inter', 10),
                       padding=(20, 10))

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="32")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === 快速配置 ===
        config_frame = ttk.LabelFrame(main_frame, text=" 📧 快速配置 ", padding="16")
        config_frame.pack(fill=tk.X, pady=(0, 16))

        # 邮箱账号
        ttk.Label(config_frame, text="邮箱账号").grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(config_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=1, column=0, sticky=tk.EW, pady=(0, 4))
        self.email_entry.bind('<KeyRelease>', self.on_email_change)

        self.provider_label = ttk.Label(config_frame, text="", foreground='#059669')
        self.provider_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 12))

        # 授权码
        ttk.Label(config_frame, text="授权码").grid(row=3, column=0, sticky=tk.W, pady=(0, 8))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(config_frame, textvariable=self.password_var,
                                       width=40, show='*')
        self.password_entry.grid(row=4, column=0, sticky=tk.EW, pady=(0, 4))

        self.password_hint_label = ttk.Label(config_frame,
                                            text="QQ邮箱请在 设置→账户→授权码管理 中生成",
                                            foreground='#6B7280')
        self.password_hint_label.grid(row=5, column=0, sticky=tk.W, pady=(0, 12))

        # 高级设置（折叠）
        self.advanced_visible = tk.BooleanVar(value=False)
        self.advanced_btn = ttk.Button(config_frame, text="▼ 高级设置（通常无需修改）",
                                      command=self.toggle_advanced)
        self.advanced_btn.grid(row=6, column=0, sticky=tk.EW, pady=(0, 8))

        self.advanced_frame = ttk.Frame(config_frame)
        self.advanced_frame.grid(row=7, column=0, sticky=tk.EW)
        self.advanced_frame.grid_remove()  # 默认隐藏

        # IMAP 设置
        ttk.Label(self.advanced_frame, text="IMAP 服务器 [自动]").grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
        self.imap_server_var = tk.StringVar()
        ttk.Entry(self.advanced_frame, textvariable=self.imap_server_var,
                 width=40).grid(row=1, column=0, sticky=tk.EW, pady=(0, 8))

        ttk.Label(self.advanced_frame, text="IMAP 端口").grid(row=2, column=0, sticky=tk.W, pady=(0, 4))
        self.imap_port_var = tk.StringVar(value="993")
        ttk.Entry(self.advanced_frame, textvariable=self.imap_port_var,
                 width=40).grid(row=3, column=0, sticky=tk.EW, pady=(0, 8))

        # SMTP 设置
        ttk.Label(self.advanced_frame, text="SMTP 服务器 [自动]").grid(row=4, column=0, sticky=tk.W, pady=(0, 4))
        self.smtp_server_var = tk.StringVar()
        ttk.Entry(self.advanced_frame, textvariable=self.smtp_server_var,
                 width=40).grid(row=5, column=0, sticky=tk.EW, pady=(0, 8))

        ttk.Label(self.advanced_frame, text="SMTP 端口").grid(row=6, column=0, sticky=tk.W, pady=(0, 4))
        self.smtp_port_var = tk.StringVar(value="587")
        ttk.Entry(self.advanced_frame, textvariable=self.smtp_port_var,
                 width=40).grid(row=7, column=0, sticky=tk.EW, pady=(0, 8))

        # 按钮
        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=8, column=0, sticky=tk.EW, pady=(16, 0))

        ttk.Button(btn_frame, text="测试连接",
                  command=self.test_connection).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Button(btn_frame, text="保存并启动",
                  command=self.save_and_start).pack(side=tk.LEFT)

        # === 白名单管理 ===
        whitelist_frame = ttk.LabelFrame(main_frame, text=" 🔒 白名单发件人 ", padding="16")
        whitelist_frame.pack(fill=tk.X, pady=(0, 16))

        # 白名单列表
        self.whitelist_listbox = tk.Listbox(whitelist_frame, height=4,
                                           font=('Inter', 10))
        self.whitelist_listbox.pack(fill=tk.X, pady=(0, 8))

        # 添加/删除按钮
        whitelist_btn_frame = ttk.Frame(whitelist_frame)
        whitelist_btn_frame.pack(fill=tk.X)

        self.new_whitelist_var = tk.StringVar()
        ttk.Entry(whitelist_btn_frame, textvariable=self.new_whitelist_var,
                 width=30).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(whitelist_btn_frame, text="添加",
                  command=self.add_whitelist).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(whitelist_btn_frame, text="删除",
                  command=self.remove_whitelist).pack(side=tk.LEFT)

        # === 服务状态 ===
        status_frame = ttk.LabelFrame(main_frame, text=" 🚀 服务状态 ", padding="16")
        status_frame.pack(fill=tk.X)

        # 状态指示器
        status_indicator_frame = ttk.Frame(status_frame)
        status_indicator_frame.pack(fill=tk.X, pady=(0, 12))

        self.status_canvas = tk.Canvas(status_indicator_frame, width=12, height=12,
                                       highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=(0, 8))
        self.status_dot = self.status_canvas.create_oval(2, 2, 10, 10, fill='#D97706')

        self.status_label = ttk.Label(status_indicator_frame, text="已停止",
                                      font=('Inter', 11, 'bold'))
        self.status_label.pack(side=tk.LEFT)

        # 控制按钮
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(control_frame, text="启动服务",
                                   command=self.start_service)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 12))

        self.stop_btn = ttk.Button(control_frame, text="停止服务",
                                  command=self.stop_service, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

    def on_email_change(self, event=None):
        """邮箱地址变化时自动识别服务商"""
        email = self.email_var.get()

        if '@' not in email:
            self.provider_label.config(text="")
            return

        # 识别服务商
        provider = detect_provider(email)

        # 显示提示
        self.provider_label.config(text=f"识别为：{provider['name']}")

        # 自动填充高级设置
        self.imap_server_var.set(provider['imap_server'])
        self.imap_port_var.set(str(provider['imap_port']))
        self.smtp_server_var.set(provider['smtp_server'])
        self.smtp_port_var.set(str(provider['smtp_port']))

        # 更新授权码提示
        if provider['auth_type'] == 'auth_code':
            self.password_hint_label.config(text="请在邮箱设置中生成授权码")
        elif provider['auth_type'] == 'app_password':
            self.password_hint_label.config(text="请使用应用专用密码")
        else:
            self.password_hint_label.config(text="请使用邮箱密码")

    def toggle_advanced(self):
        """切换高级设置的显示/隐藏"""
        if self.advanced_visible.get():
            self.advanced_frame.grid_remove()
            self.advanced_btn.config(text="▼ 高级设置（通常无需修改）")
            self.advanced_visible.set(False)
        else:
            self.advanced_frame.grid()
            self.advanced_btn.config(text="▲ 高级设置（通常无需修改）")
            self.advanced_visible.set(True)

    def load_config(self):
        """加载配置"""
        # 从 IMAP 配置中获取邮箱账号和密码
        imap_config = self.settings.get_imap_config()
        email = imap_config.get('username', '')
        password = imap_config.get('password', '')
        whitelist = self.settings.get_whitelist()

        self.email_var.set(email)
        self.password_var.set(password)

        # 自动识别服务商
        if email:
            self.on_email_change()

        # 加载白名单
        for item in whitelist:
            self.whitelist_listbox.insert(tk.END, item)

    def save_config(self):
        """保存配置"""
        email = self.email_var.get()
        password = self.password_var.get()

        # 获取白名单
        whitelist = []
        for i in range(self.whitelist_listbox.size()):
            whitelist.append(self.whitelist_listbox.get(i))

        # 自动识别服务商
        provider = detect_provider(email)

        # 写入 .env 文件
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f"IMAP_SERVER={provider['imap_server']}\n")
            f.write(f"IMAP_PORT={provider['imap_port']}\n")
            f.write(f"SMTP_SERVER={provider['smtp_server']}\n")
            f.write(f"SMTP_PORT={provider['smtp_port']}\n")
            f.write(f"EMAIL_USERNAME={email}\n")
            f.write(f"EMAIL_PASSWORD={password}\n")
            f.write(f"EMAIL_WHITELIST={','.join(whitelist)}\n")

        # 重新加载配置
        self.settings = get_settings()

    def test_connection(self):
        """测试连接"""
        self.save_config()

        try:
            # 测试 IMAP
            imap_config = self.settings.get_imap_config()
            receiver = EmailReceiver(
                server=imap_config['server'],
                port=imap_config['port'],
                username=imap_config['username'],
                password=imap_config['password']
            )
            if not receiver.connect() or not receiver.login():
                messagebox.showerror("错误", "IMAP 连接失败")
                return

            # 测试 SMTP
            smtp_config = self.settings.get_smtp_config()
            sender = EmailSender(
                server=smtp_config['server'],
                port=smtp_config['port'],
                username=smtp_config['username'],
                password=smtp_config['password']
            )
            if not sender.connect() or not sender.login():
                messagebox.showerror("错误", "SMTP 连接失败")
                return

            messagebox.showinfo("成功", "✅ 连接成功")
        except Exception as e:
            messagebox.showerror("错误", f"连接失败: {str(e)}")

    def add_whitelist(self):
        """添加白名单"""
        email = self.new_whitelist_var.get().strip()
        if not email:
            return

        if '@' not in email:
            messagebox.showwarning("警告", "请输入有效的邮箱地址")
            return

        self.whitelist_listbox.insert(tk.END, email)
        self.new_whitelist_var.set("")
        self.save_config()

    def remove_whitelist(self):
        """删除白名单"""
        selection = self.whitelist_listbox.curselection()
        if not selection:
            return

        self.whitelist_listbox.delete(selection[0])
        self.save_config()

    def save_and_start(self):
        """保存并启动"""
        if not self.email_var.get():
            messagebox.showwarning("警告", "请输入邮箱账号")
            return

        if not self.password_var.get():
            messagebox.showwarning("警告", "请输入授权码")
            return

        self.save_config()
        self.start_service()

    def start_service(self):
        """启动服务"""
        if self.running:
            messagebox.showwarning("警告", "服务已在运行")
            return

        try:
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

            # 更新状态
            self.update_status(True)
            messagebox.showinfo("成功", "✅ 服务已启动")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {str(e)}")

    def stop_service(self):
        """停止服务"""
        if not self.running:
            return

        try:
            if self.app:
                self.app.shutdown_requested = True
            self.running = False

            # 更新状态
            self.update_status(False)
            messagebox.showinfo("成功", "✅ 服务已停止")
        except Exception as e:
            messagebox.showerror("错误", f"停止失败: {str(e)}")

    def update_status(self, running):
        """更新状态显示"""
        if running:
            self.status_canvas.itemconfig(self.status_dot, fill='#059669')
            self.status_label.config(text="运行中")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.status_canvas.itemconfig(self.status_dot, fill='#D97706')
            self.status_label.config(text="已停止")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)

    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主函数"""
    app = EmailBridgeGUI()
    app.run()


if __name__ == '__main__':
    main()
