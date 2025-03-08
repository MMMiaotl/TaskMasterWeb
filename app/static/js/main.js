/**
 * 海帮平台主JavaScript文件
 * 包含通用功能和初始化代码
 */

// 文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM完全加载，准备初始化功能");
    
    // 初始化工具提示
    initTooltips();
    
    // 初始化简单搜索建议
    initSimpleSearch();
    
    // 初始化表单验证
    initFormValidation();
    
    console.log("DOM加载完成，简单搜索功能已启用");
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
 * 初始化简单搜索功能
 * 无自动补全，无建议列表
 */
function initSimpleSearch() {
    console.log("初始化简单搜索功能");
    
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    
    if (!searchInput || !searchForm) {
        console.error("找不到搜索输入框或表单");
        return;
    }
    
    console.log("找到搜索输入框和表单，准备初始化");
    
    // 创建新的搜索建议容器
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.id = 'simpleSuggestions';
    suggestionsContainer.className = 'simple-suggestions';
    suggestionsContainer.style.display = 'none';
    
    // 插入到搜索框后面
    searchInput.parentNode.appendChild(suggestionsContainer);
    
    // 从data-prefix属性获取前缀，但现在前缀已由HTML显示
    const prefixText = "我需要";
    let typingTimer;
    
    // 监听输入事件
    searchInput.addEventListener('input', function(e) {
        const searchTerm = searchInput.value.trim();
        console.log("搜索输入:", searchTerm);
        
        // 清除之前的定时器
        clearTimeout(typingTimer);
        
        // 如果搜索词为空，隐藏建议
        if (!searchTerm) {
            suggestionsContainer.style.display = 'none';
            return;
        }
        
        // 设置延迟获取建议
        typingTimer = setTimeout(function() {
            fetchSimpleSuggestions(searchTerm, suggestionsContainer);
        }, 300);
    });
    
    // 点击其他地方时隐藏建议
    document.addEventListener('click', function(e) {
        if (e.target !== searchInput && e.target !== suggestionsContainer && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
        }
    });
    
    // 监听表单提交
    searchForm.addEventListener('submit', function(e) {
        const searchTerm = searchInput.value.trim();
        
        // 如果用户没有输入任何内容，阻止提交
        if (!searchTerm) {
            e.preventDefault();
            return;
        }
        
        console.log("搜索表单已提交，搜索词:", searchTerm);
        
        // 隐藏建议
        suggestionsContainer.style.display = 'none';
        
        // 正常提交表单
    });
    
    console.log("简单搜索功能初始化完成");
}

/**
 * 获取简单搜索建议
 */
function fetchSimpleSuggestions(query, container) {
    console.log("获取搜索建议:", query);
    
    // 清空容器
    container.innerHTML = '';
    
    fetch(`/search/suggestions?q=${encodeURIComponent(query)}`)
        .then(response => {
            console.log("收到响应状态:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("收到搜索建议数据:", data);
            
            // 如果没有建议，隐藏容器
            if (!data || data.length === 0) {
                container.style.display = 'none';
                return;
            }
            
            // 创建建议列表
            const ul = document.createElement('ul');
            
            // 添加每个建议
            data.forEach(suggestion => {
                console.log("处理建议:", suggestion);
                
                if (!suggestion.title) {
                    console.warn("建议项缺少title属性:", suggestion);
                    return;
                }
                
                const li = document.createElement('li');
                li.textContent = suggestion.title; // 只使用文本内容，避免HTML注入
                
                // 添加点击事件
                li.addEventListener('click', function() {
                    console.log("选择建议:", suggestion.title);
                    const searchInput = document.getElementById('searchInput');
                    searchInput.value = suggestion.title;
                    searchInput.focus();
                    container.style.display = 'none';
                });
                
                ul.appendChild(li);
            });
            
            // 添加到容器
            container.appendChild(ul);
            container.style.display = 'block';
        })
        .catch(error => {
            console.error("获取搜索建议出错:", error);
            container.style.display = 'none';
        });
}

/**
 * 搜索建议功能 - 已禁用
 * 保留代码仅供参考
 */
function initSearchSuggestions() {
    console.log("搜索建议功能已禁用");
    return;
    
    // 以下代码不会执行
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
    let currentQuery = '';
    let suggestions = [];

    // 监听输入事件
    searchInput.addEventListener('input', function() {
        clearTimeout(typingTimer);
        currentQuery = searchInput.value.trim();
        
        if (currentQuery) {
            typingTimer = setTimeout(fetchSuggestions, 300);
        } else {
            searchSuggestions.classList.add('d-none');
        }
    });

    // 获取搜索建议
    function fetchSuggestions() {
        if (!currentQuery) return;

        fetch(`/search/suggestions?q=${encodeURIComponent(currentQuery)}`)
            .then(response => response.json())
            .then(data => {
                console.log("收到搜索建议数据:", data);
                suggestions = data;
                suggestionsList.innerHTML = '';
                
                if (suggestions.length > 0) {
                    // 只显示文字推荐，不显示任务子类
                    suggestions.forEach(suggestion => {
                        console.log("处理建议项:", suggestion);
                        // 创建div而不是a元素，避免点击跳转
                        const item = document.createElement('div');
                        item.className = 'list-group-item list-group-item-action';
                        // 简化HTML结构，只显示标题
                        item.innerHTML = `${suggestion.title}`;
                        
                        // 添加点击事件，点击时填充搜索框
                        item.addEventListener('click', function() {
                            searchInput.value = suggestion.title;
                            searchSuggestions.classList.add('d-none');
                            // 可选：聚焦到搜索框
                            searchInput.focus();
                        });
                        
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
        if (currentQuery && suggestions.length > 0) {
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