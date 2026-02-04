import pygame
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"

# Initialize mixer for sounds
pygame.mixer.init()


class BSD:
	# class variable for gun sound
	gun_sound = None
	
	def __init__(self, screen):
		self.screen = screen
		self.player_img_original = pygame.image.load(str(ASSETS / "joueur.png"))
		self.player_img_original = pygame.transform.scale(self.player_img_original, (128, 128))
		self.player_img = self.player_img_original.copy()
		
		self.player_hit_img_original = pygame.image.load(str(ASSETS / "persotouche.png"))
		self.player_hit_img_original = pygame.transform.scale(self.player_hit_img_original, (128, 128))
		self.player_hit_img = self.player_hit_img_original.copy()
		
		self.player_rect = self.player_img.get_rect()
		self.facing_right = True
		self.is_hit = False
		self.hit_timer = 0.0
		self.speed = 400
		self.keys_pressed = pygame.key.get_pressed()
		self.update_position()

		self.half_lives = 6
		self.max_ammo = 30
		self.ammo = self.max_ammo
		self.reloading = False
		self.reload_time = 1.5
		self.reload_remaining = 0.0

		self.hp_img = pygame.image.load(str(ASSETS / "hp.png"))
		self.hp_img = pygame.transform.scale(self.hp_img, (50, 50))
		self.mihp_img = pygame.image.load(str(ASSETS / "mihp.png"))
		self.mihp_img = pygame.transform.scale(self.mihp_img, (50, 50))
		
		self.balle_img = pygame.image.load(str(ASSETS / "balle.png"))
		self.balle_img = pygame.transform.scale(self.balle_img, (28, 28))
		
		balle = pygame.image.load(str(ASSETS / "balle.png"))
		balle = pygame.transform.scale(balle, (28, 28))
		self.balle_empty_img = balle.copy()
		self.balle_empty_img.fill((100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
		
		if BSD.gun_sound is None:
			BSD.gun_sound = pygame.mixer.Sound(str(ASSETS / "GUNPis_Coup de feu de 357 magnum 9 mm (ID 0438)_LaSonotheque.fr.mp3"))
			BSD.gun_sound.set_volume(0.3)
		
		self.reload_sound = pygame.mixer.Sound(str(ASSETS / "reload.mp3"))
		self.reload_sound.set_volume(0.4)

	def update_position(self):
		w, h = self.screen.get_size()
		self.player_rect.midbottom = (self.player_rect.centerx, h)
		self.player_rect.x = max(0, min(w - self.player_rect.width, self.player_rect.x))

	def center_player(self):
		w, h = self.screen.get_size()
		self.player_rect.centerx = w // 2
		self.player_rect.midbottom = (w // 2, h)

	def handle_event(self, event):
		if event.type == pygame.VIDEORESIZE:
			self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
			self.update_position()
		elif event.type == pygame.MOUSEBUTTONDOWN:
			# only shoot on left click and if we have ammo and not reloading
			if getattr(event, 'button', 1) == 1:
				if not self.reloading and self.ammo > 0:
					self.ammo -= 1
					# play gun sound (stop previous if playing)
					if BSD.gun_sound:
						BSD.gun_sound.stop()
						BSD.gun_sound.play()
					# start auto-reload when ammo depletes
					if self.ammo <= 0:
						self.start_reload()
					return "shoot"
				# if clicked while empty, start reload
				if self.ammo <= 0 and not self.reloading:
					self.start_reload()
		elif event.type == pygame.KEYDOWN:
			# manual reload
			if event.key == pygame.K_r and not self.reloading and self.ammo < self.max_ammo:
				self.start_reload()
		return None

	def start_reload(self):
		self.reloading = True
		self.reload_remaining = self.reload_time
		# play reload sound
		if hasattr(self, 'reload_sound') and self.reload_sound:
			self.reload_sound.play()
	
	def take_hit(self):
		self.is_hit = True
		self.hit_timer = 0.5
		roblox_sound = pygame.mixer.Sound(str(ASSETS / "roblox-death-sound-effect.mp3"))
		roblox_sound.set_volume(1.5)
		roblox_sound.play()

	def update(self, dt):
		keys = pygame.key.get_pressed()
		w, h = self.screen.get_size()
		
		# Mettre à jour le timer de l'état touché
		if self.is_hit:
			self.hit_timer -= dt
			if self.hit_timer <= 0:
				self.is_hit = False
		
		if keys[pygame.K_LEFT]:
			self.player_rect.x -= self.speed * dt
			if self.facing_right:
				self.facing_right = False
				self.player_img = pygame.transform.flip(self.player_img_original, True, False)
				if self.player_hit_img_original:
					self.player_hit_img = pygame.transform.flip(self.player_hit_img_original, True, False)
		if keys[pygame.K_RIGHT]:
			self.player_rect.x += self.speed * dt
			if not self.facing_right:
				self.facing_right = True
				self.player_img = self.player_img_original.copy()
				if self.player_hit_img_original:
					self.player_hit_img = self.player_hit_img_original.copy()
		
		self.player_rect.x = max(0, min(w - self.player_rect.width, self.player_rect.x))

		# reload processing
		if self.reloading:
			self.reload_remaining -= dt
			if self.reload_remaining <= 0:
				self.reloading = False
				self.ammo = self.max_ammo

	def draw(self):
		if self.is_hit and self.player_hit_img:
			self.screen.blit(self.player_hit_img, self.player_rect)
		else:
			self.screen.blit(self.player_img, self.player_rect)
