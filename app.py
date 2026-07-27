import streamlit as st
import streamlit.components.v1 as components

# 1. Cấu hình trang Streamlit
st.set_page_config(page_title="3D SMT Feeder Dashboard", layout="wide")

# 2. Toàn bộ mã nguồn HTML/CSS/JS của giao diện V6 3D
html_v6 = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMT Feeder 3D Digital Twin</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        /* Modern 3D / Glassmorphism Dark Theme */
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: radial-gradient(circle at top, #1a1a2e, #16213e, #0f3460);
            color: #e0e0e0; 
            margin: 0; 
            padding: 20px; 
            min-height: 100vh;
        }
        .container { 
            max-width: 1500px; 
            margin: auto; 
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 30px; 
            border-radius: 16px; 
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5); 
        }
        h1 { 
            color: #00d2ff; 
            font-size: 26px; 
            border-bottom: 2px solid rgba(0, 210, 255, 0.3); 
            padding-bottom: 15px; 
            margin-top: 0;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .control-panel { 
            background: rgba(0, 0, 0, 0.25); 
            padding: 20px; 
            border-radius: 12px; 
            margin-bottom: 25px; 
            display: flex; 
            align-items: center; 
            flex-wrap: wrap;
            gap: 15px; 
            border: 1px solid rgba(255,255,255,0.08);
        }
        input[type="file"] { display: none; }
        .btn { 
            padding: 12px 22px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: bold; 
            border: none; 
            transition: all 0.3s ease; 
            color: #fff; 
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            font-size: 13px;
        }
        .btn-upload { background: linear-gradient(45deg, #00d2ff, #3a7bd5); }
        .btn-upload:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 210, 255, 0.4); }
        .btn-demo { background: linear-gradient(45deg, #11998e, #38ef7d); }
        .btn-demo:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(56, 239, 125, 0.4); }
        
        .file-list { flex-grow: 1; font-size: 14px; color: #00d2ff; font-weight: 500; }
        
        /* KPI Cards Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        .kpi-card {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        .kpi-title { font-size: 12px; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }
        .kpi-value { font-size: 22px; font-weight: bold; color: #00d2ff; margin-top: 5px; }

        #charts-container { display: flex; flex-wrap: wrap; gap: 25px; }
        .chart-box { 
            flex: 1 1 100%; 
            height: 650px; 
            background: rgba(0, 0, 0, 0.3); 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            border-radius: 12px; 
            padding: 15px; 
        }
    </style>
</head>
<body>

<div class="container">
    <h1>
        <span>🚀 SMT Feeder - 3D Spatial Analysis Dashboard</span>
        <span style="font-size: 12px; color: #888; text-transform: none;">V6 Digital Twin</span>
    </h1>
    
    <div class="control-panel" id="dropZone">
        <label for="excelUpload" class="btn btn-upload">📦 Upload Excel Data</label>
        <input type="file" id="excelUpload" accept=".xlsx, .xls, .xlsm">
        
        <button class="btn btn-demo" onclick="loadDemoData()">⚡ Load Demo Data</button>
        
        <div class="file-list" id="fileInfo">Awaiting data injection... (Click Demo or Upload File)</div>
    </div>

    <!-- Summary KPI Cards -->
    <div class="kpi-grid" id="kpiContainer" style="display:none;">
        <div class="kpi-card">
            <div class="kpi-title">Total Samples</div>
            <div class="kpi-value" id="kpiSamples">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Max Left Dev (mm)</div>
            <div class="kpi-value" id="kpiMaxL" style="color:#3a7bd5;">0.000</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Max Right Dev (mm)</div>
            <div class="kpi-value" id="kpiMaxR" style="color:#e74c3c;">0.000</div>
        </div>
    </div>

    <div id="charts-container">
        <!-- 3D Scatter Plot Area -->
        <div id="plot3D" class="chart-box"></div>
    </div>
</div>

<script>
    document.getElementById('excelUpload').addEventListener('change', handleFileSelect, false);

    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        document.getElementById('fileInfo').innerText = `Processing Data: ${file.name}...`;

        const reader = new FileReader();
        reader.onload = function(evt) {
            try {
                const data = new Uint8Array(evt.target.result);
                const workbook = XLSX.read(data, {type: 'array'});
                const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
                const jsonData = XLSX.utils.sheet_to_json(firstSheet, {header: 1});
                
                processAndDraw3D(jsonData, file.name);
            } catch (err) {
                alert("Error reading Excel file: " + err.message);
            }
        };
        reader.readAsArrayBuffer(file);
    }

    function processAndDraw3D(jsonData, filename) {
        let parsedData = [];
        let startIndex = -1;

        for (let i = 0; i < jsonData.length; i++) {
            const row = jsonData[i];
            if (row && row.length >= 5 && (row[0] === 1 || String(row[0]).trim() === '1')) {
                startIndex = i;
                break;
            }
        }

        if (startIndex === -1) {
            for (let i = 0; i < jsonData.length; i++) {
                const r = jsonData[i];
                if (r && r.length >= 5 && !isNaN(parseFloat(r[0])) && !isNaN(parseFloat(r[1]))) {
                    startIndex = i;
                    break;
                }
            }
        }

        if (startIndex !== -1) {
            for (let i = startIndex; i < jsonData.length; i++) {
                const row = jsonData[i];
                if (!row || row.length < 5) continue;

                let no = parseInt(row[0]);
                let lx = parseFloat(row[1]);
                let ly = parseFloat(row[2]);
                let rx = parseFloat(row[3]);
                let ry = parseFloat(row[4]);

                if (!isNaN(no) && !isNaN(lx) && !isNaN(ly)) {
                    parsedData.push({
                        No: no,
                        L_X: isNaN(lx) ? 0 : lx,
                        L_Y: isNaN(ly) ? 0 : ly,
                        R_X: isNaN(rx) ? 0 : rx,
                        R_Y: isNaN(ry) ? 0 : ry
                    });
                }
            }
        }

        if (parsedData.length === 0) {
            alert("No valid numerical data sequence found in Excel file.");
            return;
        }

        document.getElementById('fileInfo').innerText = `3D Rendering Complete: ${filename}`;
        updateKPIs(parsedData);
        draw3DScatter(parsedData, filename);
    }

    function updateKPIs(data) {
        document.getElementById('kpiContainer').style.display = 'grid';
        document.getElementById('kpiSamples').innerText = data.length;
        
        let maxL = Math.max(...data.map(d => Math.hypot(d.L_X, d.L_Y)));
        let maxR = Math.max(...data.map(d => Math.hypot(d.R_X, d.R_Y)));
        
        document.getElementById('kpiMaxL').innerText = maxL.toFixed(3);
        document.getElementById('kpiMaxR').innerText = maxR.toFixed(3);
    }

    function loadDemoData() {
        let demoData = [];
        for (let i = 1; i <= 36; i++) {
            let angle = (i / 36) * Math.PI * 2;
            demoData.push({
                No: i,
                L_X: (Math.sin(angle) * 0.15 + (Math.random() - 0.5) * 0.05),
                L_Y: (Math.cos(angle) * 0.15 + (Math.random() - 0.5) * 0.05),
                R_X: (Math.sin(angle + 0.5) * 0.18 + (Math.random() - 0.5) * 0.05),
                R_Y: (Math.cos(angle + 0.5) * 0.18 + (Math.random() - 0.5) * 0.05)
            });
        }
        document.getElementById('fileInfo').innerText = "Loaded Simulated Demo Dataset (36 Positions)";
        updateKPIs(demoData);
        draw3DScatter(demoData, "Simulated_SMT_Feeder_Demo");
    }

    function draw3DScatter(data, titleFilename) {
        const traceL = {
            x: data.map(d => d.L_X), 
            y: data.map(d => d.L_Y), 
            z: data.map(d => d.No),
            mode: 'markers+lines', 
            type: 'scatter3d', 
            name: 'Left Head Trajectory',
            hovertemplate: '<b>Left Head</b><br>Sample: %{z}<br>X Dev: %{x:.3f} mm<br>Y Dev: %{y:.3f} mm<extra></extra>',
            marker: { size: 5, color: data.map(d => d.No), colorscale: 'Blues', opacity: 0.9 },
            line: { color: '#00d2ff', width: 4 }
        };
        
        const traceR = {
            x: data.map(d => d.R_X), 
            y: data.map(d => d.R_Y), 
            z: data.map(d => d.No),
            mode: 'markers+lines', 
            type: 'scatter3d', 
            name: 'Right Head Trajectory',
            hovertemplate: '<b>Right Head</b><br>Sample: %{z}<br>X Dev: %{x:.3f} mm<br>Y Dev: %{y:.3f} mm<extra></extra>',
            marker: { size: 5, color: data.map(d => d.No), colorscale: 'Reds', opacity: 0.9 },
            line: { color: '#ff4757', width: 4 }
        };

        const layout = {
            title: { 
                text: `3D Spatial Trajectory Analysis [${titleFilename}]`, 
                font: { color: '#00d2ff', size: 18 } 
            },
            paper_bgcolor: 'rgba(0,0,0,0)', 
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: { l: 0, r: 0, b: 0, t: 40 },
            scene: {
                xaxis: { title: 'X Offset (mm)', backgroundcolor: "rgba(0,0,0,0.2)", gridcolor: "rgba(255,255,255,0.1)", color: '#fff' },
                yaxis: { title: 'Y Offset (mm)', backgroundcolor: "rgba(0,0,0,0.2)", gridcolor: "rgba(255,255,255,0.1)", color: '#fff' },
                zaxis: { title: 'Sample Sequence', backgroundcolor: "rgba(0,0,0,0.2)", gridcolor: "rgba(255,255,255,0.1)", color: '#fff' },
                camera: { eye: { x: 1.4, y: 1.4, z: 1.1 } }
            },
            legend: { font: { color: '#fff' }, x: 0.02, y: 0.98 }
        };

        Plotly.newPlot('plot3D', [traceL, traceR], layout, { responsive: true, displayModeBar: true });
    }
</script>
</body>
</html>
"""

# 3. Yêu cầu Streamlit nhúng (embed) đoạn HTML này lên màn hình
components.html(html_v6, height=950, scrolling=True)
