#!/usr/bin/env python3
"""
截图管理工具
"""

import os
from datetime import datetime

CURRENT_SCREENSHOT_DIR = None

def create_screenshot_dir(account):
    global CURRENT_SCREENSHOT_DIR
    base_dir = os.path.join(os.path.dirname(__file__), "../../screenshots")
    screenshot_dir = os.path.join(base_dir, account)
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    CURRENT_SCREENSHOT_DIR = screenshot_dir
    return screenshot_dir

def get_screenshot_path(filename):
    global CURRENT_SCREENSHOT_DIR
    if CURRENT_SCREENSHOT_DIR is None:
        CURRENT_SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "../../screenshots")
    return os.path.join(CURRENT_SCREENSHOT_DIR, filename)
