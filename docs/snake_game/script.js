// Инициализация Telegram WebApp
const webapp = window.Telegram.WebApp;
webapp.ready();
webapp.expand();

// Настраиваем обработчики событий
webapp.onEvent('mainButtonClicked', function() {
    // Данные будут отправлены при клике на главную кнопку
    const gameData = {
        action: 'game_end',
        game: 'snake',
        score: window.game ? window.game.score : 0
    };
    webapp.sendData(JSON.stringify(gameData));
});

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