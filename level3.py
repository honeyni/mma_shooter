import pygame
from pathlib import Path
from level_base import Level
import level1
import random

ASSETS = Path(__file__).parent / "assets"


class Level3(Level):
	def __init__(self, screen):
		super().__init__(screen)
		self.background_img = pygame.image.load(str(ASSETS / "lvl3.png"))
		self.targets = []
		self.bullets = []
		self.completed = False
		# Système de combo
		self.combo_count = 0
		self.special_bullet_ready = False
		# Charger les images de balle spéciale
		self.spe_img = pygame.image.load(str(ASSETS / "spe.png"))
		self.spe_img = pygame.transform.scale(self.spe_img, (48, 48))
		self.speexplose_gif = pygame.image.load(str(ASSETS / "speexplose.gif"))
		self.speexplose_gif = pygame.transform.scale(self.speexplose_gif, (120, 120))
		self.faaah_sound = pygame.mixer.Sound(str(ASSETS / "faaah.mp3"))
		self.faaah_sound.set_volume(0.6)
		# Explosions actives
		self.explosions = []  # liste de (x, y, start_time)
		# preload poing image for boss bullets
		if level1.Bullet.poing_img is None:
			level1.Bullet.poing_img = pygame.image.load(str(ASSETS / "poing.png"))
			level1.Bullet.poing_img = pygame.transform.scale(level1.Bullet.poing_img, (32, 32))
		self.spawn_targets()

	def spawn_targets(self):
		w, h = self.screen.get_size()
		# Créer plusieurs rangées d'ennemis
		# Première rangée: 6 boxeurs
		positions_row1 = [(i + 1) * w // 7 for i in range(6)]
		y_row1 = h // 4
		for i in range(6):
			x = positions_row1[i]
			# randomiser légèrement la position Y
			y = y_row1 + random.randint(-20, 20)
			# cycle through boxeur images
			img_index = (i % 3) + 1
			if img_index == 2:
				img = ASSETS / "boxeur 2.png"
			else:
				img = ASSETS / f"boxeur{img_index}.png"
			# les boxeurs cherchent le joueur et infligent des dégâts au contact
			t = level1.Target(x, y, image_path=img, hp=10, radius=40, seeks_player=True, touch_damage=0.5)
			# randomize boxeur movements more
			t.vx *= random.uniform(0.35, 0.55)
			t.vy *= random.uniform(0.35, 0.55)
			# add spawn protection (2.5 seconds)
			t.invincible_duration = 2500
			self.targets.append(t)
		
		# Deuxième rangée: 3 boss
		positions_row2 = [(i + 1) * w // 4 for i in range(3)]
		y_row2 = h // 2.5
		for i in range(3):
			x = positions_row2[i]
			y = y_row2 + random.randint(-20, 20)
			img = ASSETS / "boss.png"
			# le boss est plus fort et peut tirer sur le joueur
			boss = level1.Target(x, y, image_path=img, hp=25, radius=75, can_shoot=True)
			# make boss move faster
			boss.vx *= 1.5
			boss.vy *= 0.75
			# add spawn protection (2.5 seconds)
			boss.invincible_duration = 2500
			# Délai avant le premier tir
			boss.first_shot_done = False
			self.targets.append(boss)
		boss.vy *= 0.75
		self.targets.append(boss)

	def shoot(self, player_rect):
		mx, my = pygame.mouse.get_pos()
		dx = mx - player_rect.centerx
		dy = my - player_rect.centery
		dist = (dx**2 + dy**2)**0.5
		if dist > 0:
			dx /= dist
			dy /= dist
		bullet = level1.Bullet(player_rect.centerx, player_rect.centery, dx, dy, owner='player')
		bullet.is_special = False
		self.bullets.append(bullet)
	
	def shoot_special(self, player_rect):
		"""Tirer la balle spéciale avec Espace"""
		if not self.special_bullet_ready:
			return
		
		# Jouer le son faaah
		if self.faaah_sound:
			self.faaah_sound.play()
		
		mx, my = pygame.mouse.get_pos()
		dx = mx - player_rect.centerx
		dy = my - player_rect.centery
		dist = (dx**2 + dy**2)**0.5
		if dist > 0:
			dx /= dist
			dy /= dist
		bullet = level1.Bullet(player_rect.centerx, player_rect.centery, dx, dy, owner='player', custom_image=self.spe_img)
		bullet.is_special = True
		self.bullets.append(bullet)
		# Réinitialiser le combo
		self.special_bullet_ready = False
		self.combo_count = 0

	def handle_event(self, event):
		if event.type == pygame.VIDEORESIZE:
			self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
			return self.screen
		return None

	def update(self, dt, player=None):
		w, h = self.screen.get_size()

		player_x = player.player_rect.centerx if player else w // 2
		player_y = player.player_rect.centery if player else h // 2

		for t in self.targets:
			if t.alive:
				t.update(dt, w, h, player_x, player_y)
				# prevent boss from descending too low
				if t.can_shoot:
					max_y = h * 0.6
					if t.y > max_y:
						t.y = max_y
						if t.vy > 0:
							# bounce upward a bit
							t.vy *= -0.4
				# boss shooting behavior
				if t.alive and t.can_shoot and player:
					now = pygame.time.get_ticks()
					# 2.2s entre les tirs
					if now - t.last_shot_time > 2200:
						t.last_shot_time = now
						t.first_shot_done = True
						dx = player_x - t.x
						dy = player_y - t.y
						dist = (dx**2 + dy**2) ** 0.5
						if dist > 0:
							dx /= dist
							dy /= dist
							# boss bullet with poing image
							self.bullets.append(level1.Bullet(t.x, t.y, dx, dy, speed=300, owner='enemy', custom_image=level1.Bullet.poing_img))

		for b in self.bullets:
			b.update(dt)
		
		# Track bullets going off screen for combo reset (only normal player bullets)
		bullets_off_screen = []
		for b in self.bullets:
			if not (0 <= b.x <= w and 0 <= b.y <= h):
				if getattr(b, 'owner', 'player') == 'player' and not getattr(b, 'is_special', False):
					bullets_off_screen.append(b)

		self.bullets = [b for b in self.bullets if b.alive and 0 <= b.x <= w and 0 <= b.y <= h]
		
		# Reset combo if normal bullets went off screen without hitting
		if bullets_off_screen:
			self.combo_count = 0
			self.special_bullet_ready = False

		# player bullets damage targets
		for b in list(self.bullets):
			if getattr(b, 'owner', 'player') == 'player':
				hit_target = False
				for t in self.targets:
					if t.alive:
						# check if enemy is still invincible
						now = pygame.time.get_ticks()
						if now - t.spawn_time < t.invincible_duration:
							continue  # skip damage if invincible
						dx = b.x - t.x
						dy = b.y - t.y
						dist = (dx**2 + dy**2)**0.5
						if dist <= t.radius + b.radius:
							b.alive = False
							hit_target = True
							
							# Check if it's a special bullet
							if getattr(b, 'is_special', False):
								# Special bullet kills instantly
								t.hp = 0
								# Add explosion effect only for special bullet
								self.explosions.append((t.x, t.y, pygame.time.get_ticks()))
							else:
								# Normal bullet does 1 damage
								t.hp -= 1
								# Increment combo only on boss hits, reset if hit non-boss
								if t.can_shoot:  # only count boss hits
									self.combo_count += 1
									if self.combo_count >= 10:
										self.special_bullet_ready = True
								else:
									# Hit a boxeur (non-boss), reset combo
									self.combo_count = 0
									self.special_bullet_ready = False
							
							if t.hp <= 0:
								t.alive = False
							else:
								# show hit indicator if enemy survives
								t.trigger_hit()
							break
		
		self.bullets = [b for b in self.bullets if b.alive]

		# check player collisions (touch damage from boxeurs)
		if player:
			now = pygame.time.get_ticks()
			px = player.player_rect.centerx
			py = player.player_rect.centery
			for t in self.targets:
				if t.alive and t.touch_damage > 0:
					dx = t.x - px
					dy = t.y - py
					dist = (dx**2 + dy**2) ** 0.5
					if dist <= t.radius + max(player.player_rect.width, player.player_rect.height) / 4:
						# limit touch rate per target (1000ms to avoid double hits)
						if now - t.last_touch_time > 1000:
							t.last_touch_time = now
						player.half_lives -= int(t.touch_damage * 2)
						player.take_hit()
			for b in list(self.bullets):
				if getattr(b, 'owner', None) == 'enemy':
					dx = b.x - player.player_rect.centerx
					dy = b.y - player.player_rect.centery
					dist = (dx**2 + dy**2)**0.5
					if dist <= b.radius + max(player.player_rect.width, player.player_rect.height) / 4:
						b.alive = False
						player.half_lives -= 2
						player.take_hit()

		self.bullets = [b for b in self.bullets if b.alive]
		alive_targets = [t for t in self.targets if t.alive]
		if len(alive_targets) == 0:
			self.completed = True

	def draw(self):
		w, h = self.screen.get_size()
		bg_w, bg_h = self.background_img.get_size()
		
		scale = max(w / bg_w, h / bg_h)
		new_w = int(bg_w * scale)
		new_h = int(bg_h * scale)
		
		scaled_bg = pygame.transform.scale(self.background_img, (new_w, new_h))
		x = (w - new_w) // 2
		y = (h - new_h) // 2
		self.screen.blit(scaled_bg, (x, y))

		for t in self.targets:
			if t.alive:
				if t.image:
					iw, ih = t.image.get_size()
					self.screen.blit(t.image, (int(t.x - iw // 2), int(t.y - ih // 2)))
				else:
					pygame.draw.circle(self.screen, (255, 100, 100), (int(t.x), int(t.y)), t.radius)
				# show hit indicator if active
				if t.show_hit:
					now = pygame.time.get_ticks()
					if now - t.hit_time < t.hit_duration:
						# draw hit image only
						if level1.Target.hit_img:
							hiw, hih = level1.Target.hit_img.get_size()
							self.screen.blit(level1.Target.hit_img, (int(t.x - hiw // 2), int(t.y - hih // 2)))
					else:
						t.show_hit = False

		for b in self.bullets:
			# use custom image if set, otherwise default bullet image
			img_to_use = getattr(b, 'custom_image', None) if hasattr(b, 'custom_image') else None
			if not img_to_use:
				img_to_use = level1.Bullet.bullet_img
			if img_to_use:
				iw, ih = img_to_use.get_size()
				self.screen.blit(img_to_use, (int(b.x - iw // 2), int(b.y - ih // 2)))
			else:
				pygame.draw.circle(self.screen, (255, 255, 0), (int(b.x), int(b.y)), b.radius)
		
		# Draw explosions
		now = pygame.time.get_ticks()
		explosions_to_remove = []
		for i, (ex, ey, start_time) in enumerate(self.explosions):
			if now - start_time < 500:  # show for 500ms
				if self.speexplose_gif:
					ew, eh = self.speexplose_gif.get_size()
					self.screen.blit(self.speexplose_gif, (int(ex - ew // 2), int(ey - eh // 2)))
			else:
				explosions_to_remove.append(i)
		
		# Remove old explosions
		for i in reversed(explosions_to_remove):
			self.explosions.pop(i)
		
		# Draw combo counter
		font = pygame.font.Font(str(ASSETS / "ARCADECLASSIC.TTF"), 36)
		combo_text = f"COMBO   {self.combo_count} 10"
		combo_color = (0, 255, 0) if self.special_bullet_ready else (255, 255, 255)
		text_surface = font.render(combo_text, True, combo_color)
		self.screen.blit(text_surface, (10, 50))
		
		if self.special_bullet_ready:
			special_text = font.render("SPECIAL  READY    PRESS  SPACE", True, (255, 255, 0))
			self.screen.blit(special_text, (10, 85))

