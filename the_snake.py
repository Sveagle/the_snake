"""
Модуль для реализации простого графического приложения - "Змейка".

Этот модуль предоставляет функционал для создания базового графического
интерфейса змейки с использованием библиотеки Pygame, а также вспомогательные
функции для работы со случайными числами.

Доступные импортируемые объекты:
- sys: модуль для работы с системными параметрами и функциями
- choice: функция выбора случайного элемента из последовательности
- randint: функция генерации случайного целого числа в заданном диапазоне
- pg (pygame): модуль для работы с графикой и создания интерфейса
"""

import sys
from random import choice, randint

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_POSTITON = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
CYAN = (93, 216, 228)
GRAY = (105, 105, 105)
SLATEGRAY = (112, 128, 144)
WHITE = (255, 255, 255)
BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = CYAN
APPLE_COLOR = RED
SNAKE_COLOR = GREEN
SPEED = 20
PAUSED = False
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

pg.display.set_caption('Змейка')

clock = pg.time.Clock()


def draw_screen():
    """Отрисовка экрана."""
    screen.fill((0, 0, 0))


def draw_grid(border=SLATEGRAY):
    """Отрисовка сетки в игре."""
    for x in range(0, screen.get_width(), GRID_SIZE):
        pg.draw.line(screen, border, (x, 0), (x, screen.get_height()))
    for y in range(0, screen.get_height(), GRID_SIZE):
        pg.draw.line(screen, border, (0, y), (screen.get_width(), y))


def draw_text(length):
    """Отрисовка текста."""
    font = pg.font.SysFont('Arial', 20)
    text_surface = font.render(f'Счет: {length}', True, WHITE)
    text_bg = pg.Surface((75, 25), pg.SRCALPHA)
    text_bg.fill((0, 0, 0, 128))
    text_bg.blit(text_surface, (5, 5))
    screen.blit(text_bg, (10, 10))
    # if PAUSED:
    #     pause_text = font.render("ПАУЗА", True, WHITE)
    #     text_rect = pause_text.get_rect(center=(120, 40))
    #     screen.blit(pause_text, text_rect)


def call_once(func):
    """Декоратор. Обеспечивает вызов функции единожды."""
    called = False

    def wrapper(*args, **kwargs):
        nonlocal called
        if not called:
            called = True
            return func(*args, **kwargs)
    return wrapper


def call_once_per_key(key_func):
    """Декоратор. При срабатанывании условия вызывает раз в цикле функцию."""
    called_keys = set()

    def decorator(func):
        def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs)
            if key not in called_keys:
                called_keys.add(key)
                return func(*args, **kwargs)
            return None
        wrapper.reset = lambda: called_keys.clear()
        return wrapper
    return decorator


class GameObject:
    """Родительский класс, определяющий основные характеристики объектов."""

    def __init__(self, position=CENTER_POSTITON, body_color=None) -> None:
        """Инициализиция объекта."""
        self.position = position
        self.body_color = body_color

    def randomize_position(self, occupied_positions=None):
        """Случайным образом определяет позицию объекта."""
        if occupied_positions is None:
            occupied_positions = set()
        while True:
            self.position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                             randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if self.position not in occupied_positions:
                break
        return self.position

    def draw(self) -> None:
        """Отрисовка объекта. Должен быть переопределён в дочерних классах."""
        raise NotImplementedError(
            f"Метод 'draw' не реализован в классе {self.__class__.__name__}!"
        )

    def make_rect(self, position, body_color, border=SLATEGRAY):
        """Создает квадрат для отрисовки."""
        rect = (pg.Rect(position, (GRID_SIZE, GRID_SIZE)))
        pg.draw.rect(screen, body_color, rect)
        pg.draw.rect(screen, border, rect, 1)


class Apple(GameObject):
    """Объект яблока, увеличивающий длину змейки при столкновении.

    При столкновении со змейкой:
    - Длина змейки += 1
    - Переопределяется позиция на новую, случайную.

    Атрибуты:
        position (tuple[int, int]): Координаты (x, y) на игровом поле
        body_color (str): Цвет яблока (по умолчанию 'RED')
        occupied_postions (tuple[int, int]): Занятые позиции на поле.
    """

    def __init__(self, body_color=APPLE_COLOR, positions=None):
        """Инициализирует объект яблока.

        Args:
            position (tuple, optional): Начальная позиция яблока.
                По умолчанию None (случайная позиция).
            color (tuple, optional): Цвет яблока.
                По умолчанию APPLE_COLOR (красный).
        """
        super().__init__(body_color=body_color)
        super().randomize_position(positions)

    def draw(self):
        """Отрисовка яблока."""
        self.make_rect(position=self.position,
                       body_color=self.body_color)


class Stone(GameObject):
    """Объект камня, случайно расположенный на экране.

    Класс реализует поведения препятствия в игре:
    - При столкновении с камнем - сбросить змейку в исходное.
    """

    def __init__(self, body_color=GRAY):
        super().__init__(body_color=body_color)
        self.positions = [(-20, -20)]

    def draw(self):
        """Отрисовка камня."""
        for pos in self.positions:
            self.make_rect(position=pos,
                           body_color=self.body_color,
                           border=GRAY)

    @call_once_per_key(lambda self, length: length // 5)
    def add_new_stone(self, length):
        """Добавляет новый камень на карту при выполнении условия."""
        if length % 5 == 0:
            self.positions.append(super().randomize_position())


class Snake(GameObject):
    """Игровой объект змейки, управляемый пользователем.

    Класс реализует поведение змейки в игре:
    - перемещение в 4-х направлениях
    - рост при съедании яблок
    - проверку столкновений с границами и самой собой
    """

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color=body_color)
        self.reset()

    def update_direction(self, direction):
        """Обновляет движение направления змейки"""
        self.direction = direction

    def move(self):
        """Обновляет позиции сегментов змейки при перемещении.

        Добавляет новую голову в начало списка positions. Удаляет последний
        элемент хвоста, если змейка не увеличивается в длину
        """
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction

        future_x = (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        future_y = (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT

        coordinate = (future_x, future_y)

        self.positions.insert(0, coordinate)
        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )

    def draw(self):
        """Отрисовка змейки."""
        self.make_rect(self.get_head_position(), self.body_color)
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """возвращает позицию головы змейки
        (первый элемент в списке positions).
        """
        return self.positions[0]

    def reset(self):
        """Сброс змейки в исходное состояние."""
        self.length = 1
        self.positions = [self.position]
        directions = (UP, DOWN, LEFT, RIGHT)
        self.direction = choice(directions)
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Функция, принимает указание направления для объекта и устанавливает
    значения в соответсвующую переменную.
    """
    for event in pg.event.get():
        global PAUSED
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.update_direction(UP)
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.direction = RIGHT
            elif event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            elif event.key == pg.K_SPACE:
                PAUSED = not PAUSED


def main():
    """Основной процесс игры, в котором применены и скомпонованы все выше-
    описанные функции и классы в единую логику.
    """
    pg.init()
    snake = Snake()
    apple = Apple(positions=snake.positions)
    stone = Stone()
    while True:
        clock.tick(SPEED)
        # draw_screen()
        handle_keys(game_object=snake)
        if not PAUSED:
            snake.move()
        if apple.position == snake.get_head_position():
            apple.randomize_position(snake.positions + stone.positions
                                     + [CENTER_POSTITON])
            snake.length += 1
        elif snake.get_head_position() in snake.positions[4:]:
            snake.reset()
        elif snake.get_head_position() in stone.positions:
            stone.positions = [stone.positions[0]]
            stone.add_new_stone.reset()
            snake.reset()
        apple.draw()
        stone.draw()
        snake.draw()
        draw_grid()
        draw_text(snake.length)
        if snake.length % 5 == 0:
            stone.add_new_stone(snake.length)
        pg.display.update()


if __name__ == '__main__':
    main()
