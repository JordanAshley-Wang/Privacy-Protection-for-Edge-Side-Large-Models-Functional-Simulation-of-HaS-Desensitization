#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HaS (Hide and Seek) 隐私保护技术 - 主入口文件
提供命令行界面，支持文本脱敏与还原功能
"""

from has_entropy_sensitive_retrieval import user_interaction_demo, batch_test

if __name__ == "__main__":
    # 启动用户交互演示
    user_interaction_demo()
    # 如需批量测试，取消下面一行的注释并注释掉上面一行
    # batch_test()