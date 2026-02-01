#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行单元测试脚本
"""
import subprocess
import sys
import os
from pathlib import Path

# 切换到 Backend 目录
backend_dir = Path(__file__).parent.parent / "Backend"
os.chdir(backend_dir)

# 设置测试环境变量
os.environ["TESTING"] = "1"

# 运行 pytest
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
    cwd=backend_dir,
    capture_output=False
)

sys.exit(result.returncode)
