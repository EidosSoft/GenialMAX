-- vision.lua - библиотека компьютерного зрения
local vision = {}

-- Распознавание объектов
function vision.detect_object(robot, camera_id)
    print(string.format("[Vision] Сканирование камерой %d", camera_id))
    
    -- Симуляция распознавания
    local objects = {
        {name = "cube", confidence = 0.95, x = 100, y = 50},
        {name = "sphere", confidence = 0.87, x = 200, y = 75},
        {name = "cylinder", confidence = 0.92, x = 150, y = 120},
        {name = "box", confidence = 0.78, x = 300, y = 90}
    }
    
    local detected = objects[math.random(#objects)]
    print(string.format("[Vision] Найден: %s (уверенность: %.0f%%)", 
          detected.name, detected.confidence * 100))
    
    return detected
end

-- Следование по линии
function vision.follow_line(robot, line_color, speed)
    print(string.format("[Vision] Следование по линии цвета: %s", line_color))
    local duration = 10  -- секунд
    
    for i = 1, duration * 2 do
        -- Симуляция отклонения от линии
        local deviation = math.random(-10, 10)
        
        if deviation < -5 then
            robot:rotate("left", 10, "deg", speed - 20)
        elseif deviation > 5 then
            robot:rotate("right", 10, "deg", speed - 20)
        else
            robot:move("forward", 50, "mm", speed)
        end
        robot:wait(0.5)
    end
    
    return true
end

-- Распознавание лиц
function vision.face_recognition(robot, face_id)
    print(string.format("[Vision] Поиск лица ID: %s", face_id))
    
    local faces = {
        admin = {name = "Admin", confidence = 0.98},
        user1 = {name = "Operator", confidence = 0.85}
    }
    
    local result = faces[face_id] or {name = "Unknown", confidence = 0.45}
    print(string.format("[Vision] Распознан: %s", result.name))
    
    return result
end

-- QR код сканирование
function vision.scan_qr(robot)
    print("[Vision] Сканирование QR кода")
    local codes = {"PRODUCT_001", "LOCATION_A", "TASK_COMPLETE", "MAINTENANCE"}
    local qr_code = codes[math.random(#codes)]
    print(string.format("[Vision] QR код: %s", qr_code))
    
    return qr_code
end

return vision
