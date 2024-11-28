// Инициализация Telegram WebApp
const webapp = window.Telegram.WebApp;
webapp.ready();

// Подстраиваем тему под настройки пользователя
document.documentElement.style.setProperty('--tg-theme-bg-color', webapp.backgroundColor);
document.documentElement.style.setProperty('--tg-theme-text-color', webapp.textColor);
document.documentElement.style.setProperty('--tg-theme-button-color', webapp.buttonColor);
document.documentElement.style.setProperty('--tg-theme-button-text-color', webapp.buttonTextColor);

// Отправляем данные о запуске игры
webapp.sendData(JSON.stringify({
    action: 'game_start',
    game: 'snake'
}));

// Инициализируем игру после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    const game = new SnakeGame();
});