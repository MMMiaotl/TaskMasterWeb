/**
 * 任务表单动画模块
 * 处理表单问题逐个出现的动画效果
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
                    
                    // 滚动到按钮位置
                    setTimeout(() => {
                        nextButton.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'start',
                            inline: 'nearest'
                        });
                    }, 100);
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
    
    // 修改原有的goToStep函数
    const originalGoToStep = window.goToStep;
    window.goToStep = function(stepNumber) {
        // 调用原始函数
        originalGoToStep(stepNumber);
        
        // 获取当前步骤的所有问题
        const currentStep = document.getElementById(`step-${stepNumber}`);
        const questions = currentStep.querySelectorAll('.question-item');
        
        // 重置问题显示状态
        questions.forEach((question, index) => {
            if (index === 0) {
                question.classList.add('active');
                question.classList.remove('hidden');
            } else {
                question.classList.add('hidden');
                question.classList.remove('active');
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
        addInputEventListeners(questions[0]);
    };
    
    // 为所有步骤的第一个问题添加输入字段事件监听
    steps.forEach(step => {
        const questions = step.querySelectorAll('.question-item');
        if (questions.length > 0) {
            addInputEventListeners(questions[0]);
        }
    });
    
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
            // 标记当前问题为已回答
            questionElement.classList.add('answered');
            
            // 特殊处理时间偏好问题，不自动跳转到下一个问题
            if (questionElement.id === 'time-preference-question') {
                return;
            }
            
            // 特殊处理具体日期问题，不自动跳转到下一个问题
            if (questionElement.id === 'specific-date-question') {
                return;
            }
            
            // 特殊处理日期范围问题，不自动跳转到下一个问题
            if (questionElement.id === 'date-range-question') {
                return;
            }
            
            // 获取下一个问题元素
            const nextQuestion = questionElement.nextElementSibling;
            
            // 检查是否有下一个问题项
            if (nextQuestion && nextQuestion.classList.contains('question-item')) {
                console.log('自动跳转到下一个问题:', nextQuestion.id);
                // 显示下一个问题
                nextQuestion.classList.remove('hidden');
                
                // 添加动画类
                nextQuestion.classList.add('fade-in');
                
                // 滚动到新问题，时间与动画时间匹配
                setTimeout(() => {
                    nextQuestion.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start',
                        inline: 'nearest'
                    });
                }, 100); // 减少延迟时间，使滚动与动画同步
                
                // 为下一个问题添加输入字段事件监听
                addInputEventListeners(nextQuestion);
                
                // 如果是最后一个问题，显示下一步按钮
                if (!nextQuestion.nextElementSibling || !nextQuestion.nextElementSibling.classList.contains('question-item')) {
                    const nextButton = questionElement.closest('.form-step').querySelector('.next-step');
                    if (nextButton) {
                        nextButton.classList.remove('hidden');
                        nextButton.classList.add('fade-in');
                        
                        // 滚动到按钮位置
                        setTimeout(() => {
                            nextButton.scrollIntoView({ 
                                behavior: 'smooth', 
                                block: 'start',
                                inline: 'nearest'
                            });
                        }, 100);
                    }
                }
            } else {
                console.log('没有下一个问题项，直接显示下一步按钮');
                // 如果没有下一个问题项，直接显示下一步按钮
                const nextButton = questionElement.closest('.form-step').querySelector('.next-step');
                console.log('下一步按钮元素:', nextButton);
                if (nextButton) {
                    // 移除隐藏类
                    nextButton.classList.remove('hidden');
                    // 添加动画类
                    nextButton.classList.add('fade-in');
                    
                    // 滚动到按钮位置，时间与动画时间匹配
                    setTimeout(() => {
                        nextButton.scrollIntoView({ 
                            behavior: 'smooth', 
                            block: 'start',
                            inline: 'nearest'
                        });
                    }, 100); // 减少延迟时间，使滚动与动画同步
                }
            }
        }
    }
    
    // 验证单个问题
    function validateQuestion(questionElement) {
        let isValid = true;
        
        // 特殊处理服务类别问题
        if (questionElement.id === 'service-category-question') {
            const serviceSelect = questionElement.querySelector('#service_category');
            if (serviceSelect && !serviceSelect.value) {
                serviceSelect.classList.add('is-invalid');
                isValid = false;
            } else if (serviceSelect) {
                serviceSelect.classList.remove('is-invalid');
                
                // 显示下一步按钮
                const nextStepBtn = questionElement.closest('.form-step').querySelector('.next-step');
                nextStepBtn.classList.remove('hidden');
                
                // 平滑滚动到下一步按钮
                setTimeout(() => {
                    nextStepBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
            return isValid;
        }
        
        // 特殊处理时间偏好问题
        if (questionElement.id === 'time-preference-question') {
            const selectedOption = questionElement.querySelector('input[type="radio"]:checked');
            if (!selectedOption) {
                // 标记所有单选按钮为无效
                const radioButtons = questionElement.querySelectorAll('input[type="radio"]');
                radioButtons.forEach(radio => {
                    radio.classList.add('is-invalid');
                });
                isValid = false;
            } else {
                // 移除无效标记
                const radioButtons = questionElement.querySelectorAll('input[type="radio"]');
                radioButtons.forEach(radio => {
                    radio.classList.remove('is-invalid');
                });
            }
            return isValid;
        }
        
        // 特殊处理具体日期问题
        if (questionElement.id === 'specific-date-question') {
            const deadlineInput = questionElement.querySelector('#deadline');
            if (deadlineInput && !deadlineInput.value) {
                deadlineInput.classList.add('is-invalid');
                isValid = false;
            } else if (deadlineInput) {
                deadlineInput.classList.remove('is-invalid');
                
                // 显示下一步按钮
                const nextStepBtn = questionElement.closest('.form-step').querySelector('.next-step');
                nextStepBtn.classList.remove('hidden');
                
                // 平滑滚动到下一步按钮
                setTimeout(() => {
                    nextStepBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
            return isValid;
        }
        
        // 特殊处理日期范围问题
        if (questionElement.id === 'date-range-question') {
            const startDate = questionElement.querySelector('#start_date');
            const endDate = questionElement.querySelector('#end_date');
            
            if (startDate && !startDate.value) {
                startDate.classList.add('is-invalid');
                isValid = false;
            } else if (startDate) {
                startDate.classList.remove('is-invalid');
            }
            
            if (endDate && !endDate.value) {
                endDate.classList.add('is-invalid');
                isValid = false;
            } else if (endDate) {
                endDate.classList.remove('is-invalid');
            }
            
            // 验证结束日期不早于开始日期
            if (startDate && endDate && startDate.value && endDate.value) {
                if (new Date(endDate.value) < new Date(startDate.value)) {
                    endDate.classList.add('is-invalid');
                    // 添加自定义错误消息
                    const feedbackElement = endDate.nextElementSibling.nextElementSibling;
                    if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                        feedbackElement.textContent = '结束日期不能早于开始日期';
                    }
                    isValid = false;
                }
            }
            
            if (isValid) {
                // 显示下一步按钮
                const nextStepBtn = questionElement.closest('.form-step').querySelector('.next-step');
                nextStepBtn.classList.remove('hidden');
                
                // 平滑滚动到下一步按钮
                setTimeout(() => {
                    nextStepBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
            
            return isValid;
        }
        
        // 特殊处理标题问题
        if (questionElement.id === 'title-question') {
            const titleInput = questionElement.querySelector('#title');
            if (titleInput && !titleInput.value.trim()) {
                titleInput.classList.add('is-invalid');
                isValid = false;
            } else if (titleInput) {
                titleInput.classList.remove('is-invalid');
                
                // 获取下一个问题元素
                const nextQuestion = document.getElementById('description-question');
                if (nextQuestion) {
                    // 显示下一个问题
                    nextQuestion.classList.remove('hidden');
                    nextQuestion.classList.add('fade-in');
                    
                    // 平滑滚动到下一个问题
                    setTimeout(() => {
                        nextQuestion.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 300);
                    
                    // 为下一个问题添加输入字段事件监听
                    addInputEventListeners(nextQuestion);
                }
            }
            return isValid;
        }
        
        // 特殊处理描述问题
        if (questionElement.id === 'description-question') {
            const descriptionInput = questionElement.querySelector('#description');
            if (descriptionInput && !descriptionInput.value.trim()) {
                descriptionInput.classList.add('is-invalid');
                isValid = false;
            } else if (descriptionInput) {
                descriptionInput.classList.remove('is-invalid');
                
                // 显示下一步按钮
                const nextStepBtn = questionElement.closest('.form-step').querySelector('.next-step');
                nextStepBtn.classList.remove('hidden');
                
                // 平滑滚动到下一步按钮
                setTimeout(() => {
                    nextStepBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
            return isValid;
        }
        
        // 获取问题中的所有必填输入字段
        const requiredInputs = questionElement.querySelectorAll('input[required], select[required], textarea[required]');
        
        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
    
    // 验证当前步骤
    function validateStep(stepElement) {
        let isValid = true;
        const requiredInputs = stepElement.querySelectorAll('input[required]:not([type="radio"]), select[required], textarea[required]');
        const radioGroups = {};
        
        // 收集单选按钮组
        stepElement.querySelectorAll('input[type="radio"][required]').forEach(radio => {
            if (!radioGroups[radio.name]) {
                radioGroups[radio.name] = [];
            }
            radioGroups[radio.name].push(radio);
        });
        
        // 验证单选按钮组
        for (const groupName in radioGroups) {
            const group = radioGroups[groupName];
            const isChecked = group.some(radio => radio.checked);
            
            if (!isChecked) {
                group.forEach(radio => {
                    radio.classList.add('is-invalid');
                });
                isValid = false;
            } else {
                group.forEach(radio => {
                    radio.classList.remove('is-invalid');
                });
            }
        }
        
        // 验证其他必填输入
        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        // 特殊验证：日期范围
        const timePreference = stepElement.querySelector('input[name="time_preference"]:checked');
        if (timePreference && timePreference.value === 'date_range') {
            const startDate = stepElement.querySelector('#start_date');
            const endDate = stepElement.querySelector('#end_date');
            
            if (startDate && endDate) {
                // 验证开始日期和结束日期都已填写
                if (!startDate.value) {
                    startDate.classList.add('is-invalid');
                    isValid = false;
                } else {
                    startDate.classList.remove('is-invalid');
                }
                
                if (!endDate.value) {
                    endDate.classList.add('is-invalid');
                    isValid = false;
                } else {
                    endDate.classList.remove('is-invalid');
                }
                
                // 验证结束日期不早于开始日期
                if (startDate.value && endDate.value && new Date(endDate.value) < new Date(startDate.value)) {
                    endDate.classList.add('is-invalid');
                    // 添加自定义错误消息
                    const feedbackElement = endDate.nextElementSibling.nextElementSibling;
                    if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                        feedbackElement.textContent = '结束日期不能早于开始日期';
                    }
                    isValid = false;
                }
            }
        }
        
        // 特殊验证：具体日期
        if (timePreference && timePreference.value === 'specific_date') {
            const deadlineInput = stepElement.querySelector('#deadline');
            if (deadlineInput && !deadlineInput.value) {
                deadlineInput.classList.add('is-invalid');
                isValid = false;
            } else if (deadlineInput) {
                deadlineInput.classList.remove('is-invalid');
            }
        }
        
        return isValid;
    }
    
    // 修改原有的validateStep函数
    const originalValidateStep = window.validateStep;
    window.validateStep = function(stepNumber) {
        // 如果原始验证函数存在，调用它
        if (originalValidateStep) {
            return originalValidateStep(stepNumber);
        }
        
        // 否则使用默认验证逻辑
        let isValid = true;
        const currentStep = document.getElementById(`step-${stepNumber}`);
        const requiredInputs = currentStep.querySelectorAll('input[required], select[required], textarea[required]');
        
        requiredInputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    };
    
    // 处理时间偏好选择
    handleTimePreferenceSelection();
});

// 处理时间偏好选择
function handleTimePreferenceSelection() {
    const timePreferenceQuestion = document.getElementById('time-preference-question');
    const specificDateQuestion = document.getElementById('specific-date-question');
    const dateRangeQuestion = document.getElementById('date-range-question');
    const nextStepBtn = timePreferenceQuestion.closest('.form-step').querySelector('.next-step');
    
    // 如果时间偏好问题存在
    if (timePreferenceQuestion) {
        const radioButtons = timePreferenceQuestion.querySelectorAll('input[type="radio"]');
        
        // 检查是否已经有选择
        function checkTimePreference() {
            let selectedOption = timePreferenceQuestion.querySelector('input[type="radio"]:checked');
            
            // 隐藏所有日期问题
            if (specificDateQuestion) specificDateQuestion.classList.add('hidden');
            if (dateRangeQuestion) dateRangeQuestion.classList.add('hidden');
            
            if (selectedOption) {
                // 显示下一步按钮
                nextStepBtn.classList.remove('hidden');
                
                // 根据选择显示相应的日期问题
                if (selectedOption.value === 'specific_date' && specificDateQuestion) {
                    specificDateQuestion.classList.remove('hidden');
                    specificDateQuestion.classList.add('fade-in');
                    
                    // 平滑滚动到具体日期问题
                    setTimeout(() => {
                        specificDateQuestion.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 300);
                } 
                else if (selectedOption.value === 'date_range' && dateRangeQuestion) {
                    dateRangeQuestion.classList.remove('hidden');
                    dateRangeQuestion.classList.add('fade-in');
                    
                    // 平滑滚动到日期范围问题
                    setTimeout(() => {
                        dateRangeQuestion.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 300);
                }
                
                // 平滑滚动到下一步按钮
                setTimeout(() => {
                    nextStepBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 500);
            } else {
                // 如果没有选择，隐藏下一步按钮
                nextStepBtn.classList.add('hidden');
            }
        }
        
        // 初始检查
        checkTimePreference();
        
        // 为每个单选按钮添加事件监听器
        radioButtons.forEach(radio => {
            radio.addEventListener('change', checkTimePreference);
        });
    }
}

// 跳转到指定步骤
function goToStep(stepIndex) {
    // 隐藏所有步骤
    steps.forEach(step => step.classList.add('d-none'));
    
    // 显示目标步骤
    steps[stepIndex].classList.remove('d-none');
    
    // 更新当前步骤索引
    currentStep = stepIndex;
    
    // 更新进度条
    updateProgressBar();
    
    // 如果是第一步，隐藏上一步按钮
    if (currentStep === 0) {
        document.querySelectorAll('.prev-step').forEach(btn => btn.classList.add('d-none'));
    } else {
        document.querySelectorAll('.prev-step').forEach(btn => btn.classList.remove('d-none'));
    }
    
    // 如果是最后一步，显示提交按钮，隐藏下一步按钮
    if (currentStep === steps.length - 1) {
        document.querySelectorAll('.next-step').forEach(btn => btn.classList.add('d-none'));
        document.querySelectorAll('.submit-form').forEach(btn => btn.classList.remove('d-none'));
    } else {
        document.querySelectorAll('.submit-form').forEach(btn => btn.classList.add('d-none'));
        
        // 特殊处理第一步的服务类别问题
        if (currentStep === 0) {
            const serviceSelect = document.querySelector('#service_category');
            if (serviceSelect && serviceSelect.value) {
                document.querySelectorAll('.next-step').forEach(btn => btn.classList.remove('hidden'));
            } else {
                document.querySelectorAll('.next-step').forEach(btn => btn.classList.add('hidden'));
            }
        } 
        // 特殊处理第三步的时间偏好问题
        else if (currentStep === 2) {
            const timePreference = document.querySelector('input[name="time_preference"]:checked');
            if (timePreference) {
                document.querySelectorAll('.next-step').forEach(btn => btn.classList.remove('hidden'));
                
                // 根据时间偏好显示相应的日期问题
                const specificDateQuestion = document.getElementById('specific-date-question');
                const dateRangeQuestion = document.getElementById('date-range-question');
                
                // 隐藏所有日期问题
                if (specificDateQuestion) specificDateQuestion.classList.add('hidden');
                if (dateRangeQuestion) dateRangeQuestion.classList.add('hidden');
                
                // 显示相应的日期问题
                if (timePreference.value === 'specific_date' && specificDateQuestion) {
                    specificDateQuestion.classList.remove('hidden');
                    specificDateQuestion.classList.add('fade-in');
                } 
                else if (timePreference.value === 'date_range' && dateRangeQuestion) {
                    dateRangeQuestion.classList.remove('hidden');
                    dateRangeQuestion.classList.add('fade-in');
                }
            } else {
                document.querySelectorAll('.next-step').forEach(btn => btn.classList.add('hidden'));
            }
        }
        else {
            document.querySelectorAll('.next-step').forEach(btn => btn.classList.remove('hidden'));
        }
    }
    
    // 滚动到顶部
    window.scrollTo(0, 0);
} 