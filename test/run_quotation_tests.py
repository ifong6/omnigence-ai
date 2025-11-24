#!/usr/bin/env python
"""
独立测试运行脚本 - 绕过数据库配置检查

用法:
    python test/run_quotation_tests.py
"""
import os
import sys

# ⚠️ 重要：必须在导入任何 app 模块之前设置这些环境变量！
# 因为 engine.py 在模块加载时就会检查数据库配置

# 设置测试模式环境变量
os.environ["USE_DB_SCHEMA"] = "0"
os.environ["TESTING"] = "1"

# 设置假的数据库配置，绕过 engine.py 的检查
# 测试实际使用的是 SQLite 内存数据库，不会用到这些配置
os.environ["SB_USER"] = "test_user"
os.environ["SB_PASSWORD"] = "test_pass"
os.environ["SB_HOST"] = "localhost"
os.environ["SB_PORT"] = "5432"
os.environ["SB_DBNAME"] = "test_db"

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 现在可以安全导入 unittest
import unittest

def run_tests():
    """运行所有 quotation 测试"""
    print("=" * 70)
    print("🧪 Running Quotation Tests")
    print("=" * 70)
    print()

    # 创建测试加载器
    loader = unittest.TestLoader()

    # 加载所有 quotation 测试
    suite = unittest.TestSuite()

    # 加载 test_quotation_service_create.py 的所有测试
    try:
        from test import test_quotation_service_create
        suite.addTests(loader.loadTestsFromModule(test_quotation_service_create))
        print("✅ Loaded test_quotation_service_create.py")
    except Exception as e:
        print(f"❌ Failed to load test_quotation_service_create.py: {e}")
        return False

    # 加载 test_quotation_service_update.py 的所有测试
    try:
        from test import test_quotation_service_update
        suite.addTests(loader.loadTestsFromModule(test_quotation_service_update))
        print("✅ Loaded test_quotation_service_update.py")
    except Exception as e:
        print(f"❌ Failed to load test_quotation_service_update.py: {e}")
        return False

    print()
    print("=" * 70)
    print(f"📊 Total Tests: {suite.countTestCases()}")
    print("=" * 70)
    print()

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印总结
    print()
    print("=" * 70)
    print("📈 Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
