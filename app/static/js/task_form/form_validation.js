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
                        // 验证接送机服务字段
                        validatePickupServiceFields();
                    } else if (subCategory === 'repair') {
                        const area = document.getElementById('repair_area');
                        const repairType = document.getElementById('repair_type');
                        const repairAddress = document.getElementById('repair_address');
                        
                        // 验证面积
                        if (!area.value || parseFloat(area.value) <= 0) {
                            area.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            area.classList.remove('is-invalid');
                        }
                        
                        // 验证类型
                        if (!repairType.value) {
                            repairType.classList.add('is-invalid');
                            isValid = false;
                        } else {
                            repairType.classList.remove('is-invalid');
                        }
                        
                        // 验证邮编格式
                        if (repairAddress && repairAddress.value.trim()) {
                            const addressPattern = /^[0-9]{4}[A-Za-z]{2}$/;
                            if (!addressPattern.test(repairAddress.value.trim())) {
                                repairAddress.classList.add('is-invalid');
                                isValid = false;
                            } else {
                                repairAddress.classList.remove('is-invalid');
                            }
                        }
                        
                        // 验证至少选择了一项工作内容
                        const workSelections = [
                            document.getElementById('repair_work_painting'),
                            document.getElementById('repair_work_plastering'),
                            document.getElementById('repair_work_flooring'),
                            document.getElementById('repair_work_plumbing'),
                            document.getElementById('repair_work_bathroom'),
                            document.getElementById('repair_work_toilet'),
                            document.getElementById('repair_work_kitchen'),
                            document.getElementById('repair_work_garden'),
                            document.getElementById('repair_work_extension')
                        ];
                        
                        const hasWorkSelection = workSelections.some(checkbox => checkbox && checkbox.checked);
                        const otherWork = document.getElementById('repair_work_other');
                        const hasOtherWorkText = otherWork && otherWork.value.trim().length > 0;
                        
                        if (!hasWorkSelection && !hasOtherWorkText) {
                            workSelections.forEach(checkbox => {
                                if (checkbox) {
                                    checkbox.closest('.form-check').classList.add('is-invalid');
                                }
                            });
                            if (otherWork) {
                                otherWork.classList.add('is-invalid');
                            }
                            isValid = false;
                        } else {
                            workSelections.forEach(checkbox => {
                                if (checkbox) {
                                    checkbox.closest('.form-check').classList.remove('is-invalid');
                                }
                            });
                            if (otherWork) {
                                otherWork.classList.remove('is-invalid');
                            }
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
            
            // 预算和地点已移除，不需要验证
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
    
    // 验证接送机服务字段
    function validatePickupServiceFields() {
        const isArrival = document.querySelector('input[name="pickup_is_arrival"]:checked');
        const flightNumber = document.getElementById('pickup_flight_number');
        const passengers = document.getElementById('pickup_passengers');
        const luggageCount = document.getElementById('pickup_luggage_count');
        
        let isValid = true;
        
        // 验证服务类型
        if (!isArrival) {
            document.querySelectorAll('input[name="pickup_is_arrival"]').forEach(radio => {
                radio.closest('.form-check').classList.add('is-invalid');
            });
            isValid = false;
        } else {
            document.querySelectorAll('input[name="pickup_is_arrival"]').forEach(radio => {
                radio.closest('.form-check').classList.remove('is-invalid');
            });
        }
        
        // 验证航班号
        if (!flightNumber.value.trim()) {
            flightNumber.classList.add('is-invalid');
            isValid = false;
        } else {
            flightNumber.classList.remove('is-invalid');
        }
        
        // 验证乘客数量
        if (!passengers.value || parseInt(passengers.value) < 1) {
            passengers.classList.add('is-invalid');
            isValid = false;
        } else {
            passengers.classList.remove('is-invalid');
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
                    
                    // 根据服务类型初始化问题
                    initializeServiceQuestions(subCategory);
                    
                    // 添加字段事件监听
                    setupFieldEvents(subCategory);
                }
            }
        }
    }
    
    // 初始化服务问题
    function initializeServiceQuestions(serviceType) {
        console.log(`初始化服务问题: ${serviceType}`);
        const serviceContainer = document.getElementById(`${serviceType}-fields`);
        
        if (serviceContainer) {
            // 重置所有问题状态
            const allQuestions = serviceContainer.querySelectorAll('.question-item');
            allQuestions.forEach(question => {
                question.classList.remove('active');
                question.classList.add('hidden');
            });
            
            // 显示第一个问题
            const firstQuestion = allQuestions[0];
            if (firstQuestion) {
                firstQuestion.classList.remove('hidden');
                firstQuestion.classList.add('active');
                console.log(`已激活第一个问题: ${firstQuestion.id}`);
            } else {
                console.log(`未找到问题项，服务类型: ${serviceType}`);
            }
        } else {
            console.log(`未找到服务容器: ${serviceType}-fields`);
        }
    }
    
    // 设置字段事件监听
    function setupFieldEvents(serviceType) {
        if (serviceType === 'moving') {
            // 搬家服务字段事件监听
            setupMovingFieldEvents();
        } else if (serviceType === 'pickup') {
            // 接送机服务字段事件监听
            setupPickupFieldEvents();
        } else if (serviceType === 'repair') {
            // 装修翻新服务字段事件监听
            setupRepairFieldEvents();
        }
    }
    
    // 搬家服务字段事件监听
    function setupMovingFieldEvents() {
        // 监听地址字段变化
        const outAddress = document.getElementById('moving_out_address');
        const inAddress = document.getElementById('moving_in_address');
        
        if (outAddress && inAddress) {
            function checkAddresses() {
                if (outAddress.value.trim() && inAddress.value.trim()) {
                    // 检查邮编格式
                    const pattern = /^[0-9]{4}[A-Za-z]{2}$/;
                    if (pattern.test(outAddress.value) && pattern.test(inAddress.value)) {
                        goToNextQuestion('moving-address-question', 'moving-house-type-question');
                    }
                }
            }
            
            outAddress.addEventListener('change', checkAddresses);
            inAddress.addEventListener('change', checkAddresses);
            outAddress.addEventListener('blur', checkAddresses);
            inAddress.addEventListener('blur', checkAddresses);
        }
        
        // 监听房屋类型字段变化
        const outHouseType = document.getElementById('moving_out_house_type');
        const inHouseType = document.getElementById('moving_in_house_type');
        
        if (outHouseType && inHouseType) {
            function checkHouseTypes() {
                if (outHouseType.value && inHouseType.value) {
                    // 如果有任一是公寓，显示电梯问题，否则直接跳到物品数量
                    if (outHouseType.value === 'apartment' || inHouseType.value === 'apartment') {
                        goToNextQuestion('moving-house-type-question', 'moving-elevator-question');
                    } else {
                        goToNextQuestion('moving-house-type-question', 'moving-quantity-question');
                    }
                }
            }
            
            outHouseType.addEventListener('change', checkHouseTypes);
            inHouseType.addEventListener('change', checkHouseTypes);
        }
        
        // 监听电梯和楼层字段变化
        const outElevator = document.getElementById('moving_out_has_elevator');
        const inElevator = document.getElementById('moving_in_has_elevator');
        const outFloor = document.getElementById('moving_out_floor_number');
        const inFloor = document.getElementById('moving_in_floor_number');
        
        function setupElevatorEvents() {
            function checkElevatorInfo() {
                if (outFloor.value && inFloor.value) {
                    goToNextQuestion('moving-elevator-question', 'moving-quantity-question');
                }
            }
            
            if (outElevator) outElevator.addEventListener('change', checkElevatorInfo);
            if (inElevator) inElevator.addEventListener('change', checkElevatorInfo);
            if (outFloor) outFloor.addEventListener('change', checkElevatorInfo);
            if (inFloor) inFloor.addEventListener('change', checkElevatorInfo);
        }
        
        // 仅当电梯问题显示时设置监听
        const elevatorQuestion = document.getElementById('moving-elevator-question');
        if (elevatorQuestion && !elevatorQuestion.classList.contains('hidden')) {
            setupElevatorEvents();
        }
        
        // 监听物品数量选择
        const itemQuantity = document.getElementById('moving_item_quantity_range');
        if (itemQuantity) {
            itemQuantity.addEventListener('change', function() {
                if (itemQuantity.value) {
                    goToNextQuestion('moving-quantity-question', 'moving-special-items-question');
                }
            });
        }
    }
    
    // 接送机服务字段事件监听
    function setupPickupFieldEvents() {
        // 监听服务类型选择
        const arrivalRadios = document.querySelectorAll('input[name="pickup_is_arrival"]');
        arrivalRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                goToNextQuestion('pickup-type-question', 'pickup-flight-question');
            });
        });
        
        // 监听航班号变化
        const flightNumber = document.getElementById('pickup_flight_number');
        if (flightNumber) {
            flightNumber.addEventListener('change', function() {
                if (flightNumber.value.trim()) {
                    goToNextQuestion('pickup-flight-question', 'pickup-passengers-question');
                }
            });
            
            flightNumber.addEventListener('blur', function() {
                if (flightNumber.value.trim()) {
                    goToNextQuestion('pickup-flight-question', 'pickup-passengers-question');
                }
            });
        }
        
        // 监听乘客人数变化
        const passengers = document.getElementById('pickup_passengers');
        if (passengers) {
            passengers.addEventListener('change', function() {
                if (passengers.value && parseInt(passengers.value) > 0) {
                    goToNextQuestion('pickup-passengers-question', 'pickup-luggage-question');
                }
            });
        }
    }
    
    // 装修翻新服务字段事件监听
    function setupRepairFieldEvents() {
        // 监听工作内容选择
        const workCheckboxes = document.querySelectorAll('#repair-work-question input[type="checkbox"]');
        const otherWorkInput = document.getElementById('repair_work_other');
        const continueButton = document.querySelector('#repair-work-question .btn-primary');
        
        // 监听复选框和其他工作文本框变化
        function checkWorkSelections() {
            // 检查是否有选择任何工作内容
            let hasSelection = false;
            
            workCheckboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    hasSelection = true;
                }
            });
            
            // 检查其他工作是否有填写
            if (otherWorkInput && otherWorkInput.value.trim()) {
                hasSelection = true;
            }
            
            // 如果有任何选择，启用继续按钮
            if (continueButton) {
                continueButton.disabled = !hasSelection;
            }
        }
        
        // 为每个复选框添加事件监听
        workCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', checkWorkSelections);
        });
        
        // 为其他工作文本框添加事件监听
        if (otherWorkInput) {
            otherWorkInput.addEventListener('input', checkWorkSelections);
        }
        
        // 为第一个问题的继续按钮添加点击事件
        if (continueButton) {
            continueButton.addEventListener('click', function() {
                goToNextQuestion('repair-work-question', 'repair-area-question');
            });
        }
        
        // 监听面积输入
        const areaInput = document.getElementById('repair_area');
        const areaButton = document.querySelector('#repair-area-question .btn-primary');
        
        if (areaInput && areaButton) {
            areaInput.addEventListener('input', function() {
                if (areaInput.value && parseFloat(areaInput.value) > 0) {
                    areaButton.disabled = false;
                } else {
                    areaButton.disabled = true;
                }
            });
            
            // 初始时禁用按钮
            areaButton.disabled = !(areaInput.value && parseFloat(areaInput.value) > 0);
        }
        
        // 监听地址邮编输入
        const addressInput = document.getElementById('repair_address');
        
        if (addressInput) {
            addressInput.addEventListener('input', function() {
                const pattern = /^[0-9]{4}[A-Za-z]{2}$/;
                if (pattern.test(addressInput.value)) {
                    // 如果邮编格式正确，自动进入下一步
                    // 这是最后一个问题，不需要继续
                }
            });
        }
    }
    
    // 切换到下一个问题
    function goToNextQuestion(currentId, nextId) {
        const currentQuestion = document.getElementById(currentId);
        const nextQuestion = document.getElementById(nextId);
        
        if (currentQuestion && nextQuestion) {
            // 标记当前问题为已回答
            currentQuestion.classList.add('answered');
            currentQuestion.classList.remove('active');
            
            // 检查当前问题是否属于接送机服务或装修翻新服务
            const isPickupService = currentId.includes('pickup-');
            const isRepairService = currentId.includes('repair-');
            
            // 如果不是接送机服务或装修翻新服务，则添加hidden类隐藏
            // 接送机服务和装修翻新服务的问题回答后保持显示
            if (!isPickupService && !isRepairService) {
                currentQuestion.classList.add('hidden');
            }
            
            // 显示下一个问题
            nextQuestion.classList.remove('hidden');
            nextQuestion.classList.add('active');
            nextQuestion.classList.add('fade-in');
            
            // 如果下一个问题是电梯问题，设置其事件监听
            if (nextId === 'moving-elevator-question') {
                setupElevatorEvents();
            }
            
            // 滚动到下一个问题
            nextQuestion.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // 导出全局函数
    window.validateStep = validateStep;
    window.showServiceSpecificFields = showServiceSpecificFields;
    window.goToNextQuestion = goToNextQuestion;
}); 