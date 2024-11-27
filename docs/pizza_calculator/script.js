// Инициализация Telegram WebApp
const webapp = window.Telegram.WebApp;
webapp.ready();

// Подстраиваем тему под настройки пользователя
document.documentElement.style.setProperty('--tg-theme-bg-color', webapp.backgroundColor);
document.documentElement.style.setProperty('--tg-theme-text-color', webapp.textColor);
document.documentElement.style.setProperty('--tg-theme-button-color', webapp.buttonColor);
document.documentElement.style.setProperty('--tg-theme-button-text-color', webapp.buttonTextColor);

// Получаем элементы
const calculateButton = document.getElementById('calculate');
const diameterInput = document.getElementById('diameter');
const priceInput = document.getElementById('price');
const pricePerCmSpan = document.getElementById('price-per-cm');

// Функция расчета
function calculatePricePerCm() {
    const diameter = parseFloat(diameterInput.value);
    const price = parseFloat(priceInput.value);

    if (diameter && price) {
        const area = Math.PI * Math.pow(diameter / 2, 2);
        const pricePerCm = price / area;
        pricePerCmSpan.textContent = pricePerCm.toFixed(2);
    } else {
        pricePerCmSpan.textContent = '0.00';
    }
}

// Обработчики событий
calculateButton.addEventListener('click', calculatePricePerCm);