// Paper Formatter Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    });
    // Dynamic form field updates for paper patterns
    const patternForm = document.getElementById('paper-pattern-form');
    if (patternForm) {
        const totalMarksInput = patternForm.querySelector('#id_total_marks');
        const sectionInputs = patternForm.querySelectorAll('input[name*="count"], input[name*="marks"]');
        
        function validateMarks() {
            let calculatedTotal = 0;
            
            // Calculate section A
            const sectionACount = parseInt(patternForm.querySelector('#id_section_a_count').value) || 0;
            const sectionAMarks = parseInt(patternForm.querySelector('#id_section_a_marks').value) || 0;
            calculatedTotal += sectionACount * sectionAMarks;
            
            // Calculate section B
            const sectionBCount = parseInt(patternForm.querySelector('#id_section_b_count').value) || 0;
            const sectionBMarks = parseInt(patternForm.querySelector('#id_section_b_marks').value) || 0;
            calculatedTotal += sectionBCount * sectionBMarks;
            
            // Calculate section C
            const sectionCCount = parseInt(patternForm.querySelector('#id_section_c_count').value) || 0;
            const sectionCMarks = parseInt(patternForm.querySelector('#id_section_c_marks').value) || 0;
            calculatedTotal += sectionCCount * sectionCMarks;
            
            const totalMarks = parseInt(totalMarksInput.value) || 0;
            
            if (calculatedTotal !== totalMarks) {
                totalMarksInput.classList.add('is-invalid');
                totalMarksInput.nextElementSibling.textContent = 
                    `Calculated total (${calculatedTotal}) doesn't match entered total (${totalMarks})`;
            } else {
                totalMarksInput.classList.remove('is-invalid');
            }
        }
        
        sectionInputs.forEach(input => {
            input.addEventListener('change', validateMarks);
        });
        totalMarksInput.addEventListener('change', validateMarks);
    }
    // Auto-calculate percentages for difficulty distribution
    const percentageInputs = document.querySelectorAll('input[name*="percentage"]');
    if (percentageInputs.length === 4) {
        percentageInputs.forEach(input => {
            input.addEventListener('change', function() {
                const inputs = Array.from(percentageInputs);
                const total = inputs.reduce((sum, inp) => sum + (parseInt(inp.value) || 0), 0);
                
                if (total !== 100) {
                    inputs.forEach(inp => {
                        inp.classList.add('is-invalid');
                    });
                } else {
                    inputs.forEach(inp => {
                        inp.classList.remove('is-invalid');
                    });
                }
            });
        });
    }
    // File upload preview for Excel files
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = this.files[0]?.name;
            if (fileName) {
                const label = this.nextElementSibling;
                if (label && label.classList.contains('custom-file-label')) {
                    label.textContent = fileName;
                }
            }
        });
    }
    // Search and filter functionality
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const filter = this.value.toLowerCase();
            const rows = document.querySelectorAll('table tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }
});
// Utility functions
function showLoading() {
    const loadingElem = document.createElement('div');
    loadingElem.className = 'loading-overlay';
    loadingElem.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(loadingElem);
}
function hideLoading() {
    const loadingElem = document.querySelector('.loading-overlay');
    if (loadingElem) {
        loadingElem.remove();
    }
}
// API helper functions
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}