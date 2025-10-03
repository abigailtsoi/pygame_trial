#!/usr/bin/env python3
import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
PLAYER_SPEED = 5

# --- Colors ---
REDDISH_BROWN = (139, 69, 19)

# --- Game Map ---
# 0 = Sand, 1 = Rocks, 2 = Crater
GAME_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 1],
    [1, 0, 2, 2, 2, 2, 0, 1, 1, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 1],
    [1, 0, 0, 2, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
                self.image = pygame.image.load('assets/astronaut.png').convert_alpha()
                self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except pygame.error:
            self.image = pygame.Surface((TILE_SIZE - 8, TILE_SIZE - 8))
            self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += PLAYER_SPEED

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        self.camera = pygame.Rect(x, y, self.width, self.height)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mars Explorer")
    clock = pygame.time.Clock()

    # Load assets or create placeholders
    try:
           sand_tile = pygame.image.load('assets/sand.png').convert()
           sand_tile = pygame.transform.scale(sand_tile, (TILE_SIZE, TILE_SIZE))
           rock_tile = pygame.image.load('assets/rocks.png').convert()
           rock_tile = pygame.transform.scale(rock_tile, (TILE_SIZE, TILE_SIZE))
           crater_tile = pygame.image.load('assets/crater.png').convert()
           crater_tile = pygame.transform.scale(crater_tile, (TILE_SIZE, TILE_SIZE))
    except pygame.error:
        sand_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        sand_tile.fill((194, 178, 128))
        rock_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        rock_tile.fill((112, 128, 144))
        crater_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        crater_tile.fill((160, 82, 45))
        
    tile_images = {0: sand_tile, 1: rock_tile, 2: crater_tile}

    # Set up sprites and camera
    all_sprites = pygame.sprite.Group()
    player = Player(400, 300)
    all_sprites.add(player)
    
    map_width = len(GAME_MAP[0]) * TILE_SIZE
    map_height = len(GAME_MAP) * TILE_SIZE
    camera = Camera(map_width, map_height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        all_sprites.update()
        camera.update(player)

        # Draw
        screen.fill(REDDISH_BROWN)

        # Draw the map
        for row_index, row in enumerate(GAME_MAP):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                tile_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                screen.blit(tile_images[tile], tile_rect.move(camera.camera.topleft))


        # Draw the player
        screen.blit(player.image, camera.apply(player))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()