from settings import *
import pygame
import orjson
import pygame
import time
import pickle
from datetime import timedelta

def load_image(path: str):
    return pygame.image.load(path).convert_alpha()

def write_text(text: str, size: int=FONT_SIZE, font_path: str | pygame.font.Font=DEFAULT_FONT, color: tuple=(255,255,255), antialias: bool=ANTIALIAS, get_size: bool=False):
    text = str(text)
    
    if type(font_path) == str:
        font = pygame.font.Font(font_path, size)
    else:
        font = font_path
    
    rendered_text = font.render(text, antialias, color)

    if not get_size:
        return rendered_text
    
    return (rendered_text, font.size(text))

def save(path: str, content):
    with open(path, "wb") as f:
        f.write(orjson.dumps(content))

def load(path: str):
    with open(path, 'rb') as f:
        return orjson.loads(f.read())

def play_sound(sound: str | pygame.mixer.Sound, wait_end: bool=False, volume=SOUND_VOLUME, fade_ms: int=0):
    if type(sound) == str:
        sound = pygame.mixer.Sound(sound)
        sound.set_volume(volume)
    
    sound.play(fade_ms=fade_ms)
    if wait_end:
        t_start = time.time()
        while time.time()-t_start < sound.get_length():
                continue
    
    return sound

def sort_sgi_list(sgi_list: list):
    sgis_content = []
    indexes = {}

    for index, sgi in enumerate(sgi_list):
        sgis_content.append(sgi.text)
        indexes[sgi.text] = index

    sgis_content.sort()

    for index, sgi_text in enumerate(sgis_content):
        sgi_list[index], sgi_list[indexes[sgi_text]] = sgi_list[indexes[sgi_text]], sgi_list[index]

def store_binary(path: str, content):
    pickle.dump(content, open(path, 'wb'))

def read_binary(path: str):
    return pickle.load(open(path, 'rb'))

def sort_scoreboard_function(obj):
    return obj['time']

def sort_scoreboard(array: list):
    for mode in array:
        array[mode].sort(key=sort_scoreboard_function)

def format_seconds(seconds: float):
    hour, minutes, seconds = str(timedelta(seconds=seconds)).split(':')
    
    output = {'hour':'', 'minute':'', 'second':''}
    
    if hour != '0':
        output['hour'] = hour
    
    if minutes != '00':
        output['minute'] = minutes
    
    if seconds == '00':
        output['second'] = '0'
    else:
        output['second'] = str(int(float(seconds)))
    
    return output

#https://stackoverflow.com/questions/20002242/how-to-scale-images-to-screen-size-in-pygame
def transformScaleKeepRatio(image: pygame.Surface, size: tuple[int, int]):
    width, height = image.get_size()

    scale = min(size[0] / width, size[1] / height)
    
    new_size = (round(width * scale), round(height * scale))
    
    scaled_image = pygame.transform.smoothscale(image, new_size)
    
    return scaled_image

class Cooldown:
    def __init__(self, wait_time: float, start_time: float=-1):
        self.wait_time = wait_time
        self.start_time = start_time
    
    def reset_start(self):
        self.start_time = time.time()
    
    def check(self):
        if self.start_time != -1 and time.time()-self.start_time >= self.wait_time:
            self.reset_start()

            return True
        
        return False