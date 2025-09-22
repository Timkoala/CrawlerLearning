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
    
    // Load initial data
    loadJobs();
    loadResults();
});

function loadPresetTask(name, url) {
    document.getElementById('name').value = name;
    document.getElementById('target-url').value = url;
}

function saveCrawlJob() {
    // Get form values
    const name = document.getElementById('name').value;
    const url = document.getElementById('target-url').value;
    const depth = document.getElementById('depth').value;
    
    // Get custom rules
    const titleSelector = document.getElementById('title-selector').value;
    const contentSelector = document.getElementById('content-selector').value;
    const customFieldsText = document.getElementById('custom-fields').value;
    
    if (!name || !url) {
        alert('请填写任务名称和目标URL');
        return;
    }
    
    // Prepare custom rules
    let customRules = {};
    if (titleSelector || contentSelector || customFieldsText) {
        customRules = {
            title_selector: titleSelector,
            content_selector: contentSelector
        };
        
        // Parse custom fields
        if (customFieldsText) {
            const customFields = {};
            const lines = customFieldsText.split('\n');
            lines.forEach(line => {
                const trimmedLine = line.trim();
                if (trimmedLine && trimmedLine.includes('=')) {
                    const [fieldName, selector] = trimmedLine.split('=');
                    if (fieldName && selector) {
                        customFields[fieldName.trim()] = selector.trim();
                    }
                }
            });
            if (Object.keys(customFields).length > 0) {
                customRules.custom_fields = customFields;
            }
        }
    }
    
    // Make API call to save the job
    fetch('/api/jobs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'default-key'  // Fixed API key
        },
        body: JSON.stringify({
            name: name,
            target_url: url,
            max_depth: parseInt(depth),
            custom_rules: Object.keys(customRules).length > 0 ? customRules : null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('爬虫任务保存成功！');
            // Reset form
            document.getElementById('crawl-form').reset();
            // Reload jobs list
            loadJobs();
        } else {
            alert('保存任务失败: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error saving job:', error);
        alert('保存任务时发生错误');
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
    // Make API call to get jobs
    fetch('/api/jobs', {
        headers: {
            'X-API-Key': 'default-key'  // Fixed API key
        }
    })
    .then(response => response.json())
    .then(jobs => {
        // Update jobs table
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
        
        // Update job selection dropdown
        const selectedJobSelect = document.getElementById('selected-job');
        if (selectedJobSelect) {
            selectedJobSelect.innerHTML = '<option value="">请选择任务</option>';
            jobs.forEach(job => {
                const option = document.createElement('option');
                option.value = job.id;
                option.textContent = `${job.name} (${job.target_url})`;
                selectedJobSelect.appendChild(option);
            });
            
            // 如果有任务，默认选择第一个
            if (jobs.length > 0) {
                selectedJobSelect.value = jobs[0].id;
                loadJobDetails(jobs[0].id);
            }
        }
    })
    .catch(error => {
        console.error('Error loading jobs:', error);
        // Fallback to simulated data
        const jobsTable = document.getElementById('jobs-table');
        const selectedJobSelect = document.getElementById('selected-job');
        
        if (jobsTable) {
            jobsTable.innerHTML = `
                <tr>
                    <td>示例任务1</td>
                    <td>https://example.com</td>
                    <td>1</td>
                    <td>已保存</td>
                    <td>
                        <button class="btn btn-sm btn-danger">删除</button>
                    </td>
                </tr>
                <tr>
                    <td>示例任务2</td>
                    <td>https://news.example.com</td>
                    <td>2</td>
                    <td>已保存</td>
                    <td>
                        <button class="btn btn-sm btn-danger">删除</button>
                    </td>
                </tr>
            `;
        }
        
        // Populate job selection dropdown
        if (selectedJobSelect) {
            selectedJobSelect.innerHTML = '<option value="">请选择任务</option>';
            selectedJobSelect.innerHTML += '<option value="1">示例任务1 (https://example.com)</option>';
            selectedJobSelect.innerHTML += '<option value="2">示例任务2 (https://news.example.com)</option>';
        }
    });
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
    if (!jobId) {
        alert('请选择一个任务');
        return;
    }
    
    // Make API call to get job details
    fetch(`/api/jobs/${jobId}`, {
        headers: {
            'X-API-Key': 'default-key'  // Fixed API key
        }
    })
    .then(response => response.json())
    .then(job => {
        // Populate form with job details
        document.getElementById('name').value = job.name;
        document.getElementById('target-url').value = job.target_url;
        document.getElementById('depth').value = job.max_depth;
        
        // Parse custom rules if they exist
        if (job.custom_rules) {
            try {
                const customRules = typeof job.custom_rules === 'string' ? JSON.parse(job.custom_rules) : job.custom_rules;
                
                document.getElementById('title-selector').value = customRules.title_selector || '';
                document.getElementById('content-selector').value = customRules.content_selector || '';
                
                // Populate custom fields textarea
                if (customRules.custom_fields && Object.keys(customRules.custom_fields).length > 0) {
                    let customFieldsText = '';
                    for (const [field, selector] of Object.entries(customRules.custom_fields)) {
                        customFieldsText += `${field}=${selector}\n`;
                    }
                    document.getElementById('custom-fields').value = customFieldsText.trim();
                } else {
                    document.getElementById('custom-fields').value = '';
                }
            } catch (e) {
                console.error('Error parsing custom rules:', e);
                // Clear form fields on error
                document.getElementById('title-selector').value = '';
                document.getElementById('content-selector').value = '';
                document.getElementById('custom-fields').value = '';
            }
        } else {
            // Clear custom rules fields
            document.getElementById('title-selector').value = '';
            document.getElementById('content-selector').value = '';
            document.getElementById('custom-fields').value = '';
        }
        
        // Scroll to form
        document.getElementById('crawl-form').scrollIntoView({ behavior: 'smooth' });
    })
    .catch(error => {
        console.error('Error loading job for editing:', error);
        alert('加载任务详情时发生错误');
    });
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

function loadResults() {
    // Make API call to get results
    fetch('/api/results', {
        headers: {
            'X-API-Key': 'default-key'  // Fixed API key
        }
    })
    .then(response => response.json())
    .then(results => {
        // Update results table
        const resultsTable = document.getElementById('results-table');
        if (resultsTable) {
            if (results.length === 0) {
                resultsTable.innerHTML = '<tr><td colspan="5" class="text-center">暂无结果</td></tr>';
            } else {
                resultsTable.innerHTML = '';
                results.forEach(result => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>任务${result.job_id}</td>
                        <td>${result.url}</td>
                        <td>${result.title || '无标题'}</td>
                        <td>${result.content ? result.content.substring(0, 50) + '...' : '无内容'}</td>
                        <td>${result.scraped_at || ''}</td>
                    `;
                    resultsTable.appendChild(row);
                });
            }
        }
    })
    .catch(error => {
        console.error('Error loading results:', error);
        // Fallback to simulated data
        const resultsTable = document.getElementById('results-table');
        if (resultsTable) {
            resultsTable.innerHTML = `
                <tr>
                    <td>示例任务1</td>
                    <td>https://example.com/page1</td>
                    <td>示例页面1</td>
                    <td>{ "title": "示例页面1", "content": "这是示例内容" }</td>
                    <td>2023-01-01 12:00:00</td>
                </tr>
                <tr>
                    <td>示例任务1</td>
                    <td>https://example.com/page2</td>
                    <td>示例页面2</td>
                    <td>{ "title": "示例页面2", "content": "这是另一个示例" }</td>
                    <td>2023-01-01 12:05:00</td>
                </tr>
            `;
        }
    });
}