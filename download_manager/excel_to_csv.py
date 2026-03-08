#!/usr/bin/env python3
"""
将Excel文件转换为CSV文件
"""

import pandas as pd
from pathlib import Path

def excel_to_csv(excel_path, csv_path=None):
    """
    将Excel文件转换为CSV文件

    Args:
        excel_path: Excel文件路径
        csv_path: 输出CSV文件路径（可选）
    """
    excel_file = Path(excel_path)

    if not excel_file.exists():
        print(f"错误: Excel文件不存在: {excel_file}")
        return None

    print(f"读取Excel文件: {excel_file}")

    try:
        # 读取Excel文件
        df = pd.read_excel(excel_file, engine='xlrd')

        print(f"✓ 成功读取Excel文件")
        print(f"  行数: {len(df)}")
        print(f"  列数: {len(df.columns)}")
        print(f"  列名: {list(df.columns)}")

        # 确定输出路径
        if csv_path is None:
            csv_path = excel_file.with_suffix('.csv')
        else:
            csv_path = Path(csv_path)

        # 确保输出目录存在
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入CSV文件
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        print(f"\n✓ CSV文件已生成: {csv_path}")
        print(f"  文件大小: {csv_path.stat().st_size:,} 字节")

        return csv_path

    except Exception as e:
        print(f"✗ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python excel_to_csv.py <excel文件路径> [csv输出路径]")
        print("\n示例:")
        print("  python excel_to_csv.py index_H30269.xls")
        print("  python excel_to_csv.py index_H30269.xls output.csv")
        return 1

    excel_path = sys.argv[1]
    csv_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = excel_to_csv(excel_path, csv_path)

    if result:
        return 0
    else:
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
