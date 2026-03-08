#!/usr/bin/env python3
"""
FinWatch API 测试脚本
用于测试所有API端点的功能
"""

import requests
import json
import sys
import os
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:5000"

def test_api(endpoint, method="GET", data=None, expected_status=200):
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"  不支持的方法: {method}")
            return False

        if response.status_code == expected_status:
            print(f"  ✓ {endpoint} - 状态码 {response.status_code} (预期 {expected_status})")

            # 如果是获取数据，显示简要信息
            if "subjects" in endpoint and method == "GET":
                data = response.json()
                subjects = data.get("subjects", [])
                print(f"    找到 {len(subjects)} 个科目")
                if subjects:
                    print(f"    示例科目: {subjects[0].get('name')}")

            return True
        else:
            print(f"  ✗ {endpoint} - 状态码 {response.status_code} (预期 {expected_status})")
            print(f"    响应: {response.text[:200]}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"  ✗ {endpoint} - 连接失败 (服务器可能未启动)")
        return False
    except Exception as e:
        print(f"  ✗ {endpoint} - 异常: {e}")
        return False

def test_all_apis():
    """测试所有API端点"""
    print("=" * 60)
    print("FinWatch API 测试")
    print("=" * 60)

    # 确保服务器正在运行
    print("\n1. 测试基本连接...")
    if not test_api("/", expected_status=200):
        print("\n错误: 无法连接到服务器。请确保服务器正在运行。")
        print("运行命令: python app.py")
        return False

    print("\n2. 测试科目API...")
    tests = [
        # 端点, 方法, 数据, 预期状态码
        ("/api/subjects", "GET", None, 200),
        ("/api/subjects/stock_price", "GET", None, 200),
        ("/api/subjects/nonexistent", "GET", None, 404),
    ]

    all_passed = True
    for endpoint, method, data, expected in tests:
        if not test_api(endpoint, method, data, expected):
            all_passed = False

    print("\n3. 测试数据API...")
    data_tests = [
        ("/api/data/stock_price", "GET", None, 200),
        ("/api/data/latest", "GET", None, 200),
        ("/api/data/nonexistent", "GET", None, 404),
    ]

    for endpoint, method, data, expected in data_tests:
        if not test_api(endpoint, method, data, expected):
            all_passed = False

    print("\n4. 测试文件扫描API...")
    scan_test = ("/api/scan", "POST", {}, 200)
    if not test_api(*scan_test):
        all_passed = False

    # 测试添加新科目
    print("\n5. 测试添加科目API...")
    new_subject = {
        "id": "test_subject",
        "name": "测试科目",
        "category": "测试分类",
        "unit": "测试单位",
        "description": "这是一个测试科目",
        "file": "data/market.csv",
        "column": "stock_price"
    }

    add_test = ("/api/subjects", "POST", new_subject, 201)
    if not test_api(*add_test):
        all_passed = False

    # 清理：删除测试科目
    print("\n6. 清理测试数据...")
    print("  (注: 删除API需要实现DELETE方法)")

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败")

    return all_passed

def check_dependencies():
    """检查依赖是否安装"""
    print("\n检查依赖...")

    try:
        import flask
        import pandas
        print("  ✓ Flask 已安装")
        print("  ✓ Pandas 已安装")
        return True
    except ImportError as e:
        print(f"  ✗ 依赖未安装: {e}")
        print(f"  运行: pip install -r requirements.txt")
        return False

def check_data_files():
    """检查数据文件"""
    print("\n检查数据文件...")

    required_files = [
        "data/market.csv",
        "data/economy.csv",
        "data/monetary.csv",
        "config/subjects.json"
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (未找到)")
            all_exist = False

    return all_exist

def run_manual_tests():
    """运行手动测试"""
    print("\n" + "=" * 60)
    print("手动测试指南")
    print("=" * 60)

    print("\n1. 启动服务器:")
    print("   python app.py")

    print("\n2. 访问网站:")
    print(f"   打开浏览器访问: {BASE_URL}")

    print("\n3. 测试功能:")
    print("   • 查看仪表板上的科目卡片")
    print("   • 点击科目卡片查看详情")
    print("   • 在图表页面选择科目查看趋势")
    print("   • 在表格页面查看原始数据")
    print("   • 在科目管理页面添加新科目")
    print("   • 在数据上传页面上传新CSV文件")

    print("\n4. 测试动态新增科目:")
    print("   • 将新的CSV文件放入 data/ 目录")
    print("   • 点击'扫描新科目'按钮")
    print("   • 系统会自动发现新数据列并注册为科目")

    print("\n5. API测试:")
    print("   • GET /api/subjects - 获取所有科目")
    print("   • GET /api/data/stock_price - 获取股票价格数据")
    print("   • POST /api/scan - 扫描新科目")

def main():
    """主函数"""
    print("FinWatch 系统测试")
    print("=" * 60)

    # 检查依赖
    if not check_dependencies():
        print("\n请先安装依赖!")
        sys.exit(1)

    # 检查数据文件
    if not check_data_files():
        print("\n缺少必要的数据文件!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("选择测试模式:")
    print("  1. 自动API测试")
    print("  2. 查看手动测试指南")
    print("  3. 退出")

    try:
        choice = input("\n请输入选择 (1-3): ").strip()

        if choice == "1":
            test_all_apis()
        elif choice == "2":
            run_manual_tests()
        elif choice == "3":
            print("退出测试")
        else:
            print("无效选择")

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中出错: {e}")

if __name__ == "__main__":
    main()