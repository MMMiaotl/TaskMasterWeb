/**
 * 任务表单自动生成模块
 * 处理任务标题和描述的自动生成功能
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('自动生成模块已加载');
    
    // 绑定自动生成按钮事件
    const generateTitleBtn = document.getElementById('generate-title-btn');
    const generateDescriptionBtn = document.getElementById('generate-description-btn');
    
    if (generateTitleBtn) {
        generateTitleBtn.addEventListener('click', generateTitle);
        console.log('标题生成按钮已绑定');
    } else {
        console.error('未找到标题生成按钮');
    }
    
    if (generateDescriptionBtn) {
        generateDescriptionBtn.addEventListener('click', generateDescription);
        console.log('描述生成按钮已绑定');
    } else {
        console.error('未找到描述生成按钮');
    }

    // 自动生成任务标题
    function generateTitle() {
        console.log('开始生成标题');
        const categorySelect = document.getElementById('service_category');
        if (!categorySelect) {
            console.error('未找到服务类别选择框');
            return;
        }
        
        const categoryText = categorySelect.options[categorySelect.selectedIndex].text;
        const locationInput = document.getElementById('location');
        const location = locationInput ? locationInput.value : '';
        let title = '';

        // 根据服务类别生成标题
        if (categorySelect.value) {
            const parts = categorySelect.value.split('.');
            if (parts.length === 2) {
                const subCategory = parts[1];

                if (subCategory === 'moving') {
                    // 搬家服务
                    const outAddress = document.getElementById('moving_out_address');
                    const inAddress = document.getElementById('moving_in_address');
                    const outAddressValue = outAddress ? outAddress.value : '';
                    const inAddressValue = inAddress ? inAddress.value : '';
                    
                    title = `搬家服务`;
                    if (outAddressValue && inAddressValue) {
                        title += ` - 从${outAddressValue}到${inAddressValue}`;
                    } else if (location) {
                        title += ` - ${location}`;
                    }
                } else if (subCategory === 'pickup') {
                    // 接送机服务
                    const isArrival = document.querySelector('input[name="pickup_is_arrival"]:checked');
                    const serviceType = isArrival && isArrival.value === '1' ? '接机' : '送机';
                    const passengers = document.getElementById('pickup_passengers');
                    const passengersValue = passengers ? passengers.value : '';

                    title = `${serviceType}服务`;
                    if (passengersValue) {
                        title += ` - ${passengersValue}人`;
                    }
                    
                    const flightNumber = document.getElementById('pickup_flight_number');
                    if (flightNumber && flightNumber.value) {
                        title += ` - 航班${flightNumber.value}`;        
                    }
                } else if (subCategory === 'repair') {
                    // 维修服务
                    const repairType = document.getElementById('repair_type');
                    const repairTypeText = repairType ? repairType.options[repairType.selectedIndex].text : '';

                    title = `${repairTypeText}服务`;
                    const repairArea = document.getElementById('repair_area');
                    if (repairArea && repairArea.value) {
                        title += ` - ${repairArea.value}平方米`;
                    }
                    if (location) {
                        title += ` - ${location}`;
                    }
                } else if (subCategory === 'legal') {
                    // 法律咨询
                    const caseType = document.getElementById('legal_case_type');
                    const caseTypeText = caseType ? caseType.options[caseType.selectedIndex].text : '';

                    title = `${caseTypeText}法律咨询`;
                } else if (subCategory === 'education') {
                    // 留学咨询
                    const country = document.getElementById('education_target_country');
                    const countryText = country ? country.options[country.selectedIndex].text : '';
                    const level = document.getElementById('education_study_level');
                    const levelText = level ? level.options[level.selectedIndex].text : '';

                    title = `${countryText}${levelText}留学咨询`;
                } else {
                    title = `${categoryText}服务`;
                }
            }
        }

        if (!title) {
            title = `${categoryText}服务`;
        }

        const titleInput = document.getElementById('title');
        if (titleInput) {
            titleInput.value = title;
            console.log('标题已生成:', title);
            
            // 触发输入事件，确保表单验证能够捕获到变化
            const inputEvent = new Event('input', { bubbles: true });
            titleInput.dispatchEvent(inputEvent);
        } else {
            console.error('未找到标题输入框');
        }
    }

    // 自动生成任务描述
    function generateDescription() {
        console.log('开始生成描述');
        const categorySelect = document.getElementById('service_category');
        if (!categorySelect) {
            console.error('未找到服务类别选择框');
            return;
        }
        
        const categoryText = categorySelect.options[categorySelect.selectedIndex].text;
        const locationInput = document.getElementById('location');
        const location = locationInput ? locationInput.value : '';
        
        // 获取时间偏好
        let timeInfo = '';
        const timePreference = document.querySelector('input[name="time_preference"]:checked');
        if (timePreference) {
            if (timePreference.value === 'specific_date') {
                const deadline = document.getElementById('deadline');
                if (deadline && deadline.value) {
                    const formattedDate = new Date(deadline.value).toLocaleDateString('zh-CN');
                    timeInfo = `希望在${formattedDate}完成`;
                }
            } else if (timePreference.value === 'date_range') {
                const startDate = document.getElementById('start_date');
                const endDate = document.getElementById('end_date');
                if (startDate && startDate.value && endDate && endDate.value) {
                    const formattedStartDate = new Date(startDate.value).toLocaleDateString('zh-CN');
                    const formattedEndDate = new Date(endDate.value).toLocaleDateString('zh-CN');
                    timeInfo = `希望在${formattedStartDate}至${formattedEndDate}期间完成`;
                }
            } else if (timePreference.value === 'anytime') {
                timeInfo = '任何时间都可以完成';
            } else if (timePreference.value === 'not_sure') {
                timeInfo = '时间待定';
            }
        }
        
        const budget = document.getElementById('budget');
        const budgetValue = budget ? budget.value : '';
        let description = '';

        // 基本描述开头
        description = `我需要${categoryText}服务。`;

        // 添加截止日期
        if (timeInfo) {
            description += `\n\n${timeInfo}。`;
        }

        // 添加地点信息
        if (location) {
            description += `\n\n服务地点：${location}。`;
        }

        // 添加预算信息
        if (budgetValue) {
            description += `\n\n预算：€${budgetValue}。`;
        }

        // 根据服务类别添加特定信息
        if (categorySelect.value) {
            const parts = categorySelect.value.split('.');
            if (parts.length === 2) {
                const subCategory = parts[1];

                description += '\n\n具体需求：';

                if (subCategory === 'moving') {
                    // 搬家服务特定信息
                    const outAddress = document.getElementById('moving_out_address');
                    const inAddress = document.getElementById('moving_in_address');
                    const outHouseType = document.getElementById('moving_out_house_type');
                    const inHouseType = document.getElementById('moving_in_house_type');
                    
                    if (outAddress && outAddress.value) {
                        description += `\n- 搬出地址邮编：${outAddress.value}`;
                    }
                    if (inAddress && inAddress.value) {
                        description += `\n- 搬入地址邮编：${inAddress.value}`;
                    }
                    
                    if (outHouseType && outHouseType.value) {
                        description += `\n- 搬出地房屋类型：${outHouseType.options[outHouseType.selectedIndex].text}`;
                    }
                    if (inHouseType && inHouseType.value) {
                        description += `\n- 搬入地房屋类型：${inHouseType.options[inHouseType.selectedIndex].text}`;
                    }
                    
                    // 电梯信息
                    const outElevator = document.getElementById('moving_out_has_elevator');
                    const inElevator = document.getElementById('moving_in_has_elevator');
                    if (outElevator) {
                        description += `\n- 搬出地电梯：${outElevator.checked ? '有' : '无'}`;
                    }
                    if (inElevator) {
                        description += `\n- 搬入地电梯：${inElevator.checked ? '有' : '无'}`;
                    }
                    
                    // 物品数量
                    const itemQuantity = document.getElementById('moving_item_quantity_range');
                    if (itemQuantity && itemQuantity.value) {
                        description += `\n- 物品数量：${itemQuantity.options[itemQuantity.selectedIndex].text}`;
                    }
                    
                    // 特殊物品
                    const hasLargeFurniture = document.getElementById('moving_has_large_furniture');
                    const hasAppliances = document.getElementById('moving_has_appliances');
                    const hasFragileItems = document.getElementById('moving_has_fragile_items');
                    const hasPiano = document.getElementById('moving_has_piano');
                    
                    let specialItems = [];
                    if (hasLargeFurniture && hasLargeFurniture.checked) specialItems.push('大型家具');
                    if (hasAppliances && hasAppliances.checked) specialItems.push('家用电器');
                    if (hasFragileItems && hasFragileItems.checked) specialItems.push('易碎物品');
                    if (hasPiano && hasPiano.checked) specialItems.push('钢琴或其他乐器');
                    
                    if (specialItems.length > 0) {
                        description += `\n- 特殊物品：${specialItems.join('、')}`;
                    }
                    
                    // 额外服务
                    const needPacking = document.getElementById('moving_need_packing');
                    const needUnpacking = document.getElementById('moving_need_unpacking');
                    const needDisposal = document.getElementById('moving_need_disposal');
                    const needStorage = document.getElementById('moving_need_storage');
                    
                    let extraServices = [];
                    if (needPacking && needPacking.checked) extraServices.push('打包服务');
                    if (needUnpacking && needUnpacking.checked) extraServices.push('拆包服务');
                    if (needDisposal && needDisposal.checked) extraServices.push('废物处理');
                    if (needStorage && needStorage.checked) extraServices.push('临时存储');
                    
                    if (extraServices.length > 0) {
                        description += `\n- 额外服务：${extraServices.join('、')}`;
                    }
                    
                } else if (subCategory === 'pickup') {
                    // 接送机服务特定信息
                    const isArrival = document.querySelector('input[name="pickup_is_arrival"]:checked');
                    const serviceType = isArrival && isArrival.value === '1' ? '接机' : '送机';
                    
                    description += `\n- 服务类型：${serviceType}`;
                    
                    const flightNumber = document.getElementById('pickup_flight_number');
                    if (flightNumber && flightNumber.value) {
                        description += `\n- 航班号：${flightNumber.value}`;
                    }
                    
                    const passengers = document.getElementById('pickup_passengers');
                    if (passengers && passengers.value) {
                        description += `\n- 乘客数量：${passengers.value}人`;
                    }
                    
                    const luggage = document.getElementById('pickup_luggage_count');
                    if (luggage && luggage.value) {
                        description += `\n- 行李数量：${luggage.value}件`;
                    }
                }
            }
        }

        const descriptionInput = document.getElementById('description');
        if (descriptionInput) {
            descriptionInput.value = description;
            console.log('描述已生成');
            
            // 触发输入事件，确保表单验证能够捕获到变化
            const inputEvent = new Event('input', { bubbles: true });
            descriptionInput.dispatchEvent(inputEvent);
        } else {
            console.error('未找到描述输入框');
        }
    }
}); 