# 中证指数数据下载和合并系统

## 脚本说明

本目录包含两个主要脚本：

1. **fetch_index_data.py**: 下载当天的指数估值数据
2. **merge_daily_data.py**: 每日数据合并脚本

## 数据内容

指数估值数据包含以下信息：
- **日期Date**: 估值数据日期
- **指数代码Index Code**: 指数代码（如H30269）
- **指数中文名称**: 指数的中文名称和简称
- **指数英文名称**: 指数的英文名称和简称
- **市盈率1和市盈率2**: 基于不同股本计算的市盈率
- **股息率1和股息率2**: 基于不同股本计算的股息率

## 脚本功能

### fetch_index_data.py

下载当天的Excel数据并转换为CSV格式：

```bash
# 使用默认指数代码（H30269）
python fetch_index_data.py

# 指定指数代码
python fetch_index_data.py H30269

# 使用自定义URL
python fetch_index_data.py H30269 "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/H30269indicator.xls"
```

**输出文件**:
- `index_{指数代码}_{日期}.xls` - Excel原始文件
- `index_{指数代码}_{日期}.csv` - CSV转换文件

### merge_daily_data.py

每日数据合并脚本，用于维护全量历史数据：

```bash
# 使用默认指数代码（H30269）
python merge_daily_data.py

# 指定指数代码
python merge_daily_data.py H30269
```

**处理流程**:
1. 调用 `fetch_index_data.py` 下载当天数据
2. 加载现有的全量数据文件 `index_{指数代码}_full.csv`
3. 将当天数据与全量数据合并
4. 按日期去重（一个日期一行）
5. 保存更新后的全量数据文件

**输出文件**:
- `index_{指数代码}_full.csv` - 全量历史数据

## 使用场景

### 单次下载数据

只需下载当天的数据，不需要历史数据：

```bash
python fetch_index_data.py H30269
```

### 每日自动更新

设置每日定时任务，自动下载并合并数据：

**Linux/Mac (crontab)**:

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天下午3点运行）
0 15 * * 1-5 cd /home/invest/finwatch/download_manager && /usr/bin/python3 merge_daily_data.py >> /var/log/index_data_merge.log 2>&1
```

**Windows (任务计划程序)**:
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器：每天下午3点
4. 设置操作：启动程序 `python.exe`
5. 参数：`merge_daily_data.py`
6. 起始于：`/home/invest/finwatch/download_manager`

## 文件命名规范

- **当日数据**: `index_H30269_20260307.xls/csv` (包含日期后缀)
- **全量数据**: `index_H30269_full.csv` (所有历史数据)

## 数据样例

```csv
日期Date,指数代码Index Code,指数中文全称Chinese Name(Full),指数中文简称Index Chinese Name,指数英文全称English Name(Full),指数英文简称Index English Name,市盈率1（总股本）P/E1,市盈率2（计算用股本）P/E2,股息率1（总股本）D/P1,股息率2（计算用股本）D/P2
20260306,H30269,中证红利低波动指数,红利低波,CSI Dividend Low Volatility Index,CSI Dividend Low Volatility,8.03,8.18,4.54,4.94
20260305,H30269,中证红利低波动指数,红利低波,CSI Dividend Low Volatility Index,CSI Dividend Low Volatility,8.06,8.14,4.52,4.96
20260304,H30269,中证红利低波动指数,红利低波,CSI Dividend Low Volatility Index,CSI Dividend Low Volatility,8.07,8.12,4.51,4.98
```

## 技术实现

- 使用 `requests` 库下载Excel文件
- 使用 `pandas` 和 `xlrd` 库解析Excel数据
- 使用 `subprocess` 调用其他脚本
- 使用 `pandas.concat` 合并数据
- 使用 `drop_duplicates` 按日期去重
- 支持中文编码（UTF-8-BOM）

## 依赖安装

```bash
pip install -r ../requirements.txt
```

或单独安装所需依赖：

```bash
pip install pandas requests xlrd
```

## 目录结构

```
download_manager/
├── fetch_index_data.py      # 下载当天数据
├── merge_daily_data.py      # 每日数据合并
├── downloads/               # 数据文件目录
│   ├── index_H30269_20260307.xls    # 当天Excel
│   ├── index_H30269_20260307.csv    # 当天CSV
│   └── index_H30269_full.csv          # 全量数据
└── README.md               # 本文件
```

## 常见问题

1. **xlrd导入错误**: 确保安装了xlrd 2.0.1或更高版本
2. **文件格式错误**: 确保URL指向的是有效的Excel文件（.xls或.xlsx）
3. **编码问题**: CSV文件使用UTF-8-BOM编码，支持Excel正确显示中文
4. **数据重复**: 合并脚本会自动按日期去重，确保一个日期只有一行数据

## 数据更新频率

数据通常每个交易日更新一次。建议设置定时任务在每个交易日下午3点运行合并脚本。

## 日志记录

定时任务建议将输出重定向到日志文件：

```bash
python merge_daily_data.py >> /var/log/index_data_merge.log 2>&1
```

这样可以追踪每次运行的执行情况和可能的错误。
