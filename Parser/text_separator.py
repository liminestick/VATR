import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from tqdm import tqdm
import re
from bs4 import BeautifulSoup

# Проверяем доступность GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Загрузка модели и токенизатора
model_name = 'gpt2'
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name).to(device)

# Установка модели в режим оценки
model.eval()

# Установка токена для заполнения
tokenizer.pad_token = tokenizer.eos_token

# Функция для чтения FB2 файла
def read_fb2_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'xml')
        body = soup.find('body')
        text = ''
        for p in body.find_all('p'):
            text += p.get_text() + '\n'
        return text.strip()

# Функция для генерации текста
def generate_text(chunk):
    inputs = tokenizer(chunk, return_tensors='pt', truncation=True, max_length=1024).to(device)

    input_length = inputs['input_ids'].shape[1]
    max_length = 1024

    # Рассчитываем сколько новых токенов можно сгенерировать
    max_new_tokens = max_length - input_length

    # Если не можем сгенерировать новые токены
    if max_new_tokens < 1:
        return chunk

    with torch.no_grad():
        outputs = model.generate(
            inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            max_new_tokens=max_new_tokens,
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Функция для разбиения текста на части
def split_text_into_chunks(text, max_length=1000):
    sentences = re.split(r'(?<=[.!?]) +', text)  # Разделение на предложения
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += (sentence + " ")
        else:
            if current_chunk:  # Добавляем текущий чанк в список
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "  # Начинаем новый чанк

    if current_chunk:  # Добавляем последний чанк
        chunks.append(current_chunk.strip())

    return chunks

# Функция для очистки текста
def clean_text(text):
    # Убираем неразрывные пробелы и лишние пробелы
    text = text.replace('\xa0', ' ')  # Заменяем неразрывные пробелы
    text = re.sub(r'\s+', ' ', text)  # Заменяем несколько пробелов одним
    return text.strip()

# Обработка текста
def process_text(text):
    chunks = split_text_into_chunks(text)
    results = []

    for chunk in tqdm(chunks, desc="Генерация текста", unit="часть"):
        generated_chunk = generate_text(chunk)
        results.append(generated_chunk)

    return ' '.join(results)

# Функция для отделения диалогов и авторской речи
def separate_dialogue_and_narration(text):
    lines = text.split('\n')
    narration = []
    dialogue = []

    # Регулярное выражение для распознавания диалогов
    dialogue_pattern = re.compile(r'^\s*[–—]\s*(.+)$')

    for line in lines:
        line = line.strip()
        if dialogue_pattern.match(line):
            dialogue.append(line)
        else:
            narration.append(line)

    return '\n'.join(narration), '\n'.join(dialogue)

# Основная точка входа
if __name__ == "__main__":
    input_file_path = 'book\\129769.fb2'  # Укажите путь к вашему FB2 файлу
    input_text = read_fb2_file(input_file_path)

    # Проверка длины текста перед обработкой
    print(f"Общая длина токенов исходного текста: {len(tokenizer.encode(input_text))}")

    # Генерация текста
    generated_text = process_text(input_text)

    # Разделение на авторскую речь и диалоги
    narration, dialogue = separate_dialogue_and_narration(generated_text)

    # Очистка текста перед записью в файл
    # narration = clean_text(narration)
    # dialogue = clean_text(dialogue)

    # Сохранение результатов
    with open('narration_output.txt', 'w', encoding='utf-8') as narr_file:
        narr_file.write(narration)

    with open('dialogue_output.txt', 'w', encoding='utf-8') as dial_file:
        dial_file.write(dialogue)

    # Вывод результата
    print("Авторская речь сохранена в файл 'narration_output.txt'.")
    print("Диалоги сохранены в файл 'dialogue_output.txt'.")
