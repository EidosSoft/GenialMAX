#!/usr/bin/env python3
# Genial MAX - язык программирования для роботов MAX
# Поддержка библиотек на Lua и Python
# GitHub: https://github.com/EidosSoft/genial-max

import re
import os
import sys
import json
import time
import subprocess
from pathlib import Path

# ========== КОМПИЛЯТОР ==========
class GenialCompiler:
    def __init__(self):
        self.code = []
        self.indent = 0
        self.libs = {}
        self.variables = {}
        
    def compile(self, source: str) -> str:
        lines = source.strip().split('\n')
        self.code = [
            "import time",
            "from gmax_runtime import RobotMAX, Sensor, Motor",
            ""
        ]
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('//'):
                i += 1
                continue
                
            if line.startswith('use'):
                self._handle_use(line)
                i += 1
            elif line.startswith('mode'):
                i = self._handle_mode(lines, i)
            elif line.startswith('move'):
                self._handle_move(line)
                i += 1
            elif line.startswith('rotate'):
                self._handle_rotate(line)
                i += 1
            elif line.startswith('grip'):
                self._handle_grip(line)
                i += 1
            elif line.startswith('read'):
                self._handle_sensor(line)
                i += 1
            elif line.startswith('wait'):
                self.code.append('    ' * self.indent + f'time.sleep({line[5:-1]})')
                i += 1
            elif line.startswith('let'):
                self._handle_variable(line)
                i += 1
            elif line.startswith('if'):
                i = self._handle_if(lines, i)
            elif line.startswith('loop'):
                i = self._handle_loop(lines, i)
            elif line.startswith('call'):
                self._handle_call(line)
                i += 1
            elif line == '}':
                self.indent -= 1
                i += 1
            else:
                if line and not line.startswith('}'):
                    self.code.append('    ' * self.indent + line)
                i += 1
                
        return '\n'.join(self.code)
    
    def _handle_use(self, line: str):
        # use move_lib from local:motion
        # use vision from github:EidosSoft/vision-lib
        match = re.match(r'use\s+(\w+)\s+from\s+(\w+):([\w/-]+)', line)
        if match:
            lib_name, source_type, path = match.groups()
            if source_type == 'github':
                self._install_from_github(lib_name, path)
            elif source_type == 'local':
                self._load_library(lib_name, path)
            self.code.append(f"# Библиотека {lib_name} загружена")
    
    def _install_from_github(self, lib_name: str, repo: str):
        lib_path = Path(f"libs/{lib_name}")
        if not lib_path.exists():
            print(f"📦 Установка библиотеки {lib_name} из github:{repo}")
            subprocess.run(["git", "clone", f"https://github.com/{repo}.git", str(lib_path)])
        self._load_library(lib_name, lib_name)
    
    def _load_library(self, lib_name: str, path: str):
        lib_path = Path(f"libs/{path}")
        if lib_path.exists():
            # Загружаем Lua библиотеку
            lua_file = lib_path / f"{lib_name}.lua"
            if lua_file.exists():
                self.libs[lib_name] = {'type': 'lua', 'path': str(lua_file)}
            
            # Загружаем Python библиотеку
            py_file = lib_path / f"{lib_name}.py"
            if py_file.exists():
                self.libs[lib_name] = {'type': 'python', 'path': str(py_file)}
    
    def _handle_call(self, line: str):
        # call motion.wave_arm(left, 30)
        match = re.match(r'call\s+(\w+)\.(\w+)\((.*)\)', line)
        if match:
            lib_name, func_name, args = match.groups()
            lib = self.libs.get(lib_name)
            if lib:
                if lib['type'] == 'lua':
                    self.code.append('    ' * self.indent + f'robot.call_lua("{lib["path"]}", "{func_name}", [{args}])')
                elif lib['type'] == 'python':
                    self.code.append('    ' * self.indent + f'robot.call_python("{lib["path"]}", "{func_name}", [{args}])')
    
    def _handle_mode(self, lines, start_idx):
        line = lines[start_idx].strip()
        match = re.match(r'mode\s+(\w+)(?:\s+with\s+(.+))?', line)
        if match:
            mode_name = match.group(1)
            params = match.group(2) or ""
            self.code.append(f'def mode_{mode_name}(robot, {params}):')
            self.indent += 1
            return start_idx + 1
        return start_idx + 1
    
    def _handle_move(self, line: str):
        match = re.match(r'move\s+(\w+)\s+(\d+)\s*(\w+)?\s*(?:speed\s+(\d+))?', line)
        if match:
            direction, distance, unit, speed = match.groups()
            unit = unit or "mm"
            speed = speed or "100"
            self.code.append('    ' * self.indent + f'robot.move("{direction}", {distance}, unit="{unit}", speed={speed})')
    
    def _handle_rotate(self, line: str):
        match = re.match(r'rotate\s+(\w+)\s+(\d+)\s*(\w+)?\s*(?:speed\s+(\d+))?', line)
        if match:
            direction, angle, unit, speed = match.groups()
            unit = unit or "deg"
            speed = speed or "50"
            self.code.append('    ' * self.indent + f'robot.rotate("{direction}", {angle}, unit="{unit}", speed={speed})')
    
    def _handle_grip(self, line: str):
        match = re.match(r'grip\s+(\w+)\s*(?:force\s+(\d+))?', line)
        if match:
            action, force = match.groups()
            force = force or "100"
            self.code.append('    ' * self.indent + f'robot.grip("{action}", force={force})')
    
    def _handle_sensor(self, line: str):
        match = re.match(r'read\s+(\w+)\s+(?:pin\s+(\d+))?', line)
        if match:
            sensor_type, pin = match.groups()
            pin = pin or "0"
            self.code.append('    ' * self.indent + f'value = robot.read_sensor("{sensor_type}", pin={pin})')
    
    def _handle_variable(self, line: str):
        match = re.match(r'let\s+(\w+)\s*=\s*(.+)', line)
        if match:
            var_name, var_value = match.groups()
            self.variables[var_name] = var_value
            self.code.append('    ' * self.indent + f'{var_name} = {var_value}')
    
    def _handle_if(self, lines, start_idx):
        line = lines[start_idx].strip()
        match = re.match(r'if\s+(.+)\s*:', line)
        if match:
            condition = match.group(1)
            self.code.append('    ' * self.indent + f'if {condition}:')
            self.indent += 1
            return start_idx + 1
        return start_idx + 1
    
    def _handle_loop(self, lines, start_idx):
        line = lines[start_idx].strip()
        match = re.match(r'loop\s+(\d+)\s+times', line)
        if match:
            count = match.group(1)
            self.code.append('    ' * self.indent + f'for _ in range({count}):')
            self.indent += 1
            return start_idx + 1
        return start_idx + 1


# ========== РАНТАЙМ РОБОТА ==========
class RobotMAX:
    def __init__(self, name: str, port: str = None):
        self.name = name
        self.port = port
        self.position = [0, 0, 0]  # x, y, angle
        self.gripper_state = "open"
        
    def move(self, direction: str, distance: int, unit: str = "mm", speed: int = 100):
        print(f"[{self.name}] 📍 Движение {direction} на {distance}{unit} (скорость {speed}%)")
        time.sleep(distance / 100)  # симуляция
        if direction == "forward":
            self.position[0] += distance
        elif direction == "back":
            self.position[0] -= distance
        elif direction == "left":
            self.position[1] -= distance
        elif direction == "right":
            self.position[1] += distance
        print(f"[{self.name}] 📍 Позиция: x={self.position[0]}, y={self.position[1]}")
        
    def rotate(self, direction: str, angle: int, unit: str = "deg", speed: int = 50):
        print(f"[{self.name}] 🔄 Поворот {direction} на {angle}{unit} (скорость {speed}%)")
        if direction == "left":
            self.position[2] = (self.position[2] - angle) % 360
        elif direction == "right":
            self.position[2] = (self.position[2] + angle) % 360
        print(f"[{self.name}] 🔄 Угол: {self.position[2]}°")
        
    def grip(self, action: str, force: int = 100):
        if action in ["close", "open"]:
            self.gripper_state = action
            print(f"[{self.name}] 🦾 Захват {action} (сила {force}%)")
        else:
            print(f"[{self.name}] 🦾 Неизвестное действие: {action}")
            
    def read_sensor(self, sensor_type: str, pin: int = 0):
        # Симуляция сенсоров
        import random
        if sensor_type == "ultrasonic":
            value = random.randint(5, 150)
            print(f"[{self.name}] 📡 Ультразвуковой сенсор (pin {pin}): {value} см")
        elif sensor_type == "infrared":
            value = random.randint(0, 100)
            print(f"[{self.name}] 📡 ИК-сенсор (pin {pin}): {value}%")
        elif sensor_type == "touch":
            value = random.choice([0, 1])
            print(f"[{self.name}] 📡 Тактильный сенсор (pin {pin}): {'нажат' if value else 'свободен'}")
        else:
            value = random.randint(0, 255)
            print(f"[{self.name}] 📡 Сенсор {sensor_type} (pin {pin}): {value}")
        return value
    
    def call_lua(self, lua_file: str, func_name: str, args: list):
        try:
            import lupa
            lua = lupa.LuaRuntime()
            with open(lua_file, 'r', encoding='utf-8') as f:
                lua.execute(f.read())
            result = lua.globals()[func_name](self, *args)
            return result
        except ImportError:
            print(f"[LUA] Вызов {func_name} с аргументами {args}")
            
    def call_python(self, py_file: str, func_name: str, args: list):
        import importlib.util
        spec = importlib.util.spec_from_file_location("lib", py_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        func = getattr(module, func_name)
        return func(self, *args)
    
    def run_mode(self, mode_name: str, **kwargs):
        func_name = f"mode_{mode_name}"
        if func_name in globals():
            globals()[func_name](self, **kwargs)
        else:
            print(f"[{self.name}] ❌ Режим {mode_name} не найден")


# ========== МЕНЕДЖЕР БИБЛИОТЕК ==========
class LibraryManager:
    @staticmethod
    def list():
        print("\n📚 ДОСТУПНЫЕ БИБЛИОТЕКИ:")
        print("-" * 50)
        print("1. motion (базовые движения)")
        print("2. vision (распознавание объектов)")
        print("3. arm (управление манипулятором)")
        print("4. conveyor (управление конвейером)")
        print("5. safety (безопасность и остановка)")
        print("-" * 50)
        
    @staticmethod
    def install(lib_name: str):
        print(f"📦 Установка библиотеки {lib_name}...")
        os.makedirs("libs", exist_ok=True)
        
        if lib_name == "motion":
            LibraryManager._create_motion_lib()
        elif lib_name == "vision":
            LibraryManager._create_vision_lib()
        elif lib_name == "arm":
            LibraryManager._create_arm_lib()
        else:
            print(f"❌ Библиотека {lib_name} не найдена")
            
    @staticmethod
    def _create_motion_lib():
        # Lua библиотека для плавных движений
        with open("libs/motion/motion.lua", "w") as f:
            f.write("""
-- motion.lua - библиотека плавных движений для роботов MAX
local motion = {}

function motion.curve_move(robot, x, y, duration)
    print(string.format("Плавное движение к (%d, %d) за %d сек", x, y, duration))
    robot:move("forward", x, "mm")
    robot:move("right", y, "mm")
    return {x = x, y = y}
end

function motion.wave_arm(robot, angle, speed)
    print(string.format("Взмах рукой на %d градусов со скоростью %d", angle, speed))
    robot:rotate("left", angle, "deg", speed)
    robot:rotate("right", angle, "deg", speed)
end

function motion.dance(robot, style)
    if style == "happy" then
        for i = 1, 4 do
            robot:move("forward", 50, "mm", 80)
            robot:move("back", 50, "mm", 80)
        end
    elseif style == "excited" then
        for i = 1, 3 do
            robot:rotate("left", 90, "deg", 100)
            robot:rotate("right", 90, "deg", 100)
        end
    end
end

return motion
""")
        with open("libs/motion/motion.gmax", "w") as f:
            f.write("""
# motion.gmax - библиотека движений
# Функции:
#   call motion.curve_move(x, y, duration)
#   call motion.wave_arm(angle, speed)
#   call motion.dance(style)
""")
        print("✅ Библиотека motion установлена")
        
    @staticmethod
    def _create_vision_lib():
        with open("libs/vision/vision.lua", "w") as f:
            f.write("""
-- vision.lua - компьютерное зрение для MAX
local vision = {}

function vision.detect_object(robot, camera_id)
    print(string.format("Поиск объектов камерой %d", camera_id))
    local objects = {"cube", "sphere", "cylinder"}
    return objects[math.random(#objects)]
end

function vision.follow_line(robot, line_color)
    print(string.format("Следование по линии цвета: %s", line_color))
    robot:move("forward", 100, "mm")
    return true
end

return vision
""")
        print("✅ Библиотека vision установлена")
        
    @staticmethod
    def _create_arm_lib():
        with open("libs/arm/arm.lua", "w") as f:
            f.write("""
-- arm.lua - управление манипулятором MAX
local arm = {}

function arm.pick_and_place(robot, x, y, z)
    print(string.format("Захват объекта в позиции (%d, %d, %d)", x, y, z))
    robot:grip("close", 100)
    robot:move("forward", x, "mm")
    robot:move("right", y, "mm")
    robot:grip("open", 100)
    return {picked = true}
end

return arm
""")
        print("✅ Библиотека arm установлена")
    
    @staticmethod
    def submit_to_eidossoft(lib_name: str, repo_url: str):
        print(f"""
📤 ЗАЯВКА НА ДОБАВЛЕНИЕ БИБЛИОТЕКИ В ОФИЦИАЛЬНЫЙ РЕПОЗИТОРИЙ

Имя библиотеки: {lib_name}
GitHub репозиторий: {repo_url}

Статус: ОЖИДАЕТ РАССМОТРЕНИЯ

Для отправки заявки свяжитесь с EidosSoft:
📧 Email: libs@eidossoft.com
📱 ВКонтакте: https://vk.com/EidosSoft
🌐 GitHub: https://github.com/EidosSoft/genial-max-libs

Срок рассмотрения: 1-2 недели
        """)


# ========== CLI ==========
def main():
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════╗
║     Genial MAX - язык программирования для роботов      ║
╠══════════════════════════════════════════════════════════╣
║  Команды:                                                ║
║    python gmax.py run <file.gmax>    - запустить программу║
║    python gmax.py new <name>         - создать проект    ║
║    python gmax.py lib list           - список библиотек  ║
║    python gmax.py lib install <name> - установить библиотеку║
║    python gmax.py lib submit <name>  - предложить библиотеку║
╚══════════════════════════════════════════════════════════╝
        """)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        if len(sys.argv) < 3:
            print("❌ Укажите файл: python gmax.py run bot.gmax")
            return
        filename = sys.argv[2]
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        compiler = GenialCompiler()
        python_code = compiler.compile(code)
        with open("_temp_robot.py", "w", encoding='utf-8') as f:
            f.write(python_code)
        robot = RobotMAX("MAX-1")
        exec(python_code, {"robot": robot, "time": time})
        print(f"\n🤖 Робот готов к работе!")
        
    elif cmd == "new":
        if len(sys.argv) < 3:
            print("❌ Укажите имя проекта")
            return
        name = sys.argv[2]
        os.makedirs(name, exist_ok=True)
        with open(f"{name}/robot.gmax", "w", encoding='utf-8') as f:
            f.write(f"""// {name}.gmax - программа для робота MAX

// Импорт библиотек
use motion from local:motion
use vision from local:vision

// Основной режим работы
mode main
    // Движение вперед
    move forward 200 mm speed 50
    
    // Чтение сенсоров
    read ultrasonic pin 1
    if value < 30:
        rotate left 90 deg
    else:
        move forward 100 mm
    
    // Использование библиотеки
    call motion.wave_arm(45, 60)
    call vision.detect_object(0)
    
    // Захват объекта
    grip close force 80
    wait(1)
    grip open

mode patrol
    loop 5 times:
        move forward 300 mm speed 40
        rotate right 90 deg
        wait(0.5)
""")
        print(f"✅ Проект {name} создан! Запустите:")
        print(f"   cd {name} && python ../gmax.py run robot.gmax")
        
    elif cmd == "lib":
        if len(sys.argv) < 3:
            print("❌ Используйте: lib list / install / submit")
            return
        subcmd = sys.argv[2]
        if subcmd == "list":
            LibraryManager.list()
        elif subcmd == "install":
            if len(sys.argv) < 4:
                print("❌ Укажите имя библиотеки")
                return
            LibraryManager.install(sys.argv[3])
        elif subcmd == "submit":
            if len(sys.argv) < 4:
                print("❌ Укажите имя библиотеки")
                return
            LibraryManager.submit_to_eidossoft(sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
            
if __name__ == "__main__":
    main()
