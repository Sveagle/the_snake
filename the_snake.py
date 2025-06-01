"""Для работы приложения необходимы методы choice, randint из модуля
random, также модуль pygame, как отвечающий за графический интерфейс программы.
"""

from random import choice, randint

import pygame as pg

import sys

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
BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = RED
SPEED = 20
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

pg.display.set_caption('Змейка')

clock = pg.time.Clock()


class GameObject:
    """Родительский класс, определяющий основные характеристики объектов."""

    def __init__(self, position=None, body_color=None) -> None:
        """Инициализиция объекта."""
        self.position = CENTER_POSTITON
        self.body_color = None

    def draw(self, position, body_color) -> None:
        """Отрисовка объекта. Должен быть переопределён в дочерних классах."""
        rect = (pg.Rect(position, (GRID_SIZE, GRID_SIZE)))
        pg.draw.rect(screen, body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Дочерний класс - <<Яблоко>>. Объект, который при колиззии со змейкой
    увеличивает ее длину на одну ячейку.

    При столкновении со змейкой:
    - Длина змейки += 1
    - Переопределяется позиция на новую, случайную.

    Атрибуты:
        position (tuple[int, int]): Координаты (x, y) на игровом поле
        body_color (str): Цвет яблока (по умолчанию 'RED')
        occupied_postions (tuple[int, int]): Занятые позиции на поле.
    """

    def __init__(self, body_color=RED, positions=CENTER_POSTITON):
        super().__init__()
        self.occupied_positions = positions
        self.randomize_position()
        self.body_color = body_color

    def randomize_position(self):
        """Случайным образом определяет позицию яблока."""
        while True:
            new_position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                            randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
            if new_position not in self.occupied_positions:
                self.position = new_position
                break

    def draw(self):
        """Отрисовка яблока."""
        return super().draw(position=self.position,
                            body_color=self.body_color)


class Snake(GameObject):
    """Дочерний класс <<Змейка>> - главный объект программы, находится
    под контролем игрока, обладает четырьмя направления движения,
    уничтожается при колиззии с самим собой/объектом НЕ <<Яблоко>>.
    """

    def __init__(self, body_color=None):
        super().__init__()
        self.body_color = body_color
        self.last = None
        self.reset()

    def update_direction(self, direction):
        """Обновляет движение направления змейки"""
        self.direction = direction

    def move(self):
        """Обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions и удаляя
        последний элемент, если длина змейки не увеличилась.
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
        super().draw(self.positions[0], self.body_color)
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """возвращает позицию головы змейки
        (первый элемент в списке positions).
        """
        return self.positions[0]

    def reset(self):
        """Сброс змейки в исходное состояние"""
        self.length = 1
        self.positions = [self.position]
        directions = (UP, DOWN, LEFT, RIGHT)
        self.direction = choice(directions)


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
                sys.exit()


def main():
    """Основной процесс игры, в котором применены и скомпонованы все выше-
    описанные функции и классы в единую логику.
    """
    pg.init()
    snake = Snake(GREEN)
    apple = Apple(RED, snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(game_object=snake)
        snake.move()
        if apple.position == snake.get_head_position():
            apple.randomize_position()
            snake.length += 1
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
