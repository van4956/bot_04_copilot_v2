class SnakeGame {
    constructor() {
        // Получаем элемент canvas из HTML и его контекст для рисования
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');

        // Устанавливаем размеры игрового поля
        this.canvas.width = 300;  // ширина в пикселях
        this.canvas.height = 300; // высота в пикселях

        // Настройки сетки игрового поля
        this.gridSize = 15;  // поле 15x15 клеток
        this.tileSize = this.canvas.width / this.gridSize;  // размер одной клетки

        // Начальное состояние змейки - массив координат сегментов
        // Каждый сегмент это объект с координатами x и y
        this.snake = [
            {x: 7, y: 7}, // Голова змейки
            {x: 6, y: 7}, // Тело
            {x: 5, y: 7}  // Хвост
        ];

        // Направление движения змейки (по умолчанию вправо)
        this.direction = 'right';

        // Скорость обновления игры в миллисекундах
        this.speed = 150; // чем меньше число, тем быстрее движение

        // Текущий счет игрока
        this.score = 0;

        // Состояние игры
        this.isPaused = false;
        this.gameOver = false;

        // Цветовая схема
        this.colors = {
            background: '#1A1B2E',     // Глубокий индиго-черный для фона
            snake: '#A9A9A9',          // Металлический серый для змейки
            snakeHead: '#C0C0C0',      // Чуть светлее серый для головы
            food: '#F5F5F5',           // Нежно-белый для еды
            gameOverBg: 'rgba(26, 27, 46, 0.85)', // Полупрозрачный фон для экрана окончания игры
            gameOverText: '#F5F5F5'    // Нежно-белый для текста
        };

        // Кнопка паузы
        this.pauseButton = document.getElementById('pauseButton');
        this.pauseButton.addEventListener('click', () => this.togglePause());

        // Запускаем инициализацию игры
        this.init();
    }

    // Метод инициализации игры
    init() {
        this.bindControls();  // Привязываем управление
        this.createFood();    // Создаем первую еду
        this.gameLoop();      // Запускаем игровой цикл
    }

    // Метод для переключения паузы
    togglePause() {
        this.isPaused = !this.isPaused;
        this.pauseButton.textContent = this.isPaused ? 'Продолжить' : 'Пауза';
        if (!this.isPaused) {
            this.gameLoop();
        }
    }

    // Метод привязки элементов управления
    bindControls() {
        // Обработчик нажатий клавиш на клавиатуре
        document.addEventListener('keydown', (e) => {
            if (this.isPaused) return; // Игнорируем управление на паузе

            switch(e.key) {
                case 'ArrowUp':    // Если нажата стрелка вверх
                    if (this.direction !== 'down') this.direction = 'up';
                    break;
                case 'ArrowDown':  // Если нажата стрелка вниз
                    if (this.direction !== 'up') this.direction = 'down';
                    break;
                case 'ArrowLeft':  // Если нажата стрелка влево
                    if (this.direction !== 'right') this.direction = 'left';
                    break;
                case 'ArrowRight': // Если нажата стрелка вправо
                    if (this.direction !== 'left') this.direction = 'right';
                    break;
            }
        });

        // Обработчики нажатий экранных кнопок
        document.getElementById('upButton').addEventListener('click', () => {
            if (!this.isPaused && this.direction !== 'down') this.direction = 'up';
        });
        document.getElementById('downButton').addEventListener('click', () => {
            if (!this.isPaused && this.direction !== 'up') this.direction = 'down';
        });
        document.getElementById('leftButton').addEventListener('click', () => {
            if (!this.isPaused && this.direction !== 'right') this.direction = 'left';
        });
        document.getElementById('rightButton').addEventListener('click', () => {
            if (!this.isPaused && this.direction !== 'left') this.direction = 'right';
        });
    }

    // Метод создания новой еды
    createFood() {
        do {
            // Генерируем случайные координаты в пределах игрового поля
            this.food = {
                x: Math.floor(Math.random() * this.gridSize),
                y: Math.floor(Math.random() * this.gridSize)
            };
        // Проверяем, не появилась ли еда внутри змейки
        } while (this.snake.some(segment =>
            segment.x === this.food.x && segment.y === this.food.y));
    }

    // Основной игровой цикл
    gameLoop() {
        if (this.gameOver || this.isPaused) return;  // Прерываем цикл если игра окончена или на паузе

        // Планируем следующее обновление через this.speed миллисекунд
        setTimeout(() => {
            this.update();  // Обновляем состояние игры
            this.draw();    // Отрисовываем новое состояние
            this.gameLoop(); // Запускаем следующий цикл
        }, this.speed);
    }

    // Метод обновления состояния игры
    update() {
        // Создаем новую голову змейки на основе текущей
        const head = {x: this.snake[0].x, y: this.snake[0].y};

        // Обновляем позицию головы в зависимости от направления
        switch(this.direction) {
            case 'up': head.y--; break;
            case 'down': head.y++; break;
            case 'left': head.x--; break;
            case 'right': head.x++; break;
        }

        // Проверяем столкновение со стеной
        if (head.x < 0 || head.x >= this.gridSize ||
            head.y < 0 || head.y >= this.gridSize) {
            this.gameOver = true;
            return;
        }

        // Проверяем столкновение с собой
        if (this.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
            this.gameOver = true;
            return;
        }

        // Добавляем новую голову в начало массива
        this.snake.unshift(head);

        // Проверяем, съела ли змейка еду
        if (head.x === this.food.x && head.y === this.food.y) {
            // Увеличиваем счет
            this.score += 10;
            document.getElementById('score').textContent = this.score;
            // Создаем новую еду
            this.createFood();
        } else {
            // Если еду не съели, удаляем последний сегмент змейки
            this.snake.pop();
        }
    }

    // Метод отрисовки игры
    draw() {
        // Очищаем все игровое поле
        this.ctx.fillStyle = this.colors.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Рисуем змейку
        this.snake.forEach((segment, index) => {
            this.ctx.fillStyle = index === 0 ? this.colors.snakeHead : this.colors.snake;
            this.ctx.fillRect(
                segment.x * this.tileSize,
                segment.y * this.tileSize,
                this.tileSize - 1,
                this.tileSize - 1
            );
        });

        // Рисуем еду
        this.ctx.fillStyle = this.colors.food;
        this.ctx.beginPath();
        this.ctx.arc(
            this.food.x * this.tileSize + this.tileSize/2,
            this.food.y * this.tileSize + this.tileSize/2,
            this.tileSize/2 - 1,
            0,
            Math.PI * 2
        );
        this.ctx.fill();

        // Если игра окончена, показываем сообщение
        if (this.gameOver) {
            this.ctx.fillStyle = this.colors.gameOverBg;
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

            this.ctx.fillStyle = this.colors.gameOverText;
            this.ctx.font = '20px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(
                'Игра окончена! Счёт: ' + this.score,
                this.canvas.width/2,
                this.canvas.height/2
            );
        }
    }
}
