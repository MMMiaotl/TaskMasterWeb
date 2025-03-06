/**
 * 海帮平台主JavaScript文件
 * 包含通用功能和初始化代码
 */

// 文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    initTooltips();
    
    // 初始化搜索建议
    initSearchSuggestions();
    
    // 初始化表单验证
    initFormValidation();
});

/**
 * 初始化Bootstrap工具提示
 */
function initTooltips() {
    // 查找所有带有data-bs-toggle="tooltip"属性的元素
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0 && typeof bootstrap !== 'undefined') {
        // 初始化所有工具提示
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
}

/**
 * 初始化搜索建议功能
 */
function initSearchSuggestions() {
    const searchInput = document.getElementById('searchInput');
    const searchSuggestions = document.getElementById('searchSuggestions');
    
    if (!searchInput || !searchSuggestions) return;
    
    const suggestionsList = searchSuggestions.querySelector('.list-group');
    
    // 检查suggestionsList是否存在
    if (!suggestionsList) {
        console.log('警告: 在搜索建议容器中未找到列表组元素 (class: list-group)');
        return;
    }
    
    let typingTimer;

    // 监听输入事件
    searchInput.addEventListener('input', function() {
        clearTimeout(typingTimer);
        if (searchInput.value) {
            typingTimer = setTimeout(fetchSuggestions, 300);
        } else {
            searchSuggestions.classList.add('d-none');
        }
    });

    // 获取搜索建议
    function fetchSuggestions() {
        const query = searchInput.value.trim();
        if (!query) return;

        fetch(`/task/search/suggestions?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(suggestions => {
                suggestionsList.innerHTML = '';
                if (suggestions.length > 0) {
                    suggestions.forEach(suggestion => {
                        const item = document.createElement('a');
                        item.href = `/task/create_task?category=${encodeURIComponent(suggestion.title)}`;
                        item.className = 'list-group-item list-group-item-action';
                        item.innerHTML = `
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <div class="fw-bold">${suggestion.title}</div>
                                    <small class="text-muted">${suggestion.description}</small>
                                </div>
                            </div>
                        `;
                        suggestionsList.appendChild(item);
                    });
                    searchSuggestions.classList.remove('d-none');
                } else {
                    searchSuggestions.classList.add('d-none');
                }
            })
            .catch(error => {
                console.error('Error fetching suggestions:', error);
                searchSuggestions.classList.add('d-none');
            });
    }

    // 点击其他地方时隐藏建议
    document.addEventListener('click', function(e) {
        if (!searchSuggestions.contains(e.target) && e.target !== searchInput) {
            searchSuggestions.classList.add('d-none');
        }
    });

    // 监听搜索框获得焦点
    searchInput.addEventListener('focus', function() {
        if (searchInput.value) {
            searchSuggestions.classList.remove('d-none');
        }
    });
}

/**
 * 初始化表单验证
 */
function initFormValidation() {
    // 获取所有需要验证的表单
    const forms = document.querySelectorAll('.needs-validation');
    
    if (forms.length === 0) return;
    
    // 遍历表单并添加验证
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
} 