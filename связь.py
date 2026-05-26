# Отправка заявки через API
import requests

def submit_library(lib_name, github_url, description):
    data = {
        "name": lib_name,
        "github": github_url,
        "description": description,
        "contact": "https://vk.com/your_id"
    }
    
    # Отправляем в EidosSoft
    response = requests.post(
        "https://api.eidossoft.com/genial/submit",
        json=data
    )
    
    print("✅ Заявка отправлена!")
    print("📧 Ждите ответ в течение 1-2 недель")
    print("💬 Вопросы: https://vk.com/EidosSoft")
