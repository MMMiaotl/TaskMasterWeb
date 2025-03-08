/**
 * 任务表单动画模块 - 简洁高级版
 * 处理表单进度和元素过渡的动画效果
 */
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有步骤元素
    const steps = document.querySelectorAll('.form-step');
    
    // 初始化：为每个步骤中的问题添加动画类
    steps.forEach(step => {
        const questions = step.querySelectorAll('.question-item');
        questions.forEach((question, index) => {
            // 第一个问题默认显示，其他问题隐藏
            if (index === 0) {
                question.classList.add('active');
            } else {
                question.classList.add('hidden');
            }
        });
        
        // 初始化：隐藏下一步按钮
        const nextButton = step.querySelector('.next-step');
        if (nextButton) {
            nextButton.classList.add('hidden');
        }
    });
    
    // 初始化问题监控 - 添加MutationObserver监控类变化
    initQuestionMonitoring();
    
    // 初始化时间偏好选择监听
    initTimePreferenceListeners();
    
    // 初始化自动生成功能监听
    initAutoGenerationListeners();
    
    // 为服务类别选择添加特殊处理
    const categorySelect = document.getElementById('service_category');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            if (this.value) {
                // 如果选择了服务类别，显示下一步按钮
                const nextButton = document.querySelector('#step-1 .next-step');
                if (nextButton) {
                    nextButton.classList.remove('hidden');
                    nextButton.classList.add('fade-in');
                    
                    // 平滑滚动到按钮位置
                    setTimeout(() => {
                        smoothScrollToElement(nextButton);
                    }, 50);
                }
            }
        });
        
        // 如果已经选择了服务类别，显示下一步按钮
        if (categorySelect.value) {
            const nextButton = document.querySelector('#step-1 .next-step');
            if (nextButton) {
                nextButton.classList.remove('hidden');
            }
        }
    }
});

// 初始化自动生成功能监听
function initAutoGenerationListeners() {
    console.log('初始化自动生成功能监听');
    
    // 使用MutationObserver监听步骤的可见性变化
    const formSteps = document.querySelectorAll('.form-step');
    const config = { attributes: true, attributeFilter: ['class'] };
    
    // 监听每个步骤的class变化
    formSteps.forEach((step, index) => {
        // 对第4步特殊处理（注意：index是从0开始的，所以第4步的index是3）
        if (step.id === 'step-4') {
            console.log('找到第4步元素:', step.id);
            
            // 创建观察器实例
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'class') {
                        const classList = mutation.target.classList;
                        console.log('第4步类名变化:', Array.from(classList).join(', '));
                        
                        // 如果步骤变为可见（不包含d-none类）
                        if (!classList.contains('d-none')) {
                            console.log('第4步变为可见，准备自动生成标题和描述');
                            
                            // 添加描述文本区域高度自动调整功能
                            initDescriptionTextareaAutoResize();
                            
                            // 延迟执行，确保DOM已完全更新
                            setTimeout(() => {
                                autoGenerateTaskTitleAndDescription();
                            }, 500);
                            
                            // 停止观察，避免重复触发
                            observer.disconnect();
                        }
                    }
                });
            });
            
            // 开始观察
            observer.observe(step, config);
        }
    });
    
    // 查找并监听所有"下一步"按钮的点击事件，作为备份触发机制
    const nextButtons = document.querySelectorAll('.next-step');
    nextButtons.forEach((button, index) => {
        // 我们关心的是第3步的下一步按钮（它会触发跳转到第4步）
        if (button.closest('.form-step') && button.closest('.form-step').id === 'step-3') {
            console.log('找到第3步的下一步按钮');
            button.addEventListener('click', function() {
                console.log('第3步的下一步按钮被点击');
                
                // 延迟执行，确保DOM已完全更新
                setTimeout(() => {
                    const step4 = document.getElementById('step-4');
                    if (step4 && !step4.classList.contains('d-none')) {
                        console.log('检测到第4步已显示，准备自动生成标题和描述');
                        
                        // 添加描述文本区域高度自动调整功能
                        initDescriptionTextareaAutoResize();
                        
                        autoGenerateTaskTitleAndDescription();
                    }
                }, 800);
            });
        }
    });
    
    // 修改原始goToStep函数（直接替换而不是嵌套，避免多层包装）
    if (typeof window.originalGoToStep === 'undefined') {
        console.log('保存原始goToStep函数并替换');
        window.originalGoToStep = window.goToStep;
        
        window.goToStep = function(stepNumber) {
            console.log('调用修改后的goToStep函数，步骤:', stepNumber);
            
            // 调用原始函数
            window.originalGoToStep(stepNumber);
            
            // 处理第四步 - 自动生成标题和描述
            if (stepNumber === 4) {
                console.log('检测到进入第4步，准备自动生成');
                
                // 添加描述文本区域高度自动调整功能
                initDescriptionTextareaAutoResize();
                
                // 延迟执行，确保DOM已更新
                setTimeout(function() {
                    autoGenerateTaskTitleAndDescription();
                }, 500);
            }
            
            // 更新进度条
            updateProgressBar(stepNumber);
            
            // 获取当前步骤的所有问题
            const currentStep = document.getElementById(`step-${stepNumber}`);
            if (!currentStep) return;
            
            // 隐藏所有问题
            const allQuestions = currentStep.querySelectorAll('.question-item');
            allQuestions.forEach(question => {
                if (!question.classList.contains('answered')) {
                    question.classList.add('hidden');
                    question.classList.remove('active');
                }
            });
            
            // 显示第一个问题
            const firstQuestion = allQuestions[0];
            if (firstQuestion) {
                showQuestion(firstQuestion);
            }
            
            // 显示其他已回答的问题
            allQuestions.forEach(question => {
                if (question !== firstQuestion && question.classList.contains('answered')) {
                    question.classList.remove('hidden');
                }
            });
            
            // 隐藏下一步按钮，除非是第一步且已选择服务类别
            const nextButton = currentStep.querySelector('.next-step');
            if (nextButton) {
                if (stepNumber === 1 && categorySelect && categorySelect.value) {
                    nextButton.classList.remove('hidden');
                } else {
                    nextButton.classList.add('hidden');
                }
            }
            
            // 为当前步骤的第一个问题中的输入字段添加事件监听
            if (firstQuestion) {
                addInputEventListeners(firstQuestion);
            }
            
            console.log('切换到步骤: ' + stepNumber);
        };
    }
}

// 为描述文本区域添加自动调整高度的功能
function initDescriptionTextareaAutoResize() {
    const descriptionTextarea = document.getElementById('description');
    if (!descriptionTextarea) {
        console.warn('找不到描述文本区域元素');
        return;
    }
    
    console.log('初始化描述文本区域自动调整高度功能');
    
    // 调整文本区域高度的函数
    function adjustHeight() {
        // 重置高度以获取准确的scrollHeight
        descriptionTextarea.style.height = 'auto';
        
        // 计算新高度，确保至少有最小高度
        const minHeight = 200; // 最小高度与CSS中设置一致
        const newHeight = Math.max(descriptionTextarea.scrollHeight, minHeight);
        
        // 设置新高度
        descriptionTextarea.style.height = `${newHeight}px`;
        console.log('调整描述文本区域高度为:', newHeight);
    }
    
    // 为文本区域添加输入事件监听
    descriptionTextarea.addEventListener('input', adjustHeight);
    
    // 添加焦点事件监听
    descriptionTextarea.addEventListener('focus', adjustHeight);
    
    // 初始调整高度（如果有初始内容）
    if (descriptionTextarea.value) {
        adjustHeight();
    }
    
    // 监听文本区域内容变化（适用于自动生成内容）
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                adjustHeight();
                break;
            }
        }
    });
    
    observer.observe(descriptionTextarea, { 
        attributes: true, 
        attributeFilter: ['value'] 
    });
    
    // 窗口调整大小时也调整高度
    window.addEventListener('resize', adjustHeight);
}

// 初始化问题监控
function initQuestionMonitoring() {
    // 监控所有问题元素的类变化
    const questions = document.querySelectorAll('.question-item');
    
    // 创建MutationObserver实例
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                const question = mutation.target;
                const questionId = question.id;
                const classList = Array.from(question.classList);
                
                console.log(`问题[${questionId}]类变化: ${classList.join(', ')}`);
                
                // 特别检查已回答问题的可见性
                if (classList.includes('answered') && classList.includes('hidden')) {
                    console.warn(`警告: 已回答的问题[${questionId}]被隐藏了!`);
                    // 立即修复 - 移除hidden类
                    setTimeout(() => {
                        question.classList.remove('hidden');
                        console.log(`已修复: 问题[${questionId}]的hidden类已移除`);
                    }, 10);
                }
            }
        });
    });
    
    // 配置observer
    const config = { attributes: true, attributeFilter: ['class'] };
    
    // 开始监控所有问题元素
    questions.forEach(question => {
        observer.observe(question, config);
    });
    
    console.log('问题监控已初始化，总共监控 ' + questions.length + ' 个问题');
}

// 初始化时间偏好选择监听
function initTimePreferenceListeners() {
    // 获取时间偏好问题中的所有单选按钮
    const timePreferenceRadios = document.querySelectorAll('#time-preference-question input[type="radio"]');
    if (!timePreferenceRadios.length) return;
    
    console.log('初始化时间偏好选择监听器');
    
    // 为每个单选按钮添加变更事件监听
    timePreferenceRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            handleTimePreferenceChange(this.value);
        });
    });
    
    // 初始检查 - 如果已有选择，显示对应输入栏
    const selectedTimePreference = document.querySelector('#time-preference-question input[type="radio"]:checked');
    if (selectedTimePreference) {
        handleTimePreferenceChange(selectedTimePreference.value);
    }
}

// 处理时间偏好变更
function handleTimePreferenceChange(preference) {
    console.log('时间偏好已变更为:', preference);
    
    // 获取具体日期和日期范围问题元素
    const specificDateQuestion = document.getElementById('specific-date-question');
    const dateRangeQuestion = document.getElementById('date-range-question');
    
    // 隐藏所有日期输入栏
    if (specificDateQuestion) {
        specificDateQuestion.classList.add('hidden');
        specificDateQuestion.classList.remove('active');
    }
    if (dateRangeQuestion) {
        dateRangeQuestion.classList.add('hidden');
        dateRangeQuestion.classList.remove('active');
    }
    
    // 根据选择显示对应输入栏
    if (preference === 'specific_date' && specificDateQuestion) {
        specificDateQuestion.classList.remove('hidden');
        specificDateQuestion.classList.add('active');
        specificDateQuestion.classList.add('fade-in');
        
        // 平滑滚动到具体日期问题
        setTimeout(() => {
            smoothScrollToElement(specificDateQuestion);
        }, 50);
        
        // 为具体日期问题中的输入添加事件监听
        addInputEventListeners(specificDateQuestion);
        
        // 添加日期变更监听器
        const dateInput = specificDateQuestion.querySelector('input[type="date"]');
        if (dateInput) {
            dateInput.addEventListener('change', function() {
                updateNextButtonForTimeQuestions(specificDateQuestion);
            });
            
            // 初始检查日期是否已有值
            if (dateInput.value) {
                updateNextButtonForTimeQuestions(specificDateQuestion);
            }
        }
    }
    else if (preference === 'date_range' && dateRangeQuestion) {
        dateRangeQuestion.classList.remove('hidden');
        dateRangeQuestion.classList.add('active');
        dateRangeQuestion.classList.add('fade-in');
        
        // 平滑滚动到日期范围问题
        setTimeout(() => {
            smoothScrollToElement(dateRangeQuestion);
        }, 50);
        
        // 为日期范围问题中的输入添加事件监听
        addInputEventListeners(dateRangeQuestion);
        
        // 添加日期范围变更监听器
        const startDateInput = dateRangeQuestion.querySelector('input[name="start_date"]');
        const endDateInput = dateRangeQuestion.querySelector('input[name="end_date"]');
        
        if (startDateInput && endDateInput) {
            // 监听两个日期输入的变化
            startDateInput.addEventListener('change', function() {
                updateNextButtonForTimeQuestions(dateRangeQuestion);
            });
            
            endDateInput.addEventListener('change', function() {
                updateNextButtonForTimeQuestions(dateRangeQuestion);
            });
            
            // 初始检查日期是否已有值
            if (startDateInput.value && endDateInput.value) {
                updateNextButtonForTimeQuestions(dateRangeQuestion);
            }
        }
    }
    else if (preference === 'anytime' || preference === 'not_sure') {
        // 对于这些选项，直接显示下一步按钮
        const timePreferenceQuestion = document.getElementById('time-preference-question');
        if (timePreferenceQuestion) {
            const nextButton = timePreferenceQuestion.closest('.form-step').querySelector('.next-step');
            if (nextButton) {
                nextButton.classList.remove('hidden');
                nextButton.classList.add('fade-in');
                
                // 平滑滚动到按钮位置
                setTimeout(() => {
                    smoothScrollToElement(nextButton);
                }, 50);
            }
        }
    }
}

// 更新下一步按钮的状态
function updateNextButtonForTimeQuestions(questionElement) {
    const questionId = questionElement.id;
    const formStep = questionElement.closest('.form-step');
    
    if (!formStep) return;
    
    const nextButton = formStep.querySelector('.next-step');
    if (!nextButton) return;

    // 根据不同的问题ID进行验证
    if (questionId === 'specific-date-question') {
        // 验证日期是否已选择
        const dateInput = questionElement.querySelector('input[type="date"]');
        if (dateInput && dateInput.value) {
            // 日期已选择，显示下一步按钮
            nextButton.classList.remove('hidden');
            nextButton.classList.add('fade-in');
            
            // 平滑滚动到按钮位置
            setTimeout(() => {
                smoothScrollToElement(nextButton);
            }, 50);
        }
    } 
    else if (questionId === 'date-range-question') {
        // 验证日期范围是否都已选择
        const startDateInput = questionElement.querySelector('input[name="start_date"]');
        const endDateInput = questionElement.querySelector('input[name="end_date"]');
        
        if (startDateInput && endDateInput && startDateInput.value && endDateInput.value) {
            // 检查结束日期是否晚于开始日期
            const startDate = new Date(startDateInput.value);
            const endDate = new Date(endDateInput.value);
            
            if (endDate >= startDate) {
                // 日期范围有效，显示下一步按钮
                nextButton.classList.remove('hidden');
                nextButton.classList.add('fade-in');
                
                // 平滑滚动到按钮位置
                setTimeout(() => {
                    smoothScrollToElement(nextButton);
                }, 50);
            } else {
                console.warn('结束日期早于开始日期');
                // 可以添加错误提示逻辑
            }
        }
    }
}

// 自动生成任务标题和详细描述
function autoGenerateTaskTitleAndDescription() {
    console.log('自动生成任务标题和详细描述开始执行');
    
    // 获取问题元素
    const titleQuestion = document.getElementById('title-question');
    const descriptionQuestion = document.getElementById('description-question');
    const additionalInfoQuestion = document.getElementById('additional-info-question');
    
    if (!titleQuestion || !descriptionQuestion) {
        console.error('找不到标题或描述问题元素');
        return;
    }
    
    // 自动点击生成标题按钮
    const generateTitleBtn = document.getElementById('generate-title-btn');
    if (generateTitleBtn) {
        console.log('点击生成标题按钮');
        generateTitleBtn.click();
        
        // 标记标题问题为已回答
        setTimeout(() => {
            const titleInput = document.getElementById('title');
            if (titleInput && titleInput.value.trim()) {
                console.log('标题已生成:', titleInput.value);
                titleQuestion.classList.add('answered');
                
                // 显示描述问题
                descriptionQuestion.classList.remove('hidden');
                descriptionQuestion.classList.add('active');
                descriptionQuestion.classList.add('fade-in');
                
                // 自动点击生成描述按钮
                const generateDescriptionBtn = document.getElementById('generate-description-btn');
                if (generateDescriptionBtn) {
                    console.log('点击生成描述按钮');
                    generateDescriptionBtn.click();
                    
                    // 标记描述问题为已回答
                    setTimeout(() => {
                        const descriptionInput = document.getElementById('description');
                        if (descriptionInput && descriptionInput.value.trim()) {
                            console.log('描述已生成:', descriptionInput.value.substring(0, 50) + '...');
                            // 添加自动生成类，应用更大的高度样式
                            descriptionInput.classList.add('auto-generated');
                            descriptionQuestion.classList.add('answered');
                            
                            // 显示下一个问题 - 补充信息问题
                            if (additionalInfoQuestion) {
                                additionalInfoQuestion.classList.remove('hidden');
                                additionalInfoQuestion.classList.add('active');
                                additionalInfoQuestion.classList.add('fade-in');
                                
                                // 平滑滚动到补充信息问题
                                smoothScrollToElement(additionalInfoQuestion);
                                
                                console.log('显示补充信息问题');
                            }
                            
                            // 触发表单验证，显示下一步按钮
                            const formStep = titleQuestion.closest('.form-step');
                            if (formStep) {
                                const nextButton = formStep.querySelector('.next-step');
                                if (nextButton) {
                                    nextButton.classList.remove('hidden');
                                    nextButton.classList.add('fade-in');
                                    console.log('显示下一步按钮');
                                }
                            }
                        } else {
                            console.warn('描述未能成功生成');
                        }
                    }, 1000);
                } else {
                    console.error('找不到生成描述按钮');
                }
            } else {
                console.warn('标题未能成功生成');
            }
        }, 1000);
    } else {
        console.error('找不到生成标题按钮');
    }
}

// 更新进度条
function updateProgressBar(stepNumber) {
    const progressBar = document.getElementById('form-progress-bar');
    if (progressBar) {
        const progressPercentage = (stepNumber - 1) * 20;
        progressBar.style.width = `${progressPercentage}%`;
        progressBar.setAttribute('aria-valuenow', progressPercentage);
    }
    
    // 更新步骤指示器的活跃状态
    document.querySelectorAll('.step').forEach(step => {
        const stepNum = parseInt(step.getAttribute('data-step'));
        
        // 移除所有状态类
        step.classList.remove('active', 'completed');
        
        // 添加适当的状态类
        if (stepNum === stepNumber) {
            step.classList.add('active');
        } else if (stepNum < stepNumber) {
            step.classList.add('completed');
        }
    });
}

// 为所有步骤的第一个问题添加输入字段事件监听
const steps = document.querySelectorAll('.form-step');
steps.forEach(step => {
    const questions = step.querySelectorAll('.question-item');
    if (questions.length > 0) {
        addInputEventListeners(questions[0]);
    }
});

// 平滑滚动到元素
function smoothScrollToElement(element) {
    if (!element) return;
    
    element.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center'
    });
}

// 为问题中的输入字段添加事件监听
function addInputEventListeners(questionElement) {
    if (!questionElement) return;
    
    // 获取问题中的所有输入字段
    const textInputs = questionElement.querySelectorAll('input[type="text"], input[type="number"], input[type="date"], textarea');
    const checkboxes = questionElement.querySelectorAll('input[type="checkbox"]');
    const radios = questionElement.querySelectorAll('input[type="radio"]');
    const selects = questionElement.querySelectorAll('select');
    
    // 为文本、数字和日期输入添加事件监听
    textInputs.forEach(input => {
        input.addEventListener('input', function() {
            handleInputChange(questionElement);
        });
        
        // 如果已有值，立即触发验证
        if (input.value.trim()) {
            handleInputChange(questionElement);
        }
    });
    
    // 为复选框添加事件监听
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            handleInputChange(questionElement);
        });
        
        // 如果已选中，立即触发验证
        if (checkbox.checked) {
            handleInputChange(questionElement);
        }
    });
    
    // 为单选按钮添加事件监听
    radios.forEach(radio => {
        radio.addEventListener('change', function() {
            handleInputChange(questionElement);
        });
        
        // 如果已选中，立即触发验证
        if (radio.checked) {
            handleInputChange(questionElement);
        }
    });
    
    // 为下拉选择添加事件监听
    selects.forEach(select => {
        select.addEventListener('change', function() {
            handleInputChange(questionElement);
        });
        
        // 如果已有选择，立即触发验证
        if (select.value) {
            handleInputChange(questionElement);
        }
    });
}

// 处理输入字段变化
function handleInputChange(questionElement) {
    // 验证当前问题
    if (validateQuestion(questionElement)) {
        // 标记当前问题为已回答，并移除active类
        questionElement.classList.add('answered');
        
        // 特殊处理：这些问题不自动跳转到下一个问题 - 由于添加了专门的处理函数，可以移除time-preference-question
        const nonAutoAdvanceQuestions = [
            'specific-date-question',
            'date-range-question'
        ];
        
        if (nonAutoAdvanceQuestions.includes(questionElement.id)) {
            // 更新下一步按钮的状态
            updateNextButtonForTimeQuestions(questionElement);
            return;
        }
        
        // 特殊处理搬家地址问题 - 必须同时填写搬出和搬入地址
        if (questionElement.id === 'moving-address-question') {
            const movingOutAddress = questionElement.querySelector('#moving_out_address');
            const movingInAddress = questionElement.querySelector('#moving_in_address');
            
            // 如果任一地址未填写，不进行跳转
            if (!movingOutAddress || !movingOutAddress.value.trim() || 
                !movingInAddress || !movingInAddress.value.trim()) {
                return;
            }
            
            console.log('搬家地址已填写完毕，准备显示下一个问题');
        }
        
        // 特殊处理其他多字段问题
        // 检查是否为多字段问题并且有未填写的必填字段
        if (hasMultipleRequiredFields(questionElement) && !areAllFieldsInQuestionFilled(questionElement)) {
            return;
        }
        
        // 获取下一个问题
        const nextQuestion = getNextQuestion(questionElement);
        
        if (nextQuestion) {
            // 显示下一个问题
            showQuestion(nextQuestion);
            
            // 平滑滚动到新问题
            setTimeout(() => {
                smoothScrollToElement(nextQuestion);
            }, 50);
            
            // 为下一个问题添加输入字段事件监听
            addInputEventListeners(nextQuestion);
            
            console.log('显示下一个问题: ' + nextQuestion.id);
        } else {
            // 如果没有下一个问题，显示下一步按钮
            showNextButton(questionElement);
            
            console.log('没有下一个问题，显示下一步按钮');
        }
    }
}

// 显示问题元素(同时不隐藏其他问题)
function showQuestion(questionElement) {
    if (!questionElement) return;
    
    // 移除隐藏类
    questionElement.classList.remove('hidden');
    
    // 添加活跃类和动画类
    questionElement.classList.add('active');
    questionElement.classList.add('fade-in');
    
    // 在同一容器内移除其他问题的active类(但不隐藏它们)
    const container = getParentQuestionContainer(questionElement);
    if (container) {
        const allQuestions = Array.from(container.querySelectorAll('.question-item:not(.hidden)'));
        allQuestions.forEach(q => {
            if (q !== questionElement) {
                q.classList.remove('active');
            }
        });
    }
    
    console.log('问题已显示: ' + questionElement.id);
}

// 检查问题元素是否包含多个必填字段
function hasMultipleRequiredFields(questionElement) {
    if (!questionElement) return false;
    
    const requiredFields = questionElement.querySelectorAll('input[required], textarea[required], select[required]');
    return requiredFields.length > 1;
}

// 检查问题元素中的所有字段是否都已填写
function areAllFieldsInQuestionFilled(questionElement) {
    if (!questionElement) return true;
    
    // 获取所有输入类型字段
    const inputFields = questionElement.querySelectorAll('input:not([type="radio"]):not([type="checkbox"]), textarea, select');
    for (const field of inputFields) {
        // 如果是必填字段且为空
        if (field.hasAttribute('required') && !field.value.trim()) {
            return false;
        }
    }
    
    // 检查单选按钮组
    const radioGroups = {};
    questionElement.querySelectorAll('input[type="radio"][required]').forEach(radio => {
        if (!radioGroups[radio.name]) {
            radioGroups[radio.name] = [];
        }
        radioGroups[radio.name].push(radio);
    });
    
    for (const groupName in radioGroups) {
        const isAnyChecked = radioGroups[groupName].some(radio => radio.checked);
        if (!isAnyChecked) {
            return false;
        }
    }
    
    // 检查必填的复选框
    const requiredCheckboxes = questionElement.querySelectorAll('input[type="checkbox"][required]');
    for (const checkbox of requiredCheckboxes) {
        if (!checkbox.checked) {
            return false;
        }
    }
    
    return true;
}

// 获取下一个问题
function getNextQuestion(questionElement) {
    // 先尝试获取同一容器内的下一个问题
    const container = getParentQuestionContainer(questionElement);
    const allQuestions = Array.from(container.querySelectorAll('.question-item'));
    const currentIndex = allQuestions.indexOf(questionElement);
    
    // 如果当前问题不是容器内的最后一个问题，返回下一个问题
    if (currentIndex !== -1 && currentIndex < allQuestions.length - 1) {
        return allQuestions[currentIndex + 1];
    }
    
    // 如果当前问题是容器内的最后一个问题，尝试获取下一个容器的第一个问题
    const nextContainer = getNextQuestionContainer(container);
    if (nextContainer) {
        const nextContainerQuestions = nextContainer.querySelectorAll('.question-item');
        if (nextContainerQuestions.length > 0) {
            return nextContainerQuestions[0];
        }
    }
    
    // 如果没有下一个容器或下一个容器没有问题，返回null
    return null;
}

// 获取问题元素中的所有必填字段
function getAllRequiredFields(questionElement) {
    if (!questionElement) return [];
    
    const requiredInputs = questionElement.querySelectorAll('input[required], textarea[required], select[required]');
    const radioGroups = {};
    
    // 收集单选按钮组
    questionElement.querySelectorAll('input[type="radio"][required]').forEach(radio => {
        if (!radioGroups[radio.name]) {
            radioGroups[radio.name] = [];
        }
        radioGroups[radio.name].push(radio);
    });
    
    return {
        inputs: Array.from(requiredInputs),
        radioGroups: radioGroups
    };
}

// 检查是否所有必填字段都已填写
function areAllRequiredFieldsFilled(fields) {
    if (!fields) return true;
    
    // 检查常规输入字段
    const allInputsFilled = fields.inputs.every(input => {
        // 跳过单选按钮，因为它们已在radioGroups中处理
        if (input.type === 'radio') return true;
        return input.value.trim() !== '';
    });
    
    if (!allInputsFilled) return false;
    
    // 检查单选按钮组
    for (const groupName in fields.radioGroups) {
        const isAnyChecked = fields.radioGroups[groupName].some(radio => radio.checked);
        if (!isAnyChecked) return false;
    }
    
    return true;
}

// 获取问题所在的父容器（服务字段组或步骤）
function getParentQuestionContainer(questionElement) {
    // 首先检查父元素是否是服务字段容器
    const serviceFieldsParent = questionElement.closest('.service-fields:not(.d-none)');
    if (serviceFieldsParent) {
        return serviceFieldsParent;
    }
    
    // 如果不是服务字段容器，则返回所在的步骤
    return questionElement.closest('.form-step');
}

// 获取容器内当前可见的所有问题
function getVisibleQuestionsInContainer(container) {
    if (!container) return [];
    return Array.from(container.querySelectorAll('.question-item:not(.hidden)'));
}

// 检查所有问题是否都已回答
function areAllQuestionsAnswered(questions) {
    if (!questions || questions.length === 0) return true;
    
    // 检查每个问题是否已回答或隐藏
    return questions.every(question => {
        // 如果问题被隐藏，视为已回答
        if (question.classList.contains('hidden')) return true;
        
        // 获取问题中的所有必填字段
        const requiredFields = getAllRequiredFields(question);
        
        // 检查所有必填字段是否已填写
        return areAllRequiredFieldsFilled(requiredFields);
    });
}

// 获取下一个问题容器
function getNextQuestionContainer(container) {
    // 如果是服务字段容器
    if (container.classList.contains('service-fields')) {
        // 在同一个步骤中查找下一个服务字段容器
        const step = container.closest('.form-step');
        const allServiceContainers = Array.from(step.querySelectorAll('.service-fields:not(.d-none)'));
        const currentIndex = allServiceContainers.indexOf(container);
        
        if (currentIndex !== -1 && currentIndex < allServiceContainers.length - 1) {
            return allServiceContainers[currentIndex + 1];
        }
        
        // 如果没有下一个服务字段容器，返回null
        return null;
    }
    
    // 如果是步骤容器
    if (container.classList.contains('form-step')) {
        // 查找下一个步骤
        const allSteps = Array.from(document.querySelectorAll('.form-step'));
        const currentIndex = allSteps.indexOf(container);
        
        if (currentIndex !== -1 && currentIndex < allSteps.length - 1) {
            return allSteps[currentIndex + 1];
        }
    }
    
    return null;
}

// 显示下一步按钮
function showNextButton(questionElement) {
    const nextButton = questionElement.closest('.form-step').querySelector('.next-step');
    if (nextButton) {
        // 移除隐藏类
        nextButton.classList.remove('hidden');
        // 添加动画类
        nextButton.classList.add('fade-in');
        
        // 平滑滚动到按钮位置
        setTimeout(() => {
            smoothScrollToElement(nextButton);
        }, 50);
    }
}

// 验证单个问题
function validateQuestion(questionElement) {
    // 根据问题的特殊ID进行不同的验证逻辑
    const questionId = questionElement.id;
    
    // 特殊验证逻辑
    switch(questionId) {
        case 'service-category-question':
            return validateServiceCategory();
        case 'time-preference-question':
            return validateTimePreference();
        case 'specific-date-question':
            return validateSpecificDate();
        case 'date-range-question':
            return validateDateRange();
        case 'budget-question':
            return validateBudget();
        case 'title-question':
            return validateTitle();
        case 'description-question':
            return validateDescription();
        default:
            // 默认验证逻辑：检查必填字段是否有值
            return validateRequired(questionElement);
    }
}

// 默认验证：检查必填字段
function validateRequired(questionElement) {
    let isValid = true;
    
    // 获取所有必填输入字段
    const requiredInputs = questionElement.querySelectorAll('input[required], textarea[required], select[required]');
    
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
        }
    });
    
    // 获取必填的复选框和单选按钮组
    const checkboxGroups = questionElement.querySelectorAll('.checkbox-group[data-required="true"]');
    const radioGroups = questionElement.querySelectorAll('.radio-group[data-required="true"]');
    
    // 验证复选框组
    checkboxGroups.forEach(group => {
        const checkedBoxes = group.querySelectorAll('input[type="checkbox"]:checked');
        if (checkedBoxes.length === 0) {
            isValid = false;
        }
    });
    
    // 验证单选按钮组
    radioGroups.forEach(group => {
        const checkedRadios = group.querySelectorAll('input[type="radio"]:checked');
        if (checkedRadios.length === 0) {
            isValid = false;
        }
    });
    
    return isValid;
}

// 服务类别验证
function validateServiceCategory() {
    const select = document.getElementById('service_category');
    return select && select.value;
}

// 时间偏好验证
function validateTimePreference() {
    const radioGroup = document.querySelector('#time-preference-question .radio-group');
    const checkedRadio = radioGroup ? radioGroup.querySelector('input[type="radio"]:checked') : null;
    return checkedRadio !== null;
}

// 具体日期验证
function validateSpecificDate() {
    const dateInput = document.getElementById('specific_date');
    return dateInput && dateInput.value;
}

// 日期范围验证
function validateDateRange() {
    const startDate = document.getElementById('date_range_start');
    const endDate = document.getElementById('date_range_end');
    return startDate && endDate && startDate.value && endDate.value;
}

// 预算验证
function validateBudget() {
    const budgetInput = document.getElementById('budget');
    return budgetInput && budgetInput.value && !isNaN(parseFloat(budgetInput.value));
}

// 标题验证
function validateTitle() {
    const titleInput = document.getElementById('title');
    return titleInput && titleInput.value.trim().length >= 5;
}

// 描述验证
function validateDescription() {
    const descriptionInput = document.getElementById('description');
    return descriptionInput && descriptionInput.value.trim().length >= 20;
} 