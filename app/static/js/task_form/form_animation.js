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
    
    // 修改原有的goToStep函数
    const originalGoToStep = window.goToStep;
    window.goToStep = function(stepNumber) {
        // 调用原始函数
        originalGoToStep(stepNumber);
        
        // 更新进度条
        updateProgressBar(stepNumber);
        
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
            // 标记当前问题为已回答
            questionElement.classList.add('answered');
            
            // 特殊处理：这些问题不自动跳转到下一个问题
            const nonAutoAdvanceQuestions = [
                'time-preference-question',
                'specific-date-question',
                'date-range-question'
            ];
            
            if (nonAutoAdvanceQuestions.includes(questionElement.id)) {
                return;
            }
            
            // 获取下一个问题元素
            const nextQuestion = questionElement.nextElementSibling;
            
            // 检查是否有下一个问题项
            if (nextQuestion && nextQuestion.classList.contains('question-item')) {
                // 显示下一个问题
                nextQuestion.classList.remove('hidden');
                
                // 添加动画类
                nextQuestion.classList.add('fade-in');
                
                // 平滑滚动到新问题
                setTimeout(() => {
                    smoothScrollToElement(nextQuestion);
                }, 50);
                
                // 为下一个问题添加输入字段事件监听
                addInputEventListeners(nextQuestion);
                
                // 如果是最后一个问题，显示下一步按钮
                if (!nextQuestion.nextElementSibling || !nextQuestion.nextElementSibling.classList.contains('question-item')) {
                    showNextButton(questionElement);
                }
            } else {
                // 如果没有下一个问题项，直接显示下一步按钮
                showNextButton(questionElement);
            }
        }
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
}); 