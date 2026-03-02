# Ввод строки
text = input("Введите строку: ")

max_count = 0
most_char = ""

# Проходим по каждой букве
for i in text:
    count = 0
    
    # Считаем сколько раз она встречается
    for j in text:
        if i == j:
            count += 1
    
    # Проверяем максимум
    if count > max_count:
        max_count = count
        most_char = i

# Вывод результата
print("Самая часто встречающаяся буква:", most_char)
print("Количество повторений:", max_count)