import wave # Модуль для работы с .wav аудиофайлами
import numpy as np # Библиотека для работы с массивами и математикой.
import matplotlib.pyplot as plt # Библиотека для построения графиков.
import time # Нужна для измерения времени выполнения программы.

def run_audio_analysis(): # Главная функция программы
    filename = input("Введите имя wav-файла (с расширением .wav): ").strip() # Ввод данных  .strip() убирает лишние пробелы
    
    try: #
        n_input = input("Введите желаемое количество отсчетов (например, 500): ") # Вводим, сколько точек анализировать
        n_points = int(n_input) if n_input.strip() else 1000 # Если введено число используем его
        if n_points <= 0: # Проверка: число должно быть положительным
            raise ValueError 
    except ValueError: # Если ошибка → ставим 1000
        print("Введено некорректное число. Установлено значение по умолчанию: 1000") 
        n_points = 1000 

    start_time = time.time()  # Запоминаем время начала работы

    try:                                             #  Чтение из wav файла 
        with wave.open(filename, 'r') as wav_file: # Открываем файл в режиме чтения
            # Получение параметров аудио
            framerate = wav_file.getframerate() # Частота дискретизации
            n_channels = wav_file.getnchannels() # Количество каналов
            n_frames = wav_file.getnframes() # Количество аудио-сэмплов
            
            # Читаем все байты звука
            raw_data = wav_file.readframes(n_frames)
            
            # Преобразуем байты в числа (16-битный звук)
            signal = np.frombuffer(raw_data, dtype=np.int16)

            # Если файл стерео, берем только первый канал для анализа
            if n_channels > 1:
                signal = signal[::n_channels]

            # Ограничиваем количество отсчетов согласно вводу
            actual_n = min(n_points, len(signal))
            data = signal[:actual_n] # Берём нужный кусок сигнала

    except FileNotFoundError:  
        print(f"Ошибка: Файл '{filename}' не найден.") # Если файл не найден
        return
    except Exception as e: #
        print(f"Ошибка при обработке файла: {e}")
        return

    # ВРЕМЕННАЯ ОСЬ И ОСЦИЛЛОГРАММА 
    # Время каждого отсчета: t = index / framerate
    time_axis = np.arange(actual_n) / framerate

    # ДИСКРЕТНОЕ КОСИНУСНОЕ ПРЕОБРАЗОВАНИЕ (DCT) 
    N = actual_n # количество точек
    dct_result = np.zeros(N) # массив результата
    indices = np.arange(N) # массив индексов
    
    # Формула DCT-II
    for k in range(N): # Перебираем частоты
        cos_terms = np.cos(np.pi * k * (2 * indices + 1) / (2 * N)) #Считаем косинус по формуле DCT-II
        dct_result[k] = np.sum(data * cos_terms) # умножаем сигнал на косинусы
    
    # Частотная ось: f = k * framerate / (2 * N)
    freq_axis = np.arange(N) * framerate / (2 * N) # Формула перевода индекса в частоту

    # ВИЗУАЛИЗАЦИЯ (Пунктир с маркерами 'o')
    plt.figure(figsize=(12, 10)) #Создаём окно графиков

    # График 1: Дискретные отсчеты
    plt.subplot(4, 1, 1) # 4 графика, текущий — первый
    plt.plot(data, linestyle='--', marker='o', markersize=4, color='b')
    plt.title("Визуализация дискретных отсчетов")
    plt.xlabel("Номер отсчета (n)")
    plt.ylabel("Амплитуда (y)")
    plt.grid(True)

    # График 2: Осциллограмма 
    plt.subplot(4, 1, 2)
    plt.plot(time_axis, data, linestyle='--', marker='o', markersize=3, color='r') # Амплитуда по времени
    plt.title("Осциллограмма звукового сигнала")
    plt.xlabel("Время (секунды)")
    plt.ylabel("Амплитуда (y)")
    plt.grid(True)

    # График 3: Спектральный анализ 
    plt.subplot(4, 1, 3)
    plt.plot(freq_axis, np.abs(dct_result), linestyle='--', marker='o', 
             markersize=3, color='g')
    plt.title("Спектр (Дискретное косинусное преобразование)")
    plt.xlabel("Частота (Герцы)")
    plt.ylabel("Мощность спектра")
    plt.grid(True)

    # График 4: Гистограмма
    plt.subplot(4, 1, 4)
    plt.hist(data, bins=30, color='purple', edgecolor='black', alpha=0.7)
    plt.title("Гистограмма отсчетов сигнала")
    plt.xlabel("Амплитуда (интервалы)")
    plt.ylabel("Частота попадания (количество)")
    plt.grid(True)

    plt.tight_layout()
    
    # Вывод итоговой информации
    print("-" * 30)
    print(f"Обработка завершена успешно!")
    print(f"Частота дискретизации: {framerate} Гц")
    print(f"Всего отсчетов в файле: {n_frames}")
    print(f"Проанализировано отсчетов: {actual_n}")
    print(f"Время вычисления: {time.time() - start_time:.4f} seconds")
    print("-" * 30)

    plt.show()

if __name__ == "__main__":
    run_audio_analysis()