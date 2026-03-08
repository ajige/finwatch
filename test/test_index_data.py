#!/usr/bin/env python3
"""
测试新指数数据的访问和显示
"""

import sys
sys.path.insert(0, '.')

from app import subject_manager, get_subject_data

def test_index_data():
    """测试指数数据访问"""
    print("=" * 60)
    print("测试 H30269 指数数据")
    print("=" * 60)

    # 识别H30269相关科目
    index_subjects = []
    all_subjects = subject_manager.get_all_subjects()

    for subject in all_subjects:
        if 'H30269' in subject['id']:
            index_subjects.append(subject)

    if index_subjects:
        print(f"\n✓ 找到 {len(index_subjects)} 个H30269相关科目:\n")

        # 选择几个主要的数值科目进行测试
        test_subjects = [
            'index_H30269_full_1PE1',  # 市盈率1
            'index_H30269_full_2PE2',  # 市盈率2
            'index_H30269_full_1DP1',  # 股息率1
            'index_H30269_full_2DP2'   # 股息率2
        ]

        for subject_id in test_subjects:
            subject = subject_manager.get_subject(subject_id)
            if subject:
                print(f"\n科目: {subject['name']}")
                print(f"ID: {subject['id']}")
                print(f"列名: {subject['column']}")

                # 获取数据
                subject_data = get_subject_data(subject_id)
                if subject_data and subject_data['data']:
                    data_count = subject_data['count']
                    latest = subject_data['latest']

                    print(f"数据点数: {data_count}")

                    if latest:
                        print(f"最新值: {latest['value']} (日期: {latest['date']})")

                    # 显示前5个数据点
                    print("前5个数据点:")
                    for i, point in enumerate(subject_data['data'][:5], 1):
                        print(f"  {i}. {point['date']}: {point['value']}")
                else:
                    print("✗ 无法获取数据")
            else:
                print(f"\n✗ 科目 {subject_id} 未找到")
    else:
        print("\n✗ 未找到H30269相关科目")

    # 显示所有可用科目
    print("\n" + "=" * 60)
    print(f"总科目数: {len(all_subjects)}")
    print("=" * 60)

    print("\nH30269指数相关科目列表:")
    for i, subject in enumerate(index_subjects, 1):
        print(f"{i}. {subject['name']:50s}")

if __name__ == '__main__':
    try:
        test_index_data()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)