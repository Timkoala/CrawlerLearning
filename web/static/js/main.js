// Main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Handle form submissions
    const crawlForm = document.getElementById('crawl-form');
    if (crawlForm) {
        crawlForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Save crawl job
            saveCrawlJob();
        });
    }
    
    // Add event listener for job selection
    const selectedJobSelect = document.getElementById('selected-job');
    const startCrawlBtn = document.getElementById('start-crawl-btn');
    const stopCrawlBtn = document.getElementById('stop-crawl-btn');
    
    if (selectedJobSelect) {
        selectedJobSelect.addEventListener('change', function() {
            const jobId = this.value;
            if (jobId) {
                startCrawlBtn.disabled = false;
                // In a real implementation, you would check if the job is running
                // and enable/disable stop button accordingly
                stopCrawlBtn.disabled = true;
                // Load job details
                loadJobDetails(jobId);
            } else {
                startCrawlBtn.disabled = true;
                stopCrawlBtn.disabled = true;
                // Hide job details
                document.getElementById('selected-job-details').style.display = 'none';
            }
        });
    }
    
    if (startCrawlBtn) {
        startCrawlBtn.addEventListener('click', startCrawl);
    }
    
    if (stopCrawlBtn) {
        stopCrawlBtn.addEventListener('click', stopCrawl);
    }
    
    const settingsForms = [
        'general-settings-form',
        'proxy-settings-form',
        'anti-detection-form'
    ];
    
    settingsForms.forEach(formId => {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                // Save settings
                saveSettings(formId);
            });
        }
    });
    
    // Results page: setup filters and initial load
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            resultsState.page = 1; // reset to first page
            loadResults();
        });
    }
    
    // Load initial data
    loadJobs();
    loadResults();
    loadPresets();
});

function loadPresetTask(name, url) {
    document.getElementById('name').value = name;
    document.getElementById('target-url').value = url;
}

function saveCrawlJob() {
    const name = document.getElementById('name').value;
    const url = document.getElementById('target-url').value;
    const depth = document.getElementById('depth').value;
    const titleSelector = document.getElementById('title-selector').value;
    const contentSelector = document.getElementById('content-selector').value;
    const customFieldsText = document.getElementById('custom-fields').value;
    const editingJobId = document.getElementById('editing-job-id') ? document.getElementById('editing-job-id').value : '';

    if (!name || !url) {
        alert('请填写任务名称和目标URL');
        return;
    }

    let customRules = {};
    if (titleSelector || contentSelector || customFieldsText) {
        customRules = { title_selector: titleSelector, content_selector: contentSelector };
        if (customFieldsText) {
            const customFields = {};
            const lines = customFieldsText.split('\n');
            lines.forEach(line => {
                const trimmedLine = line.trim();
                if (trimmedLine && trimmedLine.includes('=')) {
                    const idx = trimmedLine.indexOf('=');
                    const fieldName = trimmedLine.slice(0, idx).trim();
                    const selector = trimmedLine.slice(idx + 1).trim();
                    if (fieldName && selector) customFields[fieldName] = selector;
                }
            });
            if (Object.keys(customFields).length > 0) customRules.custom_fields = customFields;
        }
    }

    const payload = JSON.stringify({
        name: name,
        target_url: url,
        max_depth: parseInt(depth),
        custom_rules: Object.keys(customRules).length > 0 ? customRules : null
    });

    const isEdit = editingJobId && editingJobId !== '';
    const endpoint = isEdit ? `/api/jobs/${editingJobId}` : '/api/jobs';
    const method = isEdit ? 'PUT' : 'POST';

    fetch(endpoint, {
        method: method,
        headers: { 'Content-Type': 'application/json', 'X-API-Key': 'default-key' },
        body: payload
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(isEdit ? '任务更新成功！' : '爬虫任务保存成功！');
            document.getElementById('crawl-form').reset();
            if (document.getElementById('editing-job-id')) document.getElementById('editing-job-id').value = '';
            const saveBtn = document.querySelector('#crawl-form button[type="submit"]');
            if (saveBtn) saveBtn.textContent = '保存任务';
            loadJobs();
        } else {
            alert((isEdit ? '更新任务失败: ' : '保存任务失败: ') + data.error);
        }
    })
    .catch(error => {
        console.error('Error saving job:', error);
        alert(isEdit ? '更新任务时发生错误' : '保存任务时发生错误');
    });
}

function startCrawl() {
    const jobId = document.getElementById('selected-job').value;
    if (!jobId) {
        alert('请选择一个任务');
        return;
    }
    
    // Make API call to start the crawl
    fetch(`/api/jobs/${jobId}/start`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'default-key'  // Fixed API key
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        // Check if response is OK
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            console.log('Starting crawl for job:', jobId);
            
            // Enable stop button and disable start button
            document.getElementById('start-crawl-btn').disabled = true;
            document.getElementById('stop-crawl-btn').disabled = false;
            
            // Start real crawl status updates
            updateCrawlStatus(jobId);
        } else {
            alert('启动任务失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error starting job:', error);
        alert('启动任务时发生错误: ' + error.message);
    });
}

function stopCrawl() {
    const jobId = document.getElementById('selected-job').value;
    if (!jobId) {
        alert('请选择一个任务');
        return;
    }
    
    // Make API call to stop the crawl
    fetch(`/api/jobs/${jobId}/stop`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'default-key'  // Fixed API key
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Stopping crawl for job:', jobId);
            
            // Enable start button and disable stop button
            document.getElementById('start-crawl-btn').disabled = false;
            document.getElementById('stop-crawl-btn').disabled = true;
            
            // Add stop message to status
            const statusDiv = document.getElementById('crawl-status');
            const timestamp = new Date().toLocaleTimeString();
            statusDiv.innerHTML += `<div>[${timestamp}] 爬取任务已停止</div>`;
            statusDiv.scrollTop = statusDiv.scrollHeight;
        } else {
            alert('停止任务失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error stopping job:', error);
        alert('停止任务时发生错误');
    });
}

function updateCrawlStatus(jobId) {
    const statusDiv = document.getElementById('crawl-status');
    statusDiv.innerHTML = ''; // Clear previous status
    
    // Add initial message
    const startTime = new Date().toLocaleTimeString();
    statusDiv.innerHTML += `<div>[${startTime}] 开始爬取任务...</div>`;
    statusDiv.scrollTop = statusDiv.scrollHeight;
    
    // Start polling for real status updates
    const interval = setInterval(() => {
        fetch(`/api/jobs/${jobId}`, {
            headers: {
                'X-API-Key': 'default-key'
            }
        })
        .then(response => response.json())
        .then(job => {
            // Update status display with real information
            const timestamp = new Date().toLocaleTimeString();
            
            // Check job status and update display accordingly
            if (job.status === 'running') {
                statusDiv.innerHTML += `<div>[${timestamp}] 任务正在运行中...</div>`;
            } else if (job.status === 'completed') {
                statusDiv.innerHTML += `<div>[${timestamp}] 爬取完成</div>`;
                clearInterval(interval);
                // Re-enable start button and disable stop button
                document.getElementById('start-crawl-btn').disabled = false;
                document.getElementById('stop-crawl-btn').disabled = true;
            } else if (job.status === 'failed') {
                statusDiv.innerHTML += `<div>[${timestamp}] 爬取失败</div>`;
                clearInterval(interval);
                // Re-enable start button and disable stop button
                document.getElementById('start-crawl-btn').disabled = false;
                document.getElementById('stop-crawl-btn').disabled = true;
            }
            
            statusDiv.scrollTop = statusDiv.scrollHeight;
        })
        .catch(error => {
            console.error('Error updating status:', error);
            // Stop polling on error
            clearInterval(interval);
        });
    }, 3000); // Poll every 3 seconds
}

function saveSettings(formId) {
    // In a real implementation, this would make an API call to save settings
    console.log('Saving settings for form:', formId);
    
    // Show success message
    alert('设置保存成功！');
}

function loadJobs() {
    const prevSelected = document.getElementById('selected-job') ? document.getElementById('selected-job').value : '';
    fetch('/api/jobs', { headers: { 'X-API-Key': 'default-key' }})
    .then(response => response.json())
    .then(jobs => {
        const jobsTable = document.getElementById('jobs-table');
        if (jobsTable) {
            if (jobs.length === 0) {
                jobsTable.innerHTML = '<tr><td colspan="5" class="text-center">暂无任务</td></tr>';
            } else {
                jobsTable.innerHTML = '';
                jobs.forEach(job => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${job.name}</td>
                        <td>${job.target_url}</td>
                        <td>${job.max_depth}</td>
                        <td>${job.status}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="deleteJob(${job.id})">删除</button>
                        </td>
                    `;
                    jobsTable.appendChild(row);
                });
            }
        }
        const selectedJobSelect = document.getElementById('selected-job');
        if (selectedJobSelect) {
            const old = selectedJobSelect.value;
            selectedJobSelect.innerHTML = '<option value="">请选择任务</option>';
            jobs.forEach(job => {
                const option = document.createElement('option');
                option.value = job.id; option.textContent = `${job.name} (${job.target_url})`;
                selectedJobSelect.appendChild(option);
            });
            // 恢复之前的选择
            if (prevSelected && jobs.some(j=>String(j.id) === String(prevSelected))) {
                selectedJobSelect.value = prevSelected;
                loadJobDetails(prevSelected);
            }
        }
    })
    .catch(error => { console.error('Error loading jobs:', error); });
}

function loadJobDetails(jobId) {
    // Make API call to get job details
    fetch(`/api/jobs/${jobId}`, {
        headers: {
            'X-API-Key': 'default-key'  // Fixed API key
        }
    })
    .then(response => response.json())
    .then(job => {
        // Update job details display
        document.getElementById('selected-job-url').textContent = job.target_url;
        document.getElementById('selected-job-depth').textContent = job.max_depth;
        
        // Parse custom rules if they exist
        if (job.custom_rules) {
            try {
                const customRules = typeof job.custom_rules === 'string' ? JSON.parse(job.custom_rules) : job.custom_rules;
                
                document.getElementById('selected-job-title-selector').textContent = customRules.title_selector || '未设置';
                document.getElementById('selected-job-content-selector').textContent = customRules.content_selector || '未设置';
                
                // Display custom fields
                const customFieldsDiv = document.getElementById('selected-job-custom-fields');
                if (customRules.custom_fields && Object.keys(customRules.custom_fields).length > 0) {
                    let customFieldsHtml = '<ul class="mb-0">';
                    for (const [field, selector] of Object.entries(customRules.custom_fields)) {
                        customFieldsHtml += `<li>${field}: ${selector}</li>`;
                    }
                    customFieldsHtml += '</ul>';
                    customFieldsDiv.innerHTML = customFieldsHtml;
                } else {
                    customFieldsDiv.innerHTML = '<span class="text-muted">无自定义字段</span>';
                }
            } catch (e) {
                console.error('Error parsing custom rules:', e);
                document.getElementById('selected-job-title-selector').textContent = '解析错误';
                document.getElementById('selected-job-content-selector').textContent = '解析错误';
                document.getElementById('selected-job-custom-fields').innerHTML = '<span class="text-danger">解析错误</span>';
            }
        } else {
            document.getElementById('selected-job-title-selector').textContent = '使用默认规则';
            document.getElementById('selected-job-content-selector').textContent = '使用默认规则';
            document.getElementById('selected-job-custom-fields').innerHTML = '<span class="text-muted">无自定义字段</span>';
        }
        
        // Show job details
        document.getElementById('selected-job-details').style.display = 'block';
    })
    .catch(error => {
        console.error('Error loading job details:', error);
    });
}

function editSelectedJob() {
    const jobId = document.getElementById('selected-job').value;
    if (!jobId) { alert('请选择一个任务'); return; }
    fetch(`/api/jobs/${jobId}`, { headers: { 'X-API-Key': 'default-key' }})
    .then(r=>r.json())
    .then(job=>{
        document.getElementById('name').value = job.name;
        document.getElementById('target-url').value = job.target_url;
        document.getElementById('depth').value = job.max_depth;
        if (job.custom_rules) {
            try {
                const customRules = typeof job.custom_rules === 'string' ? JSON.parse(job.custom_rules) : job.custom_rules;
                document.getElementById('title-selector').value = customRules.title_selector || '';
                document.getElementById('content-selector').value = customRules.content_selector || '';
                if (customRules.custom_fields && Object.keys(customRules.custom_fields).length > 0) {
                    let customFieldsText = '';
                    for (const [field, selector] of Object.entries(customRules.custom_fields)) {
                        customFieldsText += `${field}=${selector}\n`;
                    }
                    document.getElementById('custom-fields').value = customFieldsText.trim();
                } else {
                    document.getElementById('custom-fields').value = '';
                }
            } catch { document.getElementById('custom-fields').value = ''; }
        } else {
            document.getElementById('title-selector').value = '';
            document.getElementById('content-selector').value = '';
            document.getElementById('custom-fields').value = '';
        }
        if (!document.getElementById('editing-job-id')) {
            const hidden = document.createElement('input');
            hidden.type = 'hidden'; hidden.id = 'editing-job-id'; hidden.value = job.id;
            hidden.name = 'editing_job_id';
            document.getElementById('crawl-form').appendChild(hidden);
        } else {
            document.getElementById('editing-job-id').value = job.id;
        }
        const saveBtn = document.querySelector('#crawl-form button[type="submit"]');
        if (saveBtn) saveBtn.textContent = '更新任务';
        document.getElementById('crawl-form').scrollIntoView({ behavior: 'smooth' });
    })
    .catch(()=>alert('加载任务详情时发生错误'));
}

function deleteJob(jobId) {
    if (!confirm('确定要删除这个任务吗？')) {
        return;
    }
    
    // Make API call to delete the job
    fetch(`/api/jobs/${jobId}`, {
        method: 'DELETE',
        headers: {
            'X-API-Key': 'default-key'  // Fixed API key
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('任务删除成功！');
            // Reload jobs list
            loadJobs();
        } else {
            alert('删除任务失败');
        }
    })
    .catch(error => {
        console.error('Error deleting job:', error);
        alert('删除任务时发生错误');
    });
}

// ---- Results pagination & filtering ----
const resultsState = {
    page: 1,
    page_size: 10,
    job_id: '',
    run_id: '',
    q: ''
};

function readResultsFilters() {
    const jobFilter = document.getElementById('job-filter');
    const runFilter = document.getElementById('run-filter');
    const searchFilter = document.getElementById('search-filter');
    resultsState.job_id = jobFilter ? jobFilter.value : '';
    resultsState.run_id = runFilter ? runFilter.value : '';
    resultsState.q = searchFilter ? searchFilter.value.trim() : '';
}

function loadRuns() {
    const runFilter = document.getElementById('run-filter');
    if (!runFilter) return;
    const params = new URLSearchParams();
    if (resultsState.job_id) params.set('job_id', resultsState.job_id);
    fetch(`/api/runs?${params.toString()}`, { headers: { 'X-API-Key': 'default-key' }})
    .then(r=>r.json())
    .then(runs=>{
        const prev = runFilter.value;
        runFilter.innerHTML = '<option value="">所有批次</option>';
        runs.forEach(run=>{
            const opt = document.createElement('option');
            const label = `#${run.id} · ${run.status} · ${run.started_at ? run.started_at.replace('T',' ') : ''}`;
            opt.value = run.id; opt.textContent = label;
            runFilter.appendChild(opt);
        });
        if (prev && [...runFilter.options].some(o=>o.value === prev)) runFilter.value = prev;
    })
    .catch(()=>{ runFilter.innerHTML = '<option value="">所有批次</option>'; });
}

function loadResults() {
    const resultsTable = document.getElementById('results-table');
    if (!resultsTable) return;
    readResultsFilters();

    const params = new URLSearchParams();
    params.set('page', String(resultsState.page));
    params.set('page_size', String(resultsState.page_size));
    if (resultsState.job_id) params.set('job_id', resultsState.job_id);
    if (resultsState.run_id) params.set('run_id', resultsState.run_id);
    if (resultsState.q) params.set('q', resultsState.q);

    fetch(`/api/results?${params.toString()}`, { headers: { 'X-API-Key': 'default-key' }})
    .then(response => response.json())
    .then(payload => {
        renderResults(payload.items || []);
        renderResultsMeta(payload.total, payload.page, payload.page_size);
        renderResultsPagination(payload.total, payload.page, payload.page_size);
        bindSelectionControls();
        loadRuns();
    })
    .catch(error => {
        console.error('Error loading results:', error);
        resultsTable.innerHTML = '<tr><td colspan="7" class="text-center">加载结果失败</td></tr>';
        const pagination = document.getElementById('results-pagination');
        if (pagination) pagination.innerHTML = '';
        const meta = document.getElementById('results-meta');
        if (meta) meta.textContent = '';
    });
}

function renderResults(items) {
    const resultsTable = document.getElementById('results-table');
    resultsTable.innerHTML = '';
    if (!items || items.length === 0) {
        resultsTable.innerHTML = '<tr><td colspan="7" class="text-center">暂无结果</td></tr>';
        return;
    }

    items.forEach(result => {
        const row = document.createElement('tr');
        const previewData = JSON.stringify(result, null, 2);
        const singleJson = encodeURIComponent(previewData);
        row.innerHTML = `
            <td><input type="checkbox" class="row-check" data-id="${result.id}"></td>
            <td>任务${result.job_id}${result.run_id ? ` / 批次#${result.run_id}` : ''}</td>
            <td>${result.url}</td>
            <td>${result.title || '无标题'}</td>
            <td>${result.content ? result.content.substring(0, 50) + '...' : '无内容'}</td>
            <td>${result.scraped_at || ''}</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary" onclick='previewResult(${JSON.stringify(result).replace(/'/g, "&#39;")})'>预览</button>
                    <button class="btn btn-outline-secondary" onclick='copyResult(${JSON.stringify(result).replace(/'/g, "&#39;")})'>复制</button>
                    <a class="btn btn-outline-success" href="data:application/json;charset=utf-8,${singleJson}" download="result_${result.id || ''}.json">下载</a>
                    <button class="btn btn-outline-danger" onclick='deleteResult(${result.id})'>删除</button>
                </div>
            </td>
        `;
        resultsTable.appendChild(row);
    });
}

function resetAndAddListenerById(id, event, handler) {
    const el = document.getElementById(id);
    if (!el) return null;
    const clone = el.cloneNode(true);
    el.parentNode.replaceChild(clone, el);
    clone.addEventListener(event, handler);
    return clone;
}

function bindSelectionControls() {
    resetAndAddListenerById('select-all', 'change', () => {
        const selectAllCb = document.getElementById('select-all');
        document.querySelectorAll('#results-table .row-check').forEach(cb => { cb.checked = !!(selectAllCb && selectAllCb.checked); });
    });

    resetAndAddListenerById('btn-delete-selected', 'click', () => {
        const ids = [...document.querySelectorAll('#results-table .row-check:checked')].map(cb => parseInt(cb.getAttribute('data-id')));
        if (ids.length === 0) { alert('请选择要删除的记录'); return; }
        if (!confirm(`确定删除已选的 ${ids.length} 条记录吗？`)) return;
        document.querySelectorAll('#results-table .row-check:checked').forEach(cb => { const tr = cb.closest('tr'); if (tr) tr.parentNode.removeChild(tr); });
        fetch('/api/results/batch_delete', {
            method: 'POST', headers: { 'Content-Type': 'application/json', 'X-API-Key': 'default-key' }, body: JSON.stringify({ ids })
        }).then(r=>r.json()).then(res=>{ const selectAll = document.getElementById('select-all'); if (selectAll) selectAll.checked = false; loadResults(); })
        .catch(()=>{ alert('删除失败'); loadResults(); });
    });

    resetAndAddListenerById('btn-delete-run', 'click', () => {
        const runFilter = document.getElementById('run-filter');
        const runId = runFilter ? runFilter.value : '';
        if (!runId) { alert('请先选择批次'); return; }
        if (!confirm('确定删除当前批次的所有结果吗？')) return;
        fetch('/api/results/batch_delete', {
            method: 'POST', headers: { 'Content-Type': 'application/json', 'X-API-Key': 'default-key' }, body: JSON.stringify({ run_id: parseInt(runId) })
        }).then(r=>r.json()).then(res=>{ const selectAll = document.getElementById('select-all'); if (selectAll) selectAll.checked = false; loadRuns(); loadResults(); })
        .catch(()=>alert('删除失败'));
    });

    // 预览全部
    resetAndAddListenerById('btn-preview-run', 'click', () => {
        const runId = document.getElementById('run-filter')?.value || '';
        if (!runId) { alert('请先选择批次'); return; }
        const params = new URLSearchParams(); params.set('run_id', runId);
        fetch(`/api/results/export?format=json&${params.toString()}`, { headers: { 'X-API-Key': 'default-key' }})
        .then(r=>r.json()).then(list=>{ previewResult(list); }).catch(()=>alert('预览失败'));
    });

    // 下载全部
    resetAndAddListenerById('btn-download-run', 'click', () => {
        const runId = document.getElementById('run-filter')?.value || '';
        if (!runId) { alert('请先选择批次'); return; }
        const a = document.createElement('a');
        a.href = `/api/results/export?format=json&run_id=${encodeURIComponent(runId)}`;
        a.download = `run_${runId}.json`;
        a.target = '_blank';
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
    });
}

// 在筛选变更时加载批次
(function bindFilters(){
    const jobFilter = document.getElementById('job-filter');
    if (jobFilter) {
        jobFilter.addEventListener('change', ()=>{ resultsState.page = 1; loadRuns(); loadResults(); });
    }
    const runFilter = document.getElementById('run-filter');
    if (runFilter) {
        runFilter.addEventListener('change', ()=>{ resultsState.page = 1; loadResults(); });
    }
})();

function deleteResult(id) {
    if (!id) return;
    if (!confirm('确定删除该条结果吗？')) return;
    fetch(`/api/results/${id}`, {
        method: 'DELETE',
        headers: { 'X-API-Key': 'default-key' }
    }).then(r=>r.json()).then(data=>{
        const selectAll = document.getElementById('select-all');
        if (selectAll) selectAll.checked = false;
        if (data.success) {
            loadResults();
        } else {
            alert('删除失败');
        }
    }).catch(()=>alert('删除失败'));
}

function renderResultsMeta(total, page, page_size) {
    const meta = document.getElementById('results-meta');
    if (!meta) return;
    const start = total === 0 ? 0 : (page - 1) * page_size + 1;
    const end = Math.min(page * page_size, total);
    meta.textContent = `共 ${total} 条，显示第 ${start}-${end} 条`;
}

function renderResultsPagination(total, page, page_size) {
    const pagination = document.getElementById('results-pagination');
    if (!pagination) return;

    pagination.innerHTML = '';
    const totalPages = Math.max(1, Math.ceil(total / page_size));

    function createPageItem(label, targetPage, disabled = false, active = false) {
        const li = document.createElement('li');
        li.className = `page-item${disabled ? ' disabled' : ''}${active ? ' active' : ''}`;
        const a = document.createElement('a');
        a.className = 'page-link';
        a.href = '#';
        a.textContent = label;
        if (!disabled && !active) {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                resultsState.page = targetPage;
                loadResults();
            });
        }
        li.appendChild(a);
        return li;
    }

    // Prev
    pagination.appendChild(createPageItem('上一页', Math.max(1, page - 1), page === 1));

    // Page numbers (simple window)
    const windowSize = 5;
    const start = Math.max(1, page - Math.floor(windowSize / 2));
    const end = Math.min(totalPages, start + windowSize - 1);
    for (let p = start; p <= end; p++) {
        pagination.appendChild(createPageItem(String(p), p, false, p === page));
    }

    // Next
    pagination.appendChild(createPageItem('下一页', Math.min(totalPages, page + 1), page === totalPages));
}

function previewResult(obj) {
    try {
        const modalEl = document.getElementById('previewModal');
        const pre = document.getElementById('previewContent');
        pre.textContent = JSON.stringify(obj, null, 2);
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    } catch (e) {
        alert('无法预览该结果');
    }
}

function copyResult(obj) {
    const text = JSON.stringify(obj, null, 2);
    navigator.clipboard.writeText(text).then(()=>{
        alert('已复制到剪贴板');
    }).catch(()=>{
        // 兼容回退
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); alert('已复制到剪贴板'); } catch(e) { alert('复制失败'); }
        document.body.removeChild(ta);
    });
}

// augment status updates to refresh results and jobs list upon completion/stop
(function augmentStatusUI(){
    const originalUpdateCrawlStatus = window.updateCrawlStatus;
    window.updateCrawlStatus = function(jobId){
        const statusDiv = document.getElementById('crawl-status');
        const badge = document.createElement('span');
        badge.className = 'badge bg-secondary ms-2';
        badge.id = 'job-status-badge';
        // ensure exists
        if (statusDiv && !document.getElementById('job-status-badge')) {
            statusDiv.parentElement.parentElement.querySelector('.card-header h6')?.appendChild(badge);
        }
        function setBadge(text, cls){
            const b = document.getElementById('job-status-badge');
            if (!b) return;
            b.className = `badge ${cls} ms-2`;
            b.textContent = text;
        }
        const interval = setInterval(() => {
            fetch(`/api/jobs/${jobId}`, { headers: { 'X-API-Key': 'default-key' }})
            .then(r=>r.json())
            .then(job=>{
                if (job.status === 'running') setBadge('运行中', 'bg-info');
                if (job.status === 'completed' || job.status === 'finished') {
                    setBadge('已完成', 'bg-success');
                    clearInterval(interval);
                    // refresh results and jobs list
                    loadResults();
                    loadJobs();
                }
                if (job.status === 'failed') {
                    setBadge('失败', 'bg-danger');
                    clearInterval(interval);
                    loadJobs();
                }
                if (job.status === 'stopped') {
                    setBadge('已停止', 'bg-warning text-dark');
                    clearInterval(interval);
                    loadJobs();
                }
            })
            .catch(()=>{ clearInterval(interval); });
        }, 3000);
        // call original to keep existing behavior
        try { originalUpdateCrawlStatus(jobId); } catch(e) {}
    }
})();

function loadPresets() {
    const acc = document.getElementById('preset-accordion');
    const simpleList = document.getElementById('preset-list');
    const container = acc || simpleList;
    if (!container) return;
    fetch('/api/sites', { headers: { 'X-API-Key': 'default-key' }})
    .then(r=>r.json())
    .then(sites=>{
        // 分组：country + category
        const groups = {};
        sites.forEach(s=>{
            const key = `${s.country} | ${s.category}`;
            if (!groups[key]) groups[key] = [];
            groups[key].push(s);
        });
        if (acc) acc.innerHTML = '';
        Object.entries(groups).forEach(([key, items], idx)=>{
            if (acc) {
                const collapseId = `preset-collapse-${idx}`;
                const card = document.createElement('div');
                card.className = 'accordion-item';
                card.innerHTML = `
                    <h2 class="accordion-header" id="heading-${idx}">
                        <button class="accordion-button ${idx>0?'collapsed':''}" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}">
                            ${key}
                        </button>
                    </h2>
                    <div id="${collapseId}" class="accordion-collapse collapse ${idx===0?'show':''}" data-bs-parent="#preset-accordion">
                        <div class="accordion-body">
                            <div class="list-group" id="preset-group-${idx}"></div>
                        </div>
                    </div>`;
                acc.appendChild(card);
                const list = card.querySelector(`#preset-group-${idx}`);
                items.forEach(site=>{
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
                    const nameCn = site.name; // 已含中文名
                    btn.innerHTML = `<span><strong>${nameCn}</strong> <small class="text-muted">${site.url}</small></span>`;
                    btn.addEventListener('click', ()=>{
                        document.getElementById('name').value = nameCn;
                        document.getElementById('target-url').value = site.url;
                        if (site.selectors) {
                            document.getElementById('title-selector').value = site.selectors.title_selector || '';
                            document.getElementById('content-selector').value = site.selectors.content_selector || '';
                            if (site.selectors.custom_fields) {
                                const lines = Object.entries(site.selectors.custom_fields).map(([k,v])=>`${k}=${v}`);
                                document.getElementById('custom-fields').value = lines.join('\n');
                            } else {
                                document.getElementById('custom-fields').value = '';
                            }
                        } else {
                            document.getElementById('title-selector').value = '';
                            document.getElementById('content-selector').value = '';
                            document.getElementById('custom-fields').value = '';
                        }
                        if (document.getElementById('editing-job-id')) document.getElementById('editing-job-id').value = '';
                        const saveBtn = document.querySelector('#crawl-form button[type="submit"]');
                        if (saveBtn) saveBtn.textContent = '保存任务';
                        document.getElementById('crawl-form').scrollIntoView({ behavior: 'smooth' });
                    });
                    list.appendChild(btn);
                });
            } else if (simpleList) {
                simpleList.innerHTML = '';
                items.forEach(site=>{
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'list-group-item list-group-item-action';
                    btn.textContent = `${site.country} / ${site.category} · ${site.name}`;
                    btn.addEventListener('click', ()=>{
                        document.getElementById('name').value = site.name;
                        document.getElementById('target-url').value = site.url;
                    });
                    simpleList.appendChild(btn);
                });
            }
        });
    })
    .catch(()=>{
        if (acc) acc.innerHTML = '<div class="text-muted">预置站点加载失败</div>';
        if (simpleList) simpleList.innerHTML = '<div class="text-muted">预置站点加载失败</div>';
    });
}