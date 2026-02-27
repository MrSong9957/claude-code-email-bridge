"""
邮箱服务商配置
自动识别邮箱类型并配置 IMAP/SMTP 服务器
"""

MAIL_PROVIDERS = {
    # QQ 邮箱
    'qq.com': {
        'name': 'QQ邮箱',
        'imap_server': 'imap.qq.com',
        'imap_port': 993,
        'smtp_server': 'smtp.qq.com',
        'smtp_port': 587,
        'auth_type': 'auth_code'  # 授权码
    },

    # 163 邮箱
    '163.com': {
        'name': '163邮箱',
        'imap_server': 'imap.163.com',
        'imap_port': 993,
        'smtp_server': 'smtp.163.com',
        'smtp_port': 465,
        'auth_type': 'auth_code'
    },

    # 126 邮箱
    '126.com': {
        'name': '126邮箱',
        'imap_server': 'imap.126.com',
        'imap_port': 993,
        'smtp_server': 'smtp.126.com',
        'smtp_port': 465,
        'auth_type': 'auth_code'
    },

    # Gmail
    'gmail.com': {
        'name': 'Gmail',
        'imap_server': 'imap.gmail.com',
        'imap_port': 993,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'auth_type': 'app_password'  # 应用专用密码
    },

    # Outlook
    'outlook.com': {
        'name': 'Outlook',
        'imap_server': 'outlook.office365.com',
        'imap_port': 993,
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'auth_type': 'password'
    },

    # Hotmail
    'hotmail.com': {
        'name': 'Hotmail',
        'imap_server': 'outlook.office365.com',
        'imap_port': 993,
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'auth_type': 'password'
    },

    # Yahoo Mail
    'yahoo.com': {
        'name': 'Yahoo Mail',
        'imap_server': 'imap.mail.yahoo.com',
        'imap_port': 993,
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'auth_type': 'app_password'
    },

    # iCloud
    'icloud.com': {
        'name': 'iCloud',
        'imap_server': 'imap.mail.me.com',
        'imap_port': 993,
        'smtp_server': 'smtp.mail.me.com',
        'smtp_port': 587,
        'auth_type': 'app_password'
    },

    # 企业邮箱（需用户手动配置）
    'custom': {
        'name': '自定义',
        'imap_server': '',
        'imap_port': 993,
        'smtp_server': '',
        'smtp_port': 587,
        'auth_type': 'password'
    }
}


def detect_provider(email):
    """
    根据邮箱地址识别服务商

    Args:
        email: 邮箱地址

    Returns:
        服务商配置字典
    """
    if not email or '@' not in email:
        return MAIL_PROVIDERS['custom']

    domain = email.split('@')[-1].lower()
    return MAIL_PROVIDERS.get(domain, MAIL_PROVIDERS['custom'])
