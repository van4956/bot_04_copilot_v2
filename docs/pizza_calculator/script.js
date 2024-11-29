// Инициализация Telegram WebApp
const webapp = window.Telegram.WebApp; // Создаем экземпляр веб-приложения Telegram
webapp.ready(); // Сообщаем Telegram, что приложение готово к работе

// Подстраиваем тему под настройки пользователя
document.documentElement.style.setProperty('--tg-theme-bg-color', webapp.backgroundColor); // Устанавливаем цвет фона
document.documentElement.style.setProperty('--tg-theme-text-color', webapp.textColor); // Устанавливаем цвет текста
document.documentElement.style.setProperty('--tg-theme-button-color', webapp.buttonColor); // Устанавливаем цвет кнопок
document.documentElement.style.setProperty('--tg-theme-button-text-color', webapp.buttonTextColor); // Устанавливаем цвет текста кнопок

// Получаем элементы со страницы
const diameterInput = document.getElementById('diameter'); // Поле ввода диаметра
const quantityInput = document.getElementById('quantity'); // Поле ввода количества
const priceInput = document.getElementById('price'); // Поле ввода цены
const pricePerCmSpan = document.getElementById('price-per-cm'); // Элемент для вывода цены за см²
const pricePerPizzaSpan = document.getElementById('price-per-pizza'); // Элемент для вывода цены за пиццу

// Функция расчета стоимости
function calculatePricePerCm() {
    const diameter = parseFloat(diameterInput.value); // Получаем значение диаметра
    const quantity = parseFloat(quantityInput.value) || 1; // Получаем количество (если не указано, то 1)
    const totalPrice = parseFloat(priceInput.value); // Получаем общую цену

    if (diameter && totalPrice) { // Если указаны диаметр и цена
        const area = Math.PI * Math.pow(diameter / 2, 2); // Вычисляем площадь пиццы
        const pricePerPizza = totalPrice / quantity; // Вычисляем цену одной пиццы
        const pricePerCm = pricePerPizza / area; // Вычисляем цену за квадратный сантиметр

        // Выводим результаты с округлением до двух знаков после запятой
        pricePerCmSpan.textContent = pricePerCm.toFixed(2);
        pricePerPizzaSpan.textContent = Math.round(pricePerPizza); // Округляем до целого числа
    } else {
        // Если не хватает данных, выводим нули
        pricePerCmSpan.textContent = '0.00';
        pricePerPizzaSpan.textContent = '0';
    }
}

// Добавляем обработчики событий для автоматического пересчета
diameterInput.addEventListener('input', calculatePricePerCm); // При изменении диаметра
quantityInput.addEventListener('input', calculatePricePerCm); // При изменении количества
priceInput.addEventListener('input', calculatePricePerCm); // При изменении цены