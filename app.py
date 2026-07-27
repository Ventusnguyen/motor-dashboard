"""
Factory Data Engineering Module: Web-App Generator V3
Generates an advanced standalone HTML Application with Cpk calculation, 
PDF export, Local API simulation, and Smart Drift Warning (Nelson Rules).
"""

import os

def generate_offline_analyzer_v3(output_filename: str = "Feeder_Analyzer_V3.html") -> str:
    """Generates the V3 HTML Application with comprehensive QA features."""
    
    html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Feeder Data Auto Analyzer V3 (Pro)</title>
    <!-- Thư viện xử lý Excel, Biểu đồ và Xuất PDF -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 1400px; margin: auto; background: #fff; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { color: #2c3e50; font-size: 24px; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 0; }
        .control-panel { background: #eef2f5; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; gap: 15px; flex-wrap: wrap; }
        input[type="file"] { display: none; }
        .btn { padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; border: none; transition: background 0.3s; color: white; }
        .btn-upload { background-color: #3498db; }
        .btn-upload:hover { background-color: #2980b9; }
        .btn-pdf { background-color: #9b59b6; display: none; }
        .btn-pdf:hover { background-color: #8e44ad; }
        .btn-api { background-color: #e67e22; display: none; }
        .btn-api:hover { background-color: #d35400; }
        .file-list { flex-grow: 1; font-size: 14px; color: #555; }
        #report-content { padding: 10px; }
        #charts-container { display: flex; flex-wrap: wrap; gap: 20px; }
        .chart-box { flex: 1 1 48%; min-width: 500px; height: 500px; background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 10px; }
        #summary-stats { margin-bottom: 20px; font-size: 14px; display: flex; flex-wrap: wrap; gap: 10px; }
        .stat-card { background: #fff; border-left: 4px solid #34495e; padding: 10px 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border-radius: 4px; }
        .status-ok { border-left-color: #2ecc71; color: #27ae60; }
        .status-ng { border-left-color: #e74c3c; color: #c0392b; }
        .warning-text { color: red; font-weight: bold; }
    </style>
</head>
<body>

<div class="container">
    <h1>🏭 SMT Feeder QA Dashboard V3</h1>
    
    <div class="control-panel">
        <label for="excelUpload" class="btn btn-upload">📂 Chọn File Excel</label>
        <input type="file" id="excelUpload" accept=".xlsx, .xls, .xlsm" multiple>
        <select id="fileSelector" style="display:none; padding: 8px; border-radius: 4px;"></select>
        <div class="file-list" id="fileInfo">Chưa có file nào được chọn.</div>
        
        <!-- Các nút chức năng V3 -->
        <button id="btnPdf" class="btn btn-pdf" onclick="exportPDF()">📄 Xuất PDF</button>
        <button id="btnApi" class="btn btn-api" onclick="saveToDB()">💾 Lưu Database (Mock API)</button>
    </div>

    <!-- Vùng xuất báo cáo PDF -->
    <div id="report-content">
        <div id="summary-stats"></div>
        <div id="charts-container">
            <div id="scatterPlot" class="chart-box"></div>
            <div id="trendPlot" class="chart-box"></div>
        </div>
    </div>
</div>

<script>
    let uploadedFiles = {}; 
    let currentPayload = {}; // Dùng để lưu trữ trạng thái gửi API
    const SPEC_LIMIT = 0.12;

    document.getElementById('excelUpload').addEventListener('change', handleFileSelect, false);
    document.getElementById('fileSelector').addEventListener('change', function(e) {
        processAndDraw(uploadedFiles[e.target.value], e.target.value);
    });

    function handleFileSelect(e) {
        const files = e.target.files;
        if (files.length === 0) return;
        
        document.getElementById('fileInfo').innerText = `Đang xử lý ${files.length} file...`;
        const selector = document.getElementById('fileSelector');
        selector.innerHTML = '';
        uploadedFiles = {};

        let filesProcessed = 0;

        Array.from(files).forEach(file => {
            const reader = new FileReader();
            reader.onload = function(evt) {
                const data = new Uint8Array(evt.target.result);
                const workbook = XLSX.read(data, {type: 'array'});
                const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                const jsonData = XLSX.utils.sheet_to_json(firstSheet, {header: 1});
                
                uploadedFiles[file.name] = jsonData;
                
                const option = document.createElement('option');
                option.value = file.name;
                option.text = file.name;
                selector.appendChild(option);

                filesProcessed++;
                if(filesProcessed === files.length) {
                    selector.style.display = files.length > 1 ? 'block' : 'none';
                    document.getElementById('fileInfo').innerText = `Hoàn tất. Đang hiển thị file: ${files[0].name}`;
                    
                    // Hiển thị nút V3
                    document.getElementById('btnPdf').style.display = 'block';
                    document.getElementById('btnApi').style.display = 'block';
                    
                    processAndDraw(uploadedFiles[files[0].name], files[0].name);
                }
            };
            reader.readAsArrayBuffer(file);
        });
    }

    // JS Math functions for Cpk calculation
    function getMean(arr) { return arr.reduce((a, b) => a + b, 0) / arr.length; }
    function getStdDev(arr, mean) {
        let sum = arr.reduce((a, b) => a + Math.pow(b - mean, 2), 0);
        return Math.sqrt(sum / (arr.length - 1)) || 0.0001; // Tránh chia cho 0
    }
    function getCpk(arr, usl, lsl) {
        let mean = getMean(arr);
        let std = getStdDev(arr, mean);
        let cpku = (usl - mean) / (3 * std);
        let cpkl = (mean - lsl) / (3 * std);
        return Math.min(cpku, cpkl).toFixed(2);
    }

    // Nelson Rule: 7 consecutive points on the same side of 0
    function checkNelsonRule(arr) {
        let countPos = 0, countNeg = 0;
        for(let v of arr) {
            if(v > 0) { countPos++; countNeg = 0; }
            else if (v < 0) { countNeg++; countPos = 0; }
            else { countPos = 0; countNeg = 0; }
            
            if (countPos >= 7 || countNeg >= 7) return true;
        }
        return false;
    }

    function processAndDraw(jsonData, filename) {
        let parsedData = [];
        let inspector = "Unknown", status = "Unknown";
        
        if(jsonData.length > 0 && jsonData[0].length >= 5) {
            inspector = jsonData[0][3] || "Unknown";
            status = jsonData[0][4] || "Unknown";
        }

        // Auto-detect block starting with '1'
        for (let i = 0; i < jsonData.length; i++) {
            const row = jsonData[i];
            if (row && row.length >= 5 && String(row[0]).trim() === '1') {
                for(let j = 0; j < 36; j++) {
                    if (i + j < jsonData.length && jsonData[i+j].length >= 5) {
                        let rowData = jsonData[i+j];
                        parsedData.push({
                            No: parseInt(rowData[0]),
                            L_X: parseFloat(rowData[1] || 0), L_Y: parseFloat(rowData[2] || 0),
                            R_X: parseFloat(rowData[3] || 0), R_Y: parseFloat(rowData[4] || 0)
                        });
                    }
                }
                break;
            }
        }

        if (parsedData.length === 0) {
            alert(`Lỗi: Không tìm thấy 36 điểm đo trong file ${filename}.`);
            return;
        }

        // Lưu trạng thái cho API
        currentPayload = { filename: filename, inspector: inspector, status: status, spec: SPEC_LIMIT, data: parsedData };

        updateSummaryAndCpk(parsedData, filename, inspector, status);
        drawScatterPlot(parsedData, filename, inspector);
        drawTrendPlot(parsedData, filename, inspector);
    }

    function updateSummaryAndCpk(data, filename, insp, stat) {
        const L_X = data.map(d => d.L_X); const L_Y = data.map(d => d.L_Y);
        const R_X = data.map(d => d.R_X); const R_Y = data.map(d => d.R_Y);

        let cpk_Lx = getCpk(L_X, SPEC_LIMIT, -SPEC_LIMIT);
        let cpk_Ry = getCpk(R_Y, SPEC_LIMIT, -SPEC_LIMIT);

        let statusClass = stat.toUpperCase() === 'OK' ? 'status-ok' : 'status-ng';

        document.getElementById('summary-stats').innerHTML = `
            <div class="stat-card"><b>File:</b> ${filename}</div>
            <div class="stat-card"><b>Insp:</b> ${insp}</div>
            <div class="stat-card ${statusClass}"><b>Judge:</b> <b>${stat}</b></div>
            <div class="stat-card"><b>Cpk (L_X):</b> ${cpk_Lx}</div>
            <div class="stat-card"><b>Cpk (R_Y):</b> ${cpk_Ry}</div>
        `;
    }

    function drawScatterPlot(data, title, insp) {
        const traceL = { x: data.map(d => d.L_X), y: data.map(d => d.L_Y), mode: 'markers', name: 'Left (L)', marker: { color: 'royalblue', size: 8 } };
        const traceR = { x: data.map(d => d.R_X), y: data.map(d => d.R_Y), mode: 'markers', name: 'Right (R)', marker: { color: 'crimson', size: 8 } };

        const layout = {
            title: { text: `Target Scatter Plot<br><sub>${title} | Insp: ${insp}</sub>` },
            xaxis: { title: 'X (mm)', range: [-0.15, 0.15], zerolinecolor: 'gray' },
            yaxis: { title: 'Y (mm)', range: [-0.15, 0.15], zerolinecolor: 'gray', scaleanchor: 'x', scaleratio: 1 },
            shapes: [{ type: 'circle', xref: 'x', yref: 'y', x0: -SPEC_LIMIT, y0: -SPEC_LIMIT, x1: SPEC_LIMIT, y1: SPEC_LIMIT, line: { color: 'green', dash: 'dot' } }],
            margin: { t: 60, b: 40, l: 40, r: 40 }
        };
        Plotly.newPlot('scatterPlot', [traceL, traceR], layout, {responsive: true});
    }

    function drawTrendPlot(data, title, insp) {
        const x_vals = data.map(d => d.No);
        const L_X = data.map(d => d.L_X), L_Y = data.map(d => d.L_Y);
        const R_X = data.map(d => d.R_X), R_Y = data.map(d => d.R_Y);

        // Kiểm tra Nelson Rules
        let hasWarning = checkNelsonRule(L_X) || checkNelsonRule(L_Y) || checkNelsonRule(R_X) || checkNelsonRule(R_Y);
        let titleHtml = `Trend Plot<br><sub>${title} | Insp: ${insp}</sub>`;
        if(hasWarning) titleHtml += `<br><span class="warning-text">⚠️ Cảnh báo: Lệch tâm hệ thống (Nelson Rule)</span>`;

        const traces = [
            { x: x_vals, y: L_X, mode: 'lines+markers', name: 'L_X', marker: {color: 'royalblue'} },
            { x: x_vals, y: L_Y, mode: 'lines+markers', name: 'L_Y', marker: {color: 'darkcyan'} },
            { x: x_vals, y: R_X, mode: 'lines+markers', name: 'R_X', marker: {color: 'crimson'} },
            { x: x_vals, y: R_Y, mode: 'lines+markers', name: 'R_Y', marker: {color: 'darkorange'} }
        ];

        const layout = {
            title: { text: titleHtml },
            xaxis: { title: 'No.', dtick: 5 },
            yaxis: { title: 'Dev (mm)', range: [-0.15, 0.15] },
            shapes: [
                { type: 'line', xref: 'paper', x0: 0, x1: 1, yref: 'y', y0: SPEC_LIMIT, y1: SPEC_LIMIT, line: { color: 'red', dash: 'dash' } },
                { type: 'line', xref: 'paper', x0: 0, x1: 1, yref: 'y', y0: -SPEC_LIMIT, y1: -SPEC_LIMIT, line: { color: 'red', dash: 'dash' } },
                { type: 'line', xref: 'paper', x0: 0, x1: 1, yref: 'y', y0: 0, y1: 0, line: { color: 'black', width: 1 } }
            ],
            margin: { t: 80, b: 40, l: 40, r: 40 }
        };

        // Tô đỏ nền nếu vi phạm
        if(hasWarning) {
            layout.shapes.push({
                type: 'rect', xref: 'paper', yref: 'paper', x0: 0, x1: 1, y0: 0, y1: 1,
                fillcolor: 'rgba(255, 0, 0, 0.1)', line: {width: 0}, layer: 'below'
            });
        }

        Plotly.newPlot('trendPlot', traces, layout, {responsive: true});
    }

    // V3 Action: Export PDF
    function exportPDF() {
        const element = document.getElementById('report-content');
        const opt = {
            margin:       10,
            filename:     'QA_Report_' + currentPayload.filename + '.pdf',
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2, useCORS: true },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'landscape' }
        };
        html2pdf().set(opt).from(element).save();
    }

    // V3 Action: Simulate Local API
    function saveToDB() {
        console.log("=== SENDING TO LOCAL API (FASTAPI) ===");
        console.log(JSON.stringify(currentPayload, null, 2));
        alert(`Đã mô phỏng gửi dữ liệu tới Database thành công!\n\nPayload:\n- File: ${currentPayload.filename}\n- Kỹ thuật viên: ${currentPayload.inspector}\n- Số lượng điểm: ${currentPayload.data.length}\n\n(Kiểm tra Console F12 để xem JSON chi tiết)`);
    }
</script>
</body>
</html>"""
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return f"Bản nâng cấp V3 (Pro) đã được tạo thành công tại: {output_filename}"

if __name__ == "__main__":
    result = generate_offline_analyzer_v3()
    print(result)
