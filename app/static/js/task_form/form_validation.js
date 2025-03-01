/**
 * 任务表单验证模块
 * 处理表单字段的验证逻辑
 */
document.addEventListener('DOMContentLoaded', function() {
    // 服务类别选择变化事件
    const categorySelect = document.getElementById('service_category');
    categorySelect.addEventListener('change', function() {
        showServiceSpecificFields(this.value);
    });
    
    // 初始化时显示对应的服务特定字段
    if (categorySelect.value) {
        showServiceSpecificFields(categorySelect.value);
    }
    
    // 设置最小日期为当前日期
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('deadline').min = today;
    
    // 验证当前步骤
    function validateStep(stepNumber) {
        let isValid = true;
        const currentStepElement = document.getElementById(`step-${stepNumber}`);
        
        // 根据当前步骤验证不同的字段
        if (stepNumber === 1) {
            const categorySelect = document.getElementById('service_category');
            if (!categorySelect.value) {
                categorySelect.classList.add('is-invalid');
                isValid = false;
            } else {
                categorySelect.classList.remove('is-invalid');
                
                // 如果选择了服务类别，显示对应的特定字段
                showServiceSpecificFields(categorySelect.value);
            }
        } else if (stepNumber === 2) {
            // 验证服务特定字段
            const categorySelect = document.getElementById('service_category');
            if (categorySelect.value) {
                const parts = categorySelect.value.split('.');
                if (parts.length === 2) {
                    const subCategory = parts[1];
                    
                    // 根据子类别验证特定字段
                    if (subCategory === 'moving') {
                        // 验证搬家地址
                        const outAddress = document.getElementById('moving_out_address');
                        const inAddress = document.getElementById('moving_in_address');
                        
                        // 验证搬出地址格式
                        if (outAddress && outAddress.value.trim()) {
                            const outAddressPattern = /^[0-9]{4}[A-Za-z]{2}$/;
                            if (!outAddressPattern.test(outAddress.value.trim())) {
                                outAddress.classList.add('is-invalid');
                                isValid = false;
                            } else {
                                outAddress.classList.remove('is-invalid');
                            }
                        } else if (outAddress) {
                            outAddress.classList.add('is-invalid');
                            isValid = false;
                        }
                        
                        // 验证搬入地址格式
                        if (inAddress && inAddress.value.trim()) {
                            const inAddressPattern = /^[0-9]{4}[A-Za-z]{2}$/;
                            if (!inAddressPattern.test(inAddress.value.trim())) {
                                inAddress.classList.add('is-invalid');
                                isValid = false;
                            } else {
                                inAddress.classList.remove('is-invalid');
                            }
                        } else if (inAddress) {
                            inAddress.classList.add('is-invalid');
                            isValid = false;
                        }
                        
                        // 验证房屋类型
                        const outHouseType = document.getElementById('moving_out_house_type');
                        const inHouseType = document.getElementById('moving_in_house_type');
                        
                        if (outHouseType && !outHouseType.value) {
                            outHouseType.classList.add('is-invalid');
                            isValid = false;
                        } else if (outHouseType) {
                            outHouseType.classList.remove('is-invalid');
                        }
                        
                        if (inHouseType && !inHouseType.value) {
                            inHouseType.classList.add('is-invalid');
                            isValid = false;
                        } else if (inHouseType) {
                            inHouseType.classList.remove('is-invalid');
                        }
                        
                        // 验证物品数量范围
                        const itemQuantityRange = document.getElementById('moving_item_quantity_range');
                        if (itemQuantityRange && !itemQuantityRange.value) {
                            itemQuantityRange.classList.add('is-invalid');
                            isValid = false;
                        } else if (itemQuantityRange) {
                            itemQuantityRange.classList.remove('is-invalid');
                        }
                    } else if (subCategory === 'pickup') {
                        const passengers = document.getElementById('pickup_passengers');
                        
                        if (!passengers.value || parseInt(passengers.value) < 1) {
                            passengers.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            passengers.classList.remove('is-invalid');
                        }
                    } else if (subCategory === 'repair') {
                        const area = document.getElementById('repair_area');
                        const repairType = document.getElementById('repair_type');
                        
                        if (!area.value || parseFloat(area.value) <= 0) {
                            area.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            area.classList.remove('is-invalid');
                        }
                        
                        if (!repairType.value) {
                            repairType.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            repairType.classList.remove('is-invalid');
                        }
                    } else if (subCategory === 'legal') {
                        const caseType = document.getElementById('legal_case_type');
                        
                        if (!caseType.value) {
                            caseType.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            caseType.classList.remove('is-invalid');
                        }
                    } else if (subCategory === 'education') {
                        const targetCountry = document.getElementById('education_target_country');
                        const studyLevel = document.getElementById('education_study_level');
                        
                        if (!targetCountry.value) {
                            targetCountry.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            targetCountry.classList.remove('is-invalid');
                        }
                        
                        if (!studyLevel.value) {
                            studyLevel.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            studyLevel.classList.remove('is-invalid');
                        }
                    } else if (subCategory === 'repair_service') {
                        const repairType = document.getElementById('repair_service_type');
                        const itemAge = document.getElementById('repair_service_item_age');
                        
                        if (!repairType.value) {
                            repairType.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            repairType.classList.remove('is-invalid');
                        }
                        
                        if (!itemAge.value) {
                            itemAge.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            itemAge.classList.remove('is-invalid');
                        }
                    } else if (subCategory === 'other_business') {
                        const serviceType = document.getElementById('other_business_service_type');
                        const projectScale = document.getElementById('other_business_project_scale');
                        
                        if (!serviceType.value) {
                            serviceType.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            serviceType.classList.remove('is-invalid');
                        }
                        
                        if (!projectScale.value) {
                            projectScale.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            projectScale.classList.remove('is-invalid');
                        }
                    }
                }
            }
        } else if (stepNumber === 3) {
            const deadline = document.getElementById('deadline');
            
            if (!deadline.value) {
                deadline.classList.add('is-invalid');
                isValid = false;
            } else {
                deadline.classList.remove('is-invalid');
            }
            
            // 预算和地点是可选的，不需要验证
        } else if (stepNumber === 4) {
            // 第4步中的字段都是可选的，不需要验证
            // 如果用户没有填写，自动生成标题和描述
            const title = document.getElementById('title');
            const description = document.getElementById('description');
            
            if (!title.value) {
                window.generateTitle();
            }
            
            if (!description.value) {
                window.generateDescription();
            }
        }
        
        return isValid;
    }
    
    // 显示服务特定字段
    function showServiceSpecificFields(categoryValue) {
        // 隐藏所有服务特定字段
        document.querySelectorAll('.service-fields').forEach(field => {
            field.classList.add('d-none');
        });
        
        // 如果选择了服务类别，显示对应的特定字段
        if (categoryValue) {
            const parts = categoryValue.split('.');
            if (parts.length === 2) {
                const subCategory = parts[1];
                const fieldId = `${subCategory}-fields`;
                const field = document.getElementById(fieldId);
                
                if (field) {
                    field.classList.remove('d-none');
                }
            }
        }
    }
    
    // 导出全局函数
    window.validateStep = validateStep;
    window.showServiceSpecificFields = showServiceSpecificFields;
}); 