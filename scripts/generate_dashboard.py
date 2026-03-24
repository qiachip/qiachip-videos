import json
import os

def generate_dashboard():
    json_path = "data/processed/videos_with_model.json"
    output_path = "reports/dashboard.html"

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Qiachip-Lens Classification Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #0f1117;
            --bg-card: #1a1d26;
            --bg-hover: #242836;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --border: #334155;

            --color-exact: #4ade80;
            --color-regex: #60a5fa;
            --color-keyword: #f59e0b;
            --color-auto-label: #6b7280;
            --color-unclassified: #ef4444;

            --model-kr: #3b82f6;
            --model-rx: #10b981;
            --model-tx: #8b5cf6;
            --model-qa: #f97316;
            --model-other: #06b6d4;
            --model-gray: #6b7280;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-deep);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            line-height: 1.5;
            padding-top: 140px; /* Space for fixed header */
        }

        .font-mono {
            font-family: 'IBM Plex Mono', monospace;
        }

        /* 区域 1：顶部概览栏 */
        header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background-color: var(--bg-deep);
            border-bottom: 1px solid var(--border);
            padding: 20px;
            z-index: 1000;
            backdrop-filter: blur(8px);
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 12px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .summary-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 12px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
            overflow: hidden;
        }

        .summary-card:hover {
            border-color: var(--text-secondary);
            transform: translateY(-2px);
        }

        .summary-card.active {
            border-color: var(--text-primary);
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
        }

        .summary-card .label {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }

        .summary-card .value {
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .summary-card .percent {
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 2px;
        }

        .summary-card::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            height: 3px;
            width: 100%;
            background: var(--model-gray);
        }

        .card-total::after { background: #fff; }
        .card-exact::after { background: var(--color-exact); }
        .card-regex::after { background: var(--color-regex); }
        .card-keyword::after { background: var(--color-keyword); }
        .card-auto_label::after { background: var(--color-auto-label); }
        .card-unclassified::after { background: var(--color-unclassified); }

        /* 区域 2：筛选控制栏 */
        .controls {
            max-width: 1400px;
            margin: 20px auto;
            padding: 0 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            align-items: center;
            background: var(--bg-card);
            padding: 15px;
            border-radius: 4px;
            border: 1px solid var(--border);
        }

        .filter-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .methods-checkboxes {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }

        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            font-size: 13px;
        }

        .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        select, input {
            background: #0f1117;
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 6px 12px;
            border-radius: 4px;
            outline: none;
            font-size: 14px;
        }

        select:focus, input:focus {
            border-color: var(--text-secondary);
        }

        .search-box {
            flex-grow: 1;
            min-width: 200px;
        }

        .stats-info {
            margin-left: auto;
            color: var(--text-secondary);
            font-size: 13px;
        }

        /* 区域 3：视频卡片网格 */
        .video-grid {
            max-width: 1400px;
            margin: 0 auto 40px;
            padding: 0 20px;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 24px;
        }

        .video-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 4px;
            overflow: hidden;
            transition: transform 0.2s, border-color 0.2s;
            cursor: pointer;
            display: flex;
            flex-direction: column;
        }

        .video-card:hover {
            transform: translateY(-2px);
            border-color: var(--text-secondary);
        }

        .thumbnail-container {
            width: 100%;
            aspect-ratio: 16/9;
            background: #242836;
            position: relative;
        }

        .thumbnail-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .video-content {
            padding: 16px;
            flex-grow: 1;
        }

        .video-title {
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 12px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            min-height: 48px;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }

        .badge {
            font-size: 11px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 2px;
            text-transform: uppercase;
        }

        .badge-method {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
        }

        .meta-row {
            display: flex;
            align-items: center;
            gap: 15px;
            color: var(--text-secondary);
            font-size: 12px;
            margin-top: auto;
        }

        .source-tag {
            background: rgba(255, 255, 255, 0.05);
            padding: 1px 4px;
            border-radius: 2px;
            font-style: italic;
        }

        /* 详情展开 */
        .description-panel {
            display: none;
            padding: 16px;
            background: #12141c;
            border-top: 1px solid var(--border);
            font-size: 13px;
            color: var(--text-secondary);
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }

        .video-card.expanded .description-panel {
            display: block;
        }

        /* 空状态 */
        .empty-state {
            grid-column: 1 / -1;
            padding: 100px;
            text-align: center;
            color: var(--text-secondary);
            border: 2px dashed var(--border);
            border-radius: 8px;
        }

        /* 滚动条 */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-deep);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }

        /* Toast 通知 */
        .toast {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: var(--bg-card);
            color: var(--color-exact);
            padding: 10px 20px;
            border-radius: 4px;
            border: 1px solid var(--color-exact);
            z-index: 2000;
            transition: transform 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28);
            font-size: 14px;
            pointer-events: none;
        }
        .toast.show {
            transform: translateX(-50%) translateY(0);
        }

        .link-icon {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(15, 17, 23, 0.8);
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            color: var(--text-primary);
            text-decoration: none;
            transition: all 0.2s;
            z-index: 10;
        }
        .link-icon:hover {
            background: var(--color-exact);
            color: var(--bg-deep);
        }

        @media (max-width: 1000px) {
            .summary-grid {
                grid-template-columns: repeat(3, 1fr);
            }
            body { padding-top: 220px; }
        }

        @media (max-width: 600px) {
            .summary-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            body { padding-top: 380px; }
            .video-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <header>
        <div class="summary-grid" id="summary-container">
            <!-- JS 填充 -->
        </div>
    </header>

    <div class="controls">
        <div class="filter-group">
            <span style="font-size: 13px; color: var(--text-secondary);">匹配方法:</span>
            <div class="methods-checkboxes" id="methods-filter">
                <!-- JS 填充 -->
            </div>
        </div>

        <div class="filter-group">
            <select id="model-select">
                <option value="all">全部型号</option>
                <option value="unclassified">Unclassified</option>
            </select>
        </div>

        <input type="text" class="search-box" id="search-input" placeholder="搜索标题或型号...">

        <div class="filter-group">
            <select id="sort-select">
                <option value="date-desc">发布时间 ↓</option>
                <option value="date-asc">发布时间 ↑</option>
                <option value="views-desc">浏览量 ↓</option>
                <option value="likes-desc">点赞数 ↓</option>
            </select>
        </div>

        <div class="stats-info" id="count-info">
            显示 0 / 0 条
        </div>
    </div>

    <main class="video-grid" id="video-container">
        <!-- JS 填充 -->
    </main>

    <div id="toast" class="toast">已复制视频链接</div>

    <script>
        const DATA = /* JSON_DATA_PLACEHOLDER */;

        const COLORS = {
            exact: '#4ade80',
            regex: '#60a5fa',
            keyword: '#f59e0b',
            auto_label: '#6b7280',
            unclassified: '#ef4444'
        };

        const MODEL_COLORS = {
            KR: '#3b82f6',
            RX: '#10b981',
            TX: '#8b5cf6',
            QA: '#f97316',
            OTH: '#06b6d4',
            SPEC: '#6b7280'
        };

        let currentFilters = {
            methods: Object.keys(COLORS),
            model: 'all',
            search: '',
            sort: 'date-desc',
            quickMethod: null
        };

        function getModelColor(model) {
            if (['unclassified', 'factory_content', 'off_topic'].includes(model)) return MODEL_COLORS.SPEC;
            if (model.startsWith('KR')) return MODEL_COLORS.KR;
            if (model.startsWith('RX')) return MODEL_COLORS.RX;
            if (model.startsWith('TX')) return MODEL_COLORS.TX;
            if (model.startsWith('QA')) return MODEL_COLORS.QA;
            return MODEL_COLORS.OTH;
        }

        function init() {
            renderSummary();
            renderMethodFilters();
            renderModelSelect();
            applyFilters();

            // Event Listeners
            document.getElementById('model-select').addEventListener('change', e => {
                currentFilters.model = e.target.value;
                applyFilters();
            });
            document.getElementById('search-input').addEventListener('input', e => {
                currentFilters.search = e.target.value.toLowerCase();
                applyFilters();
            });
            document.getElementById('sort-select').addEventListener('change', e => {
                currentFilters.sort = e.target.value;
                applyFilters();
            });
        }

        function renderSummary() {
            const counts = { total: DATA.length };
            Object.keys(COLORS).forEach(m => {
                counts[m] = DATA.filter(v => v.match_method === m).length;
            });

            const container = document.getElementById('summary-container');

            const createCard = (label, method, count) => {
                const percent = ((count / counts.total) * 100).toFixed(1);
                const card = document.createElement('div');
                card.className = `summary-card card-${method} ${currentFilters.quickMethod === method ? 'active' : ''}`;
                card.innerHTML = `
                    <div class="label">${label}</div>
                    <div class="value font-mono">${count.toLocaleString()}</div>
                    <div class="percent">${percent}%</div>
                `;
                card.onclick = () => {
                    if (currentFilters.quickMethod === method) {
                        currentFilters.quickMethod = null;
                        currentFilters.methods = Object.keys(COLORS);
                    } else {
                        currentFilters.quickMethod = method;
                        currentFilters.methods = method === 'total' ? Object.keys(COLORS) : [method];
                    }
                    updateCheckboxStates();
                    applyFilters();
                    renderSummary();
                };
                return card;
            };

            container.innerHTML = '';
            container.appendChild(createCard('Total', 'total', counts.total));
            Object.keys(COLORS).forEach(m => {
                container.appendChild(createCard(m.replace('_', ' '), m, counts[m]));
            });
        }

        function renderMethodFilters() {
            const container = document.getElementById('methods-filter');
            Object.keys(COLORS).forEach(m => {
                const item = document.createElement('label');
                item.className = 'checkbox-item';
                item.innerHTML = `
                    <input type="checkbox" value="${m}" checked>
                    <span class="dot" style="background: ${COLORS[m]}"></span>
                    <span>${m.replace('_', ' ')}</span>
                `;
                item.querySelector('input').onchange = (e) => {
                    if (e.target.checked) {
                        currentFilters.methods.push(m);
                    } else {
                        currentFilters.methods = currentFilters.methods.filter(x => x !== m);
                    }
                    currentFilters.quickMethod = null;
                    applyFilters();
                    renderSummary();
                };
                container.appendChild(item);
            });
        }

        function updateCheckboxStates() {
            const checkboxes = document.querySelectorAll('#methods-filter input');
            checkboxes.forEach(cb => {
                cb.checked = currentFilters.methods.includes(cb.value);
            });
        }

        function renderModelSelect() {
            const models = new Set();
            DATA.forEach(v => {
                if (v.model && v.model !== 'unclassified' && v.model !== 'factory_content' && v.model !== 'off_topic') {
                    v.model.split(',').forEach(m => models.add(m.trim()));
                }
            });
            const sortedModels = Array.from(models).sort();
            const select = document.getElementById('model-select');
            sortedModels.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                select.appendChild(opt);
            });
        }

        function applyFilters() {
            let filtered = DATA.filter(v => {
                const methodMatch = currentFilters.methods.includes(v.match_method);
                const modelMatch = currentFilters.model === 'all' ||
                                 (currentFilters.model === 'unclassified' && (v.model === 'unclassified' || v.model === 'factory_content' || v.model === 'off_topic')) ||
                                 (v.model && v.model.split(',').map(s => s.trim()).includes(currentFilters.model));
                const searchMatch = !currentFilters.search ||
                                  v.title.toLowerCase().includes(currentFilters.search) ||
                                  (v.model && v.model.toLowerCase().includes(currentFilters.search));

                return methodMatch && modelMatch && searchMatch;
            });

            // Sort
            filtered.sort((a, b) => {
                if (currentFilters.sort === 'date-desc') return new Date(b.published_at) - new Date(a.published_at);
                if (currentFilters.sort === 'date-asc') return new Date(a.published_at) - new Date(b.published_at);
                if (currentFilters.sort === 'views-desc') return b.view_count - a.view_count;
                if (currentFilters.sort === 'likes-desc') return b.like_count - a.like_count;
                return 0;
            });

            renderVideos(filtered);
            document.getElementById('count-info').textContent = `显示 ${filtered.length} / ${DATA.length} 条`;
        }

        function showToast() {
            const t = document.getElementById('toast');
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 2000);
        }

        function renderVideos(videos) {
            const container = document.getElementById('video-container');
            container.innerHTML = '';

            if (videos.length === 0) {
                container.innerHTML = '<div class="empty-state">未找到匹配的视频</div>';
                return;
            }

            videos.forEach(v => {
                const videoUrl = `https://www.youtube.com/watch?v=${v.video_id}`;
                const card = document.createElement('div');
                card.className = 'video-card';
                card.onclick = (e) => {
                    // Prevent expansion when clicking the link icon
                    if (e.target.closest('.link-icon')) return;
                    card.classList.toggle('expanded');
                };

                card.ondblclick = (e) => {
                    navigator.clipboard.writeText(videoUrl).then(() => {
                        showToast();
                    });
                };

                const models = v.model.split(',').map(m => m.trim());
                const modelBadges = models.map(m => `
                    <span class="badge" style="background: ${getModelColor(m)}; color: #fff;">${m}</span>
                `).join('');

                const methodLabel = v.match_method;
                const methodColor = COLORS[v.match_method];

                const date = new Date(v.published_at).toLocaleDateString();

                card.innerHTML = `
                    <div class="thumbnail-container">
                        <img src="${v.thumbnail_url}" alt="thumbnail" onerror="this.src='https://via.placeholder.com/320x180/242836/94a3b8?text=Image+Load+Failed'">
                        <a href="${videoUrl}" target="_blank" class="link-icon" title="在 YouTube 中打开">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                        </a>
                    </div>
                    <div class="video-content">
                        <div class="video-title" title="${v.title}">${v.title}</div>
                        <div class="badge-row">
                            ${modelBadges}
                            <span class="badge badge-method" style="border: 1px solid ${methodColor}; color: ${methodColor}; background: transparent;">${methodLabel}</span>
                        </div>
                        <div class="meta-row">
                            <span>📅 ${date}</span>
                            <span>👁 ${v.view_count.toLocaleString()}</span>
                            <span>👍 ${v.like_count.toLocaleString()}</span>
                            ${v.match_source ? `<span class="source-tag">src: ${v.match_source}</span>` : ''}
                        </div>
                    </div>
                    <div class="description-panel">
                        <strong>Full Description:</strong>\\n${v.description || 'No description available.'}
                    </div>
                `;
                container.appendChild(card);
            });
        }

        window.onload = init;
    </script>
</body>
</html>"""

    final_html = html_template.replace("/* JSON_DATA_PLACEHOLDER */", json.dumps(data, ensure_ascii=False))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"Dashboard generated successfully: {output_path}")

if __name__ == "__main__":
    generate_dashboard()
