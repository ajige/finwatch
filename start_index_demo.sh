#!/bin/bash

# H30269 指数数据演示启动脚本

echo "=========================================="
echo "FinWatch - H30269指数数据演示"
echo "=========================================="
echo ""

# 检查数据文件
if [ ! -f "data/index_H30269_full.csv" ]; then
    echo "✗ 数据文件不存在: data/index_H30269_full.csv"
    echo "  请先运行: cp /home/invest/finwatch/download_manager/downloads/index_H30269_full.csv data/"
    exit 1
fi

echo "✓ 数据文件已就绪"
echo ""

# 检查依赖
echo "检查依赖..."
python3 -c "import flask, pandas" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Python依赖已安装"
else
    echo "✗ 请先安装依赖: pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "=========================================="
echo "启动选项:"
echo "=========================================="
echo ""
echo "1. 启动Web服务器"
echo "   python3 app.py"
echo "   然后访问: http://localhost:5000"
echo ""
echo "2. 测试数据访问"
echo "   python3 test_index_data.py"
echo "   查看H30269指数数据详情"
echo ""
echo "3. 查看数据指南"
echo "   cat INDEX_DATA_GUIDE.md"
echo ""

read -p "请选择 (1-3): " choice

case $choice in
    1)
        echo ""
        echo "正在启动Web服务器..."
        echo "服务器将在 http://localhost:5000 运行"
        echo "按 Ctrl+C 停止服务器"
        echo ""
        python3 app.py
        ;;
    2)
        echo ""
        echo "运行数据访问测试..."
        python3 test_index_data.py
        ;;
    3)
        echo ""
        echo "显示数据指南:"
        echo ""
        cat INDEX_DATA_GUIDE.md
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac