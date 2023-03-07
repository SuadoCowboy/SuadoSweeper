import pygame
from sprite import *
from support import *
from settings import *
import time
import numpy as np
import random

# b - bomb
# p - pressed
# f - flag
# fb - flagged bomb
# u - unknown/undiscovered/unpressed but it's not a bomb

class Level:
    def __init__(self):
        self.map = []

        self.width = WIDTH
        self.height = HEIGHT - (TILE_SIZE*2)

        self.actual_surface = pygame.Surface((self.width, self.height))

        self.bombs_amount = 1

        self.background_color = LEVEL_BACKGROUND_COLOR

        self.tiles = pygame.sprite.Group()

        self.x = 0
        self.y = 64

        self.tile_size = TILE_SIZE
        
        self.y_amount = 10
        self.x_amount = 10

        self.air_tiles_indexes = [] # [ (x, y), (x2, y2), ... ]

        self.rect_scale = (self.width/self.x_amount, self.height/self.y_amount)

        self.camera_vel = CAMERA_VELOCITY

        self.default_lives = 1
        self.reset_variables()
    
    def delete_tiles(self):
        for row in self.map:
            for tile in row:
                tile.kill()
        self.map = []

    def reset_variables(self):
        self.safe_tiles_amount = 0
        self.tiles_pressed = 0

        self.reset_offset_position()

        self.bombs_found = 0

        self.lives = self.default_lives
        
        self.flagged_tiles_amount = 0

        self.time = 0.0
        self.time_start = -1

    def load(self, path: str):
        content = load(path)

        self.x_amount = content['x_amount']
        self.y_amount = content['y_amount']

        self.air_tiles_indexes = content['air_tiles_indexes']

        if not content['random']:
            self.delete_tiles()
            self.reset_variables()

            for y, row in enumerate(content['map']):
                self.map.append([])
                for x, tile in enumerate(row):
                    pos = (x*TILE_SIZE, y*TILE_SIZE)

                    if tile == 'b': # Bomb
                        self.map[-1].append(create_bomb(pos, [self.tiles]))
                    
                    elif tile == 'p': # Pressed
                        self.map[-1].append(create_pressed(pos, [self.tiles]))
                    
                    elif tile == 'f': # Flag
                        self.map[-1].append(create_flag(pos, [self.tiles], False))
                    
                    elif tile == 'fb': # Flagged Bomb
                        self.map[-1].append(create_flag(pos, [self.tiles], True))
                    
                    elif tile == 'u': # Unknown
                        self.map[-1].append(Tile(pos, [self.tiles]))
                    
                    elif tile == 'a':
                        self.map[-1].append(AirTile(pos, [self.tiles]))

            self.set_bombs_in_range()

            self.flagged_tiles_amount = content['flagged_tiles_amount']
            self.bombs_found = content['bombs_found']
            self.safe_tiles_amount = content['safe_tiles_amount']
            self.tiles_pressed = content['tiles_pressed']

            self.start_time_counting()
            
            self.time_start -= content['time']
        else:
            self.set_tiles()

        self.bombs_amount = content['bombs_amount']
        self.default_lives = content['default_lives']
        self.lives = content['lives']

        self.reset_zoom()

        return content['random']
    
    def zoom(self, value: int):
        if self.zoom_value+value < TILE_SIZE or self.zoom_value+value > ZOOM_LIMIT:
            return
        
        self.zoom_value += value
        self.bomb_font = pygame.font.Font(BOMB_FONT, self.zoom_value)

        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                self.map[y][x].rect.width = self.zoom_value
                self.map[y][x].rect.height = self.zoom_value

                self.map[y][x].set_image()
                
                self.map[y][x].rect.x = self.zoom_value * x
                self.map[y][x].rect.y = self.zoom_value * y
                
        self.surface = self.reset_surface(self.map[-1][-1].rect)

    def reset_zoom(self):
        """
        WARNING: it will change offset_x and y to +TILE_SIZE
        """ 
        self.zoom_value = int(ZOOM_AMOUNT*ZOOM_LEVEL)
        self.bomb_font = pygame.font.Font(BOMB_FONT, self.zoom_value)
        self.zoom(TILE_SIZE)

    def randomize(self, collided_tile=None):
        if collided_tile != None:
            collided_tile_pos = self.get_tile_position(collided_tile)
            ignore_area = (np.array([i for i in range(collided_tile_pos[0]-2, collided_tile_pos[0]+3, 1)]), np.array([i for i in range(collided_tile_pos[1]-2, collided_tile_pos[1]+3, 1)]))

        bombs_amount = 0
        while bombs_amount != self.bombs_amount:
            y = random.randint(0, len(self.map)-1)
            x = random.randint(0,len(self.map[y])-1)

            if [x,y] in self.air_tiles_indexes or np.all([collided_tile != None, x in ignore_area[0], y in ignore_area[1]]) or self.map[y][x].is_bomb:
                continue

            self.map[y][x].is_bomb = True
            bombs_amount += 1

        self.set_bombs_in_range()

    def set_tiles(self):
        self.delete_tiles()
        self.reset_variables()

        for y in range(self.y_amount):
            self.map.append([])
            for x in range(self.x_amount):
                pos = (x*TILE_SIZE,y*TILE_SIZE)
                groups = [self.tiles]

                if [x,y] in self.air_tiles_indexes:
                    self.map[-1].append(AirTile(pos, groups))
                    continue
                
                self.map[-1].append(Tile(pos, groups, False, False, False))

        self.surface = self.reset_surface(self.map[-1][-1].rect)

    def reset_surface(self, rect):
        """
        rect: the last rect in the map
        """
        return pygame.Surface((rect.x+rect.width, rect.y+rect.height))

    def reset_tiles(self):
        """
        resets the already existing tiles
        """

        self.reset_variables()

        for row in self.map:
            for tile in row:
                if type(tile) == AirTile:
                    continue

                tile.is_bomb = False
                tile.is_pressed = False
                tile.toggle_flag(False)

    def start_time_counting(self):
        self.time_start = time.time()

    def move_offset_x(self, dt: float=1):
        self.offset_x += self.camera_vel * dt
    
    def move_offset_y(self, dt: float=1):
        self.offset_y += self.camera_vel * dt
    
    def reset_offset_position(self):
        self.offset_x, self.offset_y = (self.width/2-(self.x_amount*TILE_SIZE)/2,self.height/2-(self.y_amount*TILE_SIZE)/2)

    def draw(self, surface: pygame.Surface, background_surface: pygame.Surface, background_pos: tuple[int, int]):
        surface.blit(self.actual_surface, (self.x, self.y))
        self.actual_surface.fill(self.background_color)

        self.actual_surface.blit(background_surface, background_pos)

        self.actual_surface.blit(self.surface, (self.offset_x, self.offset_y))
        self.surface.fill(self.background_color)
        
        for tile in self.tiles:
            if type(tile) == AirTile:
                continue

            if tile.is_pressed:
                pygame.draw.rect(self.surface, TILE_PRESSED_COLOR, tile.rect)
                self.surface.blit(tile.bombs_to_text, (tile.rect.centerx-tile.bombs_to_text_size[0]/2, tile.rect.centery-tile.bombs_to_text_size[1]/2))
            else:
                pygame.draw.rect(self.surface, TILE_BLANK_COLOR, tile.rect)
                if tile.is_flagged:
                    self.surface.blit(tile.image, tile.rect)

    def update(self, *args, **kwargs):
        self.tiles.update(*args, **kwargs)

        if self.tiles_pressed != 0:
            self.time = time.time()-self.time_start

    def set_bombs_in_range(self):
        """
        Sets the bombs_in_range value for each tile in the map array.
        """

        self.bombs_found = 0

        self.tiles_pressed = 0
        self.safe_tiles_amount = 0

        for y in range(len(self.map)):
            for x, tile in enumerate(self.map[y]):
                if type(tile) == AirTile or tile.is_bomb:
                    continue

                self.safe_tiles_amount += 1

                surroundings = self.get_tile_surroundings(x, y)
                tile.bombs_in_range = 0
                for tile_surround in surroundings:
                    if tile_surround == None or type(tile_surround) == AirTile:
                        continue
                    
                    tile.bombs_in_range += 1 if tile_surround.is_bomb else 0
                
                if tile.bombs_in_range != 0:
                    tile.bombs_to_text, tile.bombs_to_text_size = write_text(tile.bombs_in_range, font_path=self.bomb_font, color=tile.bombs_to_text_color, get_size=True)
                else:
                    tile.bombs_to_text, tile.bombs_to_text_size = write_text('', get_size=True)

    def get_tile_position(self, tile: Tile):
        """
        Returns the tile position on map array as a tuple -> (x, y)
        """
        
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x] == tile:
                    return (x, y)
    
    def get_tile_surroundings(self, x: int, y:int):
        out = []
        for i in range(y-1, y+2, 1):
            for j in range(x-1, x+2, 1):
                if i == y and j == x:
                    continue
                
                try:
                    if i >= 0 and j >= 0:
                        out.append(self.map[i][j])
                except IndexError:
                    continue
        
        return out

    def press_tile(self, tile: Tile):
        if not tile.is_pressed:
            self.tiles_pressed += 1
        
        tile.toggle_press(True)
        
        self.find_tile_tree(tile)

    def unpress_tile(self, tile: Tile):
        tile.toggle_press(False)
        self.tiles_pressed -= 1

    def flag_tile(self, tile: Tile):
        tile.toggle_flag(True)
        if tile.is_bomb:
            self.bombs_found += 1
        
        self.flagged_tiles_amount += 1
    
    def unflag_tile(self, tile: Tile):
        tile.toggle_flag(False)
        if tile.is_bomb:
            self.bombs_found -= 1
        
        self.flagged_tiles_amount -= 1

    def find_tile_tree(self, tile: Tile):
        if tile.bombs_in_range != 0:
            return

        surroundings = np.array(self.get_tile_surroundings(*self.get_tile_position(tile)))
        
        for tile_surround in surroundings:
            if type(tile_surround) == AirTile or np.any([tile_surround == None, tile_surround.is_pressed, tile_surround.is_bomb, tile_surround.is_flagged]):
                continue

            self.press_tile(tile_surround)