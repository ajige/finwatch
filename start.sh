#!/bin/bash

# FinWatch 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_color() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo
    print_color "========================================" "$BLUE"
    print_color "FinWatch - 金融数据监控系统" "$BLUE"
    print_color "========================================" "$BLUE"
    echo
}

print_step() {
    print_color "▶ $1" "$GREEN"
}

print_warning() {
    print_color "⚠ $1" "$YELLOW"
}

print_error() {
    print_color "✗ $1" "$RED"
}

print_success() {
    print_color "✓ $1" "$GREEN"
}

check_dependencies() {
    print_step "检查系统依赖..."

    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION 已安装"
    else
        print_error "Python3 未安装"
        exit 1
    fi

    # 检查pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 已安装"
    else
        print_warning "pip3 未安装，尝试安装..."
        apt-get update && apt-get install -y python3-pip || {
            print_error "无法安装 pip3"
            exit 1
        }
    fi
}

install_requirements() {
    print_step "安装Python依赖..."

    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        if [ $? -eq 0 ]; then
            print_success "依赖安装完成"
        else
            print_error "依赖安装失败"
            exit 1
        fi
    else
        print_error "requirements.txt 文件未找到"
        exit 1
    fi
}

check_data_files() {
    print_step "检查数据文件..."

    local required_files=(
        "data/market.csv"
        "data/economy.csv"
        "data/monetary.csv"
        "config/subjects.json"
    )

    local all_exist=true
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "$file"
        else
            print_warning "$file (未找到)"
            all_exist=false
        fi
    done

    if [ "$all_exist" = false ]; then
        print_warning "部分示例文件缺失，但不影响启动"
    fi
}

start_server() {
    print_step "启动服务器..."

    # 检查端口是否被占用
    if netstat -tuln | grep :5000 > /dev/null; then
        print_warning "端口 5000 已被占用"
        read -p "是否强制重启？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pkill -f "python.*app.py" || true
            sleep 2
        else
            print_error "启动中止"
            exit 1
        fi
    fi

    # 启动服务器
    python3 app.py &
    SERVER_PID=$!

    # 等待服务器启动
    print_step "等待服务器启动..."
    sleep 3

    # 检查服务器是否运行
    if ps -p $SERVER_PID > /dev/null; then
        if curl -s http://localhost:5000 > /dev/null; then
            print_success "服务器启动成功"
            echo
            print_color "访问地址: http://localhost:5000" "$BLUE"
            print_color "按 Ctrl+C 停止服务器" "$YELLOW"
            echo

            # 保存PID到文件
            echo $SERVER_PID > .server.pid

            # 等待用户中断
            wait $SERVER_PID
        else
            print_error "服务器启动但无法访问"
            kill $SERVER_PID 2>/dev/null || true
            exit 1
        fi
    else
        print_error "服务器启动失败"
        exit 1
    fi
}

stop_server() {
    print_step "停止服务器..."

    if [ -f ".server.pid" ]; then
        local pid=$(cat .server.pid)
        if ps -p $pid > /dev/null; then
            kill $pid
            print_success "服务器已停止"
        else
            print_warning "服务器进程不存在"
        fi
        rm -f .server.pid
    else
        print_warning "未找到服务器进程记录"
        # 尝试查找并终止相关进程
        pkill -f "python.*app.py" 2>/dev/null && print_success "已终止相关进程" || print_warning "未找到相关进程"
    fi
}

run_tests() {
    print_step "运行API测试..."

    if [ -f "test_api.py" ]; then
        python3 test_api.py
    else
        print_warning "测试脚本未找到"
    fi
}

show_status() {
    print_step "系统状态检查..."

    # 检查进程
    if [ -f ".server.pid" ]; then
        local pid=$(cat .server.pid)
        if ps -p $pid > /dev/null; then
            print_success "服务器正在运行 (PID: $pid)"
            print_color "访问地址: http://localhost:5000" "$BLUE"
        else
            print_warning "服务器记录存在但进程未运行"
            rm -f .server.pid
        fi
    else
        print_warning "服务器未运行"
    fi

    # 检查端口
    if netstat -tuln | grep :5000 > /dev/null; then
        print_warning "端口 5000 被占用（可能由其他进程使用）"
    fi
}

show_usage() {
    echo
    print_color "使用方法: $0 [命令]" "$BLUE"
    echo
    print_color "命令:" "$BLUE"
    print_color "  start     启动服务器（默认）" "$GREEN"
    print_color "  stop      停止服务器" "$GREEN"
    print_color "  restart   重启服务器" "$GREEN"
    print_color "  status    查看系统状态" "$GREEN"
    print_color "  test      运行API测试" "$GREEN"
    print_color "  install   安装依赖" "$GREEN"
    print_color "  help      显示帮助信息" "$GREEN"
    echo
}

main() {
    print_header

    local command=${1:-start}

    case $command in
        start)
            check_dependencies
            install_requirements
            check_data_files
            start_server
            ;;
        stop)
            stop_server
            ;;
        restart)
            stop_server
            sleep 2
            check_dependencies
            install_requirements
            check_data_files
            start_server
            ;;
        status)
            show_status
            ;;
        test)
            check_dependencies
            install_requirements
            run_tests
            ;;
        install)
            check_dependencies
            install_requirements
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "未知命令: $command"
            show_usage
            exit 1
            ;;
    esac
}

# 捕捉Ctrl+C
trap 'echo; print_color "正在停止服务器..." "$YELLOW"; stop_server; exit 0' INT

# 运行主函数
main "$@"