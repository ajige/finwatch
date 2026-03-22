#!/usr/bin/env python3
"""
显示中证指数数据的完整内容
支持读取 full.csv 或指定指数的全量数据文件
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import sys


def find_full_csv(downloads_dir, index_code=None):
    """查找全量数据 CSV 文件"""
    downloads_dir = Path(downloads_dir)

    if not downloads_dir.exists():
        print(f"错误：目录不存在：{downloads_dir}")
        return None

    # 根据是否指定指数代码查找文件
    if index_code:
        pattern = f"index_{index_code}_full.csv"
    else:
        pattern = "*_full.csv"

    csv_files = sorted(downloads_dir.glob(pattern), reverse=True)

    if not csv_files:
        print(f"未找到全量数据文件 (pattern: {pattern})")
        return None

    return csv_files[0]


def safe_get(row, df, col_name):
    """安全获取列值，支持模糊匹配"""
    for col in df.columns:
        if col_name in col:
            return row[col]
    return None


def find_column(df, *keywords):
    """查找包含任一关键词的列名"""
    for col in df.columns:
        if any(kw in col for kw in keywords):
            return col
    return None


def display_data(csv_path):
    """显示 CSV 文件数据"""
    print(f"读取文件：{csv_path}")
    print("=" * 100)

    # 读取 CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"错误：读取 CSV 文件失败：{e}")
        return False

    print(f"\n数据统计:")
    print(f"  总行数：{len(df)}")
    print(f"  总列数：{len(df.columns)}")

    # 查找日期列
    date_col = find_column(df, '日期', 'Date', 'date')
    if date_col:
        print(f"  日期范围：{df[date_col].min()} 到 {df[date_col].max()}")
    else:
        print("  日期范围：未找到日期列")

    print(f"\n列名:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")

    print("\n" + "=" * 100)
    print("完整数据:")
    print("=" * 100)

    # 显示所有数据，格式化输出
    for idx, row in df.iterrows():
        print(f"\n第 {idx + 1} 行:")

        # 日期
        date_val = safe_get(row, df, '日期') or safe_get(row, df, 'Date')
        if date_val:
            print(f"  日期：{date_val}")

        # 指数代码
        code_val = safe_get(row, df, '指数代码') or safe_get(row, df, 'Index Code')
        if code_val:
            print(f"  指数代码：{code_val}")

        # 中文名称
        cn_full = safe_get(row, df, '指数中文全称') or safe_get(row, df, 'Chinese Name')
        cn_short = safe_get(row, df, '指数中文简称') or safe_get(row, df, 'Index Chinese Name')
        if cn_full:
            print(f"  中文名称：{cn_full} ({cn_short or 'N/A'})")

        # 英文名称
        en_full = safe_get(row, df, '指数英文全称') or safe_get(row, df, 'English Name')
        en_short = safe_get(row, df, '指数英文简称') or safe_get(row, df, 'Index English Name')
        if en_full:
            print(f"  英文名称：{en_full} ({en_short or 'N/A'})")

        # 市盈率
        pe1 = safe_get(row, df, '市盈率 1') or safe_get(row, df, 'P/E1')
        pe2 = safe_get(row, df, '市盈率 2') or safe_get(row, df, 'P/E2')
        if pe1 is not None:
            try:
                print(f"  市盈率 1 (总股本): {float(pe1):.2f}")
            except (ValueError, TypeError):
                print(f"  市盈率 1 (总股本): {pe1}")
        if pe2 is not None:
            try:
                print(f"  市盈率 2 (计算用股本): {float(pe2):.2f}")
            except (ValueError, TypeError):
                print(f"  市盈率 2 (计算用股本): {pe2}")

        # 股息率
        dp1 = safe_get(row, df, '股息率 1') or safe_get(row, df, 'D/P1')
        dp2 = safe_get(row, df, '股息率 2') or safe_get(row, df, 'D/P2')
        if dp1 is not None:
            try:
                print(f"  股息率 1 (总股本): {float(dp1):.2f}%")
            except (ValueError, TypeError):
                print(f"  股息率 1 (总股本): {dp1}")
        if dp2 is not None:
            try:
                print(f"  股息率 2 (计算用股本): {float(dp2):.2f}%")
            except (ValueError, TypeError):
                print(f"  股息率 2 (计算用股本): {dp2}")

    print("\n" + "=" * 100)
    print("数据分析:")
    print("=" * 100)

    # 查找分析列
    pe1_col = find_column(df, '市盈率 1', 'P/E1')
    pe2_col = find_column(df, '市盈率 2', 'P/E2')
    dp1_col = find_column(df, '股息率 1', 'D/P1')
    dp2_col = find_column(df, '股息率 2', 'D/P2')

    if pe1_col:
        print(f"\n市盈率 1 (总股本):")
        print(f"  最高：{df[pe1_col].max():.2f}")
        print(f"  最低：{df[pe1_col].min():.2f}")
        print(f"  平均：{df[pe1_col].mean():.2f}")
        print(f"  中位数：{df[pe1_col].median():.2f}")

    if pe2_col:
        print(f"\n市盈率 2 (计算用股本):")
        print(f"  最高：{df[pe2_col].max():.2f}")
        print(f"  最低：{df[pe2_col].min():.2f}")
        print(f"  平均：{df[pe2_col].mean():.2f}")
        print(f"  中位数：{df[pe2_col].median():.2f}")

    if dp1_col:
        print(f"\n股息率 1 (总股本):")
        print(f"  最高：{df[dp1_col].max():.2f}%")
        print(f"  最低：{df[dp1_col].min():.2f}%")
        print(f"  平均：{df[dp1_col].mean():.2f}%")
        print(f"  中位数：{df[dp1_col].median():.2f}%")

    if dp2_col:
        print(f"\n股息率 2 (计算用股本):")
        print(f"  最高：{df[dp2_col].max():.2f}%")
        print(f"  最低：{df[dp2_col].min():.2f}%")
        print(f"  平均：{df[dp2_col].mean():.2f}%")
        print(f"  中位数：{df[dp2_col].median():.2f}%")

    print("\n" + "=" * 100)
    return True


def main():
    """主函数"""
    # 可通过命令行参数指定指数代码或文件路径
    index_code = sys.argv[1] if len(sys.argv) > 1 else None

    # 查找全量数据文件
    downloads_dir = Path(__file__).parent / "downloads"

    if index_code and not index_code.startswith('/'):
        csv_path = find_full_csv(downloads_dir, index_code)
    elif index_code and index_code.startswith('/'):
        csv_path = Path(index_code)
        if not csv_path.exists():
            print(f"错误：文件不存在：{csv_path}")
            return 1
    else:
        csv_path = find_full_csv(downloads_dir)

    if not csv_path:
        return 1

    if display_data(csv_path):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
