// JavaScript for AI K-line Reader - Single File Upload

document.addEventListener('DOMContentLoaded', function() {
    const singleFileInput = document.getElementById('singleFile');
    const addFileBtn = document.getElementById('addFileBtn');
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const selectedFilesList = document.getElementById('selectedFilesList');
    const filesContainer = document.getElementById('filesContainer');
    
    // Array to store selected files
    let selectedFiles = [];
    
    // File validation function
    function validateFile(file) {
        const maxSize = 16 * 1024 * 1024; // 16MB in bytes
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
        
        if (file.size > maxSize) {
            return `檔案 ${file.name} 超過 16MB 限制`;
        }
        
        if (!allowedTypes.includes(file.type)) {
            return `檔案 ${file.name} 格式不支援`;
        }
        
        // Check if file already exists
        if (selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
            return `檔案 ${file.name} 已經選擇過了`;
        }
        
        return null;
    }
    
    // Add file to selected list
    function addFileToList(file) {
        selectedFiles.push(file);
        updateSelectedFilesDisplay();
        updateSubmitButton();
    }
    
    // Remove file from selected list
    function removeFileFromList(index) {
        selectedFiles.splice(index, 1);
        updateSelectedFilesDisplay();
        updateSubmitButton();
    }
    
    // Update the display of selected files
    function updateSelectedFilesDisplay() {
        if (selectedFiles.length === 0) {
            selectedFilesList.style.display = 'none';
            return;
        }
        
        selectedFilesList.style.display = 'block';
        filesContainer.innerHTML = '';
        
        selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'd-flex justify-content-between align-items-center py-2 border-bottom';
            fileItem.innerHTML = `
                <div>
                    <i class="bi bi-file-earmark-image text-primary me-2"></i>
                    <span class="fw-medium">${file.name}</span>
                    <small class="text-muted ms-2">(${(file.size / 1024 / 1024).toFixed(2)} MB)</small>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile(${index})">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            filesContainer.appendChild(fileItem);
        });
    }
    
    // Update submit button state
    function updateSubmitButton() {
        submitBtn.disabled = selectedFiles.length === 0;
        if (selectedFiles.length > 0) {
            submitBtn.innerHTML = `<i class="bi bi-upload"></i> 分析 ${selectedFiles.length} 個檔案`;
        } else {
            submitBtn.innerHTML = '<i class="bi bi-upload"></i> 分析所有檔案';
        }
    }
    
    // Make removeFile function global so it can be called from HTML
    window.removeFile = function(index) {
        removeFileFromList(index);
    };
    
    // Add file button click handler
    addFileBtn.addEventListener('click', function() {
        const file = singleFileInput.files[0];
        if (!file) {
            alert('請先選擇一個檔案');
            return;
        }
        
        const error = validateFile(file);
        if (error) {
            alert(error);
            singleFileInput.value = '';
            return;
        }
        
        addFileToList(file);
        singleFileInput.value = ''; // Clear the input for next file
    });
    
    // Also allow adding file by pressing Enter or changing the input
    singleFileInput.addEventListener('change', function() {
        if (this.files[0]) {
            addFileBtn.click();
        }
    });
    
    // Form submission with loading state
    uploadForm.addEventListener('submit', function(e) {
        if (selectedFiles.length === 0) {
            e.preventDefault();
            alert('請至少選擇一個檔案');
            return;
        }
        
        // Add all selected files to the form as hidden file inputs
        selectedFiles.forEach((file, index) => {
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.name = 'files';
            fileInput.style.display = 'none';
            
            // Create a DataTransfer object to set the file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            uploadForm.appendChild(fileInput);
        });
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>分析中...';
        
        // Add loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading text-center my-4';
        loadingDiv.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">正在分析您的 ${selectedFiles.length} 張K線圖，請稍候...</p>
        `;
        
        uploadForm.parentNode.appendChild(loadingDiv);
        
        // Let the form submit normally to Flask
        // Flask will handle the files and return the rendered page with results
    });
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Smooth scroll to results
    const analysisResult = document.querySelector('.card .bg-success');
    if (analysisResult) {
        setTimeout(function() {
            analysisResult.closest('.card').scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }, 100);
    }
    
    // Initialize UI
    updateSubmitButton();
});