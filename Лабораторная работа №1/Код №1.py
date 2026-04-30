s = input('Введите приложение(слово):')#Ввод строки

max_count = 0 # Максимальное кол-во повторений
most_char = "" # Сама буква

for i in range(len(s)): # Цикл перебирает каждую букву
    count = 0 #Обнуляет счетчик
    for j in range(len(s)): #Цикл считает сколько раз встречается буква
        if s[i] == s[j]: #Сравнивание букв
            count += 1
    if count > max_count:
        max_count = count
        most_char = s[i]

print("Самая часто повторяющаяся буква:", most_char)
print("Выводится:", max_count, "раз")
