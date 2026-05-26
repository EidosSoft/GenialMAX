# 🤖 Genial MAX - Язык программирования для роботов

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/EidosSoft/genial-max)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://python.org)
[![Lua](https://img.shields.io/badge/lua-5.3+-purple.svg)](https://lua.org)

**Genial MAX** - это простой и мощный язык программирования для управления роботами MAX. Позволяет легко настраивать движения, сенсоры и автоматизацию с поддержкой библиотек на **Lua** и **Python**.

## ✨ Возможности

- 🎮 **Простой синтаксис** - интуитивно понятные команды
- 📚 **Библиотеки на Lua** - расширяйте функционал
- 🔌 **Поддержка сенсоров** - ультразвук, ИК, касание
- 🦾 **Управление манипулятором** - захват, перемещение, штабелирование
- 📦 **Менеджер библиотек** - установка из GitHub
- 🌐 **Интеграция с EidosSoft** - публикация своих библиотек

## 🚀 Быстрый старт

### Установка

```bash
# Скачиваем Genial MAX
git clone https://github.com/EidosSoft/genial-max.git
cd genial-max

# Устанавливаем зависимости
pip install lupa pyserial requests

# Или используем без зависимостей (только Python)
python gmax.py --help
