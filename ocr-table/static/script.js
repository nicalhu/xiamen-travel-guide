// 初始化变量
let tableData = [];

// DOM元素
const fileInput = document.getElementById('fileInput');
const imagePreview = document.getElementById('imagePreview');
const exportBtn = document.getElementById('exportBtn');
const recognizeBtn = document.getElementById('recognizeBtn');
const dropZone = document.getElementById('dropZone');
const statusElement = document.getElementById('status');
const tableContainer = document.getElementById('tableContainer');

// 显示状态信息
function showStatus(message, type = '') {
    statusElement.textContent = message;
    statusElement.className = 'status ' + type;
}

// 处理文件选择
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        imagePreview.src = e.target.result;
        imagePreview.style.display = 'block';
        recognizeBtn.style.display = 'block';
        exportBtn.style.display = 'none';
        tableContainer.innerHTML = '';
        showStatus('图片已加载，请点击"识别为表格"按钮', 'success');
    };
    reader.readAsDataURL(file);
}

// 识别图片为表格
async function recognizeImage() {
    try {
        if (!imagePreview || !imagePreview.src) {
            showStatus('请先上传图片', 'error');
            return;
        }

        showStatus('正在识别中...', 'info');
        recognizeBtn.disabled = true;

        // 发送OCR请求
        const response = await fetch('/PaddleOCR/DetectText', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(imagePreview.src.split(',')[1])
        });

        if (!response.ok) {
            throw new Error('OCR请求失败');
        }

        const data = await response.json();

        // 处理识别结果
        processRecognizedText(data.TextBlocks);
        exportBtn.style.display = 'block';
        showStatus('识别完成！', 'success');
    } catch (error) {
        console.error('识别错误:', error);
        showStatus('识别失败：' + error.message, 'error');
    } finally {
        recognizeBtn.disabled = false;
    }
}

// 处理识别出的文字
function processRecognizedText(textBlocks) {
    // 定义表头
    const headers = ['文本', '位置'];
    tableData = [headers];

    // 处理每一行文本
    textBlocks.forEach(block => {
        tableData.push([
            block.Text,
            block.Points.map(p => [(${p.x},${p.y})](cci:1://file:///e:/autotools/ocr-table/PaddleOCRAPI.py:14:0-17:62)).join(', ')
        ]);
    });

    // 创建表格
    createTable(tableData);
}

// 创建表格
function createTable(data) {
    const table = document.createElement('table');

    // 创建表头
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    data[0].forEach(cell => {
        const th = document.createElement('th');
        th.textContent = cell;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // 创建表格内容
    const tbody = document.createElement('tbody');
    data.slice(1).forEach(row => {
        const tr = document.createElement('tr');
        row.forEach(cell => {
            const td = document.createElement('td');
            td.textContent = cell;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    // 清空表格容器并添加新表格
    tableContainer.innerHTML = '';
    tableContainer.appendChild(table);
}

// 导出Excel
function exportToExcel() {
    try {
        // 创建工作簿
        const wb = XLSX.utils.book_new();

        // 创建工作表
        const ws = XLSX.utils.aoa_to_sheet(tableData);

        // 将工作表添加到工作簿
        XLSX.utils.book_append_sheet(wb, ws, "Sheet1");

        // 生成Excel文件并下载
        XLSX.writeFile(wb, "识别结果.xlsx");

        showStatus('Excel文件已导出', 'success');
    } catch (error) {
        showStatus('导出Excel失败：' + error.message, 'error');
    }
}

// 初始化事件监听
document.addEventListener('DOMContentLoaded', () => {
    if (fileInput && imagePreview && exportBtn && recognizeBtn && dropZone && tableContainer && statusElement) {
        fileInput.addEventListener('change', handleFileSelect);
        exportBtn.addEventListener('click', exportToExcel);
        recognizeBtn.addEventListener('click', recognizeImage);
        dropZone.addEventListener('click', () => fileInput.click());
    } else {
        console.error('无法找到所需的DOM元素');
    }
});