#!/usr/bin/env python3
"""
中证指数数据下载和解析器
使用直接URL下载Excel文件并提取所有数据
"""

import os
import requests
from datetime import datetime
from pathlib import Path
import pandas as pd


# 支持的指数代码及其对应的 URL 模式
INDEX_URL_MAP = {
    "H30269": "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls",
    "930914": "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/930914indicator.xls",
    "931446": "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/931446indicator.xls",
}

class IndexValuationFetcher:
    """指数估值数据获取和解析器"""

    def __init__(self, index_code="H30269", base_url=None, download_dir=None):
        self.index_code = index_code

        # 使用用户提供的直接URL模式
        if base_url:
            self.base_url = base_url
        elif index_code in INDEX_URL_MAP:
            # 默认URL模式
            # 从映射表获取 URL
            self.base_url = INDEX_URL_MAP[index_code]
        else:
            # 默认 URL 模式（适用于未知指数代码）
            self.base_url = f"https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/{index_code}indicator.xls"

        # 设置下载目录
        if download_dir is None:
            download_dir = Path(__file__).parent / "downloads"
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True, parents=True)

        self.excel_file = None
        self.csv_file = None
        self.data = None

    def download_excel(self):
        """下载Excel文件"""
        print(f"正在下载Excel文件...")
        print(f"URL: {self.base_url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(self.base_url, headers=headers, timeout=30)

            if response.status_code == 200:
                # 构造文件名（只使用日期，不包含时间）
                date_suffix = datetime.now().strftime('%Y%m%d')
                filename = f"index_{self.index_code}_{date_suffix}.xls"
                filepath = self.download_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                self.excel_file = filepath
                print(f"✓ Excel文件已下载: {filepath}")
                print(f"  文件大小: {len(response.content):,} 字节")
                return True
            else:
                print(f"✗ 下载失败，状态码: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ 下载Excel文件时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def parse_excel_data(self):
        """解析Excel文件并提取所有数据"""
        if not self.excel_file or not self.excel_file.exists():
            print("✗ Excel文件不存在")
            return None

        print(f"\n正在解析Excel文件...")
        print(f"文件: {self.excel_file}")

        try:
            # 尝试使用xlrd引擎（针对.xls文件）
            try:
                df = pd.read_excel(self.excel_file, engine='xlrd')
                print("✓ 使用xlrd引擎解析成功")
            except:
                # 如果xlrd失败，尝试openpyxl
                df = pd.read_excel(self.excel_file, engine='openpyxl')
                print("✓ 使用openpyxl引擎解析成功")

            print(f"\n数据概览:")
            print(f"  总行数: {len(df):,}")
            print(f"  总列数: {len(df.columns)}")
            print(f"  列名: {list(df.columns)}")

            # 显示数据类型
            print(f"\n数据类型:")
            for col in df.columns:
                dtype = df[col].dtype
                null_count = df[col].isnull().sum()
                print(f"  {col}: {dtype} (空值: {null_count})")

            # 显示前几行和后几行数据
            print(f"\n前5行数据:")
            print(df.head().to_string())

            if len(df) > 5:
                print(f"\n后5行数据:")
                print(df.tail().to_string())

            # 转换为字典列表格式
            data = []
            for idx, row in df.iterrows():
                row_dict = {}
                for col in df.columns:
                    value = row[col]
                    # 处理NaN值
                    if pd.isna(value):
                        row_dict[col] = None
                    elif isinstance(value, (pd.Timestamp, datetime)):
                        row_dict[col] = value.strftime('%Y-%m-%d') if hasattr(value, 'strftime') else str(value)
                    else:
                        row_dict[col] = value
                data.append(row_dict)

            self.data = {
                "filename": self.excel_file.name,
                "index_code": self.index_code,
                "columns": list(df.columns),
                "row_count": len(df),
                "data": data,
                "raw_dataframe": df
            }

            print(f"\n✓ 数据解析完成")
            print(f"  提取记录数: {len(data):,}")
            return self.data

        except Exception as e:
            print(f"✗ 解析Excel文件时出错: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_to_csv(self, data_dict=None, csv_filename=None):
        """将数据保存为CSV文件"""
        if data_dict is None:
            data_dict = self.data

        if not data_dict or 'raw_dataframe' not in data_dict:
            print("✗ 无有效的数据可保存")
            return None

        df = data_dict['raw_dataframe']

        if csv_filename is None:
            date_suffix = datetime.now().strftime('%Y%m%d')
            csv_filename = f"index_{self.index_code}_{date_suffix}.csv"

        csv_path = self.download_dir / csv_filename
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        self.csv_file = csv_path
        print(f"\n✓ CSV文件已保存: {csv_path}")
        print(f"  文件大小: {csv_path.stat().st_size:,} 字节")
        return csv_path

    def display_data_summary(self, data_dict=None):
        """显示数据摘要"""
        if data_dict is None:
            data_dict = self.data

        if not data_dict:
            print("✗ 没有可显示的数据")
            return

        print(f"\n{'=' * 60}")
        print(f"数据摘要")
        print(f"{'=' * 60}")
        print(f"指数代码: {data_dict['index_code']}")
        print(f"数据文件: {data_dict['filename']}")
        print(f"总行数: {data_dict['row_count']:,}")
        print(f"列数: {len(data_dict['columns'])}")
        print(f"\n列名:")
        for i, col in enumerate(data_dict['columns'], 1):
            print(f"  {i}. {col}")

        print(f"\n数据样本（前3行）:")
        for i, row in enumerate(data_dict['data'][:3], 1):
            print(f"  行 {i}:")
            for col, val in list(row.items())[:5]:  # 只显示前5列
                print(f"    {col}: {val}")
            print()

    def run(self, save_csv=True):
        """执行完整的下载和解析流程"""
        print(f"{'=' * 60}")
        print(f"中证指数数据下载和解析")
        print(f"{'=' * 60}")
        print(f"指数代码: {self.index_code}")
        print(f"下载目录: {self.download_dir}")
        print(f"{'=' * 60}\n")

        # 1. 下载Excel
        if not self.download_excel():
            return None

        # 2. 解析Excel
        data_dict = self.parse_excel_data()
        if not data_dict:
            return None

        # 3. 保存CSV
        if save_csv:
            self.save_to_csv(data_dict)

        # 4. 显示摘要
        self.display_data_summary(data_dict)

        print(f"\n{'=' * 60}")
        print(f"✓ 处理完成!")
        print(f"{'=' * 60}")

        return data_dict


def main():
    """主函数"""
    # 可通过命令行参数指定指数代码
    import sys
    index_code = sys.argv[1] if len(sys.argv) > 1 else "H30269"

    # 可选：指定自定义URL
    custom_url = sys.argv[2] if len(sys.argv) > 2 else None

    fetcher = IndexValuationFetcher(index_code=index_code, base_url=custom_url)
    result = fetcher.run()

    if result:
        # 返回成功状态码
        return 0
    else:
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
