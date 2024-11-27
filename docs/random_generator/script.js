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

// Функция анимации чисел
function animateNumber(from, to, duration = 1000) {
    const start = performance.now();
    const range = to - from;

    function update(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);

        // Добавляем эффект замедления в конце
        const easeOut = 1 - Math.pow(1 - progress, 3);

        // Генерируем промежуточные случайные числа для эффекта "барабана"
        if (progress < 1) {
            const randomValue = Math.floor(Math.random() * range + from);
            resultDisplay.textContent = randomValue;
            requestAnimationFrame(update);
        } else {
            resultDisplay.textContent = to;
            resultDisplay.classList.add('animate');
            // Вибрация, если доступна
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

    // Проверяем и корректируем значения
    const validMin = Math.min(min, max);
    const validMax = Math.max(min, max);

    minInput.value = validMin;
    maxInput.value = validMax;

    const result = Math.floor(Math.random() * (validMax - validMin + 1)) + validMin;
    animateNumber(validMin, result);
}

// Обработчики событий
minInput.addEventListener('input', () => {
    if (minInput.value !== '') generateNumber();
});

maxInput.addEventListener('input', () => {
    if (maxInput.value !== '') generateNumber();
});

// Генерируем первое число при загрузке
generateNumber();