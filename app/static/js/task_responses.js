// 存储任务和用户相关信息
let taskId, currentUserId, csrfToken;

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    // 从页面元数据中获取必要的数据
    taskId = document.querySelector('meta[name="task-id"]').getAttribute('content');
    currentUserId = document.querySelector('meta[name="current-user-id"]').getAttribute('content');
    csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // 初始化事件监听器
    initializeEventListeners();
    
    // 设置专业人士列表项点击事件
    document.querySelectorAll('.pro-item').forEach(item => {
        item.addEventListener('click', function() {
            try {
                const proId = this.getAttribute('data-pro-id');
                const tabType = this.getAttribute('data-tab-id');
                logDebug('点击专业人士项', {proId, tabType});
                
                if (!proId || !tabType) {
                    logError('专业人士项缺少必要属性', {
                        element: this.outerHTML,
                        proId: proId,
                        tabType: tabType
                    });
                    return;
                }
                
                // 获取必要的DOM元素
                const chatAreaContainer = document.getElementById('chat-area-container');
                const proDetailsArea = document.getElementById('pro-details-area');
                const contentAreaTitle = document.getElementById('content-area-title');
                const backToChat = document.getElementById('back-to-chat');
                
                // 检查元素是否存在
                if (!chatAreaContainer || !proDetailsArea || !contentAreaTitle || !backToChat) {
                    logError('找不到必要的DOM元素', {
                        chatAreaContainer: chatAreaContainer ? '存在' : '不存在',
                        proDetailsArea: proDetailsArea ? '存在' : '不存在',
                        contentAreaTitle: contentAreaTitle ? '存在' : '不存在',
                        backToChat: backToChat ? '存在' : '不存在'
                    });
                    return;
                }
                
                // 显示专业人士详情区域，隐藏其他区域
                chatAreaContainer.classList.add('d-none');
                proDetailsArea.classList.remove('d-none');
                contentAreaTitle.textContent = '专业人士详情';
                backToChat.style.display = 'block';
                
                // 高亮选中的专业人士
                document.querySelectorAll('.pro-item').forEach(i => 
                    i.classList.remove('bg-primary', 'text-white'));
                this.classList.add('bg-primary', 'text-white');
                
                // 加载专业人士详情
                loadProDetails(proId, tabType);
            } catch (error) {
                logError('处理专业人士点击事件出错', error);
                logErrorStack(error);
            }
        });
    });
    
    // 预加载专业人士数据
    preloadProfessionalsData();
    
    // 页面加载完成后自动刷新聊天列表
    refreshChatList();
    
    // 每隔60秒刷新一次聊天列表
    setInterval(refreshChatList, 60000);
    
    // 初始化日志
    logDebug('页面初始化', {taskId, currentUserId});
});

// 初始化所有事件监听器
function initializeEventListeners() {
    // 处理聊天列表项点击事件
    document.querySelectorAll('.chat-item').forEach(function(item) {
        item.addEventListener('click', function() {
            const conversationId = this.dataset.conversationId;
            loadConversation(conversationId);
        });
    });

    // 处理任务详情按钮点击事件
    document.getElementById('view-task-details').addEventListener('click', function() {
        const taskDetailsModal = new bootstrap.Modal(document.getElementById('taskDetailsModal'));
        taskDetailsModal.show();
    });

    // 处理返回聊天按钮点击事件
    document.getElementById('back-to-chat').addEventListener('click', function() {
        showChatArea();
    });

    // 处理发送消息按钮点击事件
    document.getElementById('send-message-btn').addEventListener('click', sendMessage);

    // 处理消息输入框回车键事件
    document.getElementById('message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

// 添加全局错误处理
window.addEventListener('error', function(event) {
    console.error('全局错误:', event.error.message);
    console.error('错误堆栈:', event.error.stack);
});

// 添加调试日志函数
function logDebug(message, data) {
    console.log(`[DEBUG] ${message}`, data || '');
}

function logError(message, error) {
    console.error(`[ERROR] ${message}`, error || '');
    if (error && error.stack) {
        console.error(`[ERROR STACK] ${error.stack}`);
    }
}

// 单独记录错误堆栈的函数
function logErrorStack(error) {
    if (error && error.stack) {
        console.error(`[ERROR STACK详情] ${error.stack}`);
    } else {
        console.error('[ERROR] 无堆栈信息可用');
    }
}

// 刷新CSRF令牌
async function refreshCsrfToken() {
    logDebug('获取最新CSRF令牌');
    try {
        // 获取CSRF令牌
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
            return csrfMeta.content;
        } else {
            logError('未找到CSRF令牌元标签');
            return '';
        }
    } catch (error) {
        logError('获取CSRF令牌失败', error);
        logErrorStack(error);
        return '';
    }
}

// 创建带有CSRF令牌的通用fetch包装函数
async function fetchWithCsrf(url, options = {}) {
    try {
        // 确保options.headers存在
        options.headers = options.headers || {};
        
        // 如果是POST/PUT/DELETE等修改请求，需要CSRF令牌
        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method)) {
            // 添加CSRF令牌到请求头
            options.headers['X-CSRFToken'] = csrfToken;
            options.credentials = 'same-origin';
            
            // 如果CSRF令牌为空或过期，先刷新令牌
            if (!csrfToken) {
                csrfToken = await refreshCsrfToken();
                options.headers['X-CSRFToken'] = csrfToken;
            }
        }
        
        // 发送请求
        const response = await fetch(url, options);
        
        // 检查是否需要刷新CSRF令牌（如果返回403和CSRF错误）
        if (response.status === 403) {
            const responseText = await response.text();
            if (responseText.includes('CSRF') || responseText.includes('csrf')) {
                logDebug('CSRF令牌可能已过期，正在刷新');
                await refreshCsrfToken();
                
                // 使用新令牌重试请求
                options.headers['X-CSRFToken'] = csrfToken;
                return fetch(url, options);
            }
        }
        
        return response;
    } catch (error) {
        logError('fetchWithCsrf请求出错', error);
        throw error;
    }
}

// 处理聊天列表点击事件
document.querySelectorAll('.chat-item').forEach(item => {
    item.addEventListener('click', function() {
        const conversationId = this.dataset.conversationId;
        logDebug('点击聊天项', {
            conversationId: conversationId,
            element: this.outerHTML,
            hasClass: this.classList.contains('chat-item')
        });
        
        // 移除所有聊天项的活动状态
        document.querySelectorAll('.chat-item').forEach(el => {
            el.classList.remove('active-chat');
            logDebug('移除活动状态', {element: el.outerHTML});
        });
        
        // 添加活动状态到当前项
        this.classList.add('active-chat');
        logDebug('添加活动状态后', {
            hasActiveClass: this.classList.contains('active-chat')
        });
        
        // 显示聊天区域，隐藏专业人士详情区域
        document.getElementById('chat-area-container').classList.remove('d-none');
        document.getElementById('pro-details-area').classList.add('d-none');
        document.getElementById('content-area-title').textContent = '聊天详情';
        document.getElementById('back-to-chat').style.display = 'none';
        
        // 加载对话详情
        loadConversation(conversationId);
        
        // 检查聊天区域元素
        const chatPlaceholder = document.querySelector('.chat-placeholder');
        const chatMessages = document.querySelector('.chat-messages');
        const chatInputArea = document.querySelector('.chat-input-area');
        
        logDebug('聊天区域元素', {
            chatPlaceholder: chatPlaceholder ? true : false,
            chatMessages: chatMessages ? true : false,
            chatInputArea: chatInputArea ? true : false
        });
        
        // 显示对话区域
        if (chatPlaceholder) chatPlaceholder.classList.add('d-none');
        if (chatMessages) chatMessages.classList.remove('d-none');
        if (chatInputArea) chatInputArea.classList.remove('d-none');
        
        // 设置当前活跃对话ID到发送按钮的data属性
        document.getElementById('send-message-btn').setAttribute('data-conversation-id', conversationId);
    });
});

// 加载对话内容的函数
function loadConversation(conversationId) {
    logDebug('开始加载对话', {conversationId, taskId, currentUserId});
    
    try {
        // 解析对话ID，获取用户ID
        const userIds = conversationId.split('_');
        if (userIds.length !== 2) {
            logError('无效的对话ID格式', {conversationId});
            return;
        }
        
        const otherUserId = userIds[0] === currentUserId ? userIds[1] : userIds[0];
        logDebug('解析对话ID', {userIds, currentUserId, otherUserId});
        
        // 确保taskId存在
        if (!taskId) {
            logError('任务ID不存在');
            return;
        }
        
        // 确保otherUserId是数字
        const numericOtherUserId = parseInt(otherUserId);
        if (isNaN(numericOtherUserId)) {
            logError('无效的用户ID', {otherUserId});
            return;
        }
        
        // 确保taskId是数字
        const numericTaskId = parseInt(taskId);
        if (isNaN(numericTaskId)) {
            logError('无效的任务ID', {taskId});
            return;
        }
        
        const url = `/message/api/messages?task_id=${numericTaskId}&other_user_id=${numericOtherUserId}`;
        logDebug('构建API请求URL', {url, numericTaskId, numericOtherUserId});
        
        const messagesContainer = document.querySelector('.chat-messages');
        
        if (!messagesContainer) {
            logError('找不到消息容器元素', {selector: '.chat-messages'});
            return;
        }
        
        // 显示加载状态
        messagesContainer.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-3">加载聊天记录中...</p></div>';
        
        // 显示聊天窗口，隐藏占位符
        const chatPlaceholder = document.querySelector('.chat-placeholder');
        const chatInputArea = document.querySelector('.chat-input-area');
        const messageInput = document.getElementById('message-input');
        
        logDebug('聊天区域元素状态', {
            chatPlaceholder: chatPlaceholder ? {
                exists: true,
                isHidden: chatPlaceholder.classList.contains('d-none')
            } : 'not found',
            messagesContainer: {
                exists: true,
                isHidden: messagesContainer.classList.contains('d-none')
            },
            chatInputArea: chatInputArea ? {
                exists: true,
                isHidden: chatInputArea.classList.contains('d-none')
            } : 'not found',
            messageInput: messageInput ? {
                exists: true,
                disabled: messageInput.disabled
            } : 'not found'
        });
        
        if (chatPlaceholder) chatPlaceholder.classList.add('d-none');
        if (messagesContainer) messagesContainer.classList.remove('d-none');
        if (chatInputArea) chatInputArea.classList.remove('d-none');
        
        // 确保输入框可用
        if (messageInput) {
            messageInput.disabled = false;
            messageInput.focus();
        }
        
        // 发送AJAX请求
        logDebug('发送API请求', {url});
        fetchWithCsrf(url)
            .then(response => {
                logDebug('获取API响应', {status: response.status, ok: response.ok, statusText: response.statusText});
                if (!response.ok) {
                    return response.text().then(text => {
                        logError('API响应错误', {status: response.status, text: text});
                        throw new Error(`请求失败，状态码: ${response.status}, 错误信息: ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                logDebug('解析API响应数据', {
                    messagesCount: data.messages ? data.messages.length : 0, 
                    unreadCount: data.unread_count || 0,
                    firstMessage: data.messages && data.messages.length > 0 ? {
                        sender_id: data.messages[0].sender_id,
                        content: data.messages[0].content.substring(0, 50) + '...',
                        isCurrentUser: data.messages[0].sender_id === parseInt(currentUserId)
                    } : 'no messages',
                    error_info: data.error_info || null
                });
                
                // 检查是否有错误信息
                if (data.error_info) {
                    logError('API返回错误信息', {error_info: data.error_info});
                    messagesContainer.innerHTML = `<div class="alert alert-warning">
                        <p>暂无聊天记录</p>
                        <small class="text-muted">${data.error_info}</small>
                    </div>`;
                    return;
                }
                
                // 检查是否有错误
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // 检查消息数组是否存在
                if (!data.messages || !Array.isArray(data.messages)) {
                    throw new Error('API返回的数据格式不正确，缺少messages数组');
                }
                
                // 清空容器
                messagesContainer.innerHTML = '';
                
                // 如果没有消息，显示提示
                if (data.messages.length === 0) {
                    messagesContainer.innerHTML = '<div class="text-center p-5"><p class="text-muted">暂无聊天记录</p></div>';
                    return;
                }
                
                // 渲染消息
                data.messages.forEach((message, index) => {
                    try {
                        const isCurrentUser = message.sender_id === parseInt(currentUserId);
                        logDebug(`渲染消息 ${index}`, {
                            sender_id: message.sender_id,
                            current_user_id: currentUserId,
                            isCurrentUser: isCurrentUser,
                            content_preview: message.content.substring(0, 30) + '...'
                        });
                        
                        const messageHtml = `
                            <div class="message ${isCurrentUser ? 'message-outgoing' : 'message-incoming'} mb-3">
                                <div class="d-flex align-items-end ${isCurrentUser ? 'justify-content-end' : ''}">
                                    ${!isCurrentUser ? `<img src="${data.other_user.avatar || '/static/images/default-avatar.jpg'}" class="avatar-sm rounded-circle me-2" alt="${data.other_user.name}">` : ''}
                                    <div class="message-content ${isCurrentUser ? 'bg-primary text-white' : 'bg-light'} p-3 rounded">
                                        ${message.content}
                                        <div class="message-time small ${isCurrentUser ? 'text-light' : 'text-muted'} mt-1">
                                            ${formatDateTime(message.created_at)}
                                        </div>
                                    </div>
                                    ${isCurrentUser ? `<img src="${data.current_user.avatar || '/static/images/default-avatar.jpg'}" class="avatar-sm rounded-circle ms-2" alt="${data.current_user.name}">` : ''}
                                </div>
                            </div>
                        `;
                        messagesContainer.insertAdjacentHTML('beforeend', messageHtml);
                    } catch (error) {
                        logError(`渲染消息出错 (索引: ${index})`, error);
                    }
                });
                
                // 滚动到底部
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                
                // 标记为已读
                if (data.unread_count > 0) {
                    markConversationAsRead(otherUserId);
                }
                
                // 更新未读消息数
                updateUnreadCount();
                
                // 刷新聊天列表以更新未读状态
                refreshChatList();
                
                // 确保输入框可用并获取焦点
                const messageInput = document.getElementById('message-input');
                if (messageInput) {
                    messageInput.disabled = false;
                    messageInput.focus();
                }
            })
            .catch(error => {
                logError('加载对话失败', error);
                messagesContainer.innerHTML = `<div class="alert alert-danger">加载聊天记录失败: ${error.message}</div>`;
            });
    } catch (error) {
        logError('loadConversation函数执行出错', error);
    }
}

// 加载专业人士详情的函数
function loadProDetails(proId, tabType) {
    logDebug('开始加载专业人士详情', {proId, tabType});
    
    // 显示加载状态，但使用更友好的UI
    const profileContainer = document.querySelector('.pro-profile');
    const placeholderContainer = document.querySelector('.pro-placeholder');
    
    if (!profileContainer || !placeholderContainer) {
        logError('找不到专业人士资料容器元素', {
            profileContainer: profileContainer ? '存在' : '不存在',
            placeholderContainer: placeholderContainer ? '存在' : '不存在'
        });
        return;
    }
    
    // 显示更友好的加载状态
    placeholderContainer.classList.remove('d-none');
    profileContainer.classList.add('d-none');
    placeholderContainer.innerHTML = `
        <div class="text-center p-4">
            <div class="spinner-border text-primary spinner-border-sm me-2" role="status"></div>
            <span>正在加载专业人士资料...</span>
            <div class="progress mt-3" style="height: 5px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated bg-primary" 
                     role="progressbar" style="width: 100%"></div>
            </div>
        </div>
    `;
    
    // 创建一个缓存键
    const cacheKey = `pro_${proId}_${tabType}`;
    
    // 检查是否有缓存数据
    const cachedData = sessionStorage.getItem(cacheKey);
    if (cachedData) {
        try {
            const data = JSON.parse(cachedData);
            logDebug('使用缓存的专业人士数据', {proId, tabType});
            // 使用短延迟显示缓存数据，让用户感知到加载过程
            setTimeout(() => displayProData(data, tabType), 300);
            
            // 在后台仍然请求新数据以更新缓存
            fetchProDataAndUpdateCache(proId, tabType, cacheKey);
            return;
        } catch (e) {
            logError('解析缓存数据失败', e);
            // 继续正常加载流程
        }
    }
    
    // 首先尝试从页面数据中获取专业人士信息作为快速显示
    let proData = extractProDataFromPage(proId, tabType);
    
    if (proData) {
        // 立即显示从页面提取的基本数据
        displayProData(proData, tabType);
        
        // 然后在后台获取完整数据
        fetchProDataAndUpdateCache(proId, tabType, cacheKey);
    } else {
        // 如果没有页面数据，直接获取API数据
        fetchProDataAndUpdateCache(proId, tabType, cacheKey);
    }
}

// 从页面元素中提取专业人士数据
function extractProDataFromPage(proId, tabType) {
    try {
        let proData = null;
        
        if (tabType === 'interestedPros') {
            const proElements = document.querySelectorAll(`.pro-item[data-pro-id="${proId}"][data-tab-id="interestedPros"]`);
            if (proElements && proElements.length > 0) {
                const proElement = proElements[0];
                if (proElement) {
                    const nameElement = proElement.querySelector('h6.mb-0');
                    const ratingElement = proElement.querySelector('.fas.fa-star.text-warning');
                    const jobsElement = proElement.querySelector('.fas.fa-briefcase');
                    
                    proData = {
                        id: proId,
                        name: nameElement ? nameElement.textContent.trim() : '未知专业人士',
                        rating: ratingElement ? parseFloat(ratingElement.parentElement.textContent.trim() || '0') : 0,
                        completed_jobs: jobsElement ? parseInt(jobsElement.parentElement.textContent.trim().replace(/\D/g, '') || '0') : 0,
                        profession: '',
                        skills: [],
                        contact: '',
                        description: '正在加载完整资料...',
                        _fromPage: true
                    };
                }
            }
        } else if (tabType === 'matchingPros') {
            const proElements = document.querySelectorAll(`.pro-item[data-pro-id="${proId}"][data-tab-id="matchingPros"]`);
            if (proElements && proElements.length > 0) {
                const proElement = proElements[0];
                if (proElement) {
                    const nameElement = proElement.querySelector('h6.mb-0');
                    const ratingElement = proElement.querySelector('.fas.fa-star.text-warning');
                    const distanceElement = proElement.querySelector('.fas.fa-map-marker-alt');
                    const matchScoreElement = proElement.querySelector('.badge.bg-success');
                    
                    proData = {
                        id: proId,
                        name: nameElement ? nameElement.textContent.trim() : '未知专业人士',
                        rating: ratingElement ? parseFloat(ratingElement.parentElement.textContent.trim() || '0') : 0,
                        distance: distanceElement ? parseFloat(distanceElement.parentElement.textContent.trim().replace(/[^\d.]/g, '') || '0') : 0,
                        match_score: matchScoreElement ? parseInt(matchScoreElement.textContent.replace(/\D/g, '') || '0') : 0,
                        profession: '',
                        skills: [],
                        contact: '',
                        description: '正在加载完整资料...',
                        _fromPage: true
                    };
                }
            }
        }
        
        return proData;
    } catch (error) {
        logError('从页面元素提取专业人士数据失败', error);
        return null;
    }
}

// 从API获取专业人士数据并更新缓存
function fetchProDataAndUpdateCache(proId, tabType, cacheKey) {
    // 尝试不同的API路径
    const urls = [
        `/task/api/professionals/${proId}?task_id=${taskId}`,
        `/api/professionals/${proId}?task_id=${taskId}`,
        `/api/tasks/${taskId}/professionals/${proId}`
    ];
    
    // 使用Promise.any尝试所有URL，取第一个成功的结果
    const fetchPromises = urls.map(url => {
        return new Promise((resolve, reject) => {
            logDebug(`尝试API路径`, {url});
            
            fetchWithCsrf(url)
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`请求失败，状态码: ${response.status}, 错误信息: ${text}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    logDebug('获取专业人士数据成功', {url, data});
                    resolve(data);
                })
                .catch(error => {
                    logError(`API路径 ${url} 失败`, error);
                    reject(error);
                });
        });
    });
    
    // 使用Promise.allSettled替代Promise.any，以便在所有请求都失败时也能处理
    Promise.allSettled(fetchPromises)
        .then(results => {
            // 查找第一个成功的结果
            const successResult = results.find(r => r.status === 'fulfilled');
            
            if (successResult) {
                const data = successResult.value;
                
                // 缓存数据
                try {
                    sessionStorage.setItem(cacheKey, JSON.stringify(data));
                    logDebug('专业人士数据已缓存', {cacheKey});
                } catch (e) {
                    logError('缓存专业人士数据失败', e);
                }
                
                // 显示数据
                displayProData(data, tabType);
            } else {
                // 所有请求都失败
                logError('所有API路径尝试失败');
                
                // 获取当前显示的数据
                const profileContainer = document.querySelector('.pro-profile');
                const placeholderContainer = document.querySelector('.pro-placeholder');
                
                // 如果当前没有显示数据，显示错误信息
                if (profileContainer.classList.contains('d-none')) {
                    placeholderContainer.classList.add('d-none');
                    profileContainer.classList.remove('d-none');
                    profileContainer.innerHTML = `
                        <div class="alert alert-warning">
                            <h5><i class="fas fa-exclamation-triangle me-2"></i>无法加载完整资料</h5>
                            <p>我们无法从服务器获取专业人士的详细资料。</p>
                            <p>您仍然可以与该专业人士联系或接受申请。</p>
                            <div class="mt-3">
                                <button class="btn btn-primary" onclick="sendMessageToPro(${proId})">
                                    <i class="fas fa-comment-dots"></i> 发送消息
                                </button>
                                ${tabType === 'interestedPros' ? 
                                  `<button class="btn btn-success ms-2" onclick="acceptPro(${proId})">
                                      <i class="fas fa-check"></i> 接受申请
                                  </button>` : ''}
                                <button class="btn btn-outline-secondary ms-2" onclick="loadProDetails('${proId}', '${tabType}')">
                                    <i class="fas fa-sync-alt me-1"></i>重试
                                </button>
                            </div>
                        </div>
                    `;
                } else {
                    // 如果已经显示了基本数据，添加一个小提示
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-warning mt-3';
                    alertDiv.innerHTML = `
                        <p class="mb-0"><i class="fas fa-exclamation-triangle me-2"></i>无法加载完整资料，显示的是基本信息</p>
                        <button class="btn btn-sm btn-outline-warning mt-2" onclick="loadProDetails('${proId}', '${tabType}')">
                            <i class="fas fa-sync-alt me-1"></i>重试加载
                        </button>
                    `;
                    
                    // 添加到资料卡片底部
                    const cardFooter = profileContainer.querySelector('.card-footer');
                    if (cardFooter) {
                        cardFooter.parentNode.insertBefore(alertDiv, cardFooter.nextSibling);
                    } else {
                        profileContainer.appendChild(alertDiv);
                    }
                }
            }
        });
}

// 显示专业人士数据的函数
function displayProData(data, tabType) {
    try {
        // 获取容器元素
        const profileContainer = document.querySelector('.pro-profile');
        const placeholderContainer = document.querySelector('.pro-placeholder');
        
        if (!profileContainer || !placeholderContainer) {
            logError('显示专业人士数据时找不到容器元素');
            return;
        }
        
        // 隐藏加载状态，显示资料
        placeholderContainer.classList.add('d-none');
        profileContainer.classList.remove('d-none');
        
        // 如果数据来自页面元素且正在加载中，添加加载指示器
        const loadingIndicator = data._fromPage ? 
            `<div class="position-absolute top-0 end-0 p-2">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
            </div>` : '';
        
        // 创建专业人士档案HTML
        const profileHtml = `
            <div class="card mb-3 position-relative">
                ${loadingIndicator}
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">${data.name || '未知专业人士'}</h5>
                </div>
                <div class="card-body">
                    ${data.profession ? `
                    <div class="row mb-3">
                        <div class="col-md-4 fw-bold">职业:</div>
                        <div class="col-md-8">${data.profession}</div>
                    </div>` : ''}
                    
                    ${data.skills && data.skills.length > 0 ? `
                    <div class="row mb-3">
                        <div class="col-md-4 fw-bold">技能:</div>
                        <div class="col-md-8">${Array.isArray(data.skills) ? data.skills.join(', ') : data.skills}</div>
                    </div>` : ''}
                    
                    ${data.contact ? `
                    <div class="row mb-3">
                        <div class="col-md-4 fw-bold">联系方式:</div>
                        <div class="col-md-8">${data.contact}</div>
                    </div>` : ''}
                    
                    <div class="row mb-3">
                        <div class="col-md-4 fw-bold">评分:</div>
                        <div class="col-md-8">${renderStars(data.rating || 0)}</div>
                    </div>
                    
                    ${data.completed_jobs !== undefined ? `
                    <div class="row mb-3">
                        <div class="col-md-4 fw-bold">已完成工作:</div>
                        <div class="col-md-8">
                            <div class="d-flex align-items-center">
                                <span class="me-2">${data.completed_jobs} 个</span>
                                <div class="progress flex-grow-1" style="height: 8px;">
                                    <div class="progress-bar bg-success" role="progressbar" 
                                         style="width: ${Math.min(data.completed_jobs * 5, 100)}%;" 
                                         aria-valuenow="${data.completed_jobs}" aria-valuemin="0" aria-valuemax="20">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>` : ''}
                    
                    ${data.distance !== undefined ? `
                    <div class="row mb-3">
                        <div class="col-md-4 fw-bold">距离:</div>
                        <div class="col-md-8">${data.distance} km</div>
                    </div>` : ''}
                    
                    ${data.match_score !== undefined ? `
                    <div class="row mb-3">
                        <div class="col-md-4 fw-bold">匹配度:</div>
                        <div class="col-md-8">
                            <div class="progress" style="height: 20px;">
                                <div class="progress-bar bg-success" role="progressbar" style="width: ${data.match_score}%;" 
                                    aria-valuenow="${data.match_score}" aria-valuemin="0" aria-valuemax="100">
                                    ${data.match_score}%
                                </div>
                            </div>
                        </div>
                    </div>` : ''}
                    
                    ${data.description ? `
                    <div class="row mb-3">
                        <div class="col-md-4 fw-bold">简介:</div>
                        <div class="col-md-8">${data.description}</div>
                    </div>` : ''}
                </div>
                <div class="card-footer">
                    <button class="btn btn-primary" onclick="sendMessageToPro(${data.id})">
                        <i class="fas fa-comment-dots"></i> 发送消息
                    </button>
                    ${tabType === 'interestedPros' ? 
                      `<button class="btn btn-success ms-2" onclick="acceptPro(${data.id})">
                          <i class="fas fa-check"></i> 接受申请
                      </button>` : ''}
                </div>
            </div>
            
            ${data.portfolio ? 
              `<div class="card mt-3">
                  <div class="card-header bg-primary text-white">
                      <h5 class="mb-0">作品集</h5>
                  </div>
                  <div class="card-body">
                      ${data.portfolio}
                  </div>
              </div>` : ''}
        `;
        
        profileContainer.innerHTML = profileHtml;
    } catch (error) {
        logError('显示专业人士数据出错', error);
        if (profileContainer) {
            profileContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h5><i class="fas fa-exclamation-triangle me-2"></i>显示专业人士资料时出错</h5>
                    <p>${error.message}</p>
                    <button class="btn btn-outline-danger btn-sm mt-2" onclick="loadProDetails('${proId}', '${tabType}')">
                        <i class="fas fa-sync-alt me-1"></i>重试
                    </button>
                </div>
            `;
            profileContainer.classList.remove('d-none');
        }
        if (placeholderContainer) {
            placeholderContainer.classList.add('d-none');
        }
    }
}

// 标记对话为已读的函数
function markConversationAsRead(otherUserId) {
    logDebug('标记对话为已读', {otherUserId, taskId});
    
    try {
        // 确保otherUserId是数字
        const numericOtherUserId = parseInt(otherUserId);
        if (isNaN(numericOtherUserId)) {
            logError('无效的用户ID', {otherUserId});
            return;
        }
        
        // 确保taskId是数字
        const numericTaskId = parseInt(taskId);
        if (isNaN(numericTaskId)) {
            logError('无效的任务ID', {taskId});
            return;
        }
        
        const url = `/message/api/messages/mark_read`;
        logDebug('构建标记已读API请求URL', {url, body: {task_id: numericTaskId, other_user_id: numericOtherUserId}});
        
        // 使用fetchWithCsrf函数来自动处理CSRF令牌
        fetchWithCsrf(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // 显式添加CSRF令牌
            },
            body: JSON.stringify({
                task_id: numericTaskId,
                other_user_id: numericOtherUserId
            })
        })
        .then(response => {
            logDebug('标记已读响应', {status: response.status, ok: response.ok});
            if (!response.ok) {
                return response.text().then(text => {
                    logError(`标记已读请求失败，状态码: ${response.status}，响应内容:`, text);
                    throw new Error(`请求失败，状态码: ${response.status}，响应内容: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            logDebug('标记已读成功', data);
            
            // 更新UI，移除未读标记
            const conversationId = `${Math.min(parseInt(currentUserId), parseInt(otherUserId))}_${Math.max(parseInt(currentUserId), parseInt(otherUserId))}`;
            const chatItem = document.querySelector(`.chat-item[data-conversation-id="${conversationId}"]`);
            if (chatItem) {
                const badge = chatItem.querySelector('.badge');
                if (badge) {
                    badge.remove();
                }
                
                // 移除高亮背景
                chatItem.classList.remove('bg-light');
            }
            
            // 更新未读消息数
            updateUnreadCount();
        })
        .catch(error => {
            logError('标记对话为已读失败', error);
        });
    } catch (error) {
        logError('标记对话为已读失败', error);
    }
}

// 更新未读消息数的函数
function updateUnreadCount() {
    logDebug('更新未读消息数');
    fetchWithCsrf(`/message/api/users/me/unread_messages`)
        .then(response => {
            logDebug('获取未读消息数响应', {status: response.status, ok: response.ok});
            if (!response.ok) {
                throw new Error(`请求失败，状态码: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            logDebug('未读消息数', data);
            const unreadCount = data.unread_count;
            
            // 更新导航栏中的未读消息数
            const navBadge = document.querySelector('#nav-messages-badge');
            if (navBadge) {
                if (unreadCount > 0) {
                    navBadge.textContent = unreadCount;
                    navBadge.classList.remove('d-none');
                } else {
                    navBadge.classList.add('d-none');
                }
            }
            
            // 更新聊天标签中的未读消息数
            const chatBadge = document.querySelector('#chat-tab-badge');
            if (chatBadge) {
                if (unreadCount > 0) {
                    chatBadge.textContent = unreadCount;
                    chatBadge.classList.remove('d-none');
                } else {
                    chatBadge.classList.add('d-none');
                }
            }
        })
        .catch(error => {
            logError('更新未读消息数失败', error);
        });
}

// 发送消息的函数
function sendMessage() {
    try {
        const messageInput = document.getElementById('message-input');
        if (!messageInput) {
            logError('发送消息失败', {error: '找不到消息输入框'});
            return;
        }
        
        const message = messageInput.value.trim();
        // 从发送按钮的data属性获取当前活跃对话ID
        const sendButton = document.getElementById('send-message-btn');
        const conversationId = sendButton.getAttribute('data-conversation-id') || 
                              document.querySelector('.chat-item.active-chat')?.dataset.conversationId;
        
        logDebug('发送消息', {message, conversationId, taskId});
        
        if (!message) {
            logError('发送消息失败', {error: '消息不能为空'});
            return;
        }
        
        if (!conversationId) {
            logError('发送消息失败', {error: '未选择对话'});
            alert('请先选择一个对话');
            return;
        }
        
        // 解析对话ID，获取用户ID
        const userIds = conversationId.split('_');
        if (userIds.length !== 2) {
            logError('无效的对话ID格式', {conversationId});
            return;
        }
        
        const otherUserId = userIds[0] === currentUserId ? userIds[1] : userIds[0];
        logDebug('解析对话ID', {userIds, currentUserId, otherUserId});
        
        // 禁用输入框，防止重复发送
        messageInput.disabled = true;
        
        // 使用fetchWithCsrf函数发送请求
        fetchWithCsrf(`/message/api/messages/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipient_id: otherUserId,
                content: message,
                task_id: taskId
            })
        })
        .then(response => {
            logDebug('发送消息响应', {status: response.status, ok: response.ok});
            if (!response.ok) {
                throw new Error(`请求失败，状态码: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            logDebug('发送消息成功', data);
            
            // 清空输入框
            messageInput.value = '';
            
            // 启用输入框
            messageInput.disabled = false;
            messageInput.focus();
            
            // 重新加载对话
            loadConversation(conversationId);
        })
        .catch(error => {
            logError('发送消息失败', error);
            
            // 启用输入框
            messageInput.disabled = false;
        });
    } catch (error) {
        logError('发送消息函数出错', error);
        
        // 确保输入框始终可用
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.disabled = false;
        }
    }
}

// 向专业人士发送消息的函数
function sendMessageToPro(proId) {
    logDebug('向专业人士发送消息', {proId, taskId});
    
    // 构建对话ID
    const conversationId = `${Math.min(parseInt(currentUserId), parseInt(proId))}_${Math.max(parseInt(currentUserId), parseInt(proId))}`;
    logDebug('构建对话ID', {conversationId, currentUserId, proId});
    
    // 切换到聊天区域
    document.getElementById('chat-area-container').classList.remove('d-none');
    document.getElementById('pro-details-area').classList.add('d-none');
    document.getElementById('content-area-title').textContent = '聊天详情';
    document.getElementById('back-to-chat').style.display = 'none';
    
    // 高亮选中的聊天
    document.querySelectorAll('.chat-item').forEach(i => i.classList.remove('active-chat'));
    const chatItem = document.querySelector(`.chat-item[data-conversation-id="${conversationId}"]`);
    if (chatItem) {
        chatItem.classList.add('active-chat');
        
        // 更新未读消息徽章
        const badge = chatItem.querySelector('.badge');
        if (badge) {
            badge.classList.add('d-none');
        }
    } else {
        logDebug('未找到匹配的聊天项', {conversationId});
    }
    
    // 加载对话
    loadConversation(conversationId);
    
    // 刷新聊天列表
    refreshChatList();
}

// 接受专业人士申请的函数
function acceptPro(proId) {
    logDebug('接受专业人士申请', {proId, taskId});
    
    // 创建URL
    const url = `/task/api/tasks/${taskId}/accept_pro/${proId}`;
    logDebug('构建接受专业人士申请API请求URL', {url});
    
    // 显示加载状态
    const acceptBtn = document.querySelector(`.btn-success[onclick="acceptPro(${proId})"]`);
    if (acceptBtn) {
        const originalText = acceptBtn.innerHTML;
        acceptBtn.disabled = true;
        acceptBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
        
        // 恢复按钮状态的函数
        const restoreButton = () => {
            acceptBtn.disabled = false;
            acceptBtn.innerHTML = originalText;
        };
        
        fetchWithCsrf(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            logDebug('接受申请响应', {status: response.status, ok: response.ok});
            if (!response.ok) {
                return response.text().then(text => {
                    logError('接受申请失败', {status: response.status, text});
                    throw new Error(`请求失败，状态码: ${response.status}, 错误信息: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            logDebug('接受申请成功', data);
            alert('已成功接受该专业人士的申请！');
            
            // 刷新页面以更新状态
            window.location.reload();
        })
        .catch(error => {
            logError('接受专业人士申请失败', error);
            alert(`接受申请失败: ${error.message}`);
            restoreButton();
            
            // 尝试备用API路径
            const backupUrl = `/api/tasks/${taskId}/accept_pro/${proId}`;
            logDebug('尝试备用API路径', {backupUrl});
            
            fetchWithCsrf(backupUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`备用请求失败，状态码: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                logDebug('通过备用API路径接受申请成功', data);
                alert('已成功接受该专业人士的申请！');
                
                // 刷新页面以更新状态
                window.location.reload();
            })
            .catch(backupError => {
                logError('备用API路径也失败', backupError);
                // 已经显示过错误提示，不再重复
            });
        });
    } else {
        logDebug('未找到接受按钮元素', {proId});
        // 如果找不到按钮，直接发送请求
        fetchWithCsrf(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            logDebug('接受申请响应', {status: response.status, ok: response.ok});
            if (!response.ok) {
                return response.text().then(text => {
                    logError('接受申请失败', {status: response.status, text});
                    throw new Error(`请求失败，状态码: ${response.status}, 错误信息: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            logDebug('接受申请成功', data);
            alert('已成功接受该专业人士的申请！');
            
            // 刷新页面以更新状态
            window.location.reload();
        })
        .catch(error => {
            logError('接受专业人士申请失败', error);
            alert(`接受申请失败: ${error.message}`);
            
            // 尝试备用API路径
            const backupUrl = `/api/tasks/${taskId}/accept_pro/${proId}`;
            logDebug('尝试备用API路径', {backupUrl});
            
            fetchWithCsrf(backupUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`备用请求失败，状态码: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                logDebug('通过备用API路径接受申请成功', data);
                alert('已成功接受该专业人士的申请！');
                
                // 刷新页面以更新状态
                window.location.reload();
            })
            .catch(backupError => {
                logError('备用API路径也失败', backupError);
                // 已经显示过错误提示，不再重复
            });
        });
    }
}

// 刷新聊天列表的函数
function refreshChatList() {
    logDebug('刷新聊天列表');
    
    fetchWithCsrf(`/task/api/tasks/${taskId}/conversations`)
        .then(response => {
            logDebug('获取聊天列表响应', {status: response.status, ok: response.ok});
            if (!response.ok) {
                throw new Error(`请求失败，状态码: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            logDebug('获取聊天列表成功', {
                conversationsCount: data.conversations.length,
                conversations: data.conversations.map(c => ({
                    id: c.id,
                    other_user: {
                        id: c.other_user.id,
                        name: c.other_user.name
                    },
                    unread_count: c.unread_count,
                    last_message_preview: c.last_message_preview
                }))
            });
            
            // 更新聊天列表
            const chatsContainer = document.querySelector('.chats-list');
            if (chatsContainer) {
                logDebug('找到聊天列表容器', {
                    containerHTML: chatsContainer.outerHTML.substring(0, 100) + '...'
                });
                
                // 保存当前活跃的对话ID
                const activeConversationId = document.querySelector('.chat-item.active-chat')?.dataset.conversationId;
                
                chatsContainer.innerHTML = '';
                
                if (data.conversations.length === 0) {
                    chatsContainer.innerHTML = `
                        <div class="text-center p-3">
                            <p class="text-muted mb-0">您的任务尚未收到任何对话</p>
                        </div>
                    `;
                    logDebug('没有对话可显示');
                    return;
                }
                
                data.conversations.forEach(conv => {
                    const unreadBadge = conv.unread_count > 0 ? 
                        `<span class="badge bg-danger rounded-pill mt-1">${conv.unread_count}</span>` : '';
                    
                    // 检查是否是当前活跃的对话
                    const isActive = conv.id === activeConversationId;
                    
                    logDebug('创建聊天项', {
                        conversation_id: conv.id,
                        other_user: conv.other_user.name,
                        unread_count: conv.unread_count,
                        isActive: isActive
                    });
                    
                    const chatItemHtml = `
                        <div class="chat-item p-3 border-bottom ${conv.unread_count > 0 ? 'bg-light' : ''} ${isActive ? 'active-chat' : ''}" data-conversation-id="${conv.id}">
                            <div class="d-flex align-items-center position-relative">
                                <img src="${conv.other_user.avatar}" alt="${conv.other_user.name}" class="rounded-circle" width="40">
                                <div class="ms-3 flex-grow-1">
                                    <h6 class="mb-1">${conv.other_user.name}</h6>
                                    <p class="text-muted mb-0 text-truncate">${conv.last_message_preview}</p>
                                </div>
                                <div class="text-end">
                                    <small class="text-muted d-block">${formatDateTime(conv.last_message_time)}</small>
                                    ${unreadBadge}
                                </div>
                            </div>
                        </div>
                    `;
                    
                    chatsContainer.insertAdjacentHTML('beforeend', chatItemHtml);
                });
                
                // 添加点击事件处理
                const chatItems = document.querySelectorAll('.chat-item');
                logDebug('添加点击事件到聊天项', {
                    chatItemsCount: chatItems.length
                });
                
                chatItems.forEach(item => {
                    item.addEventListener('click', function() {
                        const conversationId = this.dataset.conversationId;
                        logDebug('点击刷新后的聊天项', {
                            conversationId: conversationId,
                            element: this.outerHTML
                        });
                        
                        // 移除所有聊天项的活动状态
                        document.querySelectorAll('.chat-item').forEach(el => {
                            el.classList.remove('active-chat');
                            logDebug('移除活动状态', {element: el.outerHTML});
                        });
                        
                        // 添加活动状态到当前项
                        this.classList.add('active-chat');
                        logDebug('添加活动状态后', {
                            hasActiveClass: this.classList.contains('active-chat')
                        });
                        
                        // 显示聊天区域，隐藏专业人士详情区域
                        document.getElementById('chat-area-container').classList.remove('d-none');
                        document.getElementById('pro-details-area').classList.add('d-none');
                        document.getElementById('content-area-title').textContent = '聊天详情';
                        document.getElementById('back-to-chat').style.display = 'none';
                        
                        // 加载对话详情
                        loadConversation(conversationId);
                        
                        // 检查聊天区域元素
                        const chatPlaceholder = document.querySelector('.chat-placeholder');
                        const chatMessages = document.querySelector('.chat-messages');
                        const chatInputArea = document.querySelector('.chat-input-area');
                        
                        logDebug('聊天区域元素', {
                            chatPlaceholder: chatPlaceholder ? true : false,
                            chatMessages: chatMessages ? true : false,
                            chatInputArea: chatInputArea ? true : false
                        });
                        
                        // 显示对话区域
                        if (chatPlaceholder) chatPlaceholder.classList.add('d-none');
                        if (chatMessages) chatMessages.classList.remove('d-none');
                        if (chatInputArea) chatInputArea.classList.remove('d-none');
                        
                        // 设置当前活跃对话ID到发送按钮的data属性
                        document.getElementById('send-message-btn').setAttribute('data-conversation-id', conversationId);
                    });
                });
                
                // 如果有活跃对话，确保发送按钮有正确的对话ID
                if (activeConversationId) {
                    document.getElementById('send-message-btn').setAttribute('data-conversation-id', activeConversationId);
                }
            } else {
                logError('找不到聊天列表容器', {selector: '.chats-list'});
            }
        })
        .catch(error => {
            logError('刷新聊天列表失败', error);
        });
}

// 格式化日期时间的函数
function formatDateTime(dateTimeString) {
    try {
        const date = new Date(dateTimeString);
        const now = new Date();
        
        // 分成两行显示日期和时间
        const timeStr = date.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        let dateStr;
        // 当年的消息省略年份
        if (date.getFullYear() === now.getFullYear()) {
            dateStr = date.toLocaleDateString('zh-CN', {
                month: '2-digit',
                day: '2-digit'
            });
        } else {
            dateStr = date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
        }
        
        return `<span class="d-block">${dateStr}</span><span class="d-block">${timeStr}</span>`;
    } catch (error) {
        logError('格式化日期时间出错', error);
        return dateTimeString;
    }
}

// 渲染星级评分的函数
function renderStars(rating) {
    try {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
        
        let starsHtml = '';
        
        // 添加满星
        for (let i = 0; i < fullStars; i++) {
            starsHtml += '<i class="fas fa-star text-warning"></i>';
        }
        
        // 添加半星
        if (halfStar) {
            starsHtml += '<i class="fas fa-star-half-alt text-warning"></i>';
        }
        
        // 添加空星
        for (let i = 0; i < emptyStars; i++) {
            starsHtml += '<i class="far fa-star text-warning"></i>';
        }
        
        return `<div class="stars">${starsHtml} <span class="ms-2">${rating.toFixed(1)}</span></div>`;
    } catch (error) {
        logError('渲染星级评分出错', error);
        return `${rating || 0}`;
    }
}

// 页面加载完成后自动刷新聊天列表
window.addEventListener('load', function() {
    refreshCsrfToken();
    refreshChatList();
    updateUnreadCount();
    
    // 预加载专业人士数据
    preloadProfessionalsData();
    
    // 重新绑定发送按钮事件，确保在DOM更新后仍然有效
    document.getElementById('send-message-btn')?.addEventListener('click', sendMessage);
    
    // 确保输入框可用
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.disabled = false;
    }
    
    // 添加CSS样式以确保聊天区域正确显示
    const style = document.createElement('style');
    style.textContent = `
        .message-outgoing {
            display: flex;
            justify-content: flex-end;
        }
        .message-incoming {
            display: flex;
            justify-content: flex-start;
        }
        .message-content {
            max-width: 70%; 
            word-break: break-word;
        }
        .chat-messages {
            overflow-y: auto;
            display: block !important;
        }
        .chat-input-area {
            display: block !important;
        }
        
        /* 确保聊天列表中的消息预览正确截断 */
        .chat-item .flex-grow-1 {
            min-width: 0;
            max-width: calc(100% - 100px);
        }
        
        .chat-item .text-truncate {
            width: 100%;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* 添加专业人士资料卡片的过渡效果 */
        .pro-profile {
            transition: opacity 0.3s ease;
        }
        
        /* 添加加载状态的动画 */
        .loading-pulse {
            animation: pulse 1.5s infinite ease-in-out;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
    `;
    document.head.appendChild(style);
});

// 预加载专业人士数据的函数
function preloadProfessionalsData() {
    logDebug('开始预加载专业人士数据');
    
    // 获取所有专业人士项
    const proItems = document.querySelectorAll('.pro-item');
    if (!proItems || proItems.length === 0) {
        logDebug('没有找到专业人士项，跳过预加载');
        return;
    }
    
    // 创建一个延迟队列，避免同时发送太多请求
    const queue = [];
    proItems.forEach(item => {
        const proId = item.getAttribute('data-pro-id');
        const tabType = item.getAttribute('data-tab-id');
        
        if (proId && tabType) {
            queue.push({ proId, tabType });
        }
    });
    
    // 如果队列为空，直接返回
    if (queue.length === 0) {
        logDebug('预加载队列为空');
        return;
    }
    
    logDebug(`预加载队列中有 ${queue.length} 个专业人士数据`);
    
    // 使用交错延迟加载数据
    let index = 0;
    function processNext() {
        if (index >= queue.length) {
            logDebug('所有专业人士数据预加载完成');
            return;
        }
        
        const { proId, tabType } = queue[index++];
        const cacheKey = `pro_${proId}_${tabType}`;
        
        // 如果已经有缓存，跳过
        if (sessionStorage.getItem(cacheKey)) {
            logDebug(`专业人士 ${proId} 数据已缓存，跳过预加载`);
            processNext();
            return;
        }
        
        // 先从页面提取基本数据
        const proData = extractProDataFromPage(proId, tabType);
        if (proData) {
            try {
                // 缓存基本数据
                sessionStorage.setItem(cacheKey, JSON.stringify(proData));
                logDebug(`专业人士 ${proId} 基本数据已缓存`);
            } catch (e) {
                logError(`缓存专业人士 ${proId} 基本数据失败`, e);
            }
        }
        
        // 在后台获取完整数据
        setTimeout(() => {
            // 使用低优先级获取完整数据
            fetchProDataInBackground(proId, tabType, cacheKey);
            // 处理下一个
            processNext();
        }, 500); // 每500毫秒处理一个，避免同时发送太多请求
    }
    
    // 开始处理队列
    processNext();
}

// 在后台获取专业人士数据的函数
function fetchProDataInBackground(proId, tabType, cacheKey) {
    logDebug(`在后台获取专业人士 ${proId} 数据`);
    
    // 尝试不同的API路径
    const urls = [
        `/task/api/professionals/${proId}?task_id=${taskId}`,
        `/api/professionals/${proId}?task_id=${taskId}`,
        `/api/tasks/${taskId}/professionals/${proId}`
    ];
    
    // 使用Promise.race尝试所有URL，取第一个成功的结果
    const fetchPromises = urls.map(url => {
        return new Promise((resolve, reject) => {
            fetchWithCsrf(url)
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`请求失败，状态码: ${response.status}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    resolve(data);
                })
                .catch(error => {
                    reject(error);
                });
        });
    });
    
    Promise.race(fetchPromises)
        .then(data => {
            // 缓存数据
            try {
                sessionStorage.setItem(cacheKey, JSON.stringify(data));
                logDebug(`专业人士 ${proId} 完整数据已缓存`);
            } catch (e) {
                logError(`缓存专业人士 ${proId} 完整数据失败`, e);
            }
        })
        .catch(error => {
            logDebug(`在后台获取专业人士 ${proId} 数据失败，将在用户点击时重试`);
        });
}

// 显示聊天区域，隐藏专业人士详情
function showChatArea() {
    const chatAreaContainer = document.getElementById('chat-area-container');
    const proDetailsArea = document.getElementById('pro-details-area');
    const contentAreaTitle = document.getElementById('content-area-title');
    const backToChat = document.getElementById('back-to-chat');
    
    if (chatAreaContainer && proDetailsArea && contentAreaTitle && backToChat) {
        chatAreaContainer.classList.remove('d-none');
        proDetailsArea.classList.add('d-none');
        contentAreaTitle.textContent = '聊天详情';
        backToChat.style.display = 'none';
    } else {
        logError('显示聊天区域时找不到必要的DOM元素');
    }
}