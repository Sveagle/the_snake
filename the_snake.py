"""Для работы приложения необходимы методы choice, randint из модуля
random, также модуль pygame, как отвечающий за графический интерфейс программы.
"""

from random import choice, randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 20
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

pygame.display.set_caption('Змейка')

clock = pygame.time.Clock()


class GameObject:
    """Родительский класс, определяющий основные характеристики объектов"""

    def __init__(self) -> None:
        """Инициализиция объекта"""
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = None

    def draw(self):
        """Отрисовка объекта в программе"""
        pass


class Apple(GameObject):
    """Дочерний класс - <<Яблоко>>. Объект, который при колиззии со змейкой
    увеличивает ее длину на одну ячейку.
    """

    @staticmethod
    def randomize_position():
        """Случайным образом определяет позицию яблока."""
        position = (randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                    randint(0, GRID_HEIGHT - 1) * GRID_SIZE)
        return position

    def __init__(self):
        super().__init__()
        self.position = Apple.randomize_position()
        self.body_color = APPLE_COLOR

    def draw(self):
        """Метод отрисовывает яблоко на экране."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Дочерний класс <<Змейка>> - главный объект программы, находится
    под контролем игрока, обладает четырьмя направления движения,
    уничтожается при колиззии с самим собой/объектом НЕ <<Яблоко>>.
    """

    def __init__(self):
        super().__init__()
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def update_direction(self):
        """Обновляет движение направления змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions и удаляя
        последний элемент, если длина змейки не увеличилась.
        """
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction

        future_x = head_x + direction_x * GRID_SIZE
        future_y = head_y + direction_y * GRID_SIZE

        if future_x > SCREEN_WIDTH:
            future_x = 0
        elif future_y > SCREEN_HEIGHT:
            future_y = 0
        elif future_x < 0:
            future_x = SCREEN_WIDTH - GRID_SIZE
        elif future_y < 0:
            future_y = SCREEN_HEIGHT - GRID_SIZE

        coordinate = (future_x, future_y)

        self.positions.insert(0, coordinate)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Отрисовка"""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """возвращает позицию головы змейки
        (первый элемент в списке positions).
        """
        return self.positions[0]

    def reset(self):
        """Сброс змейки в исходное состояние"""
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        directions = (UP, DOWN, LEFT, RIGHT)
        self.direction = choice(directions)


def handle_keys(game_object):
    """Функция, принимает указание направления для объекта и устанавливает
    значения в соответсвующую переменную.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной процесс игры, в котором применены и скомпонованы все выше-
    описанные функции и классы в единую логику.
    """
    pygame.init()
    apple = Apple()
    snake = Snake()

    while True:
        clock.tick(SPEED)
        handle_keys(game_object=snake)
        snake.update_direction()
        snake.move()
        if apple.position in snake.positions:
            apple.position = apple.randomize_position()
            snake.length += 1
        if snake.positions[0] in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
