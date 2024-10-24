import xml.etree.ElementTree as ET
import spacy
import re

# Загрузка языковой модели
nlp = spacy.load('ru_core_news_sm')

def parse_fb2(file_path):
    """Парсит FB2 файл и извлекает текст."""
    try:
        tree = ET.parse(file_path)
    except ET.ParseError as e:
        print(f"Ошибка при парсинге файла: {e}")
        return None

    root = tree.getroot()

    # Извлечение текста
    body = root.find('{http://www.gribuser.ru/xml/fictionbook/2.0}body')
    text_content = ""
    if body is not None:
        for elem in body.iter():
            if elem.tag == '{http://www.gribuser.ru/xml/fictionbook/2.0}p':
                text_content += (elem.text or "").strip() + "\n"
            elif elem.tag == '{http://www.gribuser.ru/xml/fictionbook/2.0}section':
                for sec_elem in elem.iter('{http://www.gribuser.ru/xml/fictionbook/2.0}p'):
                    text_content += (sec_elem.text or "").strip() + "\n"

    return text_content.strip() if text_content.strip() else None

def parse_text(text):
    """Разделяет текст на диалоги и авторскую речь."""
    dialogues = []
    author_speech = []

    # Разделяем текст на предложения с использованием spaCy
    doc = nlp(text)

    current_dialogue = ""
    current_author_speech = ""

    for sent in doc.sents:
        sentence = sent.text.strip()

        # Проверяем, начинается ли предложение с диалогового символа
        if re.match(r'^[—“]', sentence):  # Учитываем разные символы для диалога
            # Если есть текущая авторская речь, добавляем ее в список
            if current_author_speech:
                author_speech.append(current_author_speech.strip())
                current_author_speech = ""
            # Добавляем текущий диалог
            current_dialogue += sentence + " "
        else:
            # Если это не диалог, добавляем к текущей авторской речи
            current_author_speech += sentence + " "

    # Добавляем последний диалог и авторскую речь, если они есть
    if current_dialogue:
        dialogues.append(current_dialogue.strip())
    if current_author_speech:
        author_speech.append(current_author_speech.strip())

    return dialogues, author_speech

# Путь к FB2 файлу
file_path = 'book/testbook.fb2'

# Парсим FB2 файл
full_text = parse_fb2(file_path)

# Проверка на наличие текста
if full_text:
    # Парсим текст для получения диалогов и авторской речи
    dialogues, author_speech = parse_text(full_text)

    # Выводим результаты
    print("\nДиалоги:")
    for i, dialogue in enumerate(dialogues, 1):
        print(f"Диалог {i}: {dialogue}")

    print("\nАвторская речь:")
    for i, speech in enumerate(author_speech, 1):
        print(f"Авторская речь {i}: {speech}")
else:
    print("Не удалось извлечь текст из файла.")
