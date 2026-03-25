import json
import os

def generate_dashboard_v2():
    json_path = "data/processed/videos_with_model.json"
    output_path = "reports/dashboard_v2.html"

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Qiachip-Videos Dashboard V2</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #f8fafc;
            --bg-sidebar: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --text-muted: #94a3b8;
            --accent-indigo: #1e3a5f;
            --accent-amber: #f59e0b;
            --accent-green: #10b981;
            --border-color: #e2e8f0;
            --hover-bg: #f1f5f9;
            --active-bg: #eff6ff;
            --active-text: #1d4ed8;
            --sidebar-width: 280px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-primary);
            font-family: 'DM Sans', sans-serif;
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        .font-mono {
            font-family: 'DM Mono', monospace;
        }

        /* --- 左侧边栏 --- */
        .sidebar {
            width: var(--sidebar-width);
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }

        .sidebar-header {
            padding: 24px 20px 16px;
            border-bottom: 1px solid var(--border-color);
        }

        .sidebar-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--accent-indigo);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .search-container {
            position: relative;
        }

        .search-input {
            width: 100%;
            padding: 10px 12px 10px 36px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 14px;
            outline: none;
            background-color: var(--bg-main);
            transition: all 0.2s;
        }

        .search-input:focus {
            border-color: var(--accent-indigo);
            background-color: #fff;
            box-shadow: 0 0 0 3px rgba(30, 58, 95, 0.1);
        }

        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }

        .model-list {
            flex-grow: 1;
            overflow-y: auto;
            padding: 12px 8px;
        }

        .model-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 12px;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 2px;
            transition: all 0.1s;
        }

        .model-item:hover {
            background-color: var(--hover-bg);
        }

        .model-item.active {
            background-color: var(--active-bg);
            color: var(--active-text);
        }

        .model-name {
            font-family: 'DM Mono', monospace;
            font-size: 14px;
            font-weight: 500;
        }

        .video-count-badge {
            font-size: 11px;
            background-color: #f1f5f9;
            color: var(--text-secondary);
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
        }

        .model-item.active .video-count-badge {
            background-color: #dbeafe;
            color: var(--active-text);
        }

        /* --- 右侧内容区 --- */
        .main-content {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            background-color: var(--bg-main);
        }

        .top-toolbar {
            padding: 24px 32px;
            background-color: #fff;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }

        .current-model-info {
            display: flex;
            align-items: baseline;
            gap: 12px;
        }

        .current-model-name {
            font-family: 'DM Mono', monospace;
            font-size: 28px;
            font-weight: 700;
            color: var(--accent-indigo);
        }

        .current-model-stats {
            font-size: 14px;
            color: var(--text-secondary);
        }

        .action-buttons {
            display: flex;
            gap: 12px;
        }

        .btn {
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            border: 1px solid var(--border-color);
            background-color: #fff;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
            outline: none;
        }

        .btn:hover {
            background-color: var(--hover-bg);
            border-color: var(--text-secondary);
        }

        .btn-primary {
            background-color: var(--accent-indigo);
            color: #fff;
            border-color: var(--accent-indigo);
        }

        .btn-primary:hover {
            background-color: #162a45;
            border-color: #162a45;
        }

        .btn-success {
            background-color: var(--accent-green) !important;
            color: #fff !important;
            border-color: var(--accent-green) !important;
        }

        /* --- 视频列表 --- */
        .video-list-container {
            flex-grow: 1;
            overflow-y: auto;
            padding: 24px 32px;
        }

        .video-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-width: 1100px;
        }

        .video-item {
            background-color: #fff;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 20px;
            transition: border-color 0.2s;
        }

        .video-item:hover {
            border-color: var(--text-muted);
        }

        .video-index {
            font-family: 'DM Mono', monospace;
            font-size: 14px;
            color: var(--text-muted);
            width: 24px;
            text-align: right;
        }

        .video-thumbnail {
            width: 85px;
            height: 48px;
            border-radius: 4px;
            overflow: hidden;
            background-color: var(--bg-main);
            flex-shrink: 0;
        }

        .video-thumbnail img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .video-main {
            flex-grow: 1;
            min-width: 0;
        }

        .video-title {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
            text-decoration: none;
            display: block;
            margin-bottom: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .video-title:hover {
            text-decoration: underline;
            color: var(--active-text);
        }

        .video-meta {
            font-size: 12px;
            color: var(--text-secondary);
            display: flex;
            gap: 12px;
        }

        .btn-copy-mini {
            padding: 6px 12px;
            font-size: 12px;
            border-radius: 4px;
            color: var(--text-secondary);
            background-color: transparent;
            border: 1px solid var(--border-color);
            cursor: pointer;
            flex-shrink: 0;
            transition: all 0.2s;
        }

        .btn-copy-mini:hover {
            background-color: var(--hover-bg);
            color: var(--accent-indigo);
            border-color: var(--accent-indigo);
        }

        /* --- 滚动条控制 --- */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }

        /* --- Toast 通知 --- */
        .toast {
            position: fixed;
            bottom: 40px;
            right: 40px;
            background-color: #334155;
            color: #fff;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28);
            z-index: 10000;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .toast.show {
            opacity: 1;
            transform: translateY(0);
        }
    </style>
</head>
<body>

    <aside class="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                <span>qiachip-videos</span>
            </div>
            <div class="search-container">
                <div class="search-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                </div>
                <input type="text" class="search-input" id="model-search" placeholder="过滤型号...">
            </div>
        </div>
        <div class="model-list" id="model-list-container">
            <!-- JS Dynamic Fill -->
        </div>
    </aside>

    <main class="main-content">
        <div class="top-toolbar">
            <div class="current-model-info">
                <span class="current-model-name" id="display-model-name">--</span>
                <span class="current-model-stats" id="display-model-stats">0 个视频</span>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" id="btn-copy-all">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    复制全部
                </button>
                <button class="btn" id="btn-copy-links">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                    复制链接
                </button>
            </div>
        </div>

        <div class="video-list-container">
            <div class="video-list" id="video-list-container">
                <!-- JS Dynamic Fill -->
            </div>
        </div>
    </main>

    <div id="toast" class="toast">已复制到剪贴板</div>

    <script>
        const RAW_DATA = /* JSON_DATA_PLACEHOLDER */;

        const EXCLUDE_MODELS = ['unclassified', 'factory_content', 'off_topic', 'duplicator'];

        let modelGroups = {};
        let sortedModels = [];
        let currentSelectedModel = null;
        let filteredModels = [];

        function initData() {
            // Group videos by model
            RAW_DATA.forEach(v => {
                const models = v.model.split(',').map(m => m.trim());
                models.forEach(m => {
                    if (EXCLUDE_MODELS.includes(m)) return;
                    if (!modelGroups[m]) modelGroups[m] = [];
                    modelGroups[m].push(v);
                });
            });

            // Sort videos within each group by view count
            Object.keys(modelGroups).forEach(m => {
                modelGroups[m].sort((a, b) => (b.view_count || 0) - (a.view_count || 0));
            });

            // Sort models by video count
            sortedModels = Object.keys(modelGroups).sort((a, b) => {
                return modelGroups[b].length - modelGroups[a].length;
            });

            filteredModels = sortedModels;

            if (sortedModels.length > 0) {
                currentSelectedModel = sortedModels[0];
            }
        }

        function renderModelList(filter = '') {
            const container = document.getElementById('model-list-container');
            container.innerHTML = '';

            filteredModels = sortedModels.filter(m => m.toLowerCase().includes(filter.toLowerCase()));

            filteredModels.forEach(m => {
                const item = document.createElement('div');
                item.className = `model-item ${m === currentSelectedModel ? 'active' : ''}`;
                item.innerHTML = `
                    <span class="model-name">${m}</span>
                    <span class="video-count-badge">${modelGroups[m].length}</span>
                `;
                item.onclick = () => selectModel(m);
                container.appendChild(item);
            });
        }

        function selectModel(modelName) {
            currentSelectedModel = modelName;

            // Update UI
            document.querySelectorAll('.model-item').forEach(el => {
                if (el.querySelector('.model-name').textContent === modelName) {
                    el.classList.add('active');
                } else {
                    el.classList.remove('active');
                }
            });

            document.getElementById('display-model-name').textContent = modelName;
            document.getElementById('display-model-stats').textContent = `${modelGroups[modelName].length} 个视频`;

            renderVideoList();
        }

        function renderVideoList() {
            const container = document.getElementById('video-list-container');
            container.innerHTML = '';

            const videos = modelGroups[currentSelectedModel] || [];

            videos.forEach((v, idx) => {
                const item = document.createElement('div');
                item.className = 'video-item';

                const date = new Date(v.published_at).toLocaleDateString();
                const views = (v.view_count || 0).toLocaleString();
                const likes = (v.like_count || 0).toLocaleString();

                item.innerHTML = `
                    <div class="video-index">${idx + 1}</div>
                    <div class="video-thumbnail">
                        <img src="${v.thumbnail_url}" alt="thumb">
                    </div>
                    <div class="video-main">
                        <a href="https://www.youtube.com/watch?v=${v.video_id}" target="_blank" class="video-title" title="${v.title}">${v.title}</a>
                        <div class="video-meta">
                            <span>👁 ${views}</span>
                            <span>👍 ${likes}</span>
                            <span>📅 ${date}</span>
                        </div>
                    </div>
                    <button class="btn-copy-mini" onclick="copySingleVideo('${v.title}', '${v.video_id}', this)">复制此条</button>
                `;
                container.appendChild(item);
            });
        }

        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }

        function handleCopyEffect(btn, originalText) {
            btn.classList.add('btn-success');
            btn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                已复制 ✓
            `;
            setTimeout(() => {
                btn.classList.remove('btn-success');
                btn.innerHTML = originalText;
            }, 2000);
        }

        function copySingleVideo(title, videoId, btn) {
            const text = `${title}\\nhttps://www.youtube.com/watch?v=${videoId}`;
            navigator.clipboard.writeText(text).then(() => {
                const originalText = btn.innerHTML;
                btn.textContent = '已复制 ✓';
                btn.style.borderColor = 'var(--accent-green)';
                btn.style.color = 'var(--accent-green)';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.borderColor = '';
                    btn.style.color = '';
                }, 1500);
            });
        }

        document.getElementById('btn-copy-all').onclick = function() {
            const model = currentSelectedModel;
            const videos = modelGroups[model];
            let text = `${model}（共 ${videos.length} 个视频）\\n\\n`;

            videos.forEach((v, idx) => {
                text += `${idx + 1}. ${v.title}\\n   https://www.youtube.com/watch?v=${v.video_id}\\n\\n`;
            });

            navigator.clipboard.writeText(text.trim()).then(() => {
                handleCopyEffect(this, `
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    复制全部
                `);
            });
        };

        document.getElementById('btn-copy-links').onclick = function() {
            const videos = modelGroups[currentSelectedModel];
            const text = videos.map(v => `https://www.youtube.com/watch?v=${v.video_id}`).join('\\n');

            navigator.clipboard.writeText(text).then(() => {
                handleCopyEffect(this, `
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                    复制链接
                `);
            });
        };

        document.getElementById('model-search').oninput = function(e) {
            renderModelList(e.target.value);
        };

        // Init execution
        initData();
        renderModelList();
        if (currentSelectedModel) {
            selectModel(currentSelectedModel);
        }

    </script>
</body>
</html>"""

    final_html = html_template.replace("/* JSON_DATA_PLACEHOLDER */", json.dumps(data, ensure_ascii=False))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"Dashboard V2 generated successfully: {output_path}")

if __name__ == "__main__":
    generate_dashboard_v2()
