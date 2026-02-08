import pygame # type: ignore
from pathlib import Path
import random
from level_base import Level

ASSETS = Path(__file__).parent / "assets"



class Target:
	# variable de classe pour l'image d'indicateur de coup
	hit_img = None
	# class variable for hitmarker sound
	hitmarker_sound = None
	
	def __init__(self, x, y, image_path=None, hp=1, radius=20, seeks_player=False, touch_damage=0.0, can_shoot=False):
		self.x = x
		self.y = y
		self.alive = True
		# mouvement plus lent pour les cibles (réduit)
		self.vx = random.uniform(-70, 70)
		self.vy = random.uniform(-90, 90)
		self.hp = hp
		self.image = None
		# permettre un rayon personnalisé par cible; valeur par défaut de 20
		self.radius = radius
		# behavior flags
		self.seeks_player = seeks_player
		self.touch_damage = touch_damage
		self.can_shoot = can_shoot
		self.last_touch_time = 0
		self.last_shot_time = 0
		# randomiser la force de recherche par soldat
		self.steer_strength = random.uniform(30, 50) if seeks_player else 0
		# minuteur d'invincibilité (pour la protection au spawn)
		self.spawn_time = pygame.time.get_ticks()
		self.invincible_duration = 0  # ms, peut être défini après création
		# indicateur de coup
		self.show_hit = False
		self.hit_time = 0
		self.hit_duration = 400  # ms
		# charger l'image de coup si pas déjà chargée
		if Target.hit_img is None:
			Target.hit_img = pygame.image.load(str(ASSETS / "hit.png")).convert_alpha()
			Target.hit_img = pygame.transform.scale(Target.hit_img, (100, 100))
		# charger le son du hitmarker si pas déjà chargé
		if Target.hitmarker_sound is None:
			Target.hitmarker_sound = pygame.mixer.Sound(str(ASSETS / "hitmarker_2.mp3"))
			Target.hitmarker_sound.set_volume(0.4)
		if image_path:
			img = pygame.image.load(str(image_path))
			d = self.radius * 2
			self.image = pygame.transform.smoothscale(img, (d, d))
		else:
			self.image = None

	def update(self, dt, screen_width, screen_height, player_x=None, player_y=None):
		# comportement de recherche simple: ajuster légèrement la vélocité vers le joueur
		if self.seeks_player and player_x is not None and player_y is not None:
			dx = player_x - self.x
			dy = player_y - self.y
			dist = (dx ** 2 + dy ** 2) ** 0.5
			if dist > 0:
				# normaliser et appliquer la direction vers le joueur (aléatoire par soldat)
				self.vx += (dx / dist) * self.steer_strength * dt
				self.vy += (dy / dist) * self.steer_strength * dt

		self.x += self.vx * dt
		self.y += self.vy * dt

		if self.x - self.radius < 0 or self.x + self.radius > screen_width:
			self.vx *= -1
			self.x = max(self.radius, min(screen_width - self.radius, self.x))
		if self.y - self.radius < 0 or self.y + self.radius > screen_height:
			self.vy *= -1
			self.y = max(self.radius, min(screen_height - self.radius, self.y))

	def trigger_hit(self):
		"""Afficher l'indicateur de coup quand l'ennemi prend des dégâts mais ne meurt pas"""
		self.show_hit = True
		self.hit_time = pygame.time.get_ticks()
		# jouer le son du hitmarker
		if Target.hitmarker_sound:
			Target.hitmarker_sound.play()



class Bullet:
	# variable de classe pour l'image de balle (chargée une fois)
	bullet_img = None
	poing_img = None
	
	def __init__(self, x, y, dx, dy, speed=None, owner='player', custom_image=None):
		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy
		self.owner = owner
		self.custom_image = custom_image
		# définir les vitesses par défaut selon le propriétaire
		if speed is None:
			if owner == 'player':
				self.speed = 600
			else:
				self.speed = 400
		else:
			self.speed = speed
		self.radius = 4
		self.alive = True
		# charger l'image de balle si pas déjà chargée
		if Bullet.bullet_img is None:
			Bullet.bullet_img = pygame.image.load(str(ASSETS / "balle.png"))
			Bullet.bullet_img = pygame.transform.scale(Bullet.bullet_img, (24, 24))
		# charger l'image de poing si pas déjà chargée
		if Bullet.poing_img is None:
			Bullet.poing_img = pygame.image.load(str(ASSETS / "poing.png"))
			Bullet.poing_img = pygame.transform.scale(Bullet.poing_img, (32, 32))

	def update(self, dt, *_args, **_kwargs):
		# déplacer la balle dans sa direction fixe (définie au moment du tir)
		self.x += self.dx * self.speed * dt
		self.y += self.dy * self.speed * dt


class Level1(Level):
	def __init__(self, screen):
		super().__init__(screen)
		self.background_img = pygame.image.load(str(ASSETS / "lvl1.png"))
		self.targets = []
		self.bullets = []
		self.completed = False
		self.spawn_targets()

	def spawn_targets(self):
		w, h = self.screen.get_size()
		# Faire apparaître 3 soldats type1 (pv=1) et 2 soldats type2 (pv=2)
		positions = [(i + 1) * w // 6 for i in range(5)]
		# first 3 -> soldat1
		for i in range(3):
			x = positions[i]
			# randomiser légèrement la position Y
			y = h // 3 + random.randint(-30, 30)
			img = ASSETS / "soldat1.png"
			# soldat1: plus grand que par défaut, cherche le joueur, dégâts au contact
			t = Target(x, y, image_path=img, hp=1, radius=28, seeks_player=True, touch_damage=0.5)
			# randomize soldier movements more
			t.vx *= random.uniform(0.35, 0.55)
			t.vy *= random.uniform(0.35, 0.55)
			self.targets.append(t)
		# les 2 suivants -> soldat2
		for i in range(3, 5):
			x = positions[i]
			# randomize Y position slightly
			y = h // 3 + random.randint(-30, 30)
			img = ASSETS / "soldat2.png"
			# soldat2: plus de pv, cherche le joueur, dégâts au contact
			t = Target(x, y, image_path=img, hp=2, radius=40, seeks_player=True, touch_damage=0.5)
			# randomize soldier movements more
			t.vx *= random.uniform(0.35, 0.55)
			t.vy *= random.uniform(0.35, 0.55)
			self.targets.append(t)

	def shoot(self, player_rect):
		mx, my = pygame.mouse.get_pos()
		dx = mx - player_rect.centerx
		dy = my - player_rect.centery
		dist = (dx**2 + dy**2)**0.5
		if dist > 0:
			dx /= dist
			dy /= dist
		self.bullets.append(Bullet(player_rect.centerx, player_rect.centery, dx, dy, owner='player'))

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

		for b in self.bullets:
			b.update(dt)
		
		self.bullets = [b for b in self.bullets if b.alive and 0 <= b.x <= w and 0 <= b.y <= h]

		# les balles du joueur endommagent les cibles
		for b in list(self.bullets):
			if getattr(b, 'owner', 'player') == 'player':
				for t in self.targets:
					if t.alive:
						dx = b.x - t.x
						dy = b.y - t.y
						dist = (dx**2 + dy**2)**0.5
						if dist <= t.radius + b.radius:
							b.alive = False
							t.hp -= 1
							if t.hp <= 0:
								t.alive = False
							else:
								# afficher l'indicateur de coup si l'ennemi survit
								t.trigger_hit()

		# enemy bullets can hit player (defensive, mostly used by tanks)
		if player:
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

		# vérifier les collisions du joueur (dégâts au contact des soldats 1 & 2)
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
						# limiter le taux de contact par cible (1000ms pour éviter les doubles coups)
						if now - t.last_touch_time > 1000:
							t.last_touch_time = now
							player.half_lives -= int(t.touch_damage * 2)
							player.take_hit()

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
				# afficher l'indicateur de coup s'il est actif
				if t.show_hit:
					now = pygame.time.get_ticks()
					if now - t.hit_time < t.hit_duration:
						# draw hit image only
						if Target.hit_img:
							hiw, hih = Target.hit_img.get_size()
							self.screen.blit(Target.hit_img, (int(t.x - hiw // 2), int(t.y - hih // 2)))
					else:
						t.show_hit = False
		
		for b in self.bullets:
			# utiliser l'image personnalisée si définie, sinon l'image de balle par défaut
			img_to_use = b.custom_image if b.custom_image else Bullet.bullet_img
			if img_to_use:
				iw, ih = img_to_use.get_size()
				self.screen.blit(img_to_use, (int(b.x - iw // 2), int(b.y - ih // 2)))
			else:
				pygame.draw.circle(self.screen, (255, 255, 0), (int(b.x), int(b.y)), b.radius)

