from settings import *
from support import *
from level import Level
from keyInput import KeyInputHandler
from sprite import Cursor, AirTile
from UI import *
from datetime import datetime
import pygame
import random
import os

pygame.init()
pygame.font.init()

class Game:
	def __init__(self):
		self.display = pygame.display.set_mode((WIDTH, HEIGHT))

		self.running = False

		self.clock = pygame.time.Clock()

		self.background_color = BACKGROUND_COLOR

		self.level = Level()

		SQUARE_IMAGES['bomb'] = load_image(BOMB_PATH)
		SQUARE_IMAGES['flag'] = load_image(FLAG_PATH)
		SQUARE_IMAGES['blank'] = pygame.Surface(SQUARE_IMAGES['flag'].get_size())
		SQUARE_IMAGES['pressed'] = pygame.Surface(SQUARE_IMAGES['flag'].get_size())
		SQUARE_IMAGES['air'] =  pygame.Surface(SQUARE_IMAGES['flag'].get_size())

		self.background_surface = transformScaleKeepRatio(load_image(BACKGROUND_PATH), (WIDTH, HEIGHT))
		self.background_rect = self.background_surface.get_rect()
		self.background_pos = (self.level.width/2-self.background_rect.width/2, self.level.height/2-self.background_rect.height/2)

		self.mode = 'wait input'
		self.mode_before = self.mode
		# modes = wait input, play, load, no handle_input, ...

		# top bar space
		self.topbar_spacing = (5,self.level.y/2)

		self.input_handler = KeyInputHandler()
		self.input_handler.keyBinds = KEYBINDS
		self.input_handler.mouseKeyBinds = MOUSEKEYBINDS

		pygame.mouse.set_visible(False)
		self.cursor = Cursor()

		pygame.display.set_caption('SuadoSweeper')

		self.flags_text = None
		self.flags_text_size = (0,0)

		self.flag_image = SQUARE_IMAGES['flag']
		self.flag_image_size = self.flag_image.get_size()

		self.flag_counter_spacing = (2, 5)

		self.bombs_text = None
		self.bombs_text_size = (0,0)
		
		self.bomb_image = SQUARE_IMAGES['bomb']
		self.bomb_size = self.bomb_image.get_size()

		self.time_text = None
		self.time_text_size = (0,0)

		# load saved game menu variables
		self.load_surface = pygame.Surface((HALF_WIDTH, HALF_HEIGHT))
		self.load_rect = self.load_surface.get_rect()
		self.load_size = self.load_surface.get_size()
		self.load_pos = (HALF_WIDTH-self.load_size[0]/2, HALF_HEIGHT-self.load_size[1]/2)
		self.load_width_rect = (self.load_pos[0]-LOADMENU_BORDER_WIDTH, self.load_pos[1]-LOADMENU_BORDER_WIDTH, self.load_rect.width+(LOADMENU_BORDER_WIDTH*2), self.load_rect.height+(LOADMENU_BORDER_WIDTH*2))
		self.load_offset_y = 0
		self.saved_games_interfaces = []

		# difficulty menu variables
		self.difficulty_surface = pygame.Surface((HALF_WIDTH, HALF_HEIGHT))
		self.difficulty_rect = self.difficulty_surface.get_rect()
		self.difficulty_size = self.difficulty_surface.get_size()
		self.difficulty_pos = (HALF_WIDTH-self.difficulty_size[0]/2, HALF_HEIGHT-self.difficulty_size[1]/2)
		self.difficulty_width_rect = (self.difficulty_pos[0]-CHANGEDIFFICULTY_MENU_BORDER_WIDTH, self.difficulty_pos[1]-CHANGEDIFFICULTY_MENU_BORDER_WIDTH, self.difficulty_rect.width+(CHANGEDIFFICULTY_MENU_BORDER_WIDTH*2), self.difficulty_rect.height+(CHANGEDIFFICULTY_MENU_BORDER_WIDTH*2))
		self.difficulty_offset_y = 0
		self.difficulty_interfaces = []

		self.lives_image = load_image(LIVES_IMAGE)
		self.lives_size = self.lives_image.get_size()

		self.lives_text_image = None
		self.lives_text_size = None

		self.last_pressed_bomb_sound_played = None

		self.death_sequence = 0

		self.lost_image = load_image(LOST_PATH)
		self.lost_image_size = self.lost_image.get_size()
		
		self.draw_lost_image = False

		self.chrry_image = load_image(CHRRY)
		self.chrry_image_size = self.chrry_image.get_size()

		self.lost_cooldown = Cooldown(5)

		self.text_inputs = []

		self.popup = None

		self.restart_popup = ConfirmPopup(0, 0, POPUP_WIDTH, POPUP_HEIGHT)
		self.set_confirm_popup(self.restart_popup)
		
		self.restart_popup.write_text('Restart game?', POPUP_TEXT_SIZE)
		
		self.restart_popup.cancel_button.write_text('No', POPUP_BUTTON_TEXT_SIZE)
		self.center_object_text(self.restart_popup.cancel_button)

		self.restart_popup.confirm_button.write_text('Yes', POPUP_BUTTON_TEXT_SIZE)
		self.center_object_text(self.restart_popup.confirm_button)

		self.restart_popup.on_confirm_function = self.restart


		self.delete_popup = ConfirmPopup(0, 0, POPUP_WIDTH, POPUP_HEIGHT)
		self.set_confirm_popup(self.delete_popup)
		
		self.delete_popup.write_text('Delete save?', POPUP_TEXT_SIZE)
		
		self.delete_popup.cancel_button.write_text('No', POPUP_BUTTON_TEXT_SIZE)
		self.center_object_text(self.delete_popup.cancel_button)

		self.delete_popup.confirm_button.write_text('Yes', POPUP_BUTTON_TEXT_SIZE)
		self.center_object_text(self.delete_popup.confirm_button)


		self.rename_popup = TextInputLinePopup(0, 0, POPUP_WIDTH, POPUP_HEIGHT)
		self.set_textinputline_popup(self.rename_popup)

		self.rename_popup.input.allowed_chars = 'qwertyuiopasdfghjklzxcvbnm 1234567890-_=+!@#$%^&()/.,[]{\}`~\''
		
		self.rename_popup.write_text('Rename file:', POPUP_TEXT_SIZE)
		
		self.rename_popup.cancel_button.write_text('Cancel', POPUP_BUTTON_TEXT_SIZE)
		self.center_object_text(self.rename_popup.cancel_button)
		
		self.mouseButtonDownEvent = None
		self.keyDownEvent = None
		self.mouseWheelEvent = None

		# { 'difficulty': [ {'date': [ d, m, y, H, M, S ], 'time': SECONDS } ] }
		self.scoreboard = {}

		if os.path.exists(SCOREBOARD_PATH):
			self.scoreboard = read_binary(SCOREBOARD_PATH)
			sort_scoreboard(self.scoreboard)

		self.update_difficulties()

		self.scoreboard_size = (HALF_WIDTH, HALF_HEIGHT)
		self.scoreboard_surface = pygame.Surface(self.scoreboard_size)
		self.scoreboard_pos = (HALF_WIDTH-self.scoreboard_size[0]//2, HALF_HEIGHT-self.scoreboard_size[1]//2)
		self.can_draw_scoreboard = False
		self.scoreboard_offset_y = 0

		self.lost_sound = None

		self.settingsmenu = SettingsMenu(int(HALF_WIDTH*1.5), int(HALF_HEIGHT*1.5))
		self.settingsmenu.rect.topleft = (HALF_WIDTH-self.settingsmenu.rect.width//2, HALF_HEIGHT-self.settingsmenu.rect.height//2)

		self.radio = Radio(200, 75)

		self.set_difficulty(LAST_PLAYED_DIFFICULTY) # first difficulty is easy(this function also loads the difficulty)

	def set_difficulty(self, difficulty: str):
		self.actual_difficulty = difficulty

		if difficulty != 'unknown':
			self.load_map(DIFFICULTIES[difficulty])
			config['GAME']['last_played_difficulty'] = self.actual_difficulty

		self.scoreboard_difficulty_text_surface = write_text(self.actual_difficulty)
		self.scoreboard_difficulty_text_size = self.scoreboard_difficulty_text_surface.get_size()


		self.update_scoreboard_games()

	def update_difficulties(self):
		for filename in os.listdir(DIFFICULTIES_PATH):
			difficulty_path = os.path.join(DIFFICULTIES_PATH, filename)
			
			if not filename in DIFFICULTIES:
				DIFFICULTIES[filename[:filename.index('.')]] = difficulty_path

	def center_object_text(self, obj):
		obj.text_pos = (obj.rect.width/2-obj.text_size[0]/2, obj.rect.height/2-obj.text_size[1]/2)

	def set_popup(self, popup: Popup):
		popup.border_width = POPUP_BORDER_WIDTH
		popup.border_radius = POPUP_BORDER_RADIUS

		popup.background_color = POPUP_BACKGROUND_COLOR

		popup.rect.center = (HALF_WIDTH, HALF_HEIGHT)
	
	def set_confirm_popup(self, popup: ConfirmPopup):
		self.set_popup(popup)

		popup.cancel_button.background_color = POPUP_CANCEL_BUTTON_COLOR
		popup.confirm_button.background_color = POPUP_CONFIRM_BUTTON_COLOR

	def set_textinputline_popup(self, popup: TextInputLinePopup):
		self.set_popup(popup)

		popup.input.background_color = POPUP_INPUT_BACKGROUND_COLOR

		popup.cancel_button.background_color = POPUP_CANCEL_BUTTON_COLOR

		self.center_object_text(popup.cancel_button)

		popup.input.limit_text_to_border = False

	def set_mode(self, mode: str):
		self.mode_before = self.mode
		self.mode = mode
	
	def reverse_mode(self):
		"""
		swaps mode_before with mode
		"""
		actual_mode = self.mode

		self.mode = self.mode_before
		
		self.mode_before = actual_mode

	def update_scoreboard_games(self):
		self.scoreboard_games = []
		if not self.actual_difficulty in self.scoreboard:
			return

		for index, game in enumerate(self.scoreboard[self.actual_difficulty]):
			date = f'{game["date"][0]}-{game["date"][1]}-{game["date"][2]}'

			formatted_time = format_seconds(game['time'])
			if formatted_time['hour'] != '':
				formatted_time['hour'] += 'h'
			
			if formatted_time['minute'] != '':
				formatted_time['minute'] += 'm'
			
			formatted_time['second'] += 's'
			
			formatted_time = formatted_time['hour']+formatted_time['minute']+formatted_time['second']

			self.scoreboard_games.append([*write_text(f'{index+1}. {date} - {formatted_time} L: {game["lives"]}', SCOREBOARD_FONT_SIZE, DEFAULT_FONT, SCOREBOARD_TEXT_COLOR, get_size=True)])
			self.scoreboard_games[-1][1] = (self.scoreboard_size[0]/2-self.scoreboard_games[-1][1][0]/2, index*self.scoreboard_games[-1][1][1], *self.scoreboard_games[-1][1])

	def draw_scoreboard(self):
		pygame.draw.rect(self.display, SCOREBOARD_BACKGROUND_COLOR, [self.scoreboard_pos[0], self.scoreboard_pos[1]-32, self.scoreboard_size[0], 32], border_top_left_radius=6, border_top_right_radius=6)
		self.display.blit(self.scoreboard_difficulty_text_surface, (self.scoreboard_pos[0]+self.scoreboard_size[0]/2-self.scoreboard_difficulty_text_size[0]/2, self.scoreboard_pos[1]-self.scoreboard_difficulty_text_size[1]))

		self.display.blit(self.scoreboard_surface, self.scoreboard_pos)
		self.scoreboard_surface.fill(SCOREBOARD_BACKGROUND_COLOR)
		for game in self.scoreboard_games:
			self.scoreboard_surface.blit(game[0], (game[1][0], game[1][1]-self.scoreboard_offset_y))

		pygame.draw.rect(self.display, SCOREBOARD_LINE_COLOR, [self.scoreboard_pos[0], self.scoreboard_pos[1]-1, self.scoreboard_size[0], self.scoreboard_size[1]+1], 2)

		pygame.draw.rect(self.display, SCOREBOARD_LINE_COLOR, [self.scoreboard_pos[0], self.scoreboard_pos[1]-32, self.scoreboard_size[0], 32], 2, border_top_left_radius=6, border_top_right_radius=6)

	def load_map(self, path: str=None, collided_tile=None):
		if path == None:
			self.level.randomize(collided_tile)
		else:
			if not self.level.load(path): # if not is_random:
				self.set_difficulty('unknown')
		
		self.bombs_text, self.bombs_text_size = write_text(self.level.bombs_amount, get_size=True)

	def get_collided(self):
		actual_cursor_pos = self.cursor.rect.topleft
		self.cursor.rect.x -= self.level.x+self.level.offset_x
		self.cursor.rect.y -= self.level.y+self.level.offset_y

		collided_tile = None
		for sprite in self.level.tiles.sprites():
			if sprite.rect.colliderect(self.cursor.rect):
				collided_tile = sprite
				break
		
		self.cursor.rect.topleft = actual_cursor_pos
		
		if type(collided_tile) == AirTile:
			return None

		return collided_tile

	def save_game(self, filename: str=None):
		if not (os.path.exists(SAVES_PATH) and os.path.isdir(SAVES_PATH)):
			os.mkdir(SAVES_PATH)
		
		# save_num: the actual save, save_int: the past saves
		if not filename:
			save_num = 0
			for savefile in os.listdir(SAVES_PATH):
				if savefile.startswith('game_') and len(savefile) > 4:
					try:
						save_int = int(savefile[5:savefile.index('.')])
					except ValueError as e:
						continue

					if save_num <= save_int:
						save_num = save_int+1
			
			filename = f'game_{save_num}.json'
		
		content = {
			'map':[],

			'x_amount':self.level.x_amount,
			'y_amount':self.level.y_amount,

			'air_tiles_indexes':self.level.air_tiles_indexes,

			'safe_tiles_amount':self.level.safe_tiles_amount,
			'tiles_pressed':self.level.tiles_pressed,
			
			'bomb_amount':self.level.bombs_amount,
			'bombs_found':self.level.bombs_found,
			
			'default_lives':self.level.default_lives,
			'lives':self.level.lives,
			
			'flagged_tiles_amount':self.level.flagged_tiles_amount,
			
			'time': self.level.time,

			'random':False
		}

		# b - bomb
		# p - pressed
		# f - flag
		# fb - flagged bomb
		# u - unknown but it's not a bomb(basically, not pressed)
		# a - air tile

		for row in self.level.map:
			content['map'].append([])
			for tile in row:
				tile_str = ''
				
				if type(tile) == AirTile:
					tile_str += 'a'
					continue

				if tile.is_flagged:
					tile_str += 'f'
				
				if tile.is_bomb:
					tile_str += 'b'
				else:
					if tile.is_pressed:
						tile_str += 'p'
					elif not tile.is_flagged:
						tile_str += 'u'
			
				content['map'][-1].append(tile_str)

		save(os.path.join(SAVES_PATH, filename), content)

	def start_playing(self, collided_tile):
		self.level.start_time_counting()
		
		self.load_map(collided_tile=collided_tile)
		self.set_mode('play')
		
		if AUTO_SAVE_NEW_GAME:
			datetime_now = datetime.now()
			datetime_now = f'{datetime_now.date()}_{datetime_now.hour}h{datetime_now.minute}m{datetime_now.second}s'

			self.save_game(f'game_{datetime_now}.json')
	
	def restart(self):
		self.level.reset_tiles()
		self.set_mode('wait input')

		return True # returns true for the popups using this function to disappear

	def lose_life(self):
		self.level.lives -= 1
		if self.level.lives <= 0:
			return True
		return False

	def delete_sgi(self, index):
		self.saved_games_interfaces.pop(index)
		for index, sgi in enumerate(self.saved_games_interfaces):
			sgi.my_index = index

	def get_formatted_level_time(self):
		formatted_seconds = format_seconds(self.level.time)

		if formatted_seconds['hour'] != '':
			formatted_seconds['hour'] += 'h '
		if formatted_seconds['minute'] != '':
			formatted_seconds['minute'] += 'm '

		formatted_seconds['second'] += 's'

		return formatted_seconds['hour']+formatted_seconds['minute']+formatted_seconds['second']

	def handle_input(self):
		if self.mode == 'no handle_input':
			return

		collided_tile = self.get_collided()

		# modes like restart can't use the actions inside that if statement
		if self.mode == 'play':
			if self.input_handler.actionDoneOnce('save'):
				self.save_game()
			
			if self.input_handler.actionDoneOnce('restart'):
				self.popup = self.restart_popup

		if self.input_handler.actionDoneOnce('toggle loadgame_menu'): # load saves
			for i, saved_game in enumerate(self.get_saved_games()):
				sgi = SavedGameInterface(saved_game, 0,0, self.load_size[0], self.load_size[1]/10, self.delete_sgi, sort_sgi_list, i)
				
				self.saved_games_interfaces.append(sgi)

				sgi.background_color = LOADMENU_BACKGROUND_COLOR

				sgi.rect.y = i*sgi.rect.height

			self.set_mode('loadgame_menu')

		if self.input_handler.actionDoneOnce('toggle settings_menu'):
			self.set_mode('settings_menu')

		if self.input_handler.actionDoneOnce('toggle radio_menu'):
			self.set_mode('radio_menu')

		if self.input_handler.actionDoneOnce('press'): # left mouse button by default
			# Clicked tile
			if collided_tile and not collided_tile.is_flagged and not collided_tile.is_pressed:
				if self.level.tiles_pressed == 0: # first pressed tile
					self.start_playing(collided_tile)

				if collided_tile.is_bomb: # pressed a bomb tile
					if self.lose_life(): # if lives <= 0
						
						self.draw_lost_image = True
						self.lost_cooldown.reset_start()

						self.death_sequence += 1

						if self.death_sequence != 0 and self.death_sequence % 50 == 0:
							self.lost_sound = play_sound(SOLDIER_LAUGH)
						else:
							self.lost_sound = play_sound(LOST_SOUND)
						
						self.restart()

						self.set_mode('no handle_input')
					
					else:
						pressed_bomb_sound = random.choice(PRESSED_BOMB_SOUNDS)
						
						while pressed_bomb_sound == self.last_pressed_bomb_sound_played:
							pressed_bomb_sound = random.choice(PRESSED_BOMB_SOUNDS)
					
						self.last_pressed_bomb_sound_played = pressed_bomb_sound
						
						play_sound(pressed_bomb_sound)
				
				else: # pressed a safe tile
					self.level.press_tile(collided_tile)
					play_sound(PRESSED_TILE_SOUND, volume=PRESS_SOUND_VOLUME)
		
		elif self.input_handler.actionDoneOnce('toggle flag'): # right mouse button by default
			
			# toggle flag
			if collided_tile and not collided_tile.is_pressed:
				
				if collided_tile.is_flagged:
					
					self.level.unflag_tile(collided_tile)
				
				else:
					
					self.level.flag_tile(collided_tile)

		if self.input_handler.actionDone('-offset_x'):
			self.level.move_offset_x(-self.dt)

		elif self.input_handler.actionDone('+offset_x'):
			self.level.move_offset_x(self.dt)
		
		if self.input_handler.actionDone('-offset_y'):
			self.level.move_offset_y(-self.dt)

		elif self.input_handler.actionDone('+offset_y'):
			self.level.move_offset_y(self.dt)

		if self.input_handler.actionDoneOnce('zoom-'):
			self.level.zoom(-ZOOM_AMOUNT)
		elif self.input_handler.actionDoneOnce('zoom+'):
			self.level.zoom(ZOOM_AMOUNT)

		if self.input_handler.actionDoneOnce('reset offset'):
			self.level.reset_offset_position()

		if self.input_handler.actionDoneOnce('toggle changedifficulty_menu'):
			self.update_difficulties()
			for i, difficulty_name in enumerate(DIFFICULTIES):
				difficulty_interface = DifficultyInterface(DIFFICULTIES[difficulty_name], difficulty_name, 0,0, self.difficulty_size[0], self.difficulty_size[1]/10)
				
				self.difficulty_interfaces.append(difficulty_interface)

				difficulty_interface.background_color = CHANGEDIFFICULTY_MENU_BACKGROUND_COLOR
				
				difficulty_interface.rect.y = i*difficulty_interface.rect.height

			self.set_mode('changedifficulty_menu')

		self.can_draw_scoreboard = False
		if self.input_handler.actionDone('show scoreboard'):
			self.can_draw_scoreboard = True

			if self.input_handler.mouseWheelDown():
				self.scoreboard_offset_y += SCROLL_SPEED
			elif self.input_handler.mouseWheelUp():
				self.scoreboard_offset_y -= SCROLL_SPEED

			if self.scoreboard_offset_y < 0:
				self.scoreboard_offset_y = 0
			elif len(self.scoreboard_games) != 0 and self.scoreboard_games[-1][1][1]+self.scoreboard_games[-1][0].get_height() < self.scoreboard_size[1]+self.scoreboard_offset_y:
				if self.scoreboard_games[-1][1][1]+self.scoreboard_games[-1][0].get_height() > self.scoreboard_size[1]:
					self.scoreboard_offset_y = self.scoreboard_games[-1][1][1]+self.scoreboard_games[-1][0].get_height()-self.scoreboard_size[1]
				else:
					self.scoreboard_offset_y = 0
		else:
			self.scoreboard_offset_y = 0

	def handle_input_changedifficulty(self):
		if self.mode == 'no handle_input':
			return
		
		if self.input_handler.mouseKeyPressedOnce(0):
			self.cursor.rect.x -= self.difficulty_pos[0]
			self.cursor.rect.y -= self.difficulty_pos[1]

			for difficulty_interface in self.difficulty_interfaces:
				if difficulty_interface.get_collided(self.cursor.rect):
					self.set_difficulty(difficulty_interface.filename)
					self.restart()
					break

			self.cursor.rect.x += self.difficulty_pos[0]
			self.cursor.rect.y += self.difficulty_pos[1]
		
		if self.input_handler.mouseWheelDown() and len(self.difficulty_interfaces) != 0 and self.difficulty_interfaces[-1].rect.y+self.difficulty_interfaces[-1].rect.height > self.difficulty_size[1]:
			self.difficulty_offset_y -= SCROLL_SPEED
		
		elif self.input_handler.mouseWheelUp() and len(self.difficulty_interfaces) != 0 and self.difficulty_interfaces[0].rect.y < 0:
			self.difficulty_offset_y += SCROLL_SPEED

		if self.input_handler.actionDoneOnce('toggle changedifficulty_menu'):
			self.reverse_mode()

		for difficulty_interface in self.difficulty_interfaces:
			self.cursor.rect.x -= self.difficulty_pos[0]
			self.cursor.rect.y -= self.difficulty_pos[1]

			difficulty_interface.update_hovered(self.cursor.rect)

			self.cursor.rect.x += self.difficulty_pos[0]
			self.cursor.rect.y += self.difficulty_pos[1]

		if self.mode != 'changedifficulty_menu':
			self.difficulty_interfaces = []

	def handle_input_settings(self):
		if self.mode == 'no handle_input':
			return

		self.settingsmenu.update(self.cursor.rect.topleft, self.keyDownEvent, self.input_handler.mouseKeyPressedOnce(0), self.input_handler.mouseKeysPressed, self.input_handler.mouseWheelDirection*SCROLL_SPEED)

		if self.input_handler.mouseKeyPressedOnce(0):
			for cfg in self.settingsmenu.categories[self.settingsmenu.actual_category].cfgs.values():
				cfg[1].rect.x += self.settingsmenu.rect.x
				cfg[1].rect.y += self.settingsmenu.rect.y+self.settingsmenu.category_selector_size[1]

				cfg[1].mousebuttondown_event(self.mouseButtonDownEvent)

				cfg[1].rect.x -= self.settingsmenu.rect.x
				cfg[1].rect.y -= self.settingsmenu.rect.y+self.settingsmenu.category_selector_size[1]
		
		if self.input_handler.actionDoneOnce('toggle settings_menu'):
			self.reverse_mode()

	def draw_settings(self):
		self.settingsmenu.draw(self.display)

	def handle_input_radio(self):
		if self.mode == 'no handle_input':
			return
		
		self.radio.update((self.cursor.rect.x-self.radio.rect.x, self.cursor.rect.y-self.radio.rect.y))
		
		if self.input_handler.keyPressedOnce(pygame.K_SPACE): # pause/unpause
			if not pygame.mixer.music.get_busy():
				if not self.radio.started:
					self.radio.play()
				self.radio.unpause()
			else: self.radio.pause()
		
		if self.input_handler.keyPressedOnce(pygame.K_RIGHT): # skip
			self.radio.next()
		
		if self.input_handler.keyPressedOnce(pygame.K_LEFT): # restart
			self.radio.restart()
		
		if self.input_handler.actionDoneOnce('toggle radio_menu'):
			self.reverse_mode()

	def draw_radio(self):
		self.radio.draw(self.display)

	def update(self):
		self.input_handler.update(self.mouseWheelEvent)

		self.cursor.update()

		if self.popup: self.popup.update(self)
		
		elif self.mode in ['play', 'wait input']: self.handle_input()
		
		elif self.mode == 'loadgame_menu': self.handle_input_load()

		elif self.mode == 'changedifficulty_menu': self.handle_input_changedifficulty()
	
		elif self.mode == 'settings_menu': self.handle_input_settings()

		elif self.mode == 'radio_menu': self.handle_input_radio()

		self.level.update()

		self.flags_text, self.flags_text_size = write_text(self.level.flagged_tiles_amount, get_size=True)
		
		self.time_text, self.time_text_size = write_text(self.get_formatted_level_time(), get_size=True)

		self.lives_text_image, self.lives_text_size = write_text(self.level.lives, get_size=True)

		for text_input in self.text_inputs:
			text_input.update()

		# won game condition check
		if self.level.bombs_found == self.level.bombs_amount and self.level.tiles_pressed == self.level.safe_tiles_amount and self.level.tiles_pressed != 0:
			self.win_game()

	def win_game(self):
		if self.actual_difficulty != 'unknown':
			if not self.actual_difficulty in self.scoreboard:
				self.scoreboard[self.actual_difficulty] = []

			datetime_now = datetime.now()
			self.scoreboard[self.actual_difficulty].append({
				'date': [datetime_now.day, datetime_now.month, datetime_now.year, datetime_now.hour, datetime_now.minute, datetime_now.second],
				'time': self.level.time,
				'lives':self.level.lives
			})

			sort_scoreboard(self.scoreboard)
			store_binary(SCOREBOARD_PATH, self.scoreboard)
			self.update_scoreboard_games()

		self.death_sequence = 0

		play_sound(random.choice(WON_SOUNDS))
		self.restart()

	def draw(self):
		# flag counter on top left
		self.display.blit(self.flag_image, (self.flag_counter_spacing[0], self.topbar_spacing[1]-self.flag_image_size[1]/2))
		self.display.blit(self.flags_text, (self.flag_counter_spacing[0]+self.flag_image_size[0]+2, self.topbar_spacing[1]-self.flags_text_size[1]/2))
		
		# game time on top middle
		self.display.blit(self.time_text, (HALF_WIDTH-self.time_text_size[0]/2, self.topbar_spacing[1]-self.time_text_size[1]/2))

		self.display.blit(self.lives_image, (self.flag_counter_spacing[0]+self.flag_image_size[0]+self.flags_text_size[0]+7, self.topbar_spacing[1]-self.lives_size[1]/2))
		self.display.blit(self.lives_text_image, (self.flag_counter_spacing[0]+self.flag_image_size[0]+self.flags_text_size[0]+self.lives_size[0]+9, self.topbar_spacing[1]-self.lives_text_size[1]/2))

		# bomb amount on top right
		self.display.blit(self.bomb_image, (WIDTH-self.bomb_size[0]-self.topbar_spacing[0], self.topbar_spacing[1]-self.bomb_size[1]/2))
		self.display.blit(self.bombs_text, (WIDTH-self.bombs_text_size[0]-self.topbar_spacing[0]-self.bomb_size[0], self.topbar_spacing[1]-self.bombs_text_size[1]/2))

		self.level.draw(self.display, self.background_surface, self.background_pos)

		if self.can_draw_scoreboard:
			self.draw_scoreboard()

		if self.popup: self.popup.draw(self.display)
		
		elif self.mode == 'loadgame_menu': self.draw_load()
		
		elif self.mode == 'changedifficulty_menu': self.draw_changedifficulty()
		
		elif self.mode == 'settings_menu': self.draw_settings()
		
		elif self.mode == 'radio_menu': self.draw_radio()

		if self.draw_lost_image:
			if self.lost_cooldown.check() or self.input_handler.keyPressedOnce(pygame.K_ESCAPE):
				self.draw_lost_image = False
				self.reverse_mode()
				
				self.lost_sound.stop()
				self.lost_sound = None
			else:
				if self.death_sequence != 0 and self.death_sequence % 50 == 0:
					self.display.blit(self.chrry_image, (self.level.x+self.level.width/2-self.chrry_image_size[0]/2, self.level.y+self.level.height/2-self.chrry_image_size[1]/2))
				else:
					self.display.blit(self.lost_image, (self.level.x+self.level.width/2-self.lost_image_size[0]/2, self.level.y+self.level.height/2-self.lost_image_size[1]/2))

		self.cursor.draw(self.display)

	def get_saved_games(self):
		saves = []
		
		for root, _, files in os.walk(SAVES_PATH):
			for file in files:
				if file.endswith('.json'):
					saves.append(os.path.join(root, file))

		return saves
	
	def handle_input_load(self):
		if self.mode == 'no handle_input':
			return

		if self.input_handler.mouseKeyPressedOnce(0): # left mouse button
			self.cursor.rect.x -= self.load_pos[0]
			self.cursor.rect.y -= self.load_pos[1]

			for sgi in self.saved_games_interfaces:
				if self.cursor.rect.colliderect((sgi.text_pos[0], sgi.rect.y, *sgi.text_size)):
					self.load_map(sgi.path)
					self.set_mode('play')
					break
			
			self.cursor.rect.x += self.load_pos[0]
			self.cursor.rect.y += self.load_pos[1]

		if self.input_handler.mouseWheelDown() and len(self.saved_games_interfaces) != 0 and self.saved_games_interfaces[-1].rect.y+self.saved_games_interfaces[-1].rect.height > self.load_size[1]:
			self.load_offset_y -= SCROLL_SPEED
		
		elif self.input_handler.mouseWheelUp() and len(self.saved_games_interfaces) != 0 and self.saved_games_interfaces[0].rect.y < 0:
			self.load_offset_y += SCROLL_SPEED

		if self.input_handler.actionDoneOnce('toggle loadgame_menu'): # exit load game menu
			self.reverse_mode()
		
		for sgi in self.saved_games_interfaces:
			sgi.update((self.cursor.rect.x-self.load_pos[0], self.cursor.rect.y-self.load_pos[1]), self)

		if self.mode != 'loadgame_menu': # when leaving the load menu
			self.saved_games_interfaces = []

	def draw_load(self):
		pygame.draw.rect(self.display, LOADMENU_BORDER_COLOR, self.load_width_rect, LOADMENU_BORDER_WIDTH)
		self.display.blit(self.load_surface, self.load_pos)
		self.load_surface.fill(LOADMENU_BACKGROUND_COLOR)
		for i, sgi in enumerate(self.saved_games_interfaces):
			sgi.rect.y = i*sgi.rect.height+self.load_offset_y
			sgi.draw(self.load_surface)

	def draw_changedifficulty(self):
		pygame.draw.rect(self.display, CHANGEDIFFICULTY_MENU_BORDER_COLOR, self.difficulty_width_rect, CHANGEDIFFICULTY_MENU_BORDER_WIDTH)
		self.display.blit(self.difficulty_surface, self.difficulty_pos)
		self.difficulty_surface.fill(CHANGEDIFFICULTY_MENU_BACKGROUND_COLOR)
		for i, difficulty_interface in enumerate(self.difficulty_interfaces):
			difficulty_interface.rect.y = i*difficulty_interface.rect.height+self.difficulty_offset_y
			difficulty_interface.draw(self.difficulty_surface)

	def handle_events(self):
		global WIDTH, HEIGHT

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.quit()
				break
			
			elif event.type == pygame.MOUSEWHEEL:
				self.mouseWheelEvent = event
			
			elif event.type == pygame.KEYDOWN:
				self.keyDownEvent = event

			elif event.type == pygame.MOUSEBUTTONDOWN:
				self.mouseButtonDownEvent = event
			
			elif event.type == MUSIC_END:
				self.radio.next()

	def run(self):
		self.running = True
		while self.running:
			self.display.fill(self.background_color)
			self.dt = self.clock.tick(60) / 10

			self.mouseButtonDownEvent = None
			self.keyDownEvent = None
			self.mouseWheelEvent = None

			self.handle_events()
			
			self.update()
			self.draw()

			pygame.display.update()
	
	def quit(self):
		self.running = False
		self.level.delete_tiles()
		self.settingsmenu.save_settings()
		with open(CONFIG_PATH, 'w') as configfile:
			config.write(configfile)

if __name__ == '__main__':
	game = Game()
<<<<<<< HEAD
	game.run()
=======
	game.run()
>>>>>>> 91f15f5a687ae3e973afee820e36018b99164593
