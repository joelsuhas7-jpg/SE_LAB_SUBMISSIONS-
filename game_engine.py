"""
GameEngine: owns the player, coins, obstacles, lives and timer.

Features:
- Bronze = 1 point
- Silver = 3 points
- Gold = 5 points
- Player has 3 lives
- Obstacles remove one life per collision
- 30-second countdown timer
- Game over and restart
"""

import random
import pygame

from game.player import Player
from game.coin import Coin
from game.collection import check_collection
from game.renderer import WIDTH, HEIGHT

NUM_COINS = 6
GAME_DURATION = 30

BRONZE = {
    "value": 1,
    "color": (184, 115, 51)
}

SILVER = {
    "value": 3,
    "color": (192, 192, 192)
}

GOLD = {
    "value": 5,
    "color": (255, 215, 0)
}


class GameEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        # Player
        self.player = Player(x=WIDTH / 2, y=HEIGHT / 2)

        # Coins
        self.coins = [
            self._random_coin(BRONZE),
            self._random_coin(SILVER),
            self._random_coin(GOLD),
            self._random_coin(BRONZE),
            self._random_coin(SILVER),
            self._random_coin(GOLD)
        ]

        # Score
        self.score = 0

        # Lives
        self.lives = 3

        # Obstacles
        self.obstacles = [
            pygame.Rect(100, 100, 100, 30),
            pygame.Rect(500, 100, 100, 30),
            pygame.Rect(100, 350, 100, 30),
            pygame.Rect(500, 350, 100, 30)
        ]

        # Prevent repeated life loss while touching
        # the same obstacle.
        self.colliding_obstacles = set()

        # Game state
        self.game_over = False

        # Timer
        self.start_time = pygame.time.get_ticks()
        self.time_remaining = GAME_DURATION

    def _random_coin(self, coin_type):
        x = random.randint(30, WIDTH - 30)
        y = random.randint(30, HEIGHT - 30)

        return Coin(
            x=x,
            y=y,
            radius=12,
            value=coin_type["value"],
            color=coin_type["color"]
        )

    def handle_input(self, keys_pressed):
        # Do not allow movement after game over
        if self.game_over:
            return

        dx = dy = 0

        if keys_pressed[pygame.K_UP]:
            dy -= self.player.speed

        if keys_pressed[pygame.K_DOWN]:
            dy += self.player.speed

        if keys_pressed[pygame.K_LEFT]:
            dx -= self.player.speed

        if keys_pressed[pygame.K_RIGHT]:
            dx += self.player.speed

        self.player.move(dx, dy, WIDTH, HEIGHT)

    def update(self):
        if self.game_over:
            return

        # -------------------------
        # Timer
        # -------------------------
        elapsed_seconds = (
            pygame.time.get_ticks() - self.start_time
        ) // 1000

        self.time_remaining = max(
            0,
            GAME_DURATION - elapsed_seconds
        )

        # Time is over
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game_over = True
            return

        # -------------------------
        # Coin collection
        # -------------------------
        collected = check_collection(
            self.player,
            self.coins
        )

        for coin in collected:
            self.score += coin.value
            self.coins.remove(coin)

        # -------------------------
        # Obstacle collision
        # -------------------------
        player_rect = self.player.get_rect()

        current_collisions = set()

        for index, obstacle in enumerate(self.obstacles):
            if player_rect.colliderect(obstacle):
                current_collisions.add(index)

                # Lose only one life when entering
                # an obstacle.
                if index not in self.colliding_obstacles:
                    self.lives -= 1

        self.colliding_obstacles = current_collisions

        # -------------------------
        # Lives check
        # -------------------------
        if self.lives <= 0:
            self.lives = 0
            self.game_over = True

    def draw(self, surface, font):
        from game import renderer

        # Draw background, coins and player
        renderer.draw_scene(
            surface,
            self.player,
            self.coins
        )

        # Draw obstacles
        for obstacle in self.obstacles:
            pygame.draw.rect(
                surface,
                (200, 70, 70),
                obstacle,
                border_radius=5
            )

        # Score
        renderer.draw_text(
            surface,
            font,
            f"Score: {self.score}",
            (10, 10)
        )

        # Lives
        renderer.draw_text(
            surface,
            font,
            f"Lives: {self.lives}",
            (10, 40)
        )

        # Timer
        renderer.draw_text(
            surface,
            font,
            f"Time: {self.time_remaining}",
            (10, 70)
        )

        # Game Over
        if self.game_over:
            renderer.draw_banner(
                surface,
                font,
                f"GAME OVER - Final Score: {self.score} - Press R"
            )