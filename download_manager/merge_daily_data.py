#!/usr/bin/env python3
"""
每日数据合并脚本
每天运行，将新下载的数据与全量数据合并，生成最新的全量数据文件
"""

import pandas as pd
import subprocess
from pathlib import Path
from datetime import datetime


class DailyDataMerger:
    """每日数据合并器"""

    def __init__(self, index_code="H30269", download_dir=None):
        self.index_code = index_code

        # 设置目录
        if download_dir is None:
            download_dir = Path(__file__).parent / "downloads"
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True, parents=True)

        # 文件路径
        self.daily_csv = None  # 当天下载的CSV
        self.full_csv = self.download_dir / f"index_{index_code}_full.csv"

    def fetch_daily_data(self, skip_download=False):
        """运行fetch_index_data.py下载当天数据"""
        if skip_download:
            print("=" * 60)
            print("步骤1: 跳过下载，使用已有数据")
            print("=" * 60)
            # 查找最新下载的CSV文件
            csv_files = sorted(self.download_dir.glob(f"index_{self.index_code}_*.csv"), reverse=True)
            if csv_files:
                self.daily_csv = csv_files[0]
                print(f"✓ 找到已有数据文件: {self.daily_csv}")
                return self.daily_csv
            else:
                print("✗ 未找到下载的CSV文件")
                return None

        print("=" * 60)
        print("步骤1: 下载当天数据")
        print("=" * 60)

        fetch_script = Path(__file__).parent / "fetch_index_data.py"

        try:
            result = subprocess.run(
                ["python", str(fetch_script), self.index_code],
                cwd=str(Path(__file__).parent),
                capture_output=True,
                text=True,
                timeout=60
            )

            print(result.stdout)
            if result.stderr:
                print(result.stderr)

            if result.returncode != 0:
                print(f"✗ 下载数据失败，返回码: {result.returncode}")
                return None

            # 查找最新下载的CSV文件
            csv_files = sorted(self.download_dir.glob(f"index_{self.index_code}_*.csv"), reverse=True)
            if csv_files:
                self.daily_csv = csv_files[0]
                print(f"\n✓ 找到当天数据文件: {self.daily_csv}")
                return self.daily_csv
            else:
                print("✗ 未找到下载的CSV文件")
                return None

        except subprocess.TimeoutExpired:
            print("✗ 下载数据超时")
            return None
        except Exception as e:
            print(f"✗ 下载数据时出错: {e}")
            import traceback
            traceback.print_exc()
            return None

    def load_full_data(self):
        """加载全量数据"""
        print("\n" + "=" * 60)
        print("步骤2: 加载全量数据")
        print("=" * 60)

        if not self.full_csv.exists():
            print(f"全量数据文件不存在: {self.full_csv}")
            return None

        try:
            df = pd.read_csv(self.full_csv, encoding='utf-8-sig')
            print(f"✓ 成功加载全量数据")
            print(f"  文件: {self.full_csv}")
            print(f"  记录数: {len(df)}")
            print(f"  日期范围: {df['日期Date'].min()} 到 {df['日期Date'].max()}")
            return df
        except Exception as e:
            print(f"✗ 加载全量数据失败: {e}")
            return None

    def load_daily_data(self):
        """加载当天数据"""
        print("\n" + "=" * 60)
        print("步骤3: 加载当天数据")
        print("=" * 60)

        if not self.daily_csv or not self.daily_csv.exists():
            print("✗ 当天数据文件不存在")
            return None

        try:
            df = pd.read_csv(self.daily_csv, encoding='utf-8-sig')
            print(f"✓ 成功加载当天数据")
            print(f"  文件: {self.daily_csv}")
            print(f"  记录数: {len(df)}")
            if '日期Date' in df.columns:
                print(f"  日期范围: {df['日期Date'].min()} 到 {df['日期Date'].max()}")
            return df
        except Exception as e:
            print(f"✗ 加载当天数据失败: {e}")
            return None

    def merge_data(self, full_df, daily_df):
        """合并数据，一个日期一行"""
        print("\n" + "=" * 60)
        print("步骤4: 合并数据")
        print("=" * 60)

        # 确保有日期列
        if '日期Date' not in daily_df.columns:
            print("✗ 当天数据缺少日期列")
            return None

        # 如果没有全量数据，直接使用当天数据
        if full_df is None:
            print("全量数据不存在，直接使用当天数据作为全量数据")
            merged_df = daily_df.copy()
        else:
            # 合并数据
            print(f"合并数据...")
            print(f"  全量数据记录数: {len(full_df)}")
            print(f"  当天数据记录数: {len(daily_df)}")

            # 合并两个数据框
            merged_df = pd.concat([full_df, daily_df], ignore_index=True)

            # 去重：按日期列去重，保留最新的记录
            print(f"合并后记录数: {len(merged_df)}")
            merged_df = merged_df.drop_duplicates(subset=['日期Date'], keep='last')
            print(f"去重后记录数: {len(merged_df)}")

        # 按日期降序排序
        merged_df = merged_df.sort_values(by='日期Date', ascending=False).reset_index(drop=True)

        # 显示合并结果
        print(f"\n✓ 数据合并完成")
        print(f"  最终记录数: {len(merged_df)}")
        if '日期Date' in merged_df.columns:
            print(f"  日期范围: {merged_df['日期Date'].min()} 到 {merged_df['日期Date'].max()}")

        return merged_df

    def save_full_data(self, merged_df):
        """保存合并后的全量数据"""
        print("\n" + "=" * 60)
        print("步骤5: 保存全量数据")
        print("=" * 60)

        try:
            merged_df.to_csv(self.full_csv, index=False, encoding='utf-8-sig')
            print(f"✓ 全量数据已保存: {self.full_csv}")
            print(f"  记录数: {len(merged_df)}")
            print(f"  文件大小: {self.full_csv.stat().st_size:,} 字节")

            # 显示最新几条数据
            print(f"\n最新5条数据:")
            print(merged_df.head().to_string())

            return True
        except Exception as e:
            print(f"✗ 保存全量数据失败: {e}")
            return False

    def run(self, skip_download=False):
        """执行完整的合并流程

        Args:
            skip_download: 是否跳过下载步骤（当数据已经下载时使用）
        """
        print(f"\n{'=' * 60}")
        print(f"每日数据合并处理")
        print(f"{'=' * 60}")
        print(f"指数代码: {self.index_code}")
        print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 60}\n")

        # 1. 下载当天数据或使用已有数据
        if not self.fetch_daily_data(skip_download=skip_download):
            print("\n✗ 无法获取当天数据，终止处理")
            return False

        # 2. 加载全量数据
        full_df = self.load_full_data()

        # 3. 加载当天数据
        daily_df = self.load_daily_data()
        if daily_df is None:
            print("\n✗ 无法加载当天数据，终止处理")
            return False

        # 4. 合并数据
        merged_df = self.merge_data(full_df, daily_df)
        if merged_df is None:
            print("\n✗ 数据合并失败，终止处理")
            return False

        # 5. 保存全量数据
        if not self.save_full_data(merged_df):
            print("\n✗ 保存全量数据失败")
            return False

        print(f"\n{'=' * 60}")
        print(f"✓ 每日数据合并处理完成!")
        print(f"{'=' * 60}\n")
        return True


def main():
    """主函数"""
    import sys

    # 可通过命令行参数指定指数代码
    index_code = sys.argv[1] if len(sys.argv) > 1 else "H30269"

    # 可通过参数指定是否跳过下载步骤
    skip_download = "--skip-download" in sys.argv

    merger = DailyDataMerger(index_code=index_code)
    result = merger.run(skip_download=skip_download)

    if result:
        return 0
    else:
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
