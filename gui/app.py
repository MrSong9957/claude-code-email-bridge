#!/usr/bin/env python3
"""
Claude Email Bridge - GUI 应用
极简配置工具
"""

import webview
from gui.api import BridgeAPI


def main():
    """启动 GUI 应用"""
    # 创建 API 实例
    api = BridgeAPI()

    # 创建窗口
    window = webview.create_window(
        'Claude Email Bridge',
        'gui/index.html',
        js_api=api,
        width=600,
        height=650,
        resizable=False,
        min_size=(600, 650)
    )

    # 启动应用
    webview.start(debug=False)


if __name__ == '__main__':
    main()
