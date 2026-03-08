#!/usr/bin/env python3
"""
显示中证指数数据的完整内容
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# 查找最新的CSV文件
downloads_dir = Path(__file__).parent / "downloads"
csv_files = sorted(downloads_dir.glob("*.csv"), reverse=True)

if not csv_files:
    print("未找到CSV文件")
    exit(1)

latest_csv = csv_files[0]
print(f"读取文件: {latest_csv}")
print("=" * 100)

# 读取CSV
df = pd.read_csv(latest_csv)

print(f"\n数据统计:")
print(f"  总行数: {len(df)}")
print(f"  总列数: {len(df.columns)}")
print(f"  日期范围: {df['日期Date'].min()} 到 {df['日期Date'].max()}")

print(f"\n列名:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

print("\n" + "=" * 100)
print("完整数据:")
print("=" * 100)

# 显示所有数据，格式化输出
for idx, row in df.iterrows():
    print(f"\n第 {idx + 1} 行:")
    print(f"  日期: {row['日期Date']}")
    print(f"  指数代码: {row['指数代码Index Code']}")
    print(f"  中文名称: {row['指数中文全称Chinese Name(Full)']} ({row['指数中文简称Index Chinese Name']})")
    print(f"  英文名称: {row['指数英文全称English Name(Full)']} ({row['指数英文简称Index English Name']})")
    print(f"  市盈率1 (总股本): {row['市盈率1（总股本）P/E1']:.2f}")
    print(f"  市盈率2 (计算用股本): {row['市盈率2（计算用股本）P/E2']:.2f}")
    print(f"  股息率1 (总股本): {row['股息率1（总股本）D/P1']:.2f}%")
    print(f"  股息率2 (计算用股本): {row['股息率2（计算用股本）D/P2']:.2f}%")

print("\n" + "=" * 100)
print("数据分析:")
print("=" * 100)

# 市盈率分析
print(f"\n市盈率1 (总股本):")
print(f"  最高: {df['市盈率1（总股本）P/E1'].max():.2f}")
print(f"  最低: {df['市盈率1（总股本）P/E1'].min():.2f}")
print(f"  平均: {df['市盈率1（总股本）P/E1'].mean():.2f}")
print(f"  中位数: {df['市盈率1（总股本）P/E1'].median():.2f}")

print(f"\n市盈率2 (计算用股本):")
print(f"  最高: {df['市盈率2（计算用股本）P/E2'].max():.2f}")
print(f"  最低: {df['市盈率2（计算用股本）P/E2'].min():.2f}")
print(f"  平均: {df['市盈率2（计算用股本）P/E2'].mean():.2f}")
print(f"  中位数: {df['市盈率2（计算用股本）P/E2'].median():.2f}")

# 股息率分析
print(f"\n股息率1 (总股本):")
print(f"  最高: {df['股息率1（总股本）D/P1'].max():.2f}%")
print(f"  最低: {df['股息率1（总股本）D/P1'].min():.2f}%")
print(f"  平均: {df['股息率1（总股本）D/P1'].mean():.2f}%")
print(f"  中位数: {df['股息率1（总股本）D/P1'].median():.2f}%")

print(f"\n股息率2 (计算用股本):")
print(f"  最高: {df['股息率2（计算用股本）D/P2'].max():.2f}%")
print(f"  最低: {df['股息率2（计算用股本）D/P2'].min():.2f}%")
print(f"  平均: {df['股息率2（计算用股本）D/P2'].mean():.2f}%")
print(f"  中位数: {df['股息率2（计算用股本）D/P2'].median():.2f}%")

print("\n" + "=" * 100)
