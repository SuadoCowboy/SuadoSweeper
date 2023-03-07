from support import *
from settings import *
import os
import pygame
import random

class GenericUI(pygame.Surface):
    def __init__(self, x: float, y: float, width: float, height: float, *surface_args, transparent=False):
        super().__init__((width, height), *surface_args)

        self.rect = self.get_rect()
        
        self.transparent = transparent

        self.rect.x = x
        self.rect.y = y
        
        self.image = None
        self.image_pos = (0,0)

        self.text = ''
        self.text_surface = None
        self.text_pos = (0,0)
        self.text_size = (0,0)
        self.text_color = "#ffffff"

        self.font_size = FONT_SIZE
        self.font_path = DEFAULT_FONT

        self.background_color = (0,0,0)

        self.border_color = '#ffffff'
        self.border_width = 0
        self.border_radius = -1
    
    def set_image(self, image: pygame.Surface, pos: tuple[int, int]=None):
        self.image = image
        self.image_pos = pos if pos else self.image_pos
    
    def set_text(self, text: str, text_surface: pygame.Surface, size: tuple[int, int], pos: tuple[int, int]=None, font_size: int=None, color: str | tuple[int,int,int]=None):
        self.text = text
        
        self.text_surface = text_surface
        
        self.text_size = size

        self.font_size = font_size if font_size else self.font_size
        
        self.text_pos = pos if pos else self.text_pos

        self.text_color = color if color else self.text_color

    def write_text(self, text: str, font_size: int=None, color: tuple[int, int, int] | str=None, font_path: str=None, *write_text_args, **write_text_kwargs):
        """
        WARNING: it overwrites the old text
        """
        if color: self.text_color = color
        if font_size: self.font_size = font_size
        if font_path: self.font_path = font_path

        surf, size = write_text(text, self.font_size, self.font_path, *write_text_args, color=self.text_color, get_size=True, **write_text_kwargs)
        self.set_text(text, surf, size)

class TextInputLine(GenericUI):
    def __init__(self, x: float, y: float, width: float, height: float, *surface_args, font_path: str=None):
        super().__init__(x, y, width, height, *surface_args)

        self.active = False

        self.keybinds = TEXTINPUT_KEYBINDS

        self.font_path = font_path if font_path else self.font_path
        
        # fit in the box
        text_size = write_text('_', self.font_size, self.font_path, get_size=True)[1]
        while self.text_pos[1]+text_size[1] >= self.rect.height:
            self.font_size -= 1
            text_size = write_text('_', self.font_size, self.font_path, get_size=True)[1]

        self.border_color = INPUT_BORDER_COLOR
        self.border_width = 1

        self.cursor_blink = Cooldown(0.2) # 500ms
        self.cursor_surface = pygame.Surface((1,text_size[1]*2))
        self.cursor_color = (255,255,255)
        self.display_cursor = True

        self.limit_text_to_border = True

        self.start_of_sliding_text_size = (0,0)

        self.offset_x = 0

        self.allowed_chars = ''

        self.blank_text_surface = write_text('', self.font_size, self.font_path, self.text_color)

    def update(self):
        if self.active and self.cursor_blink.check():
            self.display_cursor = not self.display_cursor

        self.update_offsetx()
    
    def mousebuttondown_event(self, event):
        if event.button == 1 and self.rect.colliderect((*event.pos,1,1)):
            self.active = True
            self.cursor_blink.reset_start()
            return
        
        self.active = False

    def remove_char(self):
        self.write_text(self.text[:-1])

    def keydown_event(self, event):
        if not self.active:
            return False
        
        if event.key in self.keybinds:
            if self.keybinds[event.key] == 'deactivate':
                self.active = False
            
            elif self.keybinds[event.key] == 'remove char':
                self.remove_char()
            
            elif self.keybinds[event.key] == 'send':
                self.active = False
                return True
        else:
            if self.allowed_chars and not event.unicode.lower() in self.allowed_chars:
                return False
            
            self.write_text(self.text+event.unicode)
        
        return False

    def write_text(self, text: str, font_size: int = None, color: tuple[int, int, int] | str = None, font_path: str = None, *write_text_args, **write_text_kwargs):
        self.cursor_blink.reset_start()
        self.display_cursor = False
        
        return super().write_text(text, font_size, color, font_path, *write_text_args, **write_text_kwargs)

    def update_offsetx(self):
        if self.text_pos[0]+self.text_size[0] > self.rect.width-3:
            if self.limit_text_to_border:
                self.remove_char()
            self.offset_x = self.text_size[0]-self.rect.width+3
        else:
            self.offset_x = 0

    def draw(self, surface: pygame.Surface):
        surface.blit(self, self.rect)
        self.fill(self.background_color)
        if self.border_width:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)
        
        if self.image:
            self.blit(self.image, self.image_pos)
        
        if self.text:
            self.blit(self.text_surface, (self.text_pos[0]-self.offset_x, self.text_pos[1]))
        else:
            self.blit(self.blank_text_surface, self.text_pos)
        
        if self.active and self.display_cursor:
            self.blit(self.cursor_surface, (self.text_pos[0]+self.text_size[0]-self.offset_x, self.text_pos[1]))
            self.cursor_surface.fill(self.cursor_color)

class Button(GenericUI):
    def __init__(self, x: float, y: float, width: float, height: float, toggle_mode: bool=False, *surface_args, transparent=False):
        super().__init__(x, y, width, height, *surface_args, transparent=transparent)
        self.toggle_mode = toggle_mode
        
        self.pressed = False
        self.toggled = False
        self.hovered = False

        self.pressed_before = False

        self.pressed_color = (170,170,170)
        self.toggled_color = (150,150,150)
        self.hovered_color = (190,190,190)
    
    def write_text(self, text: str, font_size: int = None, color: tuple[int, int, int] | str = None, *write_text_args, **write_text_kwargs):
        self.font_size = font_size if font_size else self.font_size
        
        text_size = write_text(text, self.font_size, self.font_path, get_size=True)[1]
        
        while self.text_pos[0]+text_size[0] > self.rect.width or self.text_pos[1]+text_size[1] > self.rect.height:
            self.font_size -= 1
            
            text_size = write_text(text, self.font_size, self.font_path, get_size=True)[1]
        
        return super().write_text(text, self.font_size, color, *write_text_args, **write_text_kwargs)

    def mousebuttondown_event(self, event):
        """
        WARNING: this is only used for toggle mode!!!
        """
        if not self.toggle_mode:
            return

        if event.button != 1:
            return
            
        if self.rect.colliderect((*event.pos,1,1)):
            self.toggled = not self.toggled
    
    def update(self, mouse_pos: tuple[int, int]):
        self.hovered = False
        if self.rect.colliderect((*mouse_pos, 1,1)):
            self.hovered = True

        if self.toggle_mode:
            return
        
        self.pressed = False
        if pygame.mouse.get_pressed()[0] and self.hovered:
            if self.pressed_before:
                self.pressed = False
            else:
                self.pressed = True
                self.pressed_before = True
        else:
            self.pressed_before = False
    
    def draw(self, surface: pygame.Surface):
        surface.blit(self.convert_alpha(), self.rect)
        
        if self.toggled:
            to_fill = self.toggled_color
        elif self.pressed:
            to_fill = self.pressed_color
        elif self.hovered:
            to_fill = self.hovered_color
        else:
            to_fill = self.background_color
        
        # i can't fix it, i don't remember how i made it to work
        #if self.transparent:
        #    self.set_colorkey(to_fill)
        #else:
        self.fill(to_fill)

        if self.text:
            self.blit(self.text_surface, self.text_pos)
        
        if self.image:
            self.blit(self.image, self.image_pos)

class Popup(GenericUI):
    def __init__(self, x: int, y: int, width: int, height: int, *surface_args, transparent: bool=True):
        super().__init__(x, y, width, height, *surface_args, pygame.SRCALPHA, 32, transparent=transparent)

        self.text_pos = (self.rect.width/2, 2) # x - center; y - top

    def draw(self, surface: pygame.Surface):
        
        if self.border_radius != -1:
            pygame.draw.rect(surface, self.background_color, self.rect, 0, self.border_radius)
        
        if self.border_width != 0:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width, self.border_radius)
        
        surface.blit(self, self.rect)
        if self.border_radius == -1:
            self.fill(self.background_color)

        if self.text:
            self.blit(self.text_surface, (self.text_pos[0]-self.text_size[0]/2, self.text_pos[1]))
        
        if self.image:
            self.blit(self.image, self.image_pos)
        
        self._draw(surface)
    
    def _draw(_surface: pygame.Surface):
        pass

    def can_close(self, function_to_check):
        if function_to_check:
            
            if function_to_check():
                return True
            
            return False
        
        return True

class ConfirmPopup(Popup):
    def __init__(self, x: int, y: int, width: int, height: int, *surface_args, transparent: bool=True):
        super().__init__(x, y, width, height, *surface_args, transparent=transparent)

        self.cancel_button = Button(10, self.rect.height/2, 100, 50)
        self.cancel_button.write_text('Cancel')

        self.confirm_button = Button(self.rect.width-110, self.rect.height/2, 100, 50)
        self.confirm_button.write_text('Confirm')

        self.on_confirm_function = None
        self.on_cancel_function = None
    
    def _draw(self, _surface: pygame.Surface):
        self.cancel_button.draw(self)
        self.confirm_button.draw(self)
    
    def update(self, game_class):
        self.cancel_button.rect.x += self.rect.x
        self.cancel_button.rect.y += self.rect.y

        self.cancel_button.update(game_class.cursor.rect.topleft)

        self.cancel_button.rect.x -= self.rect.x
        self.cancel_button.rect.y -= self.rect.y

        ######

        self.confirm_button.rect.x += self.rect.x
        self.confirm_button.rect.y += self.rect.y

        self.confirm_button.update(game_class.cursor.rect.topleft)

        self.confirm_button.rect.x -= self.rect.x
        self.confirm_button.rect.y -= self.rect.y

        if self.cancel_button.pressed and self.can_close(self.on_cancel_function) or (self.confirm_button.pressed and self.can_close(self.on_confirm_function)):
            game_class.popup = None

class TextInputLinePopup(Popup):
    def __init__(self, x: int, y: int, width: int, height: int, *surface_args, transparent: bool=True):
        super().__init__(x, y, width, height, *surface_args, transparent=transparent)

        self.cancel_button = Button(self.rect.width/2-41, self.rect.height/2+2, 82, 50)
        self.cancel_button.write_text('Cancel')

        self.input = TextInputLine(self.rect.width/2-100, self.rect.height/2-36, 200, self.font_size)

        self.on_send_function = None
        self.on_cancel_function = None
    
    def _draw(self, _surface: pygame.Surface):
        self.input.draw(self)
        self.cancel_button.draw(self)
    
    def update(self, game_class):
        # send
        if game_class.keyDownEvent and self.input.keydown_event(game_class.keyDownEvent):
            if self.can_close(self.on_send_function):
                game_class.popup = None
            else:
                self.input.active = True
        
        self.cancel_button.rect.x += self.rect.x
        self.cancel_button.rect.y += self.rect.y

        self.cancel_button.update(game_class.cursor.rect.topleft)

        self.cancel_button.rect.x -= self.rect.x
        self.cancel_button.rect.y -= self.rect.y

        if game_class.mouseButtonDownEvent:
            self.input.rect.x += self.rect.x
            self.input.rect.y += self.rect.y

            self.input.mousebuttondown_event(game_class.mouseButtonDownEvent)

            self.input.rect.x -= self.rect.x
            self.input.rect.y -= self.rect.y

        self.input.update()

        # cancel
        if self.cancel_button.pressed and self.can_close(self.on_cancel_function):
            game_class.popup = None

class SavedGameInterface(GenericUI):
    def __init__(self, path: str, x: int, y: int, width: int, height: int, delete_sgi_function, sort_sgis_function, my_index: int, *surface_args):
        super().__init__(x,y, width,height, *surface_args)

        self.delete_sgi_function = delete_sgi_function
        self.my_index = my_index
        
        self.sort_sgis_function = sort_sgis_function

        self.path = path

        self.filename = os.path.basename(self.path)

        self.delete_button = Button(self.rect.width-4, self.rect.height/2, self.rect.height/2, self.rect.height/2, False, pygame.SRCALPHA, 32, transparent=True)
        self.rename_button = Button(self.rect.width-4, self.rect.height/2, self.rect.height/2, self.rect.height/2, False, pygame.SRCALPHA, 32, transparent=True)

        self.delete_button.rect.x -= self.delete_button.rect.width
        self.rename_button.rect.x -= (self.rename_button.rect.width*2)+4

        self.delete_button.rect.y -= self.delete_button.rect.height/2
        self.rename_button.rect.y -= self.rename_button.rect.height/2

        self.delete_button.image = pygame.transform.scale(load_image(DELETE_IMAGE), self.delete_button.rect.size)
        self.rename_button.image = pygame.transform.scale(load_image(RENAME_IMAGE), self.rename_button.rect.size)

        self.rename_popup = None

        self.update_text()
    
    def update_text(self):
        self.write_text(self.filename[:self.filename.index('.')], self.font_size)

        old_text = self.text
        while self.text_pos[0]+self.text_size[0] >= self.rename_button.rect.x:
            self.write_text(old_text[:-2]+'...')
            old_text = self.text[:-3]

    def draw(self, surface: pygame.Surface):
        surface.blit(self, self.rect)
        self.fill(self.background_color)

        self.blit(self.text_surface, self.text_pos)

        self.delete_button.draw(self)
        self.rename_button.draw(self)
    
    def remove_file(self):
        os.remove(self.path)

        self.delete_sgi_function(self.my_index)

        return True

    def rename_file(self):
        if not self.rename_popup or not self.rename_popup.input.text or self.rename_popup.input.text == self.filename:
            return False

        new_path = self.path[:len(self.path)-len(self.filename)] + self.rename_popup.input.text

        try:
            os.rename(self.path, new_path)
        except OSError:
            return False
        
        self.path = new_path
        self.filename = self.rename_popup.input.text

        self.update_text()

        return True

    def update(self, mouse_pos: tuple[int, int], game_class):

        self.delete_button.rect.y += self.rect.y
        self.delete_button.update(mouse_pos)
        self.delete_button.rect.y -= self.rect.y
        
        self.rename_button.rect.y += self.rect.y
        self.rename_button.update(mouse_pos)
        self.rename_button.rect.y -= self.rect.y

        if self.delete_button.pressed:
            game_class.popup = game_class.delete_popup
            game_class.popup.on_confirm_function = self.remove_file
        
        elif self.rename_button.pressed:
            game_class.popup = game_class.rename_popup
            game_class.popup.on_send_function = self.rename_file
            
            game_class.popup.input.write_text(self.filename)

            game_class.popup.input.active = True
            
            self.rename_popup = game_class.popup

class DifficultyInterface(GenericUI):
    def __init__(self, path: str, filename: str, x: int, y: int, width: int, height: int, *surface_args):
        super().__init__(x,y, width,height, *surface_args)
        
        self.path = path

        self.hovered = False
        self.hovered_surface = pygame.Surface(self.rect.size)
        self.hovered_surface.set_alpha(128)
        self.hovered_color = CHANGEDIFFICULTY_MENU_HOVERED_COLOR

        self.filename = filename
        self.update_text()
    
    def update_text(self):
        self.write_text(self.filename, self.font_size)

        old_text = self.text
        while self.text_pos[0]+self.text_size[0] >= self.rect.width:
            self.write_text(old_text[:-2]+'...')
            old_text = self.text[:-3]
        
        self.text_pos = (self.rect.width/2-self.text_size[0]/2, self.text_pos[1])

    def draw(self, surface: pygame.Surface):
        surface.blit(self, self.rect)
        self.fill(self.background_color)
        
        self.blit(self.text_surface, self.text_pos)
        if self.hovered:
            self.blit(self.hovered_surface, (0,0))
            self.hovered_surface.fill(self.hovered_color)
    
    def update_hovered(self, rect: pygame.Rect):
        self.hovered = False
        if self.get_collided(rect):
            self.hovered = True

    def get_collided(self, rect: pygame.Rect):
        if self.rect.colliderect(rect):
            return True
        return False

class SettingsCategory(pygame.Surface):
    def __init__(self, width: int, height: int, name: str, *init_args, **init_kwargs):
        super().__init__((width, height), *init_args, **init_kwargs)

        self.rect = self.get_rect()
        self.rect.x = 0
        self.rect.y = 0

        self.offsety = 0

        self.background_color = (0,0,0)

        self.name = name
        # { cfg_name(str): [ cfg_name(surface), cfg_input(button or textinputline), y(int) ] }
        self.cfgs = {}

        self.font_size = FONT_SIZE
    
        self.cfg_input_space = 5

        self.button_background_color = (255,0,0)
        self.button_toggled_color = (0,255,0)
        self.button_hovered_color = (255,0,0)

    def get_last_cfg_value(self):
        return list(self.cfgs.values())[-1] if self.cfgs else None

    def set_cfg(self, cfg_name, cfg_repr: str):
        if not cfg_repr:
            cfg_repr = cfg_name

        last_cfg = self.get_last_cfg_value()

        if last_cfg:
            y = last_cfg[1].rect.y+last_cfg[1].rect.height
        else:
            y = 0

        return (*write_text(cfg_repr, self.font_size, get_size=True), y)

    def add_textinputline(self, cfg_name: str, cfg_repr: str=None):
        text_surf, text_size, y = self.set_cfg(cfg_name, cfg_repr)

        self.cfgs[cfg_name] = [text_surf, TextInputLine(text_size[0]+self.cfg_input_space, y, self.rect.width-(text_size[0]+self.cfg_input_space)-1, self.font_size), y]
        self.cfgs[cfg_name][1].background_color = SETTINGSMENU_TEXTINPUTLINE_BACKGROUND_COLOR
        self.cfgs[cfg_name][1].border_color = SETTINGSMENU_TEXTINPUTLINE_BORDER_COLOR

        return self.cfgs[cfg_name][1]

    def add_button(self, cfg_name: str, cfg_repr: str=None):
        text_surf, text_size, y = self.set_cfg(cfg_name, cfg_repr)

        self.cfgs[cfg_name] = [text_surf, Button(text_size[0]+self.cfg_input_space, y, self.rect.width-text_size[1]-self.cfg_input_space, self.font_size, True), y]
        self.cfgs[cfg_name][1].background_color = self.button_background_color
        self.cfgs[cfg_name][1].toggled_color = self.button_toggled_color
        self.cfgs[cfg_name][1].hovered_color = self.button_hovered_color

        return self.cfgs[cfg_name][1]

    def draw(self, surface: pygame.Surface):
        surface.blit(self, self.rect)
        self.fill(self.background_color)
        
        for cfg_name in self.cfgs:
            self.blit(self.cfgs[cfg_name][0], (0, self.cfgs[cfg_name][2]+self.offsety))
            
            self.cfgs[cfg_name][1].rect.y += self.offsety
            self.cfgs[cfg_name][1].draw(self)
            self.cfgs[cfg_name][1].rect.y -= self.offsety
    
    def update(self, mouse_pos: tuple[int, int], mouseWheelY: int):
        for cfg_name in self.cfgs:
            if type(self.cfgs[cfg_name][1]) == Button:
                self.cfgs[cfg_name][1].update(mouse_pos)
            else:
                self.cfgs[cfg_name][1].update()

        max_height = len(self.cfgs)*self.font_size
        
        if mouseWheelY == 0:
            return

        if self.offsety+mouseWheelY > 0:
            self.offsety = 0
        elif -self.offsety-mouseWheelY+self.rect.height > max_height:
            if max_height > self.rect.height:
                self.offsety = -max_height+self.rect.height
        else:
            self.offsety += mouseWheelY

class SettingsMenu(pygame.Surface):
    def __init__(self, width: int, height: int, screen_size: tuple[int, int]):
        super().__init__((width, height))
        
        self.rect = self.get_rect()
        self.rect.x = screen_size[0]/2-width/2
        self.rect.y = screen_size[1]/2-height/2

        self.background_color = SETTINGSMENU_BACKGROUND_COLOR
        
        self.font_size = FONT_SIZE
        self.text_color = SETTINGSMENU_TEXT_COLOR

        self.category_color = SETTINGSMENU_CATEGORY_COLOR
        
        self.actual_category_color = SETTINGSMENU_ACTUAL_CATEGORY_COLOR
        self.actual_category_surface_border_width = 2

        self.category_text_space = 5

        self.category_selector_size = (self.rect.width, self.font_size)
        self.category_selector_surface = pygame.Surface(self.category_selector_size)
        self.category_selector_surface.get_rect().topleft = (0,0)
        self.category_selector_offsetx = 0

        self.restart_warn_size = (self.rect.width+1,0)
        i = 0
        while self.restart_warn_size[0] > self.rect.width:
            self.restart_warn_text, self.restart_warn_size = write_text('You need to restart the game to apply the changes.', self.font_size-i, get_size=True)
            i += 1
            if i == self.font_size:
                break

        self.configurable_variables = { 
            'SCREEN':{'width':int,'height':int},
            'PREFERENCES':{'auto_save_new_game':bool,'start_at_last_played_difficulty':bool,'auto_play_radio_when_window_starts':bool},
            'SOUND':{'volume':float,'radio_volume':float,'press_tile_volume':float},
            'CAMERA':{'velocity':int,'zoom_amount':int, 'zoom_level': int},
            'BINDS':{
                'press':str,
                'toggle flag':str,
                'restart':str,
                'show scoreboard':str,
                '+offset_x':str,
                '-offset_x':str,
                '+offset_y':str,
                '-offset_y':str,
                'reset offset':str,
                'zoom-':str,
                'zoom+':str,
                'toggle changedifficulty_menu':str,
                'save':str,
                'toggle loadgame_menu':str,
                'toggle settings_menu':str,
                'toggle radio_menu':str
            }
        }

        self.categories = {}

        for k,v in self.configurable_variables.items():
            self.categories[k] = SettingsCategory(self.rect.width, self.rect.height-self.category_selector_size[1]-self.restart_warn_size[1], k)
            category = self.categories[k]
            category.rect.y += self.category_selector_size[1]
            category.background_color = self.background_color

            for cfg_name, cfg_value_type in v.items():
                if k == 'BINDS':
                    for key in config[k]:
                        if config[k][key] == cfg_name:
                            cfg_value = key
                            break
                else:
                    cfg_value = config[k][cfg_name]

                if cfg_value_type == bool:
                    category.add_button(cfg_name, cfg_name.replace('_',' ')).toggled = convert_to_bool(cfg_value)
                else:
                    textinputline = category.add_textinputline(cfg_name, cfg_name.replace('_',' '))
                    if cfg_value_type in [int, float]:
                        textinputline.allowed_chars = '1234567890'
                        
                        if cfg_value_type == float:
                            textinputline.allowed_chars += '.'
                    
                    textinputline.write_text(cfg_value)
                
                category.cfgs[cfg_name].append(cfg_value)

        self.set_actual_category(0)

        self.categories_surfaces = []

        for category in self.categories.keys():
            self.categories_surfaces.append(write_text(category, self.category_selector_size[1], get_size=True))

    def save_settings(self):
        for category in self.categories:
            for cfg in self.categories[category].cfgs:
                if type(self.categories[category].cfgs[cfg][1]) == Button:
                    config[category][cfg] = str(self.categories[category].cfgs[cfg][1].toggled).lower()
                
                elif type(self.categories[category].cfgs[cfg][1]) == TextInputLine:
                    if category == 'BINDS':
                        config[category].pop(self.categories[category].cfgs[cfg][3]) #  cfgs[cfg][3] -> the first value
                        config[category][self.categories[category].cfgs[cfg][1].text] = cfg
                    else:
                        config[category][cfg] = self.categories[category].cfgs[cfg][1].text

    def set_actual_category(self, index: int):
        self.actual_category_surface_index = index
        self.actual_category = list(self.categories.keys())[self.actual_category_surface_index]

    def update(self, mouse_pos: tuple[int, int], keyDownEvent, mouse_pressed: bool, mouse_keys_pressed: tuple, mouseWheelY: int):
        mouse_pos = (mouse_pos[0]-self.rect.x, mouse_pos[1]-self.rect.y)

        if keyDownEvent:
            for cfg in self.categories[self.actual_category].cfgs.values():
                if type(cfg[1]) == TextInputLine:
                    cfg[1].keydown_event(keyDownEvent)

        if self.category_selector_surface.get_rect().colliderect((*mouse_pos, 1,1)) and mouse_pressed:
            old_category_xpluswidth = 0
            for i, category in enumerate(self.categories_surfaces):
                if pygame.Rect(old_category_xpluswidth+self.category_selector_offsetx, 0, *category[1]).colliderect((*mouse_pos, 1,1)):
                    self.set_actual_category(i)

                old_category_xpluswidth = old_category_xpluswidth+category[1][0]+self.category_text_space

            return

        self.categories[self.actual_category].update((mouse_pos[0], mouse_pos[1]-self.category_selector_size[1]), mouseWheelY)
    
    def draw(self, surface: pygame.Surface):
        surface.blit(self, self.rect)
        self.fill(self.background_color)

        self.blit(self.category_selector_surface, (0,0))
        self.category_selector_surface.fill(self.category_color)

        old_category_xpluswidth = 0
        for i, category in enumerate(self.categories_surfaces):
            self.category_selector_surface.blit(category[0], (old_category_xpluswidth+self.category_selector_offsetx, 0))
            
            if self.actual_category_surface_index == i:
                pygame.draw.rect(self.category_selector_surface, self.actual_category_color, (old_category_xpluswidth+self.category_selector_offsetx,0, category[1][0], self.category_selector_size[1]), 1)
                self.category_selector_offsetx = -old_category_xpluswidth+self.category_selector_size[0]//2-category[1][0]//2

            old_category_xpluswidth = old_category_xpluswidth+category[1][0]+self.category_text_space

        self.categories[self.actual_category].draw(self)
        self.blit(self.restart_warn_text, (0,self.rect.height-self.font_size))

MUSIC_END = pygame.USEREVENT+1

class Radio(pygame.Surface):
    def __init__(self, width: int, height: int, screen_size: tuple[int, int]):
        super().__init__((width, height))

        self.rect = self.get_rect()
        self.rect.x = screen_size[0]/2-width/2
        self.rect.y = screen_size[1]/2-height/2

        self.background_color = RADIOMENU_BACKGROUND_COLOR
        self.border_color = RADIOMENU_BORDER_COLOR

        self.actual_sound_index = random.randint(0, len(RADIO_SOUNDS)-1)
        self.actual_sound_length = 0

        pygame.mixer.music.set_endevent(MUSIC_END)

        self.started = False

        if RADIO_AUTO_PLAY_RADIO_WHEN_WINDOW_STARTS:
            self.load_and_play_music()
        else:
            self.load()

        self.play_button = Button(self.rect.width//2, self.rect.height-32, 30,30, False)
        self.play_button.background_color = self.background_color
        self.play_button.set_image(load_image(RADIO_PLAY_IMAGE))
        
        self.pause_button = Button(self.rect.width//2-32, self.rect.height-32, 30,30, False)
        self.pause_button.background_color = self.background_color
        self.pause_button.set_image(load_image(RADIO_PAUSE_IMAGE))

        self.end_button = Button(self.rect.width//2+32, self.rect.height-32, 30,30, False)
        self.end_button.background_color = self.background_color

        end_image = load_image(RADIO_END_IMAGE)
        self.end_button.set_image(end_image)
        
        self.restart_button = Button(self.rect.width//2-64, self.rect.height-32, 30,30, False)
        self.restart_button.background_color = self.background_color
        self.restart_button.set_image(pygame.transform.flip(end_image, True, False))

    def load(self):
        pygame.mixer.music.load(RADIO_SOUNDS[self.actual_sound_index])
        pygame.mixer.music.set_volume(RADIO_SOUND_VOLUME)
        
        self.actual_music_text, self.actual_music_text_size = write_text(os.path.basename(RADIO_SOUNDS[self.actual_sound_index]), get_size=True)
        self.actual_music_text_offsetx = 0
        self.started = False

    def load_and_play_music(self):
        self.load()
        self.play()

    def play(self):
        if self.started:
            pygame.mixer.music.unpause()
        else:
            self.started = True
            pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()
    
    def unpause(self):
        pygame.mixer.music.unpause()

    def next(self):
        pygame.mixer.music.unload()
        self.actual_sound_index = 0 if self.actual_sound_index == len(RADIO_SOUNDS)-1 else self.actual_sound_index + 1
        self.load_and_play_music()

    def restart(self):
        pygame.mixer.music.play() # rewind function does not work with wav
    
    def update(self, mouse_pos: tuple[int, int]): # UI stuff here
        if self.actual_music_text_size[0] > self.rect.width:
            self.actual_music_text_offsetx -= 1
        if self.actual_music_text_size[0]+self.actual_music_text_offsetx < 0:
            self.actual_music_text_offsetx = self.rect.width+2

        self.play_button.update(mouse_pos)
        self.pause_button.update(mouse_pos)
        self.end_button.update(mouse_pos)
        self.restart_button.update(mouse_pos)

        if self.pause_button.pressed: self.pause()
        if self.play_button.pressed:
            self.play()
        if self.end_button.pressed: self.next()
        if self.restart_button.pressed: self.restart()

    def draw(self, surface: pygame.Surface):
        surface.blit(self, self.rect)
        self.fill(self.background_color)

        self.blit(self.actual_music_text, (self.actual_music_text_offsetx,0))
        
        self.play_button.draw(self)
        self.pause_button.draw(self)
        self.end_button.draw(self)
        self.restart_button.draw(self)

        pygame.draw.rect(surface, self.border_color, self.rect, 1)