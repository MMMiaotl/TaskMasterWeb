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
            // 验证当前步骤
            if (window.validateStep(currentStep)) {
                // 如果验证通过，前进到下一步
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