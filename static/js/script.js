// JavaScript for AI K-line Reader

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const fileInput = document.getElementById('file');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // File input validation
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            // Check file size (16MB limit)
            const maxSize = 16 * 1024 * 1024; // 16MB in bytes
            if (file.size > maxSize) {
                alert('檔案大小不能超過 16MB');
                this.value = '';
                return;
            }
            
            // Check file type
            const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                alert('請選擇有效的圖片檔案');
                this.value = '';
                return;
            }
            
            // Preview file name
            const fileName = file.name;
            if (fileName.length > 30) {
                this.setAttribute('title', fileName);
            }
        }
    });
    
    // Form submission with loading state
    form.addEventListener('submit', function(e) {
        const file = fileInput.files[0];
        if (!file) {
            e.preventDefault();
            alert('請選擇一個檔案');
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
            <p class="mt-3">正在分析您的K線圖，請稍候...</p>
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