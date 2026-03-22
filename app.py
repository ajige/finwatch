#!/usr/bin/env python3
"""
FinWatch - 金融数据监控网站
支持动态新增数据科目，数据源为CSV/JSON文件
"""

import os
import json
import csv
import glob
import hashlib
import re
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd

# 初始化应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
SUBJECTS_FILE = CONFIG_DIR / "subjects.json"
ANALYST_MACRO_DIR = Path("/home/invest/data/analystmacro")

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# 科目管理类
class SubjectManager:
    """管理数据科目"""

    def __init__(self, config_file):
        self.config_file = config_file
        self.subjects = self._load_subjects()

    def _load_subjects(self):
        """加载科目配置"""
        if not self.config_file.exists():
            # 创建默认配置
            default_config = {"subjects": []}
            self._save_subjects(default_config)
            return default_config["subjects"]

        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get("subjects", [])

    def _save_subjects(self, config):
        """保存科目配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _generate_subject_id(self, file_stem, column_name):
        """生成科目ID，处理中文字符"""
        import re
        import unicodedata

        # 移除特殊字符和中文字符，保留字母、数字、下划线
        clean_name = re.sub(r'[^\w\s-]', '', column_name, flags=re.UNICODE)
        clean_name = re.sub(r'\s+', '_', clean_name.strip())

        # 如果清理后为空，使用列名的前几个字符
        if not clean_name:
            # 使用英文映射
            column_mapping = {
                '市盈率1（总股本）': 'pe_ratio1',
                '市盈率2（计算用股本）': 'pe_ratio2',
                '股息率1（总股本）': 'dividend_yield1',
                '股息率2（计算用股本）': 'dividend_yield2',
                '指数代码': 'index_code',
                '指数中文全称': 'index_cn_full',
                '指数中文简称': 'index_cn_short',
                '指数英文全称': 'index_en_full',
                '指数英文简称': 'index_en_short'
            }
            clean_name = column_mapping.get(column_name, column_name[:20])

        # 创建唯一的ID
        base_id = f"{file_stem}_{clean_name}"
        # 确保ID是有效的URL字符串
        valid_id = re.sub(r'[^a-zA-Z0-9_-]', '', base_id)

        # 如果仍然为空或太短，使用简单命名
        if len(valid_id) < 3:
            import hashlib
            hash_obj = hashlib.md5(column_name.encode('utf-8'))
            valid_id = f"{file_stem}_{hash_obj.hexdigest()[:8]}"

        return valid_id

    def _generate_subject_name(self, column_name, file_stem):
        """生成科目名称，保持中文字符显示"""
        # 如果列名包含中文字符，直接使用
        if any('\u4e00' <= char <= '\u9fff' for char in column_name):
            # 检查是否在常用中文指标映射中
            indicator_mapping = {
                '市盈率1（总股本）': '市盈率1 (总股本)',
                '市盈率2（计算用股本）': '市盈率2 (计算用股本)',
                '股息率1（总股本）': '股息率1 (总股本)',
                '股息率2（计算用股本）': '股息率2 (计算用股本)',
                '指数代码': '指数代码',
                '指数中文全称': '指数全称',
                '指数中文简称': '指数简称',
                '指数英文全称': '指数英文名',
                '指数英文简称': '指数英文名'
            }
            return indicator_mapping.get(column_name, f"{column_name} ({file_stem})")
        else:
            # 英文列名，保持原样
            return f"{column_name} ({file_stem})"

    def get_all_subjects(self):
        """获取所有科目"""
        return self.subjects

    def get_subject(self, subject_id):
        """获取特定科目"""
        for subject in self.subjects:
            if subject.get("id") == subject_id:
                return subject
        return None

    def add_subject(self, subject_data):
        """添加新科目"""
        # 检查ID是否已存在
        existing_ids = [s.get("id") for s in self.subjects]
        if subject_data.get("id") in existing_ids:
            return False, "科目ID已存在"

        self.subjects.append(subject_data)
        self._save_subjects({"subjects": self.subjects})
        return True, "科目添加成功"

    def update_subject(self, subject_id, subject_data):
        """更新科目信息"""
        for i, subject in enumerate(self.subjects):
            if subject.get("id") == subject_id:
                self.subjects[i] = subject_data
                self._save_subjects({"subjects": self.subjects})
                return True, "科目更新成功"
        return False, "科目不存在"

    def delete_subject(self, subject_id):
        """删除科目"""
        for i, subject in enumerate(self.subjects):
            if subject.get("id") == subject_id:
                del self.subjects[i]
                self._save_subjects({"subjects": self.subjects})
                return True, "科目删除成功"
        return False, "科目不存在"

    def scan_data_files(self):
        """扫描数据文件，自动发现新科目"""
        new_subjects = []
        csv_files = list(DATA_DIR.glob("*.csv"))

        for csv_file in csv_files:
            try:
                # 读取CSV文件首行获取列名
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader, [])

                # 排除date列（日期列）
                data_columns = [col for col in headers if col.lower() != 'date' and 'date' not in col.lower()]

                # 检查每个数据列是否已注册
                for column in data_columns:
                    # 生成科目ID - 处理中文字符
                    subject_id = self._generate_subject_id(csv_file.stem, column)

                    # 检查是否已存在
                    exists = any(s.get("id") == subject_id for s in self.subjects)

                    if not exists:
                        # 创建新科目
                        new_subject = {
                            "id": subject_id,
                            "name": self._generate_subject_name(column, csv_file.stem),
                            "unit": "",
                            "category": "未分类",
                            "description": f"自动发现: {column} 来自 {csv_file.name}",
                            "file": str(csv_file.relative_to(BASE_DIR)),
                            "column": column
                        }
                        new_subjects.append(new_subject)
                        self.subjects.append(new_subject)

            except Exception as e:
                print(f"扫描文件 {csv_file} 时出错: {e}")
                continue

        if new_subjects:
            self._save_subjects({"subjects": self.subjects})

        return new_subjects

# 初始化科目管理器
subject_manager = SubjectManager(SUBJECTS_FILE)

# 数据查询函数
def get_subject_data(subject_id):
    """获取科目数据"""
    subject = subject_manager.get_subject(subject_id)
    if not subject:
        return None

    file_path = BASE_DIR / subject["file"]
    column = subject["column"]

    try:
        # 使用pandas读取CSV
        df = pd.read_csv(file_path)

        # 确保有date列
        if 'date' not in df.columns:
            # 尝试查找日期列
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols:
                df = df.rename(columns={date_cols[0]: 'date'})
            else:
                # 如果没有日期列，使用索引
                df['date'] = df.index

        # 确保有目标列
        if column not in df.columns:
            return None

        # 转换为列表格式
        data = []
        for _, row in df.iterrows():
            data.append({
                "date": str(row['date']),
                "value": float(row[column]) if pd.notnull(row[column]) else None
            })

        return {
            "subject": subject,
            "data": data,
            "latest": data[-1] if data else None,
            "count": len(data)
        }

    except Exception as e:
        print(f"读取数据时出错: {e}")
        return None

def get_all_latest_data():
    """获取所有科目的最新数据"""
    latest_data = {}
    for subject in subject_manager.get_all_subjects():
        subject_data = get_subject_data(subject["id"])
        if subject_data and subject_data["latest"]:
            latest_data[subject["id"]] = {
                "name": subject["name"],
                "value": subject_data["latest"]["value"],
                "date": subject_data["latest"]["date"],
                "unit": subject.get("unit", "")
            }
    return latest_data


def get_latest_macro_summary():
    """获取最新的宏观策略摘要文件（macro 和 strategy）"""
    try:
        # 查找最新的 summary_macro 和 summary_strategy 文件
        macro_files = list(ANALYST_MACRO_DIR.glob("summary_macro_*.txt"))
        strategy_files = list(ANALYST_MACRO_DIR.glob("summary_strategy_*.txt"))

        result = {}

        # 处理宏观文件
        if macro_files:
            macro_files.sort(key=lambda x: x.name, reverse=True)
            latest_macro = macro_files[0]
            with open(latest_macro, 'r', encoding='utf-8') as f:
                content = f.read()
            result['macro'] = parse_macro_summary(content, latest_macro.name)

        # 处理策略文件
        if strategy_files:
            strategy_files.sort(key=lambda x: x.name, reverse=True)
            latest_strategy = strategy_files[0]
            with open(latest_strategy, 'r', encoding='utf-8') as f:
                content = f.read()
            result['strategy'] = parse_macro_summary(content, latest_strategy.name)

        return result if result else None
    except Exception as e:
        print(f"读取宏观策略文件时出错：{e}")
        return None


def parse_macro_summary(content, filename):
    """解析宏观策略摘要文件"""
    sections = {
        'hot_topics': [],
        'consensus': [],
        'strategies': []
    }

    current_section = None
    lines = content.split('\n')
    current_topic = None

    for line in lines:
        line = line.strip()
        if '=== 热门宏观话题 ===' in line:
            current_section = 'hot_topics'
        elif '=== 市场一致性预期 ===' in line:
            current_section = 'consensus'
        elif '=== 推荐投资策略 ===' in line:
            current_section = 'strategies'
        elif line and current_section and not line.startswith('==='):
            if current_section == 'hot_topics':
                # 热门话题格式：- 话题名称 (热度：X) 或 摘要：xxx
                if line.startswith('- '):
                    # 新话题
                    clean_line = line[2:].strip()
                    # 提取热度
                    heat_match = re.search(r'\(热度：(\d+)\)', clean_line)
                    heat = int(heat_match.group(1)) if heat_match else 0
                    topic_name = re.sub(r'\s*\(热度：\d+\)', '', clean_line).strip()
                    current_topic = {'name': topic_name, 'heat': heat, 'summary': ''}
                    sections[current_section].append(current_topic)
                elif line.startswith('摘要：') and current_topic:
                    # 话题摘要
                    current_topic['summary'] = line[3:].strip()
            else:
                # 其他部分
                clean_line = line.lstrip('- ').strip()
                if clean_line:
                    sections[current_section].append(clean_line)

    # 按热度倒序排序
    sections['hot_topics'].sort(key=lambda x: x['heat'], reverse=True)

    # 提取日期（支持 summary_macro_YYYYMMDD.txt 和 summary_strategy_YYYYMMDD.txt）
    date_match = re.search(r'summary_(?:macro|strategy)_(\d{8})\.txt', filename)
    date_str = date_match.group(1) if date_match else None
    if date_str:
        date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    else:
        date_formatted = None

    # 确定类型
    file_type = 'macro' if 'macro' in filename else 'strategy'

    return {
        'filename': filename,
        'date': date_formatted,
        'type': file_type,
        'hot_topics': sections['hot_topics'],
        'consensus': sections['consensus'],
        'strategies': sections['strategies']
    }

# API路由
@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/api/subjects', methods=['GET'])
def api_get_subjects():
    """获取所有科目"""
    subjects = subject_manager.get_all_subjects()
    return jsonify({"subjects": subjects})

@app.route('/api/subjects/<subject_id>', methods=['GET'])
def api_get_subject(subject_id):
    """获取特定科目"""
    subject = subject_manager.get_subject(subject_id)
    if not subject:
        return jsonify({"error": "科目不存在"}), 404
    return jsonify({"subject": subject})

@app.route('/api/subjects', methods=['POST'])
def api_add_subject():
    """添加新科目"""
    data = request.json
    if not data:
        return jsonify({"error": "请求数据为空"}), 400

    success, message = subject_manager.add_subject(data)
    if success:
        return jsonify({"success": True, "message": message}), 201
    else:
        return jsonify({"error": message}), 400

@app.route('/api/data/<subject_id>', methods=['GET'])
def api_get_data(subject_id):
    """获取科目数据"""
    data = get_subject_data(subject_id)
    if not data:
        return jsonify({"error": "数据不存在或读取失败"}), 404
    return jsonify(data)

@app.route('/api/data/latest', methods=['GET'])
def api_get_latest_data():
    """获取所有科目最新数据"""
    latest_data = get_all_latest_data()
    return jsonify({"latest": latest_data})

@app.route('/api/scan', methods=['POST'])
def api_scan_files():
    """扫描数据文件，发现新科目"""
    new_subjects = subject_manager.scan_data_files()
    return jsonify({
        "success": True,
        "new_subjects": new_subjects,
        "count": len(new_subjects)
    })

@app.route('/api/data-catalog', methods=['GET'])
def api_get_data_catalog():
    """获取数据目录列表"""
    catalog = []

    # 扫描 data 目录下的所有 CSV 文件
    csv_files = list(DATA_DIR.glob("*.csv"))

    for csv_file in sorted(csv_files, key=lambda x: x.name):
        try:
            # 读取 CSV 文件获取基本信息
            df = pd.read_csv(csv_file, nrows=5)  # 只读前 5 行获取元数据

            # 获取列名
            columns = list(df.columns)

            # 获取数据行数
            total_rows = len(pd.read_csv(csv_file))

            # 获取文件信息
            file_stat = csv_file.stat()

            catalog.append({
                "file_name": csv_file.name,
                "file_path": str(csv_file.relative_to(BASE_DIR)),
                "columns": columns,
                "row_count": total_rows,
                "file_size": file_stat.st_size,
                "last_modified": datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            print(f"读取文件 {csv_file} 时出错：{e}")
            continue

    return jsonify({"catalog": catalog})


@app.route('/api/files', methods=['GET'])
def api_get_files():
    """获取数据文件列表及其包含的科目"""
    files_data = []

    # 扫描 data 目录下的所有 CSV 文件
    csv_files = list(DATA_DIR.glob("*.csv"))

    for csv_file in sorted(csv_files, key=lambda x: x.name):
        try:
            # 读取 CSV 文件获取列名
            df = pd.read_csv(csv_file, nrows=1)
            columns = [col for col in df.columns if col.lower() != 'date' and 'date' not in col.lower()]

            # 获取该文件中各列对应的科目
            file_subjects = []
            for subject in subject_manager.get_all_subjects():
                if subject.get("file") == str(csv_file.relative_to(BASE_DIR)):
                    file_subjects.append({
                        "id": subject["id"],
                        "name": subject["name"],
                        "column": subject["column"],
                        "unit": subject.get("unit", "")
                    })

            files_data.append({
                "file_name": csv_file.stem,
                "file_display": csv_file.name,
                "file_path": str(csv_file.relative_to(BASE_DIR)),
                "columns": columns,
                "subjects": file_subjects
            })
        except Exception as e:
            print(f"读取文件 {csv_file} 时出错：{e}")
            continue

    return jsonify({"files": files_data})


@app.route('/api/file-data/<file_name>', methods=['GET'])
def api_get_file_data(file_name):
    """获取指定文件的完整数据（所有列）"""
    file_path = DATA_DIR / f"{file_name}.csv"

    if not file_path.exists():
        return jsonify({"error": "文件不存在"}), 404

    try:
        df = pd.read_csv(file_path)

        # 查找日期列
        date_col = 'date'
        if 'date' not in df.columns:
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols:
                date_col = date_cols[0]

        # 转换为列表格式
        data = []
        for _, row in df.iterrows():
            row_data = {"date": str(row[date_col])}
            for col in df.columns:
                if col.lower() != 'date' and 'date' not in col.lower():
                    try:
                        row_data[col] = float(row[col]) if pd.notnull(row[col]) else None
                    except (ValueError, TypeError):
                        row_data[col] = str(row[col])
            data.append(row_data)

        # 获取文件对应的科目信息
        file_subjects = []
        for subject in subject_manager.get_all_subjects():
            if subject.get("file") == f"data/{file_name}.csv":
                file_subjects.append({
                    "id": subject["id"],
                    "name": subject["name"],
                    "column": subject["column"],
                    "unit": subject.get("unit", "")
                })

        return jsonify({
            "file_name": file_name,
            "columns": [col for col in df.columns if col.lower() != 'date' and 'date' not in col.lower()],
            "subjects": file_subjects,
            "data": data,
            "count": len(data)
        })
    except Exception as e:
        print(f"读取文件 {file_path} 时出错：{e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/macro-summary', methods=['GET'])
def api_get_macro_summary():
    """获取最新的宏观策略摘要"""
    summary = get_latest_macro_summary()
    if summary:
        return jsonify({"success": True, "data": summary})
    else:
        return jsonify({"success": False, "message": "暂无宏观策略数据"}), 404

# 文件上传功能已移除
# 添加新数据文件请直接将CSV文件放入data/目录
# 然后使用/api/scan端点扫描新科目

# 静态文件服务
@app.route('/static/<path:filename>')
def serve_static(filename):
    """提供静态文件"""
    return send_from_directory('static', filename)

@app.route('/favicon.ico')
def favicon():
    """网站图标"""
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    # 初始扫描数据文件（已禁用）
    pass

    # 启动服务器
    print("启动FinWatch服务器...")
    app.run(host='0.0.0.0', port=5000, debug=True)