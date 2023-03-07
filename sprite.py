from support import load_image, write_text
from settings import *
import pygame

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], image: pygame.Surface, groups: pygame.sprite.Group=None):
        if groups == None:
            groups = []
        
        super().__init__(*groups)
        self.image = image

        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

class AirTile(Generic):
    def __init__(self, pos: tuple[int, int], groups: list[pygame.sprite.Group]):
        super().__init__(pos, SQUARE_IMAGES['air'], groups)

        self.image_type = 'air'

    def set_image(self, _image_type: str=None):
        self.image = pygame.transform.scale(SQUARE_IMAGES[self.image_type], self.rect.size)
        
        old_rect_pos = self.rect.topleft
        
        self.rect = self.image.get_rect()
        self.rect.x = old_rect_pos[0]
        self.rect.y = old_rect_pos[1]

class Tile(Generic):
    def __init__(self, pos: tuple[int, int], groups: list[pygame.sprite.Group], is_bomb: bool=False, is_flagged: bool=False, is_pressed: bool=False):
        super().__init__(pos, SQUARE_IMAGES['blank'], groups)

        self.image_type = 'blank'

        self.is_bomb = is_bomb
        self.is_flagged = is_flagged
        self.is_pressed = is_pressed

        self.bombs_in_range = 0

        self.bombs_to_text = None
        self.bombs_to_text_size = None
        self.bombs_to_text_color = TILE_FONT_COLOR

        self.toggle_flag(self.is_flagged) # updates the sprite

    def set_image(self, image_type: str=None):
        if image_type == None:
            image_type = self.image_type
        
        self.image_type = image_type
        self.image = pygame.transform.scale(SQUARE_IMAGES[self.image_type], self.rect.size)

        old_rect_pos = self.rect.topleft

        self.rect = self.image.get_rect()
        self.rect.x = old_rect_pos[0]
        self.rect.y = old_rect_pos[1]

        if self.is_pressed and self.bombs_in_range != 0:
            self.bombs_to_text, self.bombs_to_text_size = write_text(self.bombs_in_range, self.rect.width, BOMB_FONT, color=TILE_FONT_COLOR, get_size=True)

    def toggle_flag(self, toggle: bool=None):
        if self.is_pressed:
            return

        if toggle == None:
            toggle = not self.is_flagged

        self.is_flagged = toggle
        
        if self.is_flagged:
            self.set_image('flag')
        else:
            self.set_image('blank')

    def toggle_press(self, toggle: bool=None):
        if toggle == None:
            toggle = not self.is_pressed
        
        self.is_pressed = toggle

        if self.is_pressed:
            self.set_image('pressed')
        else:
            self.set_image('blank')

def create_bomb(pos, group):
    return Tile(pos, group, True, False, False)

def create_flag(pos, group, is_bomb: bool):
    return Tile(pos, group, is_bomb, True, False)

def create_pressed(pos, group):
    return Tile(pos, group, False, False, True)

class Cursor(Generic):
    def __init__(self, groups: list[pygame.sprite.Group]=None):
        super().__init__((0,0), load_image(CURSOR_PATH), groups)
        self.rect.width = 1
        self.rect.height = 1
    
    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
    
    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)