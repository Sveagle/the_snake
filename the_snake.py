"""
Модуль для реализации простого графического приложения.

Этот модуль предоставляет функционал для создания базового графического
интерфейса с использованием библиотеки Pygame, а также вспомогательные
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
BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = CYAN
APPLE_COLOR = RED
SNAKE_COLOR = GREEN
SPEED = 20
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

pg.display.set_caption('Змейка')

clock = pg.time.Clock()


class GameObject:
    """Родительский класс, определяющий основные характеристики объектов."""

    def __init__(self, position=CENTER_POSTITON, body_color=None) -> None:
        """Инициализиция объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self) -> None:
        """Отрисовка объекта. Должен быть переопределён в дочерних классах."""
        raise NotImplementedError(
            f"Метод 'draw' не реализован в классе {self.__class__.__name__}!"
        )

    def make_rect(self, position, body_color):
        """Создает квадрат для отрисовки."""
        rect = (pg.Rect(position, (GRID_SIZE, GRID_SIZE)))
        pg.draw.rect(screen, body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


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

    def __init__(self):
        """Инициализирует объект яблока.

        Args:
            position (tuple, optional): Начальная позиция яблока.
                По умолчанию None (случайная позиция).
            color (tuple, optional): Цвет яблока.
                По умолчанию APPLE_COLOR (красный).
        """
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, occupied_positions=set()):
        """Случайным образом определяет позицию яблока."""
        while True:
            self.position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                             randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовка яблока."""
        return super().make_rect(position=self.position,
                                 body_color=self.body_color)


class Snake(GameObject):
    """Игровой объект змейки, управляемый пользователем.

    Класс реализует поведение змейки в игре:
    - перемещение в 4-х направлениях
    - рост при съедании яблок
    - проверку столкновений с границами и самой собой
    """

    def __init__(self):
        super().__init__(body_color=SNAKE_COLOR)
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
        super().make_rect(self.get_head_position(), self.body_color)
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


def handle_keys(game_object):
    """Функция, принимает указание направления для объекта и устанавливает
    значения в соответсвующую переменную.
    """
    for event in pg.event.get():
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


def main():
    """Основной процесс игры, в котором применены и скомпонованы все выше-
    описанные функции и классы в единую логику.
    """
    pg.init()
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        handle_keys(game_object=snake)
        snake.move()
        if apple.position == snake.get_head_position():
            apple.randomize_position(snake.positions)
            snake.length += 1
        elif snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
