from PIL import Image # Импорт класса Image из библиотеки Pillow

keys = [
    (360, 324), (437, 214), (507, 253), (153, 173), (278, 429), # Ключи по заданию (список координат по x, y) 
    (300, 254), (517, 129), (54, 461), (586, 403), (374, 238),
    (378, 126), (161, 92), (623, 105), (683, 329), (319, 370),
    (513, 224), (430, 284), (409, 265), (268, 229), (350, 450),
    (292, 428), (423, 253), (384, 437), (349, 179), (538, 319),
    (656, 153), (437, 211), (350, 492), (497, 301) 
]


# Декодирование по ключам
def decode_old(image_name):# Функция для извлечения текста из изображения
    image = Image.open(image_name).convert("RGB") # Открывает код и конвертирует в RGB
    text = ""

    for x, y in keys:
        r, g, b = image.getpixel((x, y)) # r- красный g-зеленый b- синий 
        text += chr(b) # превращает в симфол и добавляет к тексту

    return text


# Кодирование
def encode(image_name, output_name, text): # Функция которая прячет цвет в картинку
    image = Image.open(image_name).convert("RGB")
    pixels = image.load()

    print("\nПроверка ")

    if text:
        bits = format(ord(text[0]), "08b") # Берется 1 символ текста и ord превращает в число "08b" -8 битный бинарный вид
        print("Первый символ:", text[0])
        print("Биты:", bits)

    for i in range(len(text)): # Перебирает каждый симфол текста
        x, y = keys[i] # Координаты для текущего символа

        r, g, b = pixels[x, y]
        old_pixel = (r, g, b)

        byte = ord(text[i]) #Преобразуем символ в число

        r_part = (byte >> 4) & 0b1111 # Сдвигаем на 4 бита вправо, берём старшие 4 бита
        b_part = byte & 0b1111 # Берём младшие 4 бита

        new_r = (r & 0b11110000) | r_part # Очищаем младшие 4 бита красного канала и записываем
        new_b = (b & 0b11110000) | b_part # Очищаем младшие 4 бита синего канала и записываем

        new_pixel = (new_r, g, new_b) # Создаём новый пиксель
        pixels[x, y] = new_pixel # Записываем его в изображение

        print(f"\nПиксель {x,y}") 
        print("Было:", old_pixel) 
        print("Стало:", new_pixel) 

    image.save(output_name) 
    print("\nГотово! Сохранено в:", output_name) 


# Декодирование нового файла
def decode_new(image_name, length): # Функция для извлечения текста из новой схемы
    image = Image.open(image_name).convert("RGB") 
    text = ""

    for i in range(length): # Читаем только нужное количество символов
        x, y = keys[i] 
 
        r, g, b = image.getpixel((x, y)) 

        r_part = r & 0b1111
        b_part = b & 0b1111

        byte = (r_part << 4) | b_part # Собираем обратно байт стращие 4 из R и младшие из B
        text += chr(byte)

    return text

print("1 — Декодировать по ключам")
print("2 — Закодировать текст в картинку")
print("3 — Декодировать свою картинку")

choice = input("Выбор: ")

if choice == "1":
    img = input("Имя картинки: ")
    print("Сообщение:", decode_old(img))

elif choice == "2":
    img = input("Исходная картинка: ")
    out = input("Куда сохранить: ")

    if not out.endswith(".png"):
        out += ".png"

    text = input("Текст: ")

    if len(text) > len(keys):
        print("Ошибка: текст слишком длинный!")
    else:
        encode(img, out, text)

elif choice == "3":
    img = input("Имя картинки: ")
    length = int(input("Сколько символов было зашифровано: "))
    print("Сообщение:", decode_new(img, length))