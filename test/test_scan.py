#!/usr/bin/env python3
"""
测试扫描功能，处理中文字符列名
"""

import sys
sys.path.insert(0, '.')

from app import subject_manager

def test_scan():
    """测试扫描功能"""
    print("=" * 60)
    print("测试数据文件扫描功能")
    print("=" * 60)

    print("\n正在扫描data/目录...")
    new_subjects = subject_manager.scan_data_files()

    if new_subjects:
        print(f"\n✓ 发现 {len(new_subjects)} 个新科目:\n")

        for i, subject in enumerate(new_subjects, 1):
            print(f"{i}. {subject['id']}")
            print(f"   名称: {subject['name']}")
            print(f"   列名: {subject['column']}")
            print(f"   文件: {subject['file']}")
            print()

        print("\n所有科目:")
        all_subjects = subject_manager.get_all_subjects()
        print(f"总计: {len(all_subjects)} 个科目")

        # 显示前10个科目
        for i, subject in enumerate(all_subjects[:10], 1):
            print(f"{i}. {subject['id']:40s} - {subject['name']}")
    else:
        print("\n✓ 没有发现新科目")
        print("所有数据列可能已经注册。")

    print("\n" + "=" * 60)
    print("扫描测试完成")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_scan()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)