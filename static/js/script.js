// JavaScript for AI K-line Reader

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const fileInput = document.getElementById('files');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // File input validation
    fileInput.addEventListener('change', function() {
        const files = this.files;
        let totalSize = 0;
        let invalidFiles = [];
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            
            // Check file size (16MB limit per file)
            const maxSize = 16 * 1024 * 1024; // 16MB in bytes
            if (file.size > maxSize) {
                invalidFiles.push(`${file.name} (超過 16MB)`);
                continue;
            }
            
            // Check file type
            const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                invalidFiles.push(`${file.name} (格式不支援)`);
                continue;
            }
            
            totalSize += file.size;
        }
        
        if (invalidFiles.length > 0) {
            alert('以下檔案有問題：\n' + invalidFiles.join('\n'));
            this.value = '';
            return;
        }
        
        // Show selected files count
        if (files.length > 0) {
            const fileNames = Array.from(files).map(f => f.name).join(', ');
            this.setAttribute('title', `已選擇 ${files.length} 個檔案：${fileNames}`);
        }
    });
    
    // Form submission with loading state
    form.addEventListener('submit', function(e) {
        const files = fileInput.files;
        if (!files || files.length === 0) {
            e.preventDefault();
            alert('請選擇至少一個檔案');
            return;
        }
        
        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>分析中...';
        
        // Add loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3">正在分析您的多張K線圖，請稍候...</p>
        `;
        
        form.parentNode.appendChild(loadingDiv);
        loadingDiv.style.display = 'block';
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
});

// File drag and drop functionality
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    const dropZone = fileInput.closest('.card-body');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        dropZone.classList.add('border-primary', 'bg-light');
    }
    
    function unhighlight(e) {
        dropZone.classList.remove('border-primary', 'bg-light');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);
        }
    }
});