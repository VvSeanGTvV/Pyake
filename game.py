import pygame
import random
import sys
from enum import Enum

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)

# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

class SnakeHead(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT

    def update(self):
        # Update direction
        self.direction = self.next_direction

        # Move head
        dx, dy = self.direction.value
        self.rect.x += dx * GRID_SIZE
        self.rect.y += dy * GRID_SIZE

        # Wrap around screen
        if self.rect.x >= SCREEN_WIDTH:
            self.rect.x = 0
        elif self.rect.x < 0:
            self.rect.x = SCREEN_WIDTH - GRID_SIZE
        if self.rect.y >= SCREEN_HEIGHT:
            self.rect.y = 0
        elif self.rect.y < 0:
            self.rect.y = SCREEN_HEIGHT - GRID_SIZE

    def change_direction(self, new_direction):
        # Prevent 180-degree turns
        if (new_direction == Direction.UP and self.direction != Direction.DOWN or
                new_direction == Direction.DOWN and self.direction != Direction.UP or
                new_direction == Direction.LEFT and self.direction != Direction.RIGHT or
                new_direction == Direction.RIGHT and self.direction != Direction.LEFT):
            self.next_direction = new_direction

class SnakeBody(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE

class SnakeTail(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE

class Food(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.spawn()

    def spawn(self):
        self.rect.x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
        self.rect.y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.spawn()
        self.direction = random.choice(list(Direction))
        self.move_counter = 0

    def spawn(self):
        self.rect.x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
        self.rect.y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE

    def update(self, snake_head):
        self.move_counter += 1

        if self.move_counter >= 5 or random.random() < 0.1:
            self.direction = self.choose_direction(snake_head)
            self.move_counter = 0

        dx, dy = self.direction.value
        self.rect.x += dx * GRID_SIZE
        self.rect.y += dy * GRID_SIZE

        if self.rect.x >= SCREEN_WIDTH:
            self.rect.x = 0
        elif self.rect.x < 0:
            self.rect.x = SCREEN_WIDTH - GRID_SIZE
        if self.rect.y >= SCREEN_HEIGHT:
            self.rect.y = 0
        elif self.rect.y < 0:
            self.rect.y = SCREEN_HEIGHT - GRID_SIZE

    def choose_direction(self, snake_head):
        directions = list(Direction)
        distances = []
        for direction in directions:
            new_x = self.rect.x + direction.value[0] * GRID_SIZE
            new_y = self.rect.y + direction.value[1] * GRID_SIZE
            dist = abs(new_x - snake_head.rect.x) + abs(new_y - snake_head.rect.y)
            distances.append(dist)

        min_dist = min(distances)
        best_directions = [directions[i] for i, d in enumerate(distances) if d == min_dist]
        return random.choice(best_directions)

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.all_sprites = pygame.sprite.Group()
        self.snake_sprites = pygame.sprite.Group()

        start_x, start_y = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.head = SnakeHead(start_x, start_y)
        self.all_sprites.add(self.head)
        self.snake_sprites.add(self.head)

        self.body_segments = []
        for i in range(1, 3):
            segment = SnakeBody(start_x - i, start_y)
            self.body_segments.append(segment)
            self.all_sprites.add(segment)
            self.snake_sprites.add(segment)

        self.tail = SnakeTail(start_x - 3, start_y)
        self.all_sprites.add(self.tail)
        self.snake_sprites.add(self.tail)

        self.grow = False
        self.new_segment_pos = None

    def update(self):
        # Save previous positions
        prev_head_pos = (self.head.rect.x, self.head.rect.y)
        prev_positions = [prev_head_pos]
        for segment in self.body_segments:
            prev_positions.append((segment.rect.x, segment.rect.y))
        prev_tail_pos = (self.tail.rect.x, self.tail.rect.y)

        # Update head
        self.head.update()

        # Check for collisions with body (excluding the head's previous position)
        collision_check_group = pygame.sprite.Group(self.body_segments[1:] + [self.tail])
        if pygame.sprite.spritecollide(self.head, collision_check_group, False):
            if len(self.body_segments) > 2:
                return True

        # Update body segments
        for i, segment in enumerate(self.body_segments):
            segment.rect.x, segment.rect.y = prev_positions[i]

        # Handle growth - add new segment between last body segment and tail
        if self.grow:
            # The new segment goes where the tail was
            new_segment = SnakeBody(prev_tail_pos[0], prev_tail_pos[1])
            self.body_segments.append(new_segment)
            self.all_sprites.add(new_segment)
            self.snake_sprites.add(new_segment)

            # The tail stays where it was (becomes the new end)
            self.tail.rect.x, self.tail.rect.y = prev_tail_pos
            self.grow = False
        else:
            # Move tail to where the last body segment was
            self.tail.rect.x, self.tail.rect.y = prev_positions[-1]

        return False

    def change_direction(self, direction):
        self.head.change_direction(direction)

    def check_collision_with_food(self, food):
        if pygame.sprite.collide_rect(self.head, food):
            self.grow = True
            return True
        return False

def create_walls():
    walls = []

    # Border walls
    for x in range(GRID_WIDTH):
        walls.append(Wall(x, 0))
        walls.append(Wall(x, GRID_HEIGHT - 1))
    for y in range(1, GRID_HEIGHT - 1):
        walls.append(Wall(0, y))
        walls.append(Wall(GRID_WIDTH - 1, y))

    # Random inner walls
    for _ in range(5):
        x = random.randint(5, GRID_WIDTH - 6)
        y = random.randint(5, GRID_HEIGHT - 6)
        length = random.randint(3, 7)

        if random.random() < 0.5:
            for i in range(length):
                if x + i < GRID_WIDTH - 1:
                    walls.append(Wall(x + i, y))
        else:
            for i in range(length):
                if y + i < GRID_HEIGHT - 1:
                    walls.append(Wall(x, y + i))

    return walls

def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (SCREEN_WIDTH, y), 1)

def show_start_screen():
    font = pygame.font.SysFont('Arial', 36)
    screen.fill(BLACK)
    text = font.render("Press any arrow key to start", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def show_game_over():
    font = pygame.font.SysFont('Arial', 36)
    screen.fill(BLACK)
    text = font.render("Game Over! Press R to restart", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    snake = Snake()
    food = Food()
    enemy = Enemy()
    walls = create_walls()

    all_sprites = pygame.sprite.Group()
    all_sprites.add(snake.all_sprites)
    all_sprites.add(food)
    all_sprites.add(enemy)
    for wall in walls:
        all_sprites.add(wall)

    wall_sprites = pygame.sprite.Group(walls)

    running = True
    game_over = False
    game_started = False

    # Show start screen
    show_start_screen()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        snake.reset()
                        food.spawn()
                        enemy.spawn()
                        walls = create_walls()
                        all_sprites = pygame.sprite.Group()
                        all_sprites.add(snake.all_sprites)
                        all_sprites.add(food)
                        all_sprites.add(enemy)
                        for wall in walls:
                            all_sprites.add(wall)
                        wall_sprites = pygame.sprite.Group(walls)
                        game_over = False
                        game_started = True
                elif not game_started:
                    if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                        game_started = True
                        if event.key == pygame.K_UP:
                            snake.change_direction(Direction.UP)
                        elif event.key == pygame.K_DOWN:
                            snake.change_direction(Direction.DOWN)
                        elif event.key == pygame.K_LEFT:
                            snake.change_direction(Direction.LEFT)
                        elif event.key == pygame.K_RIGHT:
                            snake.change_direction(Direction.RIGHT)
                else:
                    if event.key == pygame.K_UP:
                        snake.change_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(Direction.RIGHT)

        # Check for restart key press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r] and game_over:
            snake.reset()
            food.spawn()
            enemy.spawn()
            walls = create_walls()
            all_sprites = pygame.sprite.Group()
            all_sprites.add(snake.all_sprites)
            all_sprites.add(food)
            all_sprites.add(enemy)
            for wall in walls:
                all_sprites.add(wall)
            wall_sprites = pygame.sprite.Group(walls)
            game_over = False
            game_started = True

        if game_started and not game_over:
            # Update
            game_over = snake.update()

            enemy.update(snake.head)

            if pygame.sprite.spritecollide(snake.head, wall_sprites, False):
                game_over = True

            if pygame.sprite.collide_rect(snake.head, enemy):
                game_over = True

            if snake.check_collision_with_food(food):
                food.spawn()
                while (pygame.sprite.spritecollide(food, snake.snake_sprites, False) or
                       pygame.sprite.collide_rect(food, enemy) or
                       pygame.sprite.spritecollide(food, wall_sprites, False)):
                    food.spawn()

            screen.fill(BLACK)
            draw_grid()
            all_sprites.draw(screen)
            pygame.display.flip()
        elif game_over:
            show_game_over()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()