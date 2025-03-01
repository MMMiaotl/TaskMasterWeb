/**
 * 任务表单导航模块
 * 处理表单步骤之间的导航和进度显示
 */
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有步骤元素
    const steps = document.querySelectorAll('.form-step');
    const progressBar = document.getElementById('form-progress-bar');
    const stepIndicators = document.querySelectorAll('.step');
    const form = document.getElementById('task-form');
    
    // 当前步骤
    let currentStep = 1;
    const totalSteps = steps.length;
    
    // 下一步按钮点击事件
    document.querySelectorAll('.next-step').forEach(button => {
        button.addEventListener('click', function() {
            console.log('点击下一步按钮，当前步骤:', currentStep);
            
            // 获取当前步骤元素
            const stepElement = document.getElementById(`step-${currentStep}`);
            console.log('步骤元素:', stepElement);
            
            if (!stepElement) {
                console.error('找不到步骤元素:', `step-${currentStep}`);
                return;
            }
            
            // 验证当前步骤
            const isValid = window.validateStep(currentStep);
            console.log('验证结果:', isValid);
            
            if (isValid) {
                // 特殊处理第三步的日期范围验证
                if (currentStep === 3) {
                    console.log('处理第三步的日期范围验证');
                    const timePreference = stepElement.querySelector('input[name="time_preference"]:checked');
                    console.log('时间偏好:', timePreference ? timePreference.value : 'none');
                    
                    if (timePreference && timePreference.value === 'date_range') {
                        const startDate = stepElement.querySelector('#start_date');
                        const endDate = stepElement.querySelector('#end_date');
                        console.log('开始日期:', startDate ? startDate.value : 'none');
                        console.log('结束日期:', endDate ? endDate.value : 'none');
                        
                        // 确保开始日期和结束日期都已填写
                        if (startDate && endDate && startDate.value && endDate.value) {
                            // 确保结束日期不早于开始日期
                            const startDateObj = new Date(startDate.value);
                            const endDateObj = new Date(endDate.value);
                            console.log('开始日期对象:', startDateObj);
                            console.log('结束日期对象:', endDateObj);
                            console.log('结束日期 >= 开始日期:', endDateObj >= startDateObj);
                            
                            if (endDateObj >= startDateObj) {
                                // 验证通过，前进到下一步
                                console.log('日期范围验证通过，前进到下一步');
                                if (currentStep < totalSteps) {
                                    goToStep(currentStep + 1);
                                }
                                return; // 提前返回，避免重复执行
                            } else {
                                // 显示错误提示
                                console.log('结束日期早于开始日期，显示错误提示');
                                endDate.classList.add('is-invalid');
                                const feedbackElement = endDate.nextElementSibling;
                                if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                                    feedbackElement.textContent = '结束日期不能早于开始日期';
                                }
                                return; // 验证失败，不跳转
                            }
                        }
                    }
                }
                
                // 如果验证通过，前进到下一步
                console.log('验证通过，前进到下一步');
                if (currentStep < totalSteps) {
                    goToStep(currentStep + 1);
                }
            }
        });
    });
    
    // 上一步按钮点击事件
    document.querySelectorAll('.prev-step').forEach(button => {
        button.addEventListener('click', function() {
            if (currentStep > 1) {
                goToStep(currentStep - 1);
            }
        });
    });
    
    // 跳转到指定步骤
    function goToStep(stepNumber) {
        // 隐藏所有步骤
        steps.forEach(step => {
            step.classList.add('d-none');
        });
        
        // 显示目标步骤
        document.getElementById(`step-${stepNumber}`).classList.remove('d-none');
        
        // 更新进度条
        const progress = (stepNumber - 1) / (totalSteps - 1) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
        
        // 更新步骤指示器
        stepIndicators.forEach((indicator, index) => {
            const step = index + 1;
            indicator.classList.remove('active', 'completed');
            
            if (step === stepNumber) {
                indicator.classList.add('active');
            } else if (step < stepNumber) {
                indicator.classList.add('completed');
            }
        });
        
        // 更新当前步骤
        currentStep = stepNumber;
        
        // 如果是最后一步，更新摘要信息
        if (currentStep === totalSteps) {
            window.updateSummary();
        }
        
        // 特殊处理第一步的服务类别问题
        if (currentStep === 1) {
            const serviceSelect = document.querySelector('#service_category');
            if (serviceSelect && serviceSelect.value) {
                document.querySelectorAll('.next-step').forEach(btn => btn.classList.remove('hidden'));
            } else {
                document.querySelectorAll('.next-step').forEach(btn => btn.classList.add('hidden'));
            }
        } 
        // 特殊处理第三步的时间偏好问题
        else if (currentStep === 3) {
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
                    
                    // 确保日期范围选项的下一步按钮可点击
                    const startDate = document.querySelector('#start_date');
                    const endDate = document.querySelector('#end_date');
                    if (startDate && endDate && startDate.value && endDate.value) {
                        if (new Date(endDate.value) >= new Date(startDate.value)) {
                            document.querySelectorAll('.next-step').forEach(btn => {
                                btn.classList.remove('hidden');
                                btn.disabled = false;
                            });
                        }
                    }
                }
            } else {
                document.querySelectorAll('.next-step').forEach(btn => btn.classList.add('hidden'));
            }
        }
        
        // 滚动到顶部
        window.scrollTo(0, 0);
    }
    
    // 表单提交验证
    form.addEventListener('submit', function(event) {
        if (!window.validateStep(currentStep)) {
            event.preventDefault();
            event.stopPropagation();
        }
    });
    
    // 导出全局函数
    window.goToStep = goToStep;
}); 