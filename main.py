import pygame 
from pathlib import Path
from bsd import BSD
from level_manager import LevelManager
from level1 import Level1
from level2 import Level2
from level3 import Level3
from level_easter_egg import LevelEasterEgg
from menu import Menu
from PIL import Image

ASSETS = Path(__file__).parent / "assets"

pygame.init()
screen = pygame.display.set_mode((960, 600), pygame.RESIZABLE)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# Load animated GIF frames
def load_gif_frames(gif_path):
	frames = []
	gif = Image.open(gif_path)
	for frame_idx in range(gif.n_frames):
		gif.seek(frame_idx)
		frame = gif.convert('RGBA')
		pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
		frames.append(pygame_image)
	return frames

bsd_gif_frames = load_gif_frames(str(ASSETS / "bsd.gif"))
win_gif_frames = load_gif_frames(str(ASSETS / "win.gif"))

def show_loading_screen(duration=2):
	start_time = pygame.time.get_ticks()
	font = pygame.font.Font(str(ASSETS / "ARCADECLASSIC.TTF"), 36)
	logo_start = pygame.image.load(str(ASSETS / "Logo_start.png"))
	
	while pygame.time.get_ticks() - start_time < duration * 1000:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
		
		screen.fill((0, 0, 0))
		w, h = screen.get_size()
		
		logo_w, logo_h = logo_start.get_size()
		scale = min(w / logo_w, h / logo_h) * 0.8
		new_w = int(logo_w * scale)
		new_h = int(logo_h * scale)
		scaled_logo = pygame.transform.smoothscale(logo_start, (new_w, new_h))
		
		x = (w - new_w) // 2
		y = (h - new_h) // 2 - 40
		screen.blit(scaled_logo, (x, y))
		
		elapsed = (pygame.time.get_ticks() - start_time) / 1000
		dots = "." * (int(elapsed * 3) % 4)
		loading_text = font.render(f"CHARGEMENT{dots}", True, (255, 100, 100))
		loading_rect = loading_text.get_rect(center=(w // 2, h - 50))
		screen.blit(loading_text, loading_rect)
		
		pygame.display.flip()
		clock.tick(60)

def show_game_over():
	defait_sound = pygame.mixer.Sound(str(ASSETS / "defait.mp3"))
	defait_sound.set_volume(0.5)
	defait_sound.play()
	
	over_img = pygame.image.load(str(ASSETS / "over.png"))
	font = pygame.font.Font(str(ASSETS / "ARCADECLASSIC.TTF"), 32)
	
	# Attendre que le son soit fini ou que le joueur appuie sur ESPACE
	waiting = True
	while waiting:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					waiting = False
		
		# Vérifier si le son est toujours en cours
		if defait_sound and not pygame.mixer.get_busy():
			waiting = False
		
		screen.fill((0, 0, 0))
		w, h = screen.get_size()
		
		scaled_over = pygame.transform.smoothscale(over_img, (w, h))
		screen.blit(scaled_over, (0, 0))
		
		# Afficher le texte d'instruction
		instruction_text = font.render("APPUYEZ  SUR  ESPACE  POUR  CONTINUER", True, (255, 255, 255))
		text_rect = instruction_text.get_rect(center=(w // 2, h - 60))
		screen.blit(instruction_text, text_rect)
		
		pygame.display.flip()
		clock.tick(60)
	
	# Arrêter le son si le joueur quitte avant la fin
	if defait_sound:
		defait_sound.stop()

def show_victory(duration=4, is_easter_egg=False):
	start_time = pygame.time.get_ticks()
	frame_idx = 0
	
	victory_img = None
	if is_easter_egg:
		victory_img = pygame.image.load(str(ASSETS / "winegg.png"))
	
	while pygame.time.get_ticks() - start_time < duration * 1000:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
		
		screen.fill((0, 0, 0))
		
		w, h = screen.get_size()
		
		# Afficher winegg pour l'easter egg
		if is_easter_egg and victory_img:
			scaled_victory = pygame.transform.smoothscale(victory_img, (w, h))
			screen.blit(scaled_victory, (0, 0))
		elif win_gif_frames:
			current_frame = win_gif_frames[frame_idx % len(win_gif_frames)]
			scaled_win = pygame.transform.smoothscale(current_frame, (w, h))
			screen.blit(scaled_win, (0, 0))
			
			# Advance frame every 100ms
			if pygame.time.get_ticks() % 100 < 50:
				frame_idx += 1
		
		pygame.display.flip()
		clock.tick(60)

def show_transition(trans_number, duration=2):
	start_time = pygame.time.get_ticks()
	trans_img = pygame.image.load(str(ASSETS / f"trans{trans_number}.png"))
	
	while pygame.time.get_ticks() - start_time < duration * 1000:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
		
		screen.fill((0, 0, 0))
		w, h = screen.get_size()
		scaled_trans = pygame.transform.smoothscale(trans_img, (w, h))
		screen.blit(scaled_trans, (0, 0))
		
		pygame.display.flip()
		clock.tick(60)

def show_transition_egg(duration=2):
	start_time = pygame.time.get_ticks()
	transegg_img = pygame.image.load(str(ASSETS / "transegg.png"))
	
	while pygame.time.get_ticks() - start_time < duration * 1000:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
		
		screen.fill((0, 0, 0))
		w, h = screen.get_size()
		scaled_trans = pygame.transform.smoothscale(transegg_img, (w, h))
		screen.blit(scaled_trans, (0, 0))
		
		pygame.display.flip()
		clock.tick(60)

def draw_reticle(screen, pos, radius=15):
	pygame.draw.circle(screen, (255, 100, 100), pos, radius, 2)
	pygame.draw.line(screen, (255, 100, 100), (pos[0] - radius - 5, pos[1]), (pos[0] + radius + 5, pos[1]), 1)
	pygame.draw.line(screen, (255, 100, 100), (pos[0], pos[1] - radius - 5), (pos[0], pos[1] + radius + 5), 1)

def draw_hud(screen, game):
	font = pygame.font.Font(str(ASSETS / "ARCADECLASSIC.TTF"), 28)
	
	# Draw life images (6 half-lives = 3 full lives)
	x_offset = 10
	y_offset = 8
	
	full_lives = game.half_lives // 2
	half_life = game.half_lives % 2
	
	# draw full lives
	for i in range(full_lives):
		if game.hp_img:
			screen.blit(game.hp_img, (x_offset, y_offset))
		x_offset += 35
	
	# draw half life if any
	if half_life > 0:
		if game.mihp_img:
			screen.blit(game.mihp_img, (x_offset, y_offset))
		x_offset += 35
	
	# Ammo with bullet images
	x_offset += 30
	# draw current ammo as bullet images
	for i in range(game.ammo):
		if hasattr(game, 'balle_img') and game.balle_img:
			screen.blit(game.balle_img, (x_offset, y_offset + 3))
			x_offset += 8
	
	# draw remaining bullets as outlines (empty ammo spots)
	for i in range(game.max_ammo - game.ammo):
		if hasattr(game, 'balle_empty_img') and game.balle_empty_img:
			screen.blit(game.balle_empty_img, (x_offset, y_offset + 3))
		x_offset += 8
	
	# Reload status
	if game.reloading:
		reload_text = font.render("RECHARGEMENT", True, (200, 200, 0))
		screen.blit(reload_text, (x_offset + 20, y_offset))

def draw_pause_menu(screen):
	w, h = screen.get_size()
	
	overlay = pygame.Surface((w, h))
	overlay.set_alpha(180)
	overlay.fill((0, 0, 0))
	screen.blit(overlay, (0, 0))
	
	title_font = pygame.font.Font(str(ASSETS / "ARCADECLASSIC.TTF"), 72)
	title_text = title_font.render("PAUSE", True, (255, 255, 255))
	title_rect = title_text.get_rect(center=(w // 2, h // 4))
	screen.blit(title_text, title_rect)
	
	option_font = pygame.font.Font(str(ASSETS / "ARCADECLASSIC.TTF"), 48)
	
	# Resume option
	resume_text = option_font.render("REPRENDRE   R", True, (0, 255, 0))
	resume_rect = resume_text.get_rect(center=(w // 2, h // 2))
	screen.blit(resume_text, resume_rect)
	
	# Menu option
	menu_text = option_font.render("RETOUR  AU  MENU   M", True, (255, 100, 100))
	menu_rect = menu_text.get_rect(center=(w // 2, h // 2 + 80))
	screen.blit(menu_text, menu_rect)
	
	return resume_rect, menu_rect

game = BSD(screen)
levels = LevelManager(screen)
# Easter egg trigger
easter_egg_shots = 0
easter_egg_triggered = False
game.center_player()

show_loading_screen(2.5)

menu_loop = True
while menu_loop:
	menu = Menu(screen, [Level1, Level2, Level3], levels.completed_levels)
	
	menu_active = True
	while menu_active:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			else:
				res = menu.handle_event(event)
				if res is not None:
					selected_level = res
					levels.load(selected_level)
					# Reset easter egg
					easter_egg_shots = 0
					easter_egg_triggered = False
					# Réinitialiser les vies complètement
					game.half_lives = 6
					# Reload ammo at start of level
					game.ammo = game.max_ammo
					game.reloading = False
					# Stop menu music
					pygame.mixer.music.stop()
					pygame.mixer.music.load(str(ASSETS / "musfond.mp3"))
					pygame.mixer.music.set_volume(0.3)
					pygame.mixer.music.play(-1)
					game.center_player()
					menu_active = False
		
		menu.draw()
		pygame.display.flip()
		clock.tick(60)
	
	show_loading_screen(2.5)
	
	menu_loop = False
	running = True
	paused = False

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
					# Toggle pause
					paused = not paused
				elif paused:
					# Handle pause menu inputs
					if event.key == pygame.K_r:
						# Resume
						paused = False
					elif event.key == pygame.K_m:
						# Return to menu					pygame.mixer.music.stop()						game.half_lives = 6
						game.ammo = game.max_ammo
						game.reloading = False
						easter_egg_shots = 0
						easter_egg_triggered = False
						levels.load(0)
						game.center_player()
						running = False
						menu_loop = True
						paused = False
				elif event.key == pygame.K_SPACE:
					# Special bullet for level 3
					if hasattr(levels.current, 'shoot_special'):
						levels.current.shoot_special(game.player_rect)
				else:
					# pass other key events to game
					res = game.handle_event(event)
					if res == "shoot":
						# call shoot only if current level implements it
						if hasattr(levels.current, 'shoot'):
							levels.current.shoot(game.player_rect)
			else:
				if not paused:
					res = game.handle_event(event)
					if res == "shoot":
						# Easter egg: detect 5 shots in top-right corner during level 2
						if levels.current_index == 1 and not easter_egg_triggered:
							mouse_x, mouse_y = pygame.mouse.get_pos()
							w, h = screen.get_size()
							# Top-right corner: within 100 pixels from top and right edges
							if mouse_x > w - 100 and mouse_y < 100:
								easter_egg_shots += 1
								if easter_egg_shots >= 5:
									easter_egg_triggered = True
									# Load easter egg level
									levels.current = LevelEasterEgg(screen)
									game.ammo = game.max_ammo
									game.reloading = False
									game.center_player()
						# call shoot only if current level implements it
						if hasattr(levels.current, 'shoot'):
							levels.current.shoot(game.player_rect)
					levels.current.handle_event(event)
		
		if paused:
			# Draw game state and pause menu overlay
			screen.fill((0, 0, 0))
			levels.draw()
			game.draw()
			draw_hud(screen, game)
			mouse_pos = pygame.mouse.get_pos()
			draw_reticle(screen, mouse_pos)
			draw_pause_menu(screen)
			pygame.display.flip()
			clock.tick(60)
			continue
		
		game.update(0.016)
		# Check if player is dead
		if game.half_lives <= 0:
			# Stop music
			pygame.mixer.music.stop()
			
			# Si on perd l'easter egg, retourner au niveau 2
			if easter_egg_triggered:
				defait_sound = pygame.mixer.Sound(str(ASSETS / "defait.mp3"))
				defait_sound.set_volume(0.5)
				defait_sound.play()
				show_transition_egg(2)
				game.half_lives = 6
				game.ammo = game.max_ammo
				game.reloading = False
				easter_egg_shots = 0
				easter_egg_triggered = False
				levels.load(1)
				game.center_player()
				pygame.mixer.music.load(str(ASSETS / "musfond.mp3"))
				pygame.mixer.music.set_volume(0.3)
				pygame.mixer.music.play(-1)
			else:
				# Game over normal
				show_game_over()
				game.half_lives = 6
				game.ammo = game.max_ammo
				game.reloading = False
				easter_egg_shots = 0
				easter_egg_triggered = False
				levels.load(0)  # restart from level 1
				game.center_player()
				running = False
				menu_loop = True
			continue
		levels.current.update(0.016, game)

		# handle enemy bullets hitting the player (generic check)
		if hasattr(levels.current, 'bullets'):
			for b in list(levels.current.bullets):
				if getattr(b, 'owner', None) == 'enemy':
					dx = b.x - game.player_rect.centerx
					dy = b.y - game.player_rect.centery
					dist = (dx**2 + dy**2)**0.5
					if dist <= b.radius + max(game.player_rect.width, game.player_rect.height) / 4:
						b.alive = False
						game.half_lives -= 2
						game.take_hit()
		
		if levels.current.completed:
			# Stop music between levels
			pygame.mixer.music.stop()
			
			# Vérifier si c'est l'easter egg qui est complété
			if easter_egg_triggered and isinstance(levels.current, LevelEasterEgg):
				# Easter egg gagné! Afficher winegg puis passer au niveau 3
				show_victory(4, is_easter_egg=True)
				game.half_lives = 6
				game.ammo = game.max_ammo
				game.reloading = False
				easter_egg_shots = 0
				easter_egg_triggered = False
				# Passer au niveau 3
				levels.load(2)
				game.center_player()
				pygame.mixer.music.load(str(ASSETS / "musfond.mp3"))
				pygame.mixer.music.set_volume(0.3)
				pygame.mixer.music.play(-1)
			elif levels.current_index < len(levels.levels) - 1:
				levels.mark_completed()
				# Afficher la transition appropriée
				if levels.current_index == 0:  # Passage au niveau 2
					show_transition(1, 2)
				elif levels.current_index == 1:  # Passage au niveau 3
					show_transition(2, 2)
				
				levels.load(levels.current_index + 1)
				# Reload ammo for next level
				game.ammo = game.max_ammo
				game.reloading = False
				pygame.mixer.music.load(str(ASSETS / "musfond.mp3"))
				pygame.mixer.music.set_volume(0.3)
				pygame.mixer.music.play(-1)
			else:
				# Game completed! Show victory screen
				levels.mark_completed()
				show_victory(4, is_easter_egg=False)
				# Reset and go back to menu
				game.half_lives = 6
				game.ammo = game.max_ammo
				game.reloading = False
				levels.load(0)
				game.center_player()
				running = False
				menu_loop = True
		
		screen.fill((0, 0, 0))
		levels.draw()
		game.draw()
		# HUD
		draw_hud(screen, game)
		
		mouse_pos = pygame.mouse.get_pos()
		draw_reticle(screen, mouse_pos)
		
		pygame.display.flip()
		clock.tick(60)

pygame.quit()