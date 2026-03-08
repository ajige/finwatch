# FinWatch - 金融数据监控系统

FinWatch 是一个基于文件数据源的金融数据监控网站，支持动态新增数据科目。系统使用Python Flask作为后端，原生JavaScript作为前端，支持CSV/JSON格式数据文件。

## 功能特性

- **动态科目管理**: 支持动态添加、删除和修改数据科目
- **文件数据源**: 支持CSV格式数据文件，无需数据库
- **自动发现**: 自动扫描数据文件，发现新数据列并注册为科目
- **数据可视化**: 使用Chart.js展示时间序列数据图表
- **响应式界面**: 适配桌面和移动设备
- **RESTful API**: 提供完整的API接口供其他系统集成

## 系统架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   前端      │←──→│   Flask API │←──→│  数据文件   │
│ HTML/JS/CSS │    │  (Python)   │    │ (CSV/JSON)  │
└─────────────┘    └─────────────┘    └─────────────┘
                         │
                    ┌─────────────┐
                    │ 科目注册表  │
                    │ (动态更新)  │
                    └─────────────┘
```

## 目录结构

```
finwatch/
├── app.py                    # Flask主应用
├── requirements.txt          # Python依赖
├── test_api.py              # API测试脚本
├── README.md                # 项目说明
├── config/
│   └── subjects.json        # 科目配置文件
├── data/                    # 数据文件目录
│   ├── market.csv          # 市场数据示例
│   ├── economy.csv         # 经济数据示例
│   └── monetary.csv        # 货币政策数据示例
├── static/                  # 静态资源
│   ├── css/
│   │   └── style.css       # 自定义样式
│   └── js/
│       └── main.js         # 前端主逻辑
└── templates/               # HTML模板
    └── index.html          # 主页面
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

所需依赖：
- Flask==3.0.0
- pandas==2.2.0
- watchdog==4.0.0

### 2. 启动服务器

```bash
python app.py
```

服务器将在 `http://localhost:5000` 启动。

### 3. 访问网站

打开浏览器访问：`http://localhost:5000`

## 数据文件格式

### CSV文件格式

数据文件应为CSV格式，包含`date`列和其他数据列：

```csv
date,stock_price,trading_volume
2024-01-01,150.5,1200.3
2024-01-02,152.3,1350.7
2024-01-03,151.8,1120.5
```

### 科目配置文件

科目信息存储在 `config/subjects.json`：

```json
{
  "subjects": [
    {
      "id": "stock_price",
      "name": "股票价格",
      "unit": "元",
      "category": "市场数据",
      "description": "某股票每日收盘价",
      "file": "data/market.csv",
      "column": "stock_price"
    }
  ]
}
```

## API接口

### 科目管理

| 端点 | 方法 | 描述 | 示例响应 |
|------|------|------|----------|
| `/api/subjects` | GET | 获取所有科目 | `{"subjects": [...]}` |
| `/api/subjects/{id}` | GET | 获取特定科目 | `{"subject": {...}}` |
| `/api/subjects` | POST | 添加新科目 | `{"success": true, "message": "..."}` |

### 数据查询

| 端点 | 方法 | 描述 | 示例响应 |
|------|------|------|----------|
| `/api/data/{subject_id}` | GET | 获取科目时间序列数据 | `{"data": [{date: "...", value: ...}]}` |
| `/api/data/latest` | GET | 获取所有科目最新值 | `{"latest": {...}}` |

### 文件扫描

| 端点 | 方法 | 描述 | 示例响应 |
|------|------|------|----------|
| `/api/scan` | POST | 扫描数据文件，发现新科目 | `{"new_subjects": [...]}` |

## 动态新增科目流程

### 方法一：自动扫描

1. 将新的CSV文件放入 `data/` 目录
2. 点击网站导航栏的"扫描新科目"按钮
3. 系统自动解析CSV文件，发现新数据列
4. 新科目自动注册并立即可用

### 方法二：手动添加

1. 访问"科目管理"页面
2. 填写科目信息：
   - 科目ID：唯一标识符
   - 科目名称：显示名称
   - 数据文件：选择CSV文件
   - 数据列：选择文件中的列
3. 点击"添加科目"

### 方法三：配置文件编辑

1. 直接编辑 `config/subjects.json`
2. 添加新的科目配置
3. 重启服务器或使用扫描功能

## 前端功能

### 仪表板
- **科目卡片网格**: 显示所有科目的最新值和基本信息
- **数据趋势图**: 交互式时间序列图表，支持多科目对比
- **数据表格**: 查看原始数据，支持排序和筛选
- **统计摘要**: 显示系统整体状态和数据量

### 科目管理
- **科目列表**: 查看和管理所有科目
- **添加新科目**: 手动注册新数据科目
- **科目详情**: 查看科目详细信息和统计数据

### 数据文件管理
- **文件扫描**: 扫描data/目录下的CSV文件，自动发现新科目
- **手动添加**: 通过科目管理页面手动注册新数据科目
- **配置文件**: 直接编辑config/subjects.json配置文件

## 部署指南

### 开发环境

```bash
# 直接运行Flask开发服务器
python app.py
```

### 生产环境

#### 1. 使用Gunicorn

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 2. 使用系统服务（systemd）

创建服务文件 `/etc/systemd/system/finwatch.service`：

```ini
[Unit]
Description=FinWatch Financial Data Monitor
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/finwatch
Environment="PATH=/path/to/finwatch/venv/bin"
ExecStart=/path/to/finwatch/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start finwatch
sudo systemctl enable finwatch
```

#### 3. 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态文件缓存
    location /static {
        alias /path/to/finwatch/static;
        expires 30d;
    }
}
```

## 扩展开发

### 添加新的数据源

1. 在 `app.py` 中添加新的数据解析器
2. 实现相应的数据读取函数
3. 更新科目管理器以支持新格式

### 添加新的可视化图表

1. 在 `static/js/main.js` 中添加新的图表类型
2. 创建对应的页面组件
3. 更新API以提供所需数据格式

### 添加用户认证

1. 集成Flask-Login或Flask-Security
2. 添加登录页面和用户管理
3. 实现基于角色的科目访问控制

## 测试

### 运行API测试

```bash
python test_api.py
```

测试内容包括：
- 基本连接测试
- 科目API测试
- 数据API测试
- 文件操作测试

### 手动测试

1. 启动服务器：`python app.py`
2. 访问 `http://localhost:5000`
3. 测试各项功能：
   - 查看科目卡片
   - 查看数据图表
   - 添加新数据科目
   - 扫描新科目

## 故障排除

### 常见问题

1. **服务器无法启动**
   - 检查Python和依赖是否安装
   - 检查端口5000是否被占用

2. **数据无法加载**
   - 检查CSV文件格式是否正确
   - 检查文件路径和权限
   - 查看服务器日志获取错误信息

3. **图表不显示**
   - 检查浏览器控制台是否有JavaScript错误
   - 检查网络请求是否成功
   - 确保Chart.js正确加载

### 日志查看

服务器日志将显示在控制台，包括：
- 启动信息
- API请求记录
- 数据文件扫描结果
- 错误和异常信息

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

MIT License

## 支持

如有问题或建议，请提交Issue或联系维护者。

---

*最后更新: 2024-01-30*