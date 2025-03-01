/**
 * 任务表单自动生成模块
 * 处理任务标题和描述的自动生成功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 绑定自动生成按钮事件
    document.getElementById('generate-title-btn').addEventListener('click', generateTitle);
    document.getElementById('generate-description-btn').addEventListener('click', generateDescription);
    
    // 自动生成任务标题
    function generateTitle() {
        const categorySelect = document.getElementById('service_category');
        const categoryText = categorySelect.options[categorySelect.selectedIndex].text;
        const location = document.getElementById('location').value;
        let title = '';
        
        // 根据服务类别生成标题
        if (categorySelect.value) {
            const parts = categorySelect.value.split('.');
            if (parts.length === 2) {
                const subCategory = parts[1];
                
                if (subCategory === 'moving') {
                    const itemSize = document.getElementById('moving_item_size');
                    const itemSizeText = itemSize.options[itemSize.selectedIndex].text;
                    const quantity = document.getElementById('moving_item_quantity').value;
                    
                    title = `搬运${quantity}件${itemSizeText}`;
                    if (location) {
                        title += ` - ${location}`;
                    }
                } else if (subCategory === 'pickup') {
                    const isArrival = document.querySelector('input[name="pickup_is_arrival"]:checked');
                    const serviceType = isArrival && isArrival.value === '1' ? '接机' : '送机';
                    const passengers = document.getElementById('pickup_passengers').value;
                    
                    title = `${serviceType}服务 - ${passengers}人`;
                    if (document.getElementById('pickup_flight_number').value) {
                        title += ` - 航班${document.getElementById('pickup_flight_number').value}`;
                    }
                } else if (subCategory === 'repair') {
                    const repairType = document.getElementById('repair_type');
                    const repairTypeText = repairType.options[repairType.selectedIndex].text;
                    
                    title = `${repairTypeText}服务`;
                    if (document.getElementById('repair_area').value) {
                        title += ` - ${document.getElementById('repair_area').value}平方米`;
                    }
                    if (location) {
                        title += ` - ${location}`;
                    }
                } else if (subCategory === 'legal') {
                    const caseType = document.getElementById('legal_case_type');
                    const caseTypeText = caseType.options[caseType.selectedIndex].text;
                    
                    title = `${caseTypeText}法律咨询`;
                } else if (subCategory === 'education') {
                    const country = document.getElementById('education_target_country');
                    const countryText = country.options[country.selectedIndex].text;
                    const level = document.getElementById('education_study_level');
                    const levelText = level.options[level.selectedIndex].text;
                    
                    title = `${countryText}${levelText}留学咨询`;
                } else {
                    title = `${categoryText}服务`;
                }
            }
        }
        
        if (!title) {
            title = `${categoryText}服务`;
        }
        
        document.getElementById('title').value = title;
    }
    
    // 自动生成任务描述
    function generateDescription() {
        const categorySelect = document.getElementById('service_category');
        const categoryText = categorySelect.options[categorySelect.selectedIndex].text;
        const location = document.getElementById('location').value;
        const deadline = document.getElementById('deadline').value;
        const budget = document.getElementById('budget').value;
        let description = '';
        
        // 基本描述开头
        description = `我需要${categoryText}服务。`;
        
        // 添加截止日期
        if (deadline) {
            const formattedDate = new Date(deadline).toLocaleDateString('zh-CN');
            description += `\n\n希望在${formattedDate}前完成。`;
        }
        
        // 添加地点信息
        if (location) {
            description += `\n\n服务地点：${location}。`;
        }
        
        // 添加预算信息
        if (budget) {
            description += `\n\n预算：€${budget}。`;
        }
        
        // 根据服务类别添加特定信息
        if (categorySelect.value) {
            const parts = categorySelect.value.split('.');
            if (parts.length === 2) {
                const subCategory = parts[1];
                
                description += '\n\n具体需求：';
                
                if (subCategory === 'moving') {
                    const itemSize = document.getElementById('moving_item_size');
                    const itemSizeText = itemSize.options[itemSize.selectedIndex].text;
                    const quantity = document.getElementById('moving_item_quantity').value;
                    const hasElevator = document.getElementById('moving_has_elevator').checked;
                    const floor = document.getElementById('moving_floor_number').value;
                    
                    description += `\n- 物品大小：${itemSizeText}`;
                    description += `\n- 物品数量：${quantity}件`;
                    description += `\n- 是否有电梯：${hasElevator ? '是' : '否'}`;
                    if (floor) {
                        description += `\n- 楼层：${floor}层`;
                    }
                } else if (subCategory === 'pickup') {
                    const isArrival = document.querySelector('input[name="pickup_is_arrival"]:checked');
                    const serviceType = isArrival && isArrival.value === '1' ? '接机' : '送机';
                    const passengers = document.getElementById('pickup_passengers').value;
                    const luggage = document.getElementById('pickup_luggage_count').value;
                    const flight = document.getElementById('pickup_flight_number').value;
                    
                    description += `\n- 服务类型：${serviceType}`;
                    description += `\n- 乘客数量：${passengers}人`;
                    if (luggage) {
                        description += `\n- 行李数量：${luggage}件`;
                    }
                    if (flight) {
                        description += `\n- 航班号：${flight}`;
                    }
                } else if (subCategory === 'repair') {
                    const repairType = document.getElementById('repair_type');
                    const repairTypeText = repairType.options[repairType.selectedIndex].text;
                    const area = document.getElementById('repair_area').value;
                    const materials = document.getElementById('repair_materials_included').checked;
                    
                    description += `\n- 维修类型：${repairTypeText}`;
                    if (area) {
                        description += `\n- 面积：${area}平方米`;
                    }
                    description += `\n- 是否包含材料：${materials ? '是' : '否'}`;
                } else if (subCategory === 'legal') {
                    const caseType = document.getElementById('legal_case_type');
                    const caseTypeText = caseType.options[caseType.selectedIndex].text;
                    const urgency = document.getElementById('legal_urgency');
                    const urgencyText = urgency.options[urgency.selectedIndex].text;
                    const documents = document.getElementById('legal_documents_ready').checked;
                    
                    description += `\n- 案件类型：${caseTypeText}`;
                    description += `\n- 紧急程度：${urgencyText}`;
                    description += `\n- 文件是否准备好：${documents ? '是' : '否'}`;
                } else if (subCategory === 'education') {
                    const country = document.getElementById('education_target_country');
                    const countryText = country.options[country.selectedIndex].text;
                    const level = document.getElementById('education_study_level');
                    const levelText = level.options[level.selectedIndex].text;
                    const field = document.getElementById('education_field');
                    const fieldText = field.options[field.selectedIndex].text;
                    
                    description += `\n- 目标国家：${countryText}`;
                    description += `\n- 学习阶段：${levelText}`;
                    description += `\n- 学习领域：${fieldText}`;
                }
            }
        }
        
        description += '\n\n期待您的回复，谢谢！';
        
        document.getElementById('description').value = description;
    }
    
    // 导出全局函数
    window.generateTitle = generateTitle;
    window.generateDescription = generateDescription;
}); 