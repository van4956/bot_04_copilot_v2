// Инициализация Telegram WebApp
const webapp = window.Telegram.WebApp; // Создаем экземпляр веб-приложения Telegram
webapp.ready(); // Сообщаем Telegram, что приложение готово к работе

// Получаем элементы со страницы по их ID
const minInput = document.getElementById('min'); // Поле ввода минимального значения
const maxInput = document.getElementById('max'); // Поле ввода максимального значения
const resultDisplay = document.getElementById('result'); // Элемент для отображения результата
const generateBtn = document.getElementById('generateBtn'); // Кнопка генерации

// Функция анимации чисел - создает эффект "прокрутки" чисел
function animateNumber(from, to, duration = 2000) { // from - начальное число, to - конечное, duration - длительность анимации
    const start = performance.now(); // Засекаем время начала анимации
    const range = to - from; // Вычисляем диапазон чисел
    let lastNumber = from; // Храним последнее показанное число

    function update(currentTime) { // Функция обновления анимации
        const elapsed = currentTime - start; // Вычисляем прошедшее время
        const progress = Math.min(elapsed / duration, 1); // Вычисляем прогресс анимации (от 0 до 1)

        if (progress < 1) { // Если анимация еще не завершена
            if (Math.random() < 0.3) { // С вероятностью 30% обновляем число
                const randomValue = Math.floor(Math.random() * range + from); // Генерируем случайное число в диапазоне
                if (randomValue !== lastNumber) { // Если новое число отличается от предыдущего
                    lastNumber = randomValue; // Обновляем последнее число
                    resultDisplay.textContent = randomValue; // Отображаем новое число
                }
            }
            requestAnimationFrame(update); // Запрашиваем следующий кадр анимации
        } else { // Если анимация завершена
            resultDisplay.textContent = to; // Показываем конечное число
            resultDisplay.classList.add('animate'); // Добавляем класс для анимации
            if (window.navigator.vibrate) { // Если устройство поддерживает вибрацию
                window.navigator.vibrate(100); // Вибрируем 100мс
            }
            setTimeout(() => resultDisplay.classList.remove('animate'), 300); // Убираем класс анимации через 300мс
        }
    }

    requestAnimationFrame(update); // Запускаем анимацию
}

// Функция генерации случайного числа
function generateNumber() {
    const min = parseInt(minInput.value) || 1; // Получаем минимальное значение (или 1, если ввод некорректный)
    const max = parseInt(maxInput.value) || 100; // Получаем максимальное значение (или 100, если ввод некорректный)

    const validMin = Math.min(min, max); // Определяем правильное минимальное значение
    const validMax = Math.max(min, max); // Определяем правильное максимальное значение

    minInput.value = validMin; // Обновляем поле минимального значения
    maxInput.value = validMax; // Обновляем поле максимального значения

    const result = Math.floor(Math.random() * (validMax - validMin + 1)) + validMin; // Генерируем случайное число
    animateNumber(validMin, result); // Запускаем анимацию от минимального до сгенерированного числа
}

// Обработчики событий при вводе значений
minInput.addEventListener('input', () => { // При изменении минимального значения
    const min = parseInt(minInput.value) || 1;
    const max = parseInt(maxInput.value) || 100;
    if (min > max) { // Если минимальное больше максимального
        maxInput.value = min; // Устанавливаем максимальное равным минимальному
    }
});

maxInput.addEventListener('input', () => { // При изменении максимального значения
    const min = parseInt(minInput.value) || 1;
    const max = parseInt(maxInput.value) || 100;
    if (max < min) { // Если максимальное меньше минимального
        minInput.value = max; // Устанавливаем минимальное равным максимальному
    }
});

generateBtn.addEventListener('click', generateNumber); // Добавляем обработчик клика на кнопку

// Инициализация - генерируем первое число при загрузке
generateNumber();