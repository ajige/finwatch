#!/usr/bin/env python3
"""
多指数数据合并脚本
将三个指数的全量数据合并到一个文件中，行为日期，列为每个指数的股息率 D/P2
"""

import pandas as pd
from pathlib import Path
from datetime import datetime


class MultiIndexMerger:
    """多指数数据合并器"""

    def __init__(self, download_dir=None, output_file=None):
        # 设置目录
        if download_dir is None:
            download_dir = Path(__file__).parent / "downloads"
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True, parents=True)

        # 指数代码列表
        self.indices = ["H30269", "930914", "931446"]

        # 输出文件
        if output_file is None:
            output_file = self.download_dir / "multi_index_dividend.csv"
        self.output_file = Path(output_file)

    def load_index_data(self, index_code):
        """加载单个指数的全量数据"""
        full_csv = self.download_dir / f"index_{index_code}_full.csv"

        if not full_csv.exists():
            print(f"✗ 文件不存在：{full_csv}")
            return None

        try:
            df = pd.read_csv(full_csv, encoding='utf-8-sig')

            # 打印可用列名
            print(f"  {index_code} 可用列：{list(df.columns)}")

            # 查找日期列
            date_col = None
            for col in df.columns:
                if col.startswith('日期'):
                    date_col = col
                    break

            # 查找 D/P2 列
            dp2_col = None
            for col in df.columns:
                if 'D/P2' in col or '股息率 2' in col:
                    dp2_col = col
                    break

            if not date_col or not dp2_col:
                print(f"✗ 文件 {full_csv} 缺少必需的列")
                print(f"  找到的日期列：{date_col}")
                print(f"  找到的 D/P2 列：{dp2_col}")
                return None

            result_df = df[[date_col, dp2_col]].copy()
            result_df = result_df.rename(columns={
                date_col: '日期Date',
                dp2_col: f'{index_code}_D/P2'
            })

            print(f"✓ 加载 {index_code} 数据：{len(result_df)} 行 (使用列：{date_col}, {dp2_col})")
            return result_df

        except Exception as e:
            print(f"✗ 加载 {index_code} 数据失败：{e}")
            import traceback
            traceback.print_exc()
            return None

    def merge_all_indices(self):
        """合并所有指数数据"""
        print("=" * 60)
        print("多指数股息率数据合并")
        print("=" * 60)
        print(f"指数列表：{self.indices}")
        print(f"运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()

        # 加载每个指数的数据
        all_data = {}
        for index_code in self.indices:
            df = self.load_index_data(index_code)
            if df is not None:
                all_data[index_code] = df
            print()

        if not all_data:
            print("✗ 没有成功加载任何指数数据")
            return None

        # 以第一个指数的日期为基准进行合并
        merged_df = None
        for index_code, df in all_data.items():
            if merged_df is None:
                merged_df = df.copy()
            else:
                merged_df = merged_df.merge(
                    df,
                    on='日期Date',
                    how='outer'
                )

        # 按日期降序排序
        merged_df = merged_df.sort_values(by='日期Date', ascending=False).reset_index(drop=True)

        # 显示合并结果
        print("合并结果:")
        print(f"  总行数：{len(merged_df)}")
        print(f"  列数：{len(merged_df.columns)}")
        print(f"  日期范围：{merged_df['日期Date'].min()} 到 {merged_df['日期Date'].max()}")
        print()

        # 显示列名
        print("列名:")
        for col in merged_df.columns:
            print(f"  - {col}")
        print()

        # 显示前 10 行
        print("前 10 行数据:")
        print(merged_df.head(10).to_string())
        print()

        return merged_df

    def save_merged_data(self, merged_df):
        """保存合并后的数据"""
        print("保存合并数据...")

        try:
            merged_df.to_csv(self.output_file, index=False, encoding='utf-8-sig')
            print(f"✓ 数据已保存：{self.output_file}")
            print(f"  文件大小：{self.output_file.stat().st_size:,} 字节")
            return True
        except Exception as e:
            print(f"✗ 保存失败：{e}")
            return False

    def run(self):
        """执行完整的合并流程"""
        merged_df = self.merge_all_indices()

        if merged_df is None:
            print("\n✗ 合并失败")
            return False

        if not self.save_merged_data(merged_df):
            print("\n✗ 保存失败")
            return False

        print("\n" + "=" * 60)
        print("✓ 多指数数据合并完成!")
        print("=" * 60)

        return True


def main():
    """主函数"""
    import sys

    # 可通过命令行参数指定输出文件
    output_file = sys.argv[1] if len(sys.argv) > 1 else None

    merger = MultiIndexMerger(output_file=output_file)
    result = merger.run()

    if result:
        return 0
    else:
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
