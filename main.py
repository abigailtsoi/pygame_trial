#!/usr/bin/env python3
import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
ZOOM = 2
RENDER_SIZE = TILE_SIZE * ZOOM

# --- Colors ---
REDDISH_BROWN = (139, 69, 19)

from game_map import generate_game_map, SAND

# --- Game Map ---
# 0 = Sand, 1 = Rocks, 2 = Crater
MAP_WIDTH = 100
MAP_HEIGHT = 100
GAME_MAP = generate_game_map(MAP_WIDTH, MAP_HEIGHT)

class Player(pygame.sprite.Sprite):
    def __init__(self, tile_x, tile_y):
        super().__init__()
        self.tile_x = tile_x
        self.tile_y = tile_y
        try:
            sheet = pygame.image.load('assets/robot-sprite-sheet.png').convert_alpha()
            self.animations = {'down': [], 'right': [], 'up': [], 'left': []}
            frame_w, frame_h = 150, 150
            for row, direction in enumerate(['down', 'right', 'up', 'left']):
                for col in range(8):
                    frame = sheet.subsurface(pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h))
                    frame = pygame.transform.scale(frame, (RENDER_SIZE, RENDER_SIZE))
                    self.animations[direction].append(frame)
            self.direction = 'down'
            self.frame_index = 0
            self.image = self.animations[self.direction][self.frame_index]
            self.animation_timer = 0
            self.animation_speed = 3  # Animation updates every 3 ticks (faster)
            self.move_timer = 0
            self.move_speed = 12      # Movement duration in ticks (slower)
            self.moving = False
            self.start_pixel = (self.tile_x * RENDER_SIZE + RENDER_SIZE // 2, self.tile_y * RENDER_SIZE + RENDER_SIZE // 2)
            self.target_tile = (self.tile_x, self.tile_y)
        except pygame.error:
            self.image = pygame.Surface((TILE_SIZE - 8, TILE_SIZE - 8))
            self.image.fill((255, 255, 255))
            self.animations = {'down': [self.image], 'right': [self.image], 'up': [self.image], 'left': [self.image]}
            self.direction = 'down'
            self.frame_index = 0
            self.animation_timer = 0
            self.animation_speed = 6
        self.rect = self.image.get_rect(center=(self.tile_x * RENDER_SIZE + RENDER_SIZE // 2, self.tile_y * RENDER_SIZE + RENDER_SIZE // 2))

    def update(self, game_map):
        keys = pygame.key.get_pressed()
        if not self.moving:
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx, dy = -1, 0
                self.direction = 'left'
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx, dy = 1, 0
                self.direction = 'right'
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                dx, dy = 0, -1
                self.direction = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dx, dy = 0, 1
                self.direction = 'down'
            if dx != 0 or dy != 0:
                new_x = self.tile_x + dx
                new_y = self.tile_y + dy
                if 0 <= new_y < len(game_map) and 0 <= new_x < len(game_map[0]):
                    if game_map[new_y][new_x] != 1:
                        self.moving = True
                        self.move_timer = 0
                        self.start_pixel = (self.tile_x * RENDER_SIZE + RENDER_SIZE // 2, self.tile_y * RENDER_SIZE + RENDER_SIZE // 2)
                        self.target_tile = (new_x, new_y)
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.frame_index = (self.frame_index + 1) % 8
                self.animation_timer = 0
            self.move_timer += 1
            progress = self.move_timer / self.move_speed
            if progress >= 1.0:
                self.tile_x, self.tile_y = self.target_tile
                self.moving = False
                self.frame_index = 0
                self.animation_timer = 0
                self.move_timer = 0
                self.rect.center = (self.tile_x * RENDER_SIZE + RENDER_SIZE // 2, self.tile_y * RENDER_SIZE + RENDER_SIZE // 2)
            else:
                sx, sy = self.start_pixel
                tx, ty = (self.target_tile[0] * RENDER_SIZE + RENDER_SIZE // 2, self.target_tile[1] * RENDER_SIZE + RENDER_SIZE // 2)
                interp_x = int(sx + (tx - sx) * progress)
                interp_y = int(sy + (ty - sy) * progress)
                self.rect.center = (interp_x, interp_y)
        else:
            self.image = self.animations[self.direction][self.frame_index]
            self.rect.center = (self.tile_x * RENDER_SIZE + RENDER_SIZE // 2, self.tile_y * RENDER_SIZE + RENDER_SIZE // 2)
        self.image = self.animations[self.direction][self.frame_index]

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
    import random
    try:
        sand_tile_images = []
        for sand_img in ['sand-bushes.png', 'sand-line.png', 'sand-rocks.png']:
            img = pygame.image.load(f'assets/{sand_img}').convert()
            img = pygame.transform.scale(img, (RENDER_SIZE, RENDER_SIZE))
            sand_tile_images.append(img)
        rock_tile = pygame.image.load('assets/rocks.png').convert()
        rock_tile = pygame.transform.scale(rock_tile, (RENDER_SIZE, RENDER_SIZE))
        crater_tile = pygame.image.load('assets/crater.png').convert()
        crater_tile = pygame.transform.scale(crater_tile, (RENDER_SIZE, RENDER_SIZE))
    except pygame.error:
        sand_tile_images = []
        for _ in range(3):
            surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surf.fill((194, 178, 128))
            sand_tile_images.append(surf)
        rock_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        rock_tile.fill((112, 128, 144))
        crater_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        crater_tile.fill((160, 82, 45))
    # Precompute tile images for each map location so sand tiles don't change every frame
    map_tile_images = []
    for row in GAME_MAP:
        map_row = []
        for tile in row:
            if tile == 0:
                img = random.choice(sand_tile_images)
            elif tile == 1:
                img = rock_tile
            elif tile == 2:
                img = crater_tile
            else:
                img = pygame.Surface((RENDER_SIZE, RENDER_SIZE))
            map_row.append(img)
        map_tile_images.append(map_row)

    # Find a sand tile to spawn the player
    spawn_x, spawn_y = None, None
    for y, row in enumerate(GAME_MAP):
        for x, tile in enumerate(row):
            if tile == SAND:
                spawn_x, spawn_y = x, y
                break
        if spawn_x is not None:
            break
    # Set up sprites and camera
    all_sprites = pygame.sprite.Group()
    player = Player(spawn_x, spawn_y)
    all_sprites.add(player)
    map_width = len(GAME_MAP[0]) * RENDER_SIZE
    map_height = len(GAME_MAP) * RENDER_SIZE
    camera = Camera(map_width, map_height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        player.update(GAME_MAP)
        camera.update(player)

        # Draw
        screen.fill(REDDISH_BROWN)

        # Draw the map
        for row_index, row in enumerate(GAME_MAP):
            for col_index, tile in enumerate(row):
                x = col_index * RENDER_SIZE
                y = row_index * RENDER_SIZE
                tile_rect = pygame.Rect(x, y, RENDER_SIZE, RENDER_SIZE)
                screen.blit(map_tile_images[row_index][col_index], tile_rect.move(camera.camera.topleft))

        # Draw the player
        screen.blit(player.image, camera.apply(player))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()