from configparser import ConfigParser
import pygame
import os

config = ConfigParser()

def convert_to_bool(value: str):
    if value == '0' or value.lower() == 'false' or not bool(value):
        return False
    
    if value == '1' or value.lower() == 'true':
        return True
    
    return None

CONFIG_PATH = 'config.ini'

if os.path.exists(CONFIG_PATH):
    # Read config file
    config.read(CONFIG_PATH)
else:
    # Create config file
    config['SCREEN'] = {'width':'800', 'height':'600'}
    
    config['PREFERENCES'] = {'auto_save_new_game':'false','start_at_last_played_difficulty':'true','auto_play_radio_when_window_starts':'true'}

    config['GAME'] = {'last_played_difficulty': 'baby', 'background_color':'#2b2b2b'}

    config['LEVEL'] = {'background_color':'#3b3b3b'}

    config['FONT'] = {'antialias':'true', 'size':'24', 'default':'CourierNew.ttf','bomb':'SHPinscher-Regular.otf'}
    
    config['TILE'] = {'blank_color':'#171717', 'pressed_color':'#202020','font_color':'#ffffff'}

    config['BINDS'] = {'f1':'save', 'f2':'toggle loadgame_menu', 't':'toggle changedifficulty_menu', 'tab':'show scoreboard', 'escape':'toggle settings_menu', 'r':'restart', 'a':'+offset_x', 'd':'-offset_x', 'w':'+offset_y','s':'-offset_y', 'q':'reset offset', 'z':'zoom-','x':'zoom+', 'mouse0': 'press', 'mouse2': 'toggle flag','quote': 'toggle radio_menu'}
    
    config['LOADMENU'] = {'background_color':'#202020', 'border_color':'#ffffff', 'border_width':'2'}
    
    config['DIFFICULTYMENU'] = {'background_color':'#202020', 'hovered_color':'#646464', 'border_color':'#ffffff', 'border_width':'2'}

    config['POPUP'] = {'width':'250', 'height':'150', 'border_width':'2','border_radius':'10', 'cancel_button_color':'#404040', 'confirm_button_color':'#404040', 'border_color':'#ffffff','background_color':'#202020', 'text_size':'28', 'button_text_size':'40'}
    config['POPUP']['input_background_color'] = config['POPUP']['background_color']
    
    config['INPUTLINE'] = {'border_color':'#ffffff'}

    config['SCOREBOARD'] = {'background_color':'#202020', 'font_size':'24','text_color':'#ffffff', 'line_color': '#f0f0f0'}
    
    config['SETTINGSMENU'] = {'background_color':'#202020', 'text_color':'#ffffff', 'category_color': '#1d1d1d', 'actual_category_color':'#ffffff', 'textinputline_background_color':'#202020','textinputline_border_color':'#2d2d2d'}

    config['CAMERA'] = {'velocity':'5', 'zoom_amount':'8', 'zoom_level':'1'}

    config['SOUND'] = {'volume':'0.25','radio_volume':'0.13','press_tile_volume':'0.5'}

    config['RADIO'] = {'background_color':'#202020','border_color':'#ffffff'}
    
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)

WIDTH = int(config['SCREEN']['width'])
HEIGHT = int(config['SCREEN']['height'])

HALF_WIDTH = WIDTH//2
HALF_HEIGHT = HEIGHT//2

LEVEL_BACKGROUND_COLOR = config['LEVEL']['background_color']

TILE_SIZE = 16
TILE_PRESSED_COLOR = config['TILE']['pressed_color']
TILE_BLANK_COLOR = config['TILE']['blank_color']
TILE_FONT_COLOR = config['TILE']['font_color']

SAVES_PATH = 'saves'
if not os.path.exists(SAVES_PATH):
    os.makedirs(SAVES_PATH)

ASSETS_PATH = 'assets'

ASSETS = {
    'images':
    {
        'bomb':os.path.join(ASSETS_PATH,'images','bomb.png'),
        'flag':os.path.join(ASSETS_PATH,'images','flag.png'),
        'blank':os.path.join(ASSETS_PATH,'images','blank.png'),

        'delete_icon':os.path.join(ASSETS_PATH,'images','delete_icon.png'),
        'rename_icon':os.path.join(ASSETS_PATH,'images','rename_icon.png'),

        'cursor':os.path.join(ASSETS_PATH,'images','cursor.png'),

        'lives':os.path.join(ASSETS_PATH,'images','lives_icon.png'),

        'lost':os.path.join(ASSETS_PATH,'images','lost.png'),

        'radio_play':os.path.join(ASSETS_PATH,'images','radio_play_icon.png'),
        'radio_pause':os.path.join(ASSETS_PATH,'images','radio_pause_icon.png'),
        'radio_end':os.path.join(ASSETS_PATH,'images','radio_end_icon.png'),

        'background':os.path.join(ASSETS_PATH,'images','background.png'),

        'chrry':os.path.join(ASSETS_PATH,'images','chrry.png')
    },

    'audio':
    {
        'pressed_tile':os.path.join(ASSETS_PATH,'audio','pressed_tile.wav'),

        'lost':os.path.join(ASSETS_PATH,'audio','lost.wav'),

        'soldier_laugh':os.path.join(ASSETS_PATH,'audio','soldier_laugh.wav')
    }

}

for i in range(3):
    ASSETS['audio'][f'pressed_bomb{i+1}'] = os.path.join(ASSETS_PATH,'audio',f'pressed_bomb{i+1}.wav')

for i in range(7):
    ASSETS['audio'][f'won{i+1}'] = os.path.join(ASSETS_PATH,'audio',f'won{i+1}.wav')

CUSTOM_PATH = 'custom'
if not os.path.exists(CUSTOM_PATH):
    os.makedirs(CUSTOM_PATH)

else:
    for folder in next(os.walk(CUSTOM_PATH))[1]: # dir only
        folder_path = os.path.join(CUSTOM_PATH, folder)

        if os.path.exists(os.path.join(ASSETS_PATH, folder)):
            for filename in os.listdir(folder_path):
                print(filename)
                ASSETS[folder][os.path.splitext(filename)[0]] = os.path.join(folder_path, filename)

BACKGROUND_PATH = ASSETS['images']['background']

BOMB_PATH = ASSETS['images']['bomb']
FLAG_PATH = ASSETS['images']['flag']
BLANK_PATH = ASSETS['images']['blank']

SQUARE_IMAGES = {'bomb':None,'flag':None,'blank':None,'pressed':None,'air':None}

DELETE_IMAGE = ASSETS['images']['delete_icon']
RENAME_IMAGE = ASSETS['images']['rename_icon']

CURSOR_PATH = ASSETS['images']['cursor']

LIVES_IMAGE = ASSETS['images']['lives']

DEFAULT_FONT = os.path.join(ASSETS_PATH,'fonts',config['FONT']['default'])
BOMB_FONT = os.path.join(ASSETS_PATH,'fonts',config['FONT']['bomb'])

ANTIALIAS = convert_to_bool(config['FONT']['antialias'])

FONT_SIZE = int(config['FONT']['size'])

LOADMENU_BACKGROUND_COLOR = config['LOADMENU']['background_color']
LOADMENU_BORDER_COLOR = config['LOADMENU']['border_color']
LOADMENU_BORDER_WIDTH = int(config['LOADMENU']['border_width'])

PRESSED_BOMB_SOUNDS = [ASSETS['audio'][f'pressed_bomb{i+1}'] for i in range(3)]

PRESSED_TILE_SOUND = ASSETS['audio']['pressed_tile']

LOST_SOUND = ASSETS['audio']['lost']

WON_SOUNDS = [ASSETS['audio'][f'won{i+1}'] for i in range(7)]

SOUND_VOLUME = float(config['SOUND']['volume'])
RADIO_SOUND_VOLUME = float(config['SOUND']['radio_volume'])
PRESS_SOUND_VOLUME = float(config['SOUND']['press_tile_volume'])

LOST_PATH = ASSETS['images']['lost']

RADIO_SOUNDS = [os.path.join(ASSETS_PATH,'audio','radio',i) for i in os.listdir(os.path.join(ASSETS_PATH,'audio','radio'))]
RADIO_PLAY_IMAGE = ASSETS['images']['radio_play']
RADIO_PAUSE_IMAGE = ASSETS['images']['radio_pause']
RADIO_END_IMAGE = ASSETS['images']['radio_end']

RADIOMENU_BACKGROUND_COLOR = config['RADIO']['background_color']
RADIOMENU_BORDER_COLOR = config['RADIO']['border_color']

RADIO_AUTO_PLAY_RADIO_WHEN_WINDOW_STARTS = convert_to_bool(config['PREFERENCES']['auto_play_radio_when_window_starts'])

DIFFICULTIES_PATH = 'difficulties'
DIFFICULTIES = {
    'baby':os.path.join(DIFFICULTIES_PATH, 'baby.json'),
    'not so easy':os.path.join(DIFFICULTIES_PATH, 'not so easy.json'),
    'casual noob':os.path.join(DIFFICULTIES_PATH, 'casual noob.json'),
    'a little hard':os.path.join(DIFFICULTIES_PATH, 'a little hard.json'),
    'custom':os.path.join(DIFFICULTIES_PATH, 'custom.json')
}

LAST_PLAYED_DIFFICULTY = config['GAME']['last_played_difficulty'] if convert_to_bool(config['PREFERENCES']['start_at_last_played_difficulty']) else 'baby'
BACKGROUND_COLOR = config['GAME']['background_color']

CHANGEDIFFICULTY_MENU_BACKGROUND_COLOR = config['DIFFICULTYMENU']['background_color']
CHANGEDIFFICULTY_MENU_HOVERED_COLOR = config['DIFFICULTYMENU']['hovered_color']
CHANGEDIFFICULTY_MENU_BORDER_COLOR = config['DIFFICULTYMENU']['border_color']
CHANGEDIFFICULTY_MENU_BORDER_WIDTH = int(config['DIFFICULTYMENU']['border_width'])

POPUP_CANCEL_BUTTON_COLOR = config['POPUP']['cancel_button_color']
POPUP_CONFIRM_BUTTON_COLOR = config['POPUP']['confirm_button_color']

POPUP_BORDER_WIDTH = int(config['POPUP']['border_width'])
POPUP_BORDER_RADIUS = int(config['POPUP']['border_radius'])
POPUP_BORDER_COLOR = config['POPUP']['border_color']

POPUP_BACKGROUND_COLOR = config['POPUP']['background_color']
POPUP_INPUT_BACKGROUND_COLOR = config['POPUP']['input_background_color']

POPUP_WIDTH = int(config['POPUP']['width'])
POPUP_HEIGHT = int(config['POPUP']['height'])

POPUP_TEXT_SIZE = int(config['POPUP']['text_size'])
POPUP_BUTTON_TEXT_SIZE = int(config['POPUP']['button_text_size'])

INPUT_BORDER_COLOR = config['INPUTLINE']['border_color']

AUTO_SAVE_NEW_GAME = convert_to_bool(config['PREFERENCES']['auto_save_new_game'])

SCOREBOARD_PATH = 'scoreboard.pkl'

SCOREBOARD_BACKGROUND_COLOR = config['SCOREBOARD']['background_color']
SCOREBOARD_FONT_SIZE = int(config['SCOREBOARD']['font_size'])
SCOREBOARD_TEXT_COLOR = config['SCOREBOARD']['text_color']
SCOREBOARD_LINE_COLOR = config['SCOREBOARD']['line_color']

SETTINGSMENU_BACKGROUND_COLOR = config['SETTINGSMENU']['background_color']
SETTINGSMENU_TEXT_COLOR = config['SETTINGSMENU']['text_color']
SETTINGSMENU_CATEGORY_COLOR = config['SETTINGSMENU']['category_color']
SETTINGSMENU_ACTUAL_CATEGORY_COLOR = config['SETTINGSMENU']['actual_category_color']
SETTINGSMENU_TEXTINPUTLINE_BACKGROUND_COLOR = config['SETTINGSMENU']['textinputline_background_color']
SETTINGSMENU_TEXTINPUTLINE_BORDER_COLOR = config['SETTINGSMENU']['textinputline_border_color']

CHRRY = ASSETS['images']['chrry']
SOLDIER_LAUGH = ASSETS['audio']['soldier_laugh']

CAMERA_VELOCITY = float(config['CAMERA']['velocity'])

SPECIAL_KEYS = {
    'backspace':pygame.K_BACKSPACE,
    'tab':pygame.K_TAB,
    'clear':pygame.K_CLEAR,
    'return':pygame.K_RETURN,
    'pause':pygame.K_PAUSE,
    'escape':pygame.K_ESCAPE,
    'space':pygame.K_SPACE,
    'quote':pygame.K_QUOTE,
    'delete':pygame.K_DELETE,
    
    '!':pygame.K_EXCLAIM,
    '"':pygame.K_QUOTEDBL,
    '#':pygame.K_HASH,
    '$':pygame.K_DOLLAR,
    '&':pygame.K_AMPERSAND,
    '(':pygame.K_LEFTPAREN,
    ')':pygame.K_RIGHTPAREN,
    '*':pygame.K_ASTERISK,
    '+':pygame.K_PLUS,
    ',':pygame.K_COMMA,
    '-':pygame.K_MINUS,
    '.':pygame.K_PERIOD,
    '/':pygame.K_SLASH,
    ':':pygame.K_COLON,
    ';':pygame.K_SEMICOLON,
    '<':pygame.K_LESS,
    '=':pygame.K_EQUALS,
    '>':pygame.K_GREATER,
    '?':pygame.K_QUESTION,
    '@':pygame.K_AT,
    '[':pygame.K_LEFTBRACKET,
    '\\':pygame.K_BACKSLASH,
    ']':pygame.K_RIGHTBRACKET,
    '^':pygame.K_CARET,
    '_':pygame.K_UNDERSCORE,
    '`':pygame.K_BACKQUOTE,
    '\'':pygame.K_QUOTE,
    
    'kp_ins':pygame.K_KP0,
    'kp_end':pygame.K_KP1,
    'kp_downarrow':pygame.K_KP2,
    'kp_pgdn':pygame.K_KP3,
    'kp_leftarrow':pygame.K_KP4,
    'kp_5':pygame.K_KP5,
    'kp_rightarrow':pygame.K_KP6,
    'kp_home':pygame.K_KP7,
    'kp_uparrow':pygame.K_KP8,
    'kp_pgup':pygame.K_KP9,
    
    'kp_enter':pygame.K_KP_ENTER,
    'kp_plus':pygame.K_KP_PLUS,
    'kp_minus':pygame.K_KP_MINUS,
    'kp_multiply':pygame.K_KP_MULTIPLY,
    'kp_slash':pygame.K_KP_DIVIDE,
    'kp_equals':pygame.K_KP_EQUALS,
    
    'uparrow':pygame.K_UP,
    'downarrow':pygame.K_DOWN,
    'rightarrow':pygame.K_RIGHT,
    'leftarrow':pygame.K_LEFT,
    
    'insert':pygame.K_INSERT,
    'home':pygame.K_HOME,
    'end':pygame.K_END,
    'pgup':pygame.K_PAGEUP,
    'pgdn':pygame.K_PAGEDOWN,
    'pause':pygame.K_PAUSE,
    
    'f1':pygame.K_F1,
    'f2':pygame.K_F2,
    'f3':pygame.K_F3,
    'f4':pygame.K_F4,
    'f5':pygame.K_F5,
    'f6':pygame.K_F6,
    'f7':pygame.K_F7,
    'f8':pygame.K_F8,
    'f9':pygame.K_F9,
    'f10':pygame.K_F10,
    'f11':pygame.K_F11,
    'f12':pygame.K_F12,
    'f13':pygame.K_F13,
    'f14':pygame.K_F14,
    'f15':pygame.K_F15,
    
    'numlock':pygame.K_NUMLOCK,
    'capslock':pygame.K_CAPSLOCK,
    'scrolllock':pygame.K_SCROLLLOCK,
    
    'rshift':pygame.K_RSHIFT,
    'lshift':pygame.K_LSHIFT,
    
    'rctrl':pygame.K_RCTRL,
    'lctrl':pygame.K_LCTRL,
    
    'ralt':pygame.K_RALT,
    'LALT':pygame.K_LALT,
    
    'RMETA':pygame.K_RMETA,
    'LMETA':pygame.K_LMETA,
    
    'lwin':pygame.K_LSUPER,
    'rwin':pygame.K_RSUPER,
    
    'apps':pygame.K_MENU,
    'print':pygame.K_PRINT,
    'sysrq':pygame.K_SYSREQ,
    'break':pygame.K_BREAK,
    'menu':pygame.K_MENU,
    'power':pygame.K_POWER,
    'euro':pygame.K_EURO,
}

KEYBINDS = {}
MOUSEKEYBINDS = {}
for key in config['BINDS']:
    if key.lower().startswith('mouse'):
        MOUSEKEYBINDS[int(key.lower().replace('mouse',''))] = config['BINDS'][key]
        continue

    if key.lower() in SPECIAL_KEYS:
        KEYBINDS[SPECIAL_KEYS[key.lower()]] = config['BINDS'][key]
    else:
        try:
            KEYBINDS[ord(key)] = config['BINDS'][key]
        except ValueError:
            print('Unknown key:', key)

SCROLL_SPEED = 10

ZOOM_AMOUNT = int(config['CAMERA']['zoom_amount'])
ZOOM_LIMIT = TILE_SIZE*2
ZOOM_LEVEL = int(config['CAMERA']['zoom_level'])

TEXTINPUT_KEYBINDS = {pygame.K_ESCAPE:'deactivate', pygame.K_RETURN:'send', pygame.K_KP_ENTER:'send', pygame.K_BACKSPACE:'remove char'}