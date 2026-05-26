-- motion.lua - библиотека плавных движений для роботов MAX
local motion = {}

-- Плавное движение к точке
function motion.curve_move(robot, x, y, duration)
    print(string.format("[Motion] Плавное движение к (%d, %d) за %d сек", x, y, duration))
    local steps = duration * 10
    local step_x = x / steps
    local step_y = y / steps
    
    for i = 1, steps do
        if step_x > 0 then
            robot:move("forward", step_x, "mm", 30)
        elseif step_x < 0 then
            robot:move("back", -step_x, "mm", 30)
        end
        
        if step_y > 0 then
            robot:move("right", step_y, "mm", 30)
        elseif step_y < 0 then
            robot:move("left", -step_y, "mm", 30)
        end
        robot:wait(0.1)
    end
    return {x = x, y = y}
end

-- Взмах манипулятором
function motion.wave_arm(robot, angle, speed)
    print(string.format("[Motion] Взмах рукой на %d градусов", angle))
    robot:rotate("left", angle, "deg", speed)
    robot:wait(0.2)
    robot:rotate("right", angle * 2, "deg", speed)
    robot:wait(0.2)
    robot:rotate("left", angle, "deg", speed)
end

-- Танец робота
function motion.dance(robot, style)
    print(string.format("[Motion] Танцую стиль: %s", style))
    if style == "happy" then
        for i = 1, 4 do
            robot:move("forward", 50, "mm", 80)
            robot:move("back", 50, "mm", 80)
            robot:rotate("left", 45, "deg", 100)
            robot:rotate("right", 45, "deg", 100)
        end
    elseif style == "robot" then
        for i = 1, 3 do
            robot:grip("close", 100)
            robot:wait(0.2)
            robot:grip("open", 100)
            robot:wait(0.2)
            robot:move("forward", 30, "mm", 100)
            robot:move("back", 30, "mm", 100)
        end
    end
end

-- Круговая траектория
function motion.circle(robot, radius, speed)
    local circumference = 2 * math.pi * radius
    local steps = 36
    local angle_step = 360 / steps
    
    for i = 1, steps do
        robot:move("forward", circumference / steps, "mm", speed)
        robot:rotate("right", angle_step, "deg", speed)
    end
end

return motion
