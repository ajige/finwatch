#!/bin/bash
# 每日数据更新启动脚本
# 用于设置定时任务或手动执行每日数据更新

set -o pipefail

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 日志文件
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_DIR}/daily_update_$(date +%Y%m%d_%H%M%S).log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 获取指数代码列表（默认包含 H30269, 930914, 931446）
if [ $# -gt 0 ]; then
    INDICES=("$@")
else
    INDICES=("H30269" "930914" "931446")
fi

log "============================================================"
log "每日数据更新"
log "============================================================"
log "指数代码列表：${INDICES[*]}"
log "运行时间：$(date '+%Y-%m-%d %H:%M:%S')"
log "日志文件：$LOG_FILE"
log "============================================================"

# 跟踪是否有失败
ALL_SUCCESS=true
FAILED_INDICES=()

# 遍历每个指数代码
for INDEX_CODE in "${INDICES[@]}"; do
    log ""
    log "############################################################"
    log "# 处理指数：$INDEX_CODE"
    log "############################################################"

    # 步骤 1: 下载当天数据
    log "步骤 1: 下载当天数据"
    log "------------------------------------------------------------"
    if ! python3 fetch_index_data.py "$INDEX_CODE" 2>&1 | tee -a "$LOG_FILE"; then
        log ""
        log "✗ 指数 $INDEX_CODE 下载当天数据失败，继续处理下一个..."
        ALL_SUCCESS=false
        FAILED_INDICES+=("$INDEX_CODE")
        continue
    fi

    log ""
    log "步骤 2: 合并数据"
    log "------------------------------------------------------------"

    # 步骤 2: 合并数据
    if ! python3 merge_daily_data.py "$INDEX_CODE" 2>&1 | tee -a "$LOG_FILE"; then
        log ""
        log "✗ 指数 $INDEX_CODE 数据更新失败"
        ALL_SUCCESS=false
        FAILED_INDICES+=("$INDEX_CODE")
    else
        log ""
        log "✓ 指数 $INDEX_CODE 数据更新成功完成"
        log "  生成的文件:"
        log "    - downloads/index_${INDEX_CODE}_$(date +%Y%m%d).csv (当天数据)"
        log "    - downloads/index_${INDEX_CODE}_full.csv (全量数据)"
    fi
done

# 步骤 3: 合并多指数数据
log ""
log "############################################################"
log "# 步骤 3: 合并多指数股息率数据"
log "############################################################"

if ! python3 merge_multi_index.py 2>&1 | tee -a "$LOG_FILE"; then
    log "✗ 多指数数据合并失败"
    ALL_SUCCESS=false
else
    # 步骤 4: 复制 multi_index_dividend.csv 到 data 目录
    log ""
    log "############################################################"
    log "# 步骤 4: 复制多指数数据到 data 目录"
    log "############################################################"

    DATA_DIR="${SCRIPT_DIR}/../data"
    mkdir -p "$DATA_DIR"

    if cp "${SCRIPT_DIR}/downloads/multi_index_dividend.csv" "$DATA_DIR/"; then
        log "✓ 已复制 multi_index_dividend.csv 到 data 目录"
    else
        log "✗ 复制文件失败"
        ALL_SUCCESS=false
    fi
fi

# 总结
log ""
log "============================================================"
log "执行总结"
log "============================================================"
if [ "$ALL_SUCCESS" = true ]; then
    log "✓ 所有指数数据更新成功完成"
    log ""
    log "生成的文件:"
    log "  各指数全量数据:"
    for idx in "${INDICES[@]}"; do
        log "    - downloads/index_${idx}_full.csv"
    done
    log "  多指数合并文件:"
    log "    - downloads/multi_index_dividend.csv"
    log "  已复制到 data 目录:"
    log "    - data/multi_index_dividend.csv"
else
    log "✗ 部分指数数据更新失败，请检查日志"
    if [ ${#FAILED_INDICES[@]} -gt 0 ]; then
        log "失败的指数：${FAILED_INDICES[*]}"
    fi
fi
log "日志文件：$LOG_FILE"
log "============================================================"
