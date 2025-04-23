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
DARK_PURPLE = (80, 0, 80)
LIGHT_PURPLE = (200, 0, 200)

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
    def __init__(self, x, y, color=GREEN):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(color)
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
    def __init__(self, x, y, color=BLUE):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x * GRID_SIZE
        self.rect.y = y * GRID_SIZE

class SnakeTail(pygame.sprite.Sprite):
    def __init__(self, x, y, color=GREEN):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(color)
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

class EnemySnake:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        start_x, start_y = GRID_WIDTH // 4, GRID_HEIGHT // 4
        self.head = SnakeHead(start_x, start_y, PURPLE)
        self.all_sprites.add(self.head)
        self.enemy_sprites.add(self.head)

        self.body_segments = []
        for i in range(1, 3):
            segment = SnakeBody(start_x - i, start_y, DARK_PURPLE)
            self.body_segments.append(segment)
            self.all_sprites.add(segment)
            self.enemy_sprites.add(segment)

        self.tail = SnakeTail(start_x - 3, start_y, LIGHT_PURPLE)
        self.all_sprites.add(self.tail)
        self.enemy_sprites.add(self.tail)

        self.grow = False
        self.move_counter = 0
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT

    def update(self, player_head):
        # Save previous positions
        prev_head_pos = (self.head.rect.x, self.head.rect.y)
        prev_positions = [prev_head_pos]
        for segment in self.body_segments:
            prev_positions.append((segment.rect.x, segment.rect.y))
        prev_tail_pos = (self.tail.rect.x, self.tail.rect.y)

        # Update direction based on player position
        self.move_counter += 1
        if self.move_counter >= 3 or random.random() < 0.2:
            self.choose_direction(player_head)
            self.move_counter = 0

        # Update head direction
        self.head.direction = self.direction
        self.head.next_direction = self.next_direction
        self.head.update()
        self.direction = self.head.direction

        # Update body segments
        for i, segment in enumerate(self.body_segments):
            segment.rect.x, segment.rect.y = prev_positions[i]

        # Handle growth
        if self.grow:
            new_segment = SnakeBody(prev_tail_pos[0], prev_tail_pos[1], DARK_PURPLE)
            self.body_segments.append(new_segment)
            self.all_sprites.add(new_segment)
            self.enemy_sprites.add(new_segment)
            self.tail.rect.x, self.tail.rect.y = prev_tail_pos
            self.grow = False
        else:
            self.tail.rect.x, self.tail.rect.y = prev_positions[-1]

    def choose_direction(self, player_head):
        # Get possible directions that don't cause immediate collision
        possible_directions = []
        for direction in Direction:
            # Check if this direction would cause a collision with own body
            new_x = self.head.rect.x + direction.value[0] * GRID_SIZE
            new_y = self.head.rect.y + direction.value[1] * GRID_SIZE

            # Wrap around screen for collision check
            if new_x >= SCREEN_WIDTH:
                new_x = 0
            elif new_x < 0:
                new_x = SCREEN_WIDTH - GRID_SIZE
            if new_y >= SCREEN_HEIGHT:
                new_y = 0
            elif new_y < 0:
                new_y = SCREEN_HEIGHT - GRID_SIZE

            # Check if new position collides with own body
            collision = False
            for segment in self.body_segments + [self.tail]:
                if new_x == segment.rect.x and new_y == segment.rect.y:
                    collision = True
                    break

            if not collision:
                possible_directions.append(direction)

        # If no safe directions, just continue straight (might collide)
        if not possible_directions:
            self.next_direction = self.direction
            return

        # Choose direction that gets us closer to player
        best_direction = None
        min_distance = float('inf')

        for direction in possible_directions:
            new_x = self.head.rect.x + direction.value[0] * GRID_SIZE
            new_y = self.head.rect.y + direction.value[1] * GRID_SIZE

            # Calculate Manhattan distance to player
            distance = abs(new_x - player_head.rect.x) + abs(new_y - player_head.rect.y)

            if distance < min_distance:
                min_distance = distance
                best_direction = direction

        # Sometimes make a random move to make it less predictable
        if random.random() < 0.2 and len(possible_directions) > 1:
            best_direction = random.choice(possible_directions)

        # Prevent 180-degree turns
        if (best_direction == Direction.UP and self.direction != Direction.DOWN or
                best_direction == Direction.DOWN and self.direction != Direction.UP or
                best_direction == Direction.LEFT and self.direction != Direction.RIGHT or
                best_direction == Direction.RIGHT and self.direction != Direction.LEFT):
            self.next_direction = best_direction

    def check_collision_with_food(self, food):
        if pygame.sprite.collide_rect(self.head, food):
            self.grow = True
            return True
        return False

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
            new_segment = SnakeBody(prev_tail_pos[0], prev_tail_pos[1])
            self.body_segments.append(new_segment)
            self.all_sprites.add(new_segment)
            self.snake_sprites.add(new_segment)

            self.tail.rect.x, self.tail.rect.y = prev_tail_pos
            self.grow = False
        else:
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
    enemy = EnemySnake()
    walls = create_walls()

    all_sprites = pygame.sprite.Group()
    all_sprites.add(snake.all_sprites)
    all_sprites.add(food)
    all_sprites.add(enemy.all_sprites)
    for wall in walls:
        all_sprites.add(wall)

    wall_sprites = pygame.sprite.Group(walls)

    running = True
    game_over = False
    game_started = False

    show_start_screen()

    while running:
        # Check for restart key press
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r] and game_over:
            snake.reset()
            food.spawn()
            enemy = EnemySnake()
            walls = create_walls()
            all_sprites = pygame.sprite.Group()
            all_sprites.add(snake.all_sprites)
            all_sprites.add(food)
            all_sprites.add(enemy.all_sprites)
            for wall in walls:
                all_sprites.add(wall)
            wall_sprites = pygame.sprite.Group(walls)
            game_over = False
            game_started = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not game_started:
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

        if game_started and not game_over:
            # Update
            game_over = snake.update()

            enemy.update(snake.head)

            if pygame.sprite.spritecollide(snake.head, wall_sprites, False):
                game_over = True

            if pygame.sprite.spritecollide(snake.head, enemy.enemy_sprites, False):
                game_over = True

            if snake.check_collision_with_food(food):
                food.spawn()
                while (pygame.sprite.spritecollide(food, snake.snake_sprites, False) or
                       pygame.sprite.spritecollide(food, enemy.enemy_sprites, False) or
                       pygame.sprite.spritecollide(food, wall_sprites, False)):
                    food.spawn()

            if enemy.check_collision_with_food(food):
                food.spawn()
                while (pygame.sprite.spritecollide(food, snake.snake_sprites, False) or
                       pygame.sprite.spritecollide(food, enemy.enemy_sprites, False) or
                       pygame.sprite.spritecollide(food, wall_sprites, False)):
                    food.spawn()

            screen.fill(BLACK)
            all_sprites.draw(screen)

            all_sprites.remove(snake.all_sprites)
            all_sprites.add(snake.all_sprites)
            all_sprites.remove(enemy.all_sprites)
            all_sprites.add(enemy.all_sprites)

            pygame.display.flip()
        elif game_over:
            show_game_over()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()