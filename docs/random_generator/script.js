// Инициализация Telegram WebApp
const webapp = window.Telegram.WebApp;
webapp.ready();

// Подстраиваем тему под настройки пользователя
document.documentElement.style.setProperty('--tg-theme-bg-color', webapp.backgroundColor);
document.documentElement.style.setProperty('--tg-theme-text-color', webapp.textColor);
document.documentElement.style.setProperty('--tg-theme-button-color', webapp.buttonColor);
document.documentElement.style.setProperty('--tg-theme-button-text-color', webapp.buttonTextColor);

// Получаем элементы
const minInput = document.getElementById('min');
const maxInput = document.getElementById('max');
const resultDisplay = document.getElementById('result');
const generateBtn = document.getElementById('generateBtn');

// Функция анимации чисел
function animateNumber(from, to, duration = 2000) { // Увеличили длительность с 1000 до 2000
    const start = performance.now();
    const range = to - from;
    let lastNumber = from;

    function update(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);

        // Добавляем эффект замедления
        const easeOut = 1 - Math.pow(1 - progress, 3);

        if (progress < 1) {
            // Замедляем частоту обновления чисел
            if (Math.random() < 0.3) { // Уменьшаем вероятность обновления
                const randomValue = Math.floor(Math.random() * range + from);
                if (randomValue !== lastNumber) {
                    lastNumber = randomValue;
                    resultDisplay.textContent = randomValue;
                }
            }
            requestAnimationFrame(update);
        } else {
            resultDisplay.textContent = to;
            resultDisplay.classList.add('animate');
            if (window.navigator.vibrate) {
                window.navigator.vibrate(100);
            }
            setTimeout(() => resultDisplay.classList.remove('animate'), 300);
        }
    }

    requestAnimationFrame(update);
}

// Функция генерации случайного числа
function generateNumber() {
    const min = parseInt(minInput.value) || 1;
    const max = parseInt(maxInput.value) || 100;

    const validMin = Math.min(min, max);
    const validMax = Math.max(min, max);

    minInput.value = validMin;
    maxInput.value = validMax;

    const result = Math.floor(Math.random() * (validMax - validMin + 1)) + validMin;
    animateNumber(validMin, result);
}

// Обновляем обработчики событий
// Убираем автоматическую генерацию при вводе
minInput.addEventListener('input', () => {
    // Только валидация
    const min = parseInt(minInput.value) || 1;
    const max = parseInt(maxInput.value) || 100;
    if (min > max) {
        maxInput.value = min;
    }
});

maxInput.addEventListener('input', () => {
    // Только валидация
    const min = parseInt(minInput.value) || 1;
    const max = parseInt(maxInput.value) || 100;
    if (max < min) {
        minInput.value = max;
    }
});

// Добавляем обработчик для кнопки
generateBtn.addEventListener('click', generateNumber);

// Генерируем первое число при загрузке
generateNumber();