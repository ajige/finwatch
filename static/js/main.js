/**
 * FinWatch - 主 JavaScript 文件
 * 支持按文件分组显示，多选列显示图表
 */

// 全局变量
let allSubjects = [];
let filesData = {};  // 按文件分组的数据
let currentChart = null;
let currentTimeInterval = null;
let selectedColumns = {};  // 每个文件选中的列

// API 基础 URL
const API_BASE = window.location.origin;

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    initPage();
    updateTimeDisplay();
    currentTimeInterval = setInterval(updateTimeDisplay, 1000);
    checkApiStatus();
});

// 页面初始化函数
async function initPage() {
    try {
        await loadFilesData();
        await loadSubjects();
        updateStats();
    } catch (error) {
        console.error('初始化页面时出错:', error);
        showError('初始化失败：' + error.message);
    }
}

// 加载文件数据
async function loadFilesData() {
    try {
        const response = await fetch('/api/files');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        filesData = {};

        data.files.forEach(file => {
            filesData[file.file_name] = {
                ...file,
                selectedColumns: file.subjects.map(s => s.column)  // 默认选中所有科目列
            };
        });

        renderFileTabs();
        return filesData;
    } catch (error) {
        console.error('加载文件数据时出错:', error);
        return {};
    }
}

// 加载科目数据
async function loadSubjects() {
    try {
        const response = await fetch('/api/subjects');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        allSubjects = data.subjects || [];

        updateSubjectList();
        updateFileSelectors();
        return allSubjects;
    } catch (error) {
        console.error('加载科目时出错:', error);
        showError('无法加载科目数据');
        return [];
    }
}

// 渲染文件标签页
function renderFileTabs() {
    const tabsContainer = document.getElementById('fileTabs');
    const contentContainer = document.getElementById('fileTabsContent');

    const fileNames = Object.keys(filesData);

    if (fileNames.length === 0) {
        tabsContainer.innerHTML = '';
        contentContainer.innerHTML = `
            <div class="file-tab-content">
                <div class="empty-state">
                    <i class="bi bi-folder-x" style="font-size: 3rem;"></i>
                    <h5 class="mt-3">暂无数据文件</h5>
                    <p class="text-muted">请将 CSV 文件放入 data/ 目录，然后刷新页面</p>
                </div>
            </div>
        `;
        return;
    }

    // 生成标签页导航
    let tabsHtml = '';
    let contentHtml = '';

    fileNames.forEach((fileName, index) => {
        const file = filesData[fileName];
        const isActive = index === 0 ? 'active' : '';
        const showName = getFileNameDisplay(fileName);

        tabsHtml += `
            <li class="nav-item" role="presentation">
                <button class="nav-link ${isActive}" id="${fileName}-tab"
                        data-bs-toggle="tab" data-bs-target="#${fileName}"
                        type="button" role="tab" aria-controls="${fileName}"
                        aria-selected="${index === 0}">
                    <i class="bi bi-file-earmark-spreadsheet me-1"></i>
                    ${showName}
                </button>
            </li>
        `;

        // 生成列选择复选框
        let checkboxesHtml = '';
        file.subjects.forEach(subject => {
            const isChecked = file.selectedColumns.includes(subject.column) ? 'checked' : '';
            checkboxesHtml += `
                <div class="form-check me-3 mb-2">
                    <input class="form-check-input column-checkbox"
                           type="checkbox"
                           value="${subject.column}"
                           data-file="${fileName}"
                           id="chk_${fileName}_${subject.id}"
                           ${isChecked}
                           onchange="toggleColumn('${fileName}', '${subject.column}')">
                    <label class="form-check-label" for="chk_${fileName}_${subject.id}">
                        ${subject.name}
                    </label>
                </div>
            `;
        });

        // 生成图表容器
        contentHtml += `
            <div class="tab-pane fade ${index === 0 ? 'show active' : ''}"
                 id="${fileName}" role="tabpanel" aria-labelledby="${fileName}-tab">
                <div class="file-tab-content">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0">
                            <i class="bi bi-graph-up me-2 text-primary"></i>
                            ${showName} - 数据图表
                        </h5>
                        <div>
                            <button class="btn btn-outline-primary btn-sm" onclick="updateFileChart('${fileName}')">
                                <i class="bi bi-play-fill"></i> 更新图表
                            </button>
                            <button class="btn btn-outline-secondary btn-sm ms-2" onclick="exportChart('${fileName}')">
                                <i class="bi bi-download"></i> 导出
                            </button>
                        </div>
                    </div>

                    <div class="mb-3 p-3 bg-light rounded">
                        <label class="form-label fw-bold">
                            <i class="bi bi-check-square me-1"></i>选择显示的指标
                        </label>
                        <div class="d-flex flex-wrap">
                            ${checkboxesHtml}
                        </div>
                    </div>

                    <div class="chart-wrapper" style="height: 450px;">
                        <canvas id="chart_${fileName}"></canvas>
                    </div>

                    <div class="mt-3">
                        <h6><i class="bi bi-table me-1"></i>数据表格</h6>
                        <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                            <table class="table table-sm table-bordered" id="table_${fileName}">
                                <thead class="table-light"></thead>
                                <tbody></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    tabsContainer.innerHTML = tabsHtml;
    contentContainer.innerHTML = contentHtml;

    // 加载第一个文件的图表
    if (fileNames.length > 0) {
        setTimeout(() => updateFileChart(fileNames[0]), 500);
    }
}

// 获取文件显示名称
function getFileNameDisplay(fileName) {
    const nameMap = {
        'market': '市场数据 (Market)',
        'monetary': '货币政策 (Monetary)',
        'multi_index_dividend': '指数股息率 (Multi Index Dividend)'
    };
    return nameMap[fileName] || fileName;
}

// 切换列选择
function toggleColumn(fileName, column) {
    const file = filesData[fileName];
    if (!file) return;

    const index = file.selectedColumns.indexOf(column);
    if (index > -1) {
        file.selectedColumns.splice(index, 1);
    } else {
        file.selectedColumns.push(column);
    }
}

// 更新文件图表
async function updateFileChart(fileName) {
    const file = filesData[fileName];
    if (!file) return;

    const selectedCols = file.selectedColumns;
    if (selectedCols.length === 0) {
        showInfo('请至少选择一个指标');
        return;
    }

    try {
        const response = await fetch(`/api/file-data/${fileName}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();

        // 准备图表数据
        const labels = data.data.map(row => row.date);
        const datasets = [];

        const colors = [
            '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
            '#1abc9c', '#34495e', '#e67e22', '#1f618d', '#922b21'
        ];

        selectedCols.forEach((col, index) => {
            const subject = file.subjects.find(s => s.column === col);
            const color = colors[index % colors.length];

            datasets.push({
                label: subject ? subject.name : col,
                data: data.data.map(row => row[col]),
                borderColor: color,
                backgroundColor: color + '20',
                borderWidth: 2,
                tension: 0.3,
                fill: false
            });
        });

        // 销毁旧图表
        const chartCanvas = document.getElementById(`chart_${fileName}`);
        if (currentChart && currentChart.canvas === chartCanvas) {
            currentChart.destroy();
        }

        // 创建新图表
        const ctx = chartCanvas.getContext('2d');
        currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' +
                                    (typeof context.parsed.y === 'number' ? context.parsed.y.toFixed(2) : context.parsed.y);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: '日期'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: '数值'
                        }
                    }
                }
            }
        });

        // 更新表格
        updateFileTable(fileName, data);

    } catch (error) {
        console.error('更新图表时出错:', error);
        showError('无法加载图表数据');
    }
}

// 更新文件表格
function updateFileTable(fileName, data) {
    const table = document.getElementById(`table_${fileName}`);
    if (!table) return;

    const file = filesData[fileName];
    const selectedCols = file.selectedColumns;

    // 生成表头
    let theadHtml = '<tr><th>日期</th>';
    selectedCols.forEach(col => {
        const subject = file.subjects.find(s => s.column === col);
        const unit = subject && subject.unit ? ` (${subject.unit})` : '';
        theadHtml += `<th>${subject ? subject.name : col}${unit}</th>`;
    });
    theadHtml += '</tr>';

    // 生成表格内容
    let tbodyHtml = '';
    data.data.slice(0, 100).forEach(row => {  // 最多显示 100 行
        tbodyHtml += '<tr><td>' + row.date + '</td>';
        selectedCols.forEach(col => {
            const value = row[col];
            tbodyHtml += '<td>' + (value !== null && value !== undefined ?
                (typeof value === 'number' ? value.toFixed(2) : value) : '-') + '</td>';
        });
        tbodyHtml += '</tr>';
    });

    table.querySelector('thead').innerHTML = theadHtml;
    table.querySelector('tbody').innerHTML = tbodyHtml;
}

// 导出图表
function exportChart(fileName) {
    const chartCanvas = document.getElementById(`chart_${fileName}`);
    if (!chartCanvas || !currentChart) {
        showError('请先生成图表');
        return;
    }

    const link = document.createElement('a');
    link.download = `${fileName}_chart_${new Date().toISOString().slice(0, 10)}.png`;
    link.href = currentChart.toBase64Image();
    link.click();

    showSuccess('图表已导出');
}

// 更新统计数据
function updateStats() {
    document.getElementById('totalSubjects').textContent = allSubjects.length;
    document.getElementById('dataFiles').textContent = Object.keys(filesData).length;
    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
}

// 更新科目列表（管理页面）
function updateSubjectList() {
    const container = document.getElementById('subjectList');

    if (!allSubjects || allSubjects.length === 0) {
        container.innerHTML = `
            <div class="empty-state p-4">
                <i class="bi bi-list-ul" style="font-size: 2rem;"></i>
                <h6 class="mt-2">暂无科目</h6>
            </div>
        `;
        return;
    }

    let html = '';
    allSubjects.forEach(subject => {
        html += `
            <div class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${subject.name}</h6>
                        <small class="text-muted">ID: ${subject.id} | 文件：${subject.file}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteSubject('${subject.id}')">
                        删除
                    </button>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// 更新文件选择器（添加科目表单）
function updateFileSelectors() {
    const fileSelect = document.getElementById('subjectFile');
    const columnSelect = document.getElementById('subjectColumn');

    if (!fileSelect) return;

    // 清空现有选项
    fileSelect.innerHTML = '<option value="">选择数据文件...</option>';
    columnSelect.innerHTML = '<option value="">选择数据列...</option>';

    // 添加文件选项
    Object.keys(filesData).forEach(fileName => {
        const file = filesData[fileName];
        const option = document.createElement('option');
        option.value = `data/${fileName}.csv`;
        option.textContent = getFileNameDisplay(fileName);
        fileSelect.appendChild(option);
    });

    // 监听文件选择变化
    fileSelect.addEventListener('change', function() {
        const filePath = this.value;
        const fileName = filePath.replace('data/', '').replace('.csv', '');
        loadFileColumns(fileName);
    });
}

// 加载文件列名
function loadFileColumns(fileName) {
    const file = filesData[fileName];
    const columnSelect = document.getElementById('subjectColumn');

    if (!file || !columnSelect) return;

    columnSelect.innerHTML = '<option value="">选择数据列...</option>';

    file.subjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject.column;
        option.textContent = subject.name;
        columnSelect.appendChild(option);
    });
}

// 添加新科目
async function addNewSubject() {
    const form = document.getElementById('addSubjectForm');
    const formData = {
        id: document.getElementById('subjectId').value,
        name: document.getElementById('subjectName').value,
        category: document.getElementById('subjectCategory').value,
        unit: document.getElementById('subjectUnit').value,
        description: document.getElementById('subjectDescription').value,
        file: document.getElementById('subjectFile').value,
        column: document.getElementById('subjectColumn').value
    };

    if (!formData.id || !formData.name || !formData.file || !formData.column) {
        showError('请填写所有必填字段');
        return;
    }

    try {
        const response = await fetch('/api/subjects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess('科目添加成功');
            form.reset();
            await loadSubjects();
            await loadFilesData();
            updateStats();
        } else {
            showError(data.error || '添加科目失败');
        }
    } catch (error) {
        console.error('添加科目时出错:', error);
        showError('添加科目失败');
    }
}

// 删除科目
async function deleteSubject(subjectId) {
    if (!confirm('确定要删除这个科目吗？')) return;

    // 目前后端没有 DELETE 接口，显示提示
    showInfo('删除功能开发中...');
}

// 扫描数据文件
async function scanDataFiles() {
    try {
        showLoading('正在扫描数据文件...');

        const response = await fetch('/api/scan', { method: 'POST' });
        const data = await response.json();

        if (response.ok) {
            showSuccess(`扫描完成，发现 ${data.count} 个新科目`);
            await loadSubjects();
            await loadFilesData();
            updateStats();
        } else {
            showError(data.error || '扫描失败');
        }
    } catch (error) {
        console.error('扫描文件时出错:', error);
        showError('扫描失败');
    }
}

// 刷新数据
async function refreshData() {
    showLoading('正在刷新数据...');
    try {
        await loadFilesData();
        await loadSubjects();
        updateStats();
        showSuccess('数据刷新完成');
    } catch (error) {
        showError('刷新失败');
    }
}

// 页面导航
function showDashboard() {
    document.getElementById('dashboardPage').style.display = 'block';
    document.getElementById('subjectsPage').style.display = 'none';
    updateNavActive(0);
}

function showSubjects() {
    document.getElementById('dashboardPage').style.display = 'none';
    document.getElementById('subjectsPage').style.display = 'block';
    updateNavActive(1);
}

function updateNavActive(index) {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach((link, i) => {
        link.classList.toggle('active', i === index);
    });
}

// 表单提交
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('addSubjectForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            addNewSubject();
        });
    }
});

// 工具函数
function updateTimeDisplay() {
    const now = new Date();
    document.getElementById('timeDisplay').textContent = now.toLocaleTimeString('zh-CN');
}

async function checkApiStatus() {
    try {
        const response = await fetch('/api/subjects');
        const statusElement = document.getElementById('apiStatus');
        if (response.ok) {
            statusElement.textContent = '在线';
            statusElement.className = 'badge bg-success';
        } else {
            statusElement.textContent = '异常';
            statusElement.className = 'badge bg-warning';
        }
    } catch (error) {
        document.getElementById('apiStatus').textContent = '离线';
        document.getElementById('apiStatus').className = 'badge bg-danger';
    }
}

function formatNumber(num) {
    if (num === null || num === undefined) return '--';
    if (Math.abs(num) >= 1000000) return (num / 1000000).toFixed(2) + 'M';
    if (Math.abs(num) >= 1000) return (num / 1000).toFixed(2) + 'K';
    return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 4 });
}

function getCategoryClass(category) {
    const classMap = {
        '市场数据': 'bg-primary',
        '宏观经济': 'bg-success',
        '货币政策': 'bg-info',
        '指数股息率': 'bg-warning',
        '其他': 'bg-dark'
    };
    return classMap[category] || 'bg-dark';
}

// 消息提示
function showSuccess(message) { showToast('success', '成功', message); }
function showError(message) { showToast('danger', '错误', message); }
function showInfo(message) { showToast('info', '信息', message); }
function showLoading(message) { showToast('info', '加载中', message, 0); }

function showToast(type, title, message, duration = 3000) {
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1050';
        document.body.appendChild(toastContainer);
    }

    const toastId = 'toast_' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}:</strong> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('afterbegin', toastHtml);

    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}
