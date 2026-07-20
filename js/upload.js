// Upload logic with SheetJS integration

let uploadedData = null;
let uploadedHeaders = [];

async function initUpload() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const downloadTemplate = document.getElementById('downloadTemplate');
    
    if (!dropZone) return;
    
    // Drag and drop events
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });
    
    removeFileBtn.addEventListener('click', () => {
        uploadedData = null;
        uploadedHeaders = [];
        filePreview.classList.add('hidden');
        fileInput.value = '';
        uploadBtn.disabled = true;
        document.getElementById('uploadResult').classList.add('hidden');
    });
    
    uploadBtn.addEventListener('click', uploadData);
    
    // Download template
    downloadTemplate.addEventListener('click', (e) => {
        e.preventDefault();
        downloadTemplateFile();
    });
}

function handleFile(file) {
    const validTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'text/csv'
    ];
    
    if (!validTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls|csv)$/)) {
        showToast('Please upload an Excel or CSV file', 'error');
        return;
    }
    
    const reader = new FileReader();
    
    reader.onload = (e) => {
        try {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array' });
            const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
            const jsonData = XLSX.utils.sheet_to_json(firstSheet, { defval: '' });
            
            if (jsonData.length === 0) {
                showToast('The file appears to be empty', 'error');
                return;
            }
            
            // Extract headers
            uploadedHeaders = Object.keys(jsonData[0]);
            
            // Validate required columns
            const requiredColumns = ['admission_no', 'full_name', 'gender', 'boarding_status'];
            const missingColumns = requiredColumns.filter(col => !uploadedHeaders.includes(col));
            
            if (missingColumns.length > 0) {
                showToast(`Missing required columns: ${missingColumns.join(', ')}`, 'error');
                return;
            }
            
            uploadedData = jsonData;
            
            // Show preview
            showFilePreview(file, jsonData);
            
            showToast(`Loaded ${jsonData.length} rows from ${file.name}`, 'success');
        } catch (error) {
            console.error('File parsing error:', error);
            showToast('Error parsing file. Please ensure it\'s a valid Excel or CSV file.', 'error');
        }
    };
    
    reader.readAsArrayBuffer(file);
}

function showFilePreview(file, data) {
    const filePreview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const rowCount = document.getElementById('rowCount');
    const previewHeader = document.getElementById('previewHeader');
    const previewBody = document.getElementById('previewBody');
    const uploadBtn = document.getElementById('uploadBtn');
    
    fileName.textContent = file.name;
    fileSize.textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;
    rowCount.textContent = `${data.length} rows`;
    
    // Preview table header
    const headers = Object.keys(data[0]);
    previewHeader.innerHTML = headers.map(h => `
        <th class="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
            ${h}
        </th>
    `).join('');
    
    // Preview table body (first 5 rows)
    const previewData = data.slice(0, 5);
    previewBody.innerHTML = previewData.map(row => `
        <tr class="hover:bg-slate-50">
            ${headers.map(h => `
                <td class="px-6 py-3 text-sm text-slate-600 whitespace-nowrap">${row[h] || '-'}</td>
            `).join('')}
        </tr>
    `).join('');
    
    // Show if more rows
    if (data.length > 5) {
        previewBody.innerHTML += `
            <tr>
                <td colspan="${headers.length}" class="px-6 py-3 text-sm text-slate-400 text-center">
                    <i class="fas fa-ellipsis-h mr-2"></i>
                    ${data.length - 5} more rows
                </td>
            </tr>
        `;
    }
    
    filePreview.classList.remove('hidden');
    uploadBtn.disabled = false;
}

async function uploadData() {
    if (!uploadedData || uploadedData.length === 0) {
        showToast('No data to upload', 'error');
        return;
    }
    
    const uploadBtn = document.getElementById('uploadBtn');
    const progress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const result = document.getElementById('uploadResult');
    
    // Show progress
    uploadBtn.disabled = true;
    progress.classList.remove('hidden');
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    result.classList.add('hidden');
    
    try {
        // Simulate progress for UX
        let progressValue = 0;
        const progressInterval = setInterval(() => {
            progressValue += Math.random() * 10;
            if (progressValue > 90) progressValue = 90;
            progressBar.style.width = `${Math.min(progressValue, 90)}%`;
            progressText.textContent = `${Math.min(Math.round(progressValue), 90)}%`;
        }, 200);
        
        // Prepare data for upload
        const rows = uploadedData.map(row => [
            row.admission_no || '',
            row.full_name || '',
            row.gender || '',
            row.boarding_status || '',
            parseFloat(row.exam1) || null,
            parseFloat(row.exam2) || null,
            parseFloat(row.exam3) || null
        ]);
        
        // Send to backend
        const response = await API.post('/upload', { data: rows });
        
        clearInterval(progressInterval);
        
        // Complete progress
        progressBar.style.width = '100%';
        progressText.textContent = '100%';
        
        // Show result
        if (response.success) {
            result.className = 'mt-6 p-4 bg-green-50 border border-green-200 rounded-lg';
            result.innerHTML = `
                <div class="flex items-start">
                    <i class="fas fa-check-circle text-green-600 mt-1 mr-3"></i>
                    <div>
                        <h4 class="font-semibold text-green-800">Upload Successful!</h4>
                        <p class="text-sm text-green-700">
                            ${response.message || `${response.insertedCount || 0} students uploaded successfully`}
                        </p>
                        ${response.data ? `
                            <div class="mt-2 text-xs text-green-600">
                                <a href="/students.html" class="underline hover:text-green-800">View students</a>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            showToast('Upload completed successfully!', 'success');
            
            // Reset after success
            setTimeout(() => {
                document.getElementById('filePreview').classList.add('hidden');
                document.getElementById('fileInput').value = '';
                uploadedData = null;
                uploadBtn.disabled = true;
                progress.classList.add('hidden');
            }, 3000);
        } else {
            throw new Error(response.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        
        result.className = 'mt-6 p-4 bg-red-50 border border-red-200 rounded-lg';
        let errorMessage = 'Upload failed. Please check your data and try again.';
        
        if (error.data && error.data.errors) {
            // Show detailed validation errors
            const errors = error.data.errors;
            errorMessage = `
                <div>
                    <p class="font-semibold text-red-800">${error.data.error || 'Validation failed'}</p>
                    <ul class="mt-2 space-y-1 text-sm text-red-700 max-h-40 overflow-y-auto">
                        ${errors.map(e => `
                            <li class="flex items-start">
                                <i class="fas fa-times-circle text-red-500 mt-1 mr-2"></i>
                                <span>Row ${e.row}: ${e.message}</span>
                            </li>
                        `).join('')}
                    </ul>
                    ${error.data.errorCount ? `
                        <p class="mt-2 text-xs text-red-600">
                            ${error.data.errorCount} error(s) found in ${error.data.totalRows || 0} rows
                        </p>
                    ` : ''}
                </div>
            `;
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        result.innerHTML = `
            <div class="flex items-start">
                <i class="fas fa-exclamation-circle text-red-600 mt-1 mr-3"></i>
                <div>${errorMessage}</div>
            </div>
        `;
        
        showToast('Upload failed', 'error');
        progress.classList.add('hidden');
        uploadBtn.disabled = false;
    }
}

function downloadTemplateFile() {
    const headers = ['admission_no', 'full_name', 'gender', 'boarding_status', 'exam1', 'exam2', 'exam3'];
    const sampleData = [
        ['NHS001-2024-001', 'John Doe', 'Male', 'Boarder', '85.5', '78.0', '92.5'],
        ['NHS001-2024-002', 'Jane Smith', 'Female', 'Day', '90.0', '88.5', '91.0'],
        ['NHS001-2024-003', 'Bob Johnson', 'Male', 'Boarder', '75.0', '82.0', '79.5']
    ];
    
    const wsData = [headers, ...sampleData];
    const ws = XLSX.utils.aoa_to_sheet(wsData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Students');
    
    XLSX.writeFile(wb, 'student_template.xlsx');
    showToast('Template downloaded!', 'success');
}

// Make initUpload globally accessible
window.initUpload = initUpload;
