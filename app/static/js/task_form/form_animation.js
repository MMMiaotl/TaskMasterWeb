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
    });
    
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
        // 获取问题中的所有输入字段
        const inputs = questionElement.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // 根据输入类型添加不同的事件监听
            if (input.type === 'text' || input.type === 'number' || input.type === 'date' || input.tagName.toLowerCase() === 'textarea') {
                // 为文本、数字、日期输入和文本区域添加输入和失焦事件
                input.addEventListener('blur', function() {
                    handleInputChange(questionElement);
                });
                
                // 添加延迟输入事件（用户停止输入后）
                let typingTimer;
                input.addEventListener('input', function() {
                    clearTimeout(typingTimer);
                    typingTimer = setTimeout(function() {
                        handleInputChange(questionElement);
                    }, 1000); // 1秒后触发
                });
            } else if (input.type === 'checkbox' || input.type === 'radio') {
                // 为复选框和单选按钮添加变化事件
                input.addEventListener('change', function() {
                    handleInputChange(questionElement);
                });
            } else if (input.tagName.toLowerCase() === 'select') {
                // 为下拉菜单添加变化事件
                input.addEventListener('change', function() {
                    handleInputChange(questionElement);
                });
            }
        });
    }
    
    // 处理输入字段变化
    function handleInputChange(questionElement) {
        // 验证当前问题
        if (validateQuestion(questionElement)) {
            // 获取下一个问题元素
            const nextQuestion = questionElement.nextElementSibling;
            
            // 标记当前问题为已回答
            questionElement.classList.add('answered');
            
            // 检查是否有下一个问题项
            if (nextQuestion && nextQuestion.classList.contains('question-item')) {
                console.log('自动跳转到下一个问题');
                // 显示下一个问题
                nextQuestion.classList.remove('hidden');
                
                // 添加动画类
                nextQuestion.classList.add('fade-in');
                
                // 滚动到新问题
                setTimeout(() => {
                    nextQuestion.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 300);
                
                // 为下一个问题添加输入字段事件监听
                addInputEventListeners(nextQuestion);
                
                // 如果是最后一个问题，显示下一步按钮
                if (!nextQuestion.nextElementSibling || !nextQuestion.nextElementSibling.classList.contains('question-item')) {
                    const stepButtons = questionElement.closest('.form-step').querySelector('.step-buttons');
                    if (stepButtons) {
                        stepButtons.classList.remove('hidden');
                        stepButtons.classList.add('fade-in');
                    }
                }
            } else {
                console.log('没有下一个问题项，直接显示步骤按钮');
                // 如果没有下一个问题项，直接显示步骤按钮
                const stepButtons = questionElement.closest('.form-step').querySelector('.step-buttons');
                console.log('步骤按钮元素:', stepButtons);
                if (stepButtons) {
                    // 确保按钮可见
                    stepButtons.style.display = 'flex';
                    stepButtons.style.opacity = '1';
                    stepButtons.style.height = 'auto';
                    stepButtons.style.margin = '2rem 0 0 0';
                    stepButtons.style.padding = '0';
                    stepButtons.style.overflow = 'visible';
                    stepButtons.style.pointerEvents = 'auto';
                    
                    // 移除隐藏类
                    stepButtons.classList.remove('hidden');
                    // 添加动画类
                    stepButtons.classList.add('fade-in');
                    
                    // 滚动到按钮位置
                    setTimeout(() => {
                        stepButtons.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 300);
                }
            }
        }
    }
    
    // 验证单个问题
    function validateQuestion(questionElement) {
        let isValid = true;
        
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
        
        // 特殊处理：如果是服务类别选择问题
        if (questionElement.id === 'category-question') {
            const categorySelect = document.getElementById('service_category');
            if (!categorySelect.value) {
                categorySelect.classList.add('is-invalid');
                isValid = false;
            } else {
                categorySelect.classList.remove('is-invalid');
                // 如果选择了服务类别，显示对应的特定字段
                if (typeof window.showServiceSpecificFields === 'function') {
                    window.showServiceSpecificFields(categorySelect.value);
                }
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
}); 