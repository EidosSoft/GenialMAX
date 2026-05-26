-- arm.lua - управление манипулятором MAX
local arm = {}

-- Взять и переместить объект
function arm.pick_and_place(robot, x, y, z)
    print(string.format("[Arm] Pick & Place в (%d, %d, %d)", x, y, z))
    
    -- Опускаем руку
    robot:grip("open", 50)
    robot:wait(0.3)
    
    -- Захват
    robot:grip("close", 100)
    robot:wait(0.5)
    
    -- Подъем и перемещение
    robot:move("forward", x, "mm", 30)
    robot:move("right", y, "mm", 30)
    
    -- Опускание и отпускание
    robot:wait(0.3)
    robot:grip("open", 100)
    robot:wait(0.2)
    
    print("[Arm] Объект перемещен")
    return {picked = true, placed = true}
end

-- Поиск и захват
function arm.search_and_grab(robot, search_radius)
    print(string.format("[Arm] Поиск объекта в радиусе %d мм", search_radius))
    
    -- Сканируем область
    for angle = 0, 360, 45 do
        robot:rotate("right", 45, "deg", 40)
        
        -- Проверяем сенсор
        local distance = robot:read_sensor("ultrasonic", 1)
        
        if distance < search_radius then
            print("[Arm] Объект найден!")
            robot:move("forward", distance - 20, "mm", 20)
            robot:grip("close", 100)
            return {found = true, distance = distance}
        end
    end
    
    print("[Arm] Объект не найден")
    return {found = false}
end

-- Штабелирование
function arm.stack(robot, height, object_count)
    print(string.format("[Arm] Штабелирование %d объектов высотой %d", object_count, height))
    local current_height = 0
    
    for i = 1, object_count do
        -- Захват объекта
        robot:grip("close", 80)
        robot:wait(0.3)
        
        -- Подъем на высоту
        current_height = current_height + (height / object_count)
        print(string.format("[Arm] Укладка слоя %d на высоту %d мм", i, current_height))
        
        -- Укладка
        robot:wait(0.5)
        robot:grip("open", 80)
        robot:wait(0.3)
    end
    
    print("[Arm] Штабелирование завершено")
    return {stacked = object_count, final_height = current_height}
end

-- Калибровка манипулятора
function arm.calibrate(robot)
    print("[Arm] Запуск калибровки...")
    
    -- Движение в крайние положения
    robot:rotate("left", 180, "deg", 20)
    robot:wait(0.5)
    robot:rotate("right", 180, "deg", 20)
    robot:wait(0.5)
    
    -- Проверка захвата
    robot:grip("close", 50)
    robot:wait(0.2)
    robot:grip("open", 50)
    
    print("[Arm] Калибровка завершена")
    return {calibrated = true}
end

return arm
