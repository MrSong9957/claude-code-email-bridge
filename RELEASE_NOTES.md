# Claude Email Bridge v1.0.0

## 功能特性

- 邮件驱动的 Claude Code 远程控制
- IMAP IDLE 实时监控邮件
- SQLite 命令队列，支持重试机制
- Tkinter GUI（零额外依赖）
- 速率限制（30 次/小时）
- 白名单安全验证
- 优雅停机（5秒响应）

## 系统要求

- Windows 10/11 (64-bit)
- 邮箱账户（支持 IMAP/SMTP）
- Claude Code CLI

## 安装说明

### Windows 便携版
1. 下载 `Claude Email Bridge.exe`
2. 将文件放到任意目录
3. 首次运行会在同目录创建配置文件
4. 配置邮箱（参考 .env.example）

### 首次配置

1. **准备邮箱授权码**
   - 登录邮箱设置
   - 开启 IMAP/SMTP 服务
   - 生成授权码（非登录密码）

2. **配置白名单**
   - 设置允许发送命令的邮箱地址

3. **运行应用**
   - Windows: 双击 `Claude Email Bridge.exe`
   - 配置邮箱信息和白名单
   - 点击"启动服务"

## 使用方法

1. **发送命令邮件**
   - 从白名单邮箱发送邮件到配置的邮箱
   - 主题格式: `[command] 你的命令`
   - 例如: `[command] 创建一个 README.md 文件`

2. **查看结果**
   - Claude 执行完成后会自动回复邮件
   - 结果包含执行状态和输出

## 安全建议

- 使用专用邮箱账户
- 定期更换授权码
- 严格限制白名单邮箱
- 不要在公共网络使用
- 建议使用私有邮箱服务器

## 已知问题

- 首次启动需要手动配置邮箱授权码
- Windows Defender 可能误报（需要添加白名单）
- 暂不支持 macOS 和 Linux（可从源码运行）

## 更新日志

### v1.0.0 (2026-02-27)

首次发布：
- 核心功能完整实现
- GUI 配置界面
- 53 个单元测试全部通过
- 打包成独立可执行文件

## 使用文档

查看 [README.md](README.md) 获取详细使用说明。

## 技术栈

- Python 3.8+
- Tkinter (GUI)
- IMAP/SMTP (邮件协议)
- SQLite (命令队列)
- PyInstaller (打包)

## 贡献者

- MrSong9957

## 许可证

MIT License

## 反馈与支持

如有问题或建议，请访问：
https://github.com/MrSong9957/claude-code-email-bridge/issues
