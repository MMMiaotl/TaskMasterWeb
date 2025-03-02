/**
 * 任务表单摘要更新模块
 * 处理确认步骤中摘要信息的更新
 */
document.addEventListener('DOMContentLoaded', function() {
    // 更新摘要信息
    function updateSummary() {
        const categorySelect = document.getElementById('service_category');
        const categoryText = categorySelect.options[categorySelect.selectedIndex].text;
        document.getElementById('summary-category').textContent = categoryText;
        
        document.getElementById('summary-title').textContent = document.getElementById('title').value || '(未提供)';
        document.getElementById('summary-location').textContent = document.getElementById('location').value || '(未提供)';
        
        const deadline = document.getElementById('deadline').value;
        if (deadline) {
            const formattedDate = new Date(deadline).toLocaleDateString('zh-CN');
            document.getElementById('summary-deadline').textContent = formattedDate;
        } else {
            document.getElementById('summary-deadline').textContent = '(未设置)';
        }
        
        const budget = document.getElementById('budget').value;
        document.getElementById('summary-budget').textContent = budget ? `€${budget}` : '(未提供)';
        
        document.getElementById('summary-description').textContent = document.getElementById('description').value || '(未提供)';
        
        // 显示补充信息（如果有）
        const additionalInfo = document.getElementById('additional_info').value;
        if (additionalInfo) {
            document.getElementById('summary-additional-info-container').classList.remove('d-none');
            document.getElementById('summary-additional-info').textContent = additionalInfo;
        } else {
            document.getElementById('summary-additional-info-container').classList.add('d-none');
        }
        
        // 显示图片信息（如果有）
        const taskImages = document.getElementById('task_images').files;
        if (taskImages.length > 0) {
            document.getElementById('summary-images-container').classList.remove('d-none');
            document.getElementById('summary-images').textContent = `已上传 ${taskImages.length} 张图片`;
        } else {
            document.getElementById('summary-images-container').classList.add('d-none');
        }
        
        // 隐藏所有服务特定字段摘要
        document.querySelectorAll('.service-summary').forEach(summary => {
            summary.classList.add('d-none');
        });
        
        // 显示对应的服务特定字段摘要
        if (categorySelect.value) {
            const parts = categorySelect.value.split('.');
            if (parts.length === 2) {
                const subCategory = parts[1];
                
                // 搬家服务特定字段摘要
                if (subCategory === 'moving') {
                    document.getElementById('moving-summary').classList.remove('d-none');
                    
                    const itemSizeSelect = document.getElementById('moving_item_size');
                    let itemSizeText = itemSizeSelect.value;
                    if (itemSizeSelect.selectedIndex > 0) {
                        itemSizeText = itemSizeSelect.options[itemSizeSelect.selectedIndex].text;
                    }
                    document.getElementById('summary-moving-size').textContent = itemSizeText;
                    
                    document.getElementById('summary-moving-quantity').textContent = document.getElementById('moving_item_quantity').value || '未指定';
                    document.getElementById('summary-moving-elevator').textContent = document.getElementById('moving_has_elevator').checked ? '是' : '否';
                    document.getElementById('summary-moving-floor').textContent = document.getElementById('moving_floor_number').value || '未指定';
                }
                
                // 接送机特定字段摘要
                else if (subCategory === 'pickup') {
                    document.getElementById('pickup-summary').classList.remove('d-none');
                    
                    document.getElementById('summary-pickup-flight').textContent = document.getElementById('pickup_flight_number').value || '未指定';
                    document.getElementById('summary-pickup-passengers').textContent = document.getElementById('pickup_passengers').value || '未指定';
                    document.getElementById('summary-pickup-luggage').textContent = document.getElementById('pickup_luggage_count').value || '未指定';
                    
                    const pickupType = document.querySelector('input[name="pickup_is_arrival"]:checked');
                    document.getElementById('summary-pickup-type').textContent = pickupType && pickupType.value === '1' ? '接机' : '送机';
                }
                
                // 装修维修特定字段摘要
                else if (subCategory === 'repair') {
                    document.getElementById('repair-summary').classList.remove('d-none');
                    
                    const repairTypeSelect = document.getElementById('repair_type');
                    let repairTypeText = repairTypeSelect.value;
                    if (repairTypeSelect.selectedIndex > 0) {
                        repairTypeText = repairTypeSelect.options[repairTypeSelect.selectedIndex].text;
                    }
                    document.getElementById('summary-repair-type').textContent = repairTypeText;
                    
                    document.getElementById('summary-repair-area').textContent = document.getElementById('repair_area').value ? `${document.getElementById('repair_area').value}平方米` : '未指定';
                    document.getElementById('summary-repair-materials').textContent = document.getElementById('repair_materials_included').checked ? '是' : '否';
                }
                
                // 法律咨询特定字段摘要
                else if (subCategory === 'legal') {
                    document.getElementById('legal-summary').classList.remove('d-none');
                    
                    const caseTypeSelect = document.getElementById('legal_case_type');
                    let caseTypeText = caseTypeSelect.value;
                    if (caseTypeSelect.selectedIndex > 0) {
                        caseTypeText = caseTypeSelect.options[caseTypeSelect.selectedIndex].text;
                    }
                    document.getElementById('summary-legal-case-type').textContent = caseTypeText;
                    
                    const urgencySelect = document.getElementById('legal_urgency');
                    let urgencyText = urgencySelect.value;
                    if (urgencySelect.selectedIndex > 0) {
                        urgencyText = urgencySelect.options[urgencySelect.selectedIndex].text;
                    }
                    document.getElementById('summary-legal-urgency').textContent = urgencyText;
                    
                    document.getElementById('summary-legal-documents').textContent = document.getElementById('legal_documents_ready').checked ? '是' : '否';
                }
                
                // 留学咨询特定字段摘要
                else if (subCategory === 'education') {
                    document.getElementById('education-summary').classList.remove('d-none');
                    
                    const countrySelect = document.getElementById('education_target_country');
                    let countryText = countrySelect.value;
                    if (countrySelect.selectedIndex > 0) {
                        countryText = countrySelect.options[countrySelect.selectedIndex].text;
                    }
                    document.getElementById('summary-education-country').textContent = countryText;
                    
                    const levelSelect = document.getElementById('education_study_level');
                    let levelText = levelSelect.value;
                    if (levelSelect.selectedIndex > 0) {
                        levelText = levelSelect.options[levelSelect.selectedIndex].text;
                    }
                    document.getElementById('summary-education-level').textContent = levelText;
                    
                    const fieldSelect = document.getElementById('education_field');
                    let fieldText = fieldSelect.value;
                    if (fieldSelect.selectedIndex > 0) {
                        fieldText = fieldSelect.options[fieldSelect.selectedIndex].text;
                    }
                    document.getElementById('summary-education-field').textContent = fieldText;
                }
                
                // 维修服务特定字段摘要
                else if (subCategory === 'repair_service') {
                    document.getElementById('repair-service-summary').classList.remove('d-none');
                    
                    const repairTypeSelect = document.getElementById('repair_service_type');
                    let repairTypeText = repairTypeSelect.value;
                    if (repairTypeSelect.selectedIndex > 0) {
                        repairTypeText = repairTypeSelect.options[repairTypeSelect.selectedIndex].text;
                    }
                    document.getElementById('summary-repair-service-type').textContent = repairTypeText;
                    
                    const itemAgeSelect = document.getElementById('repair_service_item_age');
                    let itemAgeText = itemAgeSelect.value;
                    if (itemAgeSelect.selectedIndex > 0) {
                        itemAgeText = itemAgeSelect.options[itemAgeSelect.selectedIndex].text;
                    }
                    document.getElementById('summary-repair-service-age').textContent = itemAgeText;
                    
                    document.getElementById('summary-repair-service-brand').textContent = document.getElementById('repair_service_brand_model').value || '未指定';
                    document.getElementById('summary-repair-service-warranty').textContent = document.getElementById('repair_service_has_warranty').checked ? '是' : '否';
                }
                
                // 其他商业服务特定字段摘要
                else if (subCategory === 'other_business') {
                    document.getElementById('other-business-summary').classList.remove('d-none');
                    
                    const serviceTypeSelect = document.getElementById('other_business_service_type');
                    let serviceTypeText = serviceTypeSelect.value;
                    if (serviceTypeSelect.selectedIndex > 0) {
                        serviceTypeText = serviceTypeSelect.options[serviceTypeSelect.selectedIndex].text;
                    }
                    document.getElementById('summary-other-business-type').textContent = serviceTypeText;
                    
                    const scaleSelect = document.getElementById('other_business_project_scale');
                    let scaleText = scaleSelect.value;
                    if (scaleSelect.selectedIndex > 0) {
                        scaleText = scaleSelect.options[scaleSelect.selectedIndex].text;
                    }
                    document.getElementById('summary-other-business-scale').textContent = scaleText;
                    
                    const durationSelect = document.getElementById('other_business_duration');
                    let durationText = durationSelect.value;
                    if (durationSelect.selectedIndex > 0) {
                        durationText = durationSelect.options[durationSelect.selectedIndex].text;
                    }
                    document.getElementById('summary-other-business-duration').textContent = durationText;
                }
            }
        }
    }
    
    // 导出全局函数
    window.updateSummary = updateSummary;
}); 