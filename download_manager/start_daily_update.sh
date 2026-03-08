#!/bin/bash
# 每日数据更新启动脚本
# 用于设置定时任务或手动执行每日数据更新

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 获取指数代码列表（默认包含 H30269, 930914, 931446）
if [ $# -gt 0 ]; then
    INDICES=("$@")
else
    INDICES=("H30269" "930914" "931446")
fi

echo "============================================================"
echo "每日数据更新"
echo "============================================================"
echo "指数代码列表：${INDICES[*]}"
echo "运行时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"
echo ""

# 跟踪是否有失败
ALL_SUCCESS=true

# 遍历每个指数代码
for INDEX_CODE in "${INDICES[@]}"; do
    echo ""
    echo "############################################################"
    echo "# 处理指数：$INDEX_CODE"
    echo "############################################################"
    echo ""

    # 步骤 1: 下载当天数据
    echo "步骤 1: 下载当天数据"
    echo "------------------------------------------------------------"
    python3 fetch_index_data.py "$INDEX_CODE"

    # 检查下载是否成功
    if [ $? -ne 0 ]; then
        echo ""
        echo "✗ 指数 $INDEX_CODE 下载当天数据失败，继续处理下一个..."
        ALL_SUCCESS=false
        continue
    fi

    echo ""
    echo "步骤 2: 合并数据"
    echo "------------------------------------------------------------"

    # 步骤 2: 合并数据
    python3 merge_daily_data.py "$INDEX_CODE"

    # 检查执行结果
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ 指数 $INDEX_CODE 数据更新成功完成"
        echo "  生成的文件:"
        echo "    - downloads/index_${INDEX_CODE}_$(date +%Y%m%d).csv (当天数据)"
        echo "    - downloads/index_${INDEX_CODE}_full.csv (全量数据)"
    else
        echo ""
        echo "✗ 指数 $INDEX_CODE 数据更新失败"
        ALL_SUCCESS=false
    fi

    echo ""
done

# 步骤 3: 合并多指数数据
echo ""
echo "############################################################"
echo "# 步骤 3: 合并多指数股息率数据"
echo "############################################################"
echo ""
python3 merge_multi_index.py

# 总结
echo ""
echo "============================================================"
echo "执行总结"
echo "============================================================"
if [ "$ALL_SUCCESS" = true ]; then
    echo "✓ 所有指数数据更新成功完成"
    echo ""
    echo "生成的文件:"
    echo "  各指数全量数据:"
    for idx in "${INDICES[@]}"; do
        echo "    - downloads/index_${idx}_full.csv"
    done
    echo "  多指数合并文件:"
    echo "    - downloads/multi_index_dividend.csv"
else
    echo "✗ 部分指数数据更新失败，请检查日志"
fi
echo "============================================================"
