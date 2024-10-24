import lxml.etree as ET
import os

def parse_fb2(file_path):
    # Проверяем, существует ли файл
    if not os.path.isfile(file_path):
        print(f"Файл не найден: {file_path}")
        return

    # Парсим FB2 файл
    with open(file_path, 'rb') as file:
        tree = ET.parse(file)
        root = tree.getroot()

    # Пространство имен FB2
    ns = {'fb2': 'http://www.gribuser.ru/xml/fictionbook/2.0'}

    # Извлекаем заголовок книги
    title_info = root.find('fb2:description/fb2:title-info', ns)
    if title_info is not None:
        title = title_info.find('fb2:book-title', ns)
        title_text = title.text if title is not None else "Заголовок отсутствует"

        author_first = title_info.find('fb2:author/fb2:first-name', ns)
        author_last = title_info.find('fb2:author/fb2:last-name', ns)

        author = f"{author_first.text if author_first is not None else 'Имя отсутствует'} " \
                 f"{author_last.text if author_last is not None else 'Фамилия отсутствует'}"
    else:
        title_text = "Заголовок отсутствует"
        author = "Автор отсутствует"

    print(f"Заголовок: {title_text}")
    print(f"Автор: {author}")

    # Извлекаем содержание книги
    body = root.find('fb2:body', ns)

    if body is None:
        print("Не удалось найти тело книги.")
        return

    # Подготовка для записи в файл
    output_text = []

    # Итерируемся по элементам тела книги
    for section in body.findall('fb2:section', ns):
        title = section.find('fb2:title', ns)
        if title is not None:
            output_text.append(f"Заголовок раздела: {title.text}")

        # Ищем текстовые элементы
        for elem in section.findall('.//fb2:p', ns):
            text = elem.text
            if text and text.strip():  # Проверяем, что текст не пустой
                output_text.append(text.strip())

    # Записываем весь текст в файл
    with open('output.txt', 'w', encoding='utf-8') as output_file:
        output_file.write("\n".join(output_text))

    print("Обработка завершена. Весь текст сохранен в 'output.txt'.")


# Пример использования
file_path = 'book/129769.fb2'  # Укажите ваш путь к файлу
parse_fb2(file_path)
