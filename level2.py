import pygame
from pathlib import Path
from level_base import Level
import level1
import random

ASSETS = Path(__file__).parent / "assets"


class Level2(Level):
	def __init__(self, screen):
		super().__init__(screen)
		self.background_img = pygame.image.load(str(ASSETS / "lvl2.png"))
		self.targets = []
		self.bullets = []
		self.completed = False
		self.spawn_targets()

	def spawn_targets(self):
		w, h = self.screen.get_size()
		positions = [(i + 1) * w // 6 for i in range(5)]
		# spawn 4 soldat2 (hp=2)
		for i in range(4):
			x = positions[i]
			# randomize Y position slightly
			y = h // 3 + random.randint(-30, 30)
			img = ASSETS / "soldat2.png"
			# slightly spaced, radius chosen larger to match level design
			# soldat2 seek the player and deal touch damage
			t = level1.Target(x, y, image_path=img, hp=2, radius=36, seeks_player=True, touch_damage=0.5)
			# randomize soldier movements more
			t.vx *= random.uniform(0.35, 0.55)
			t.vy *= random.uniform(0.35, 0.55)
			self.targets.append(t)
		# one soldat3 (hp=4)
		x = positions[4]
		img = ASSETS / "soldat3.png"
		# soldat3 is a tank: larger and can shoot at the player
		tank = level1.Target(x, y, image_path=img, hp=4, radius=70, can_shoot=True)
		# make tank less likely to descend too low (we'll clamp in update)
		tank.vy *= 0.5
		self.targets.append(tank)

	def shoot(self, player_rect):
		mx, my = pygame.mouse.get_pos()
		dx = mx - player_rect.centerx
		dy = my - player_rect.centery
		dist = (dx**2 + dy**2)**0.5
		if dist > 0:
			dx /= dist
			dy /= dist
		self.bullets.append(level1.Bullet(player_rect.centerx, player_rect.centery, dx, dy, owner='player'))

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
				# prevent tank from descending too low
				if t.can_shoot:
					max_y = h * 0.6
					if t.y > max_y:
						t.y = max_y
						if t.vy > 0:
							# bounce upward a bit
							t.vy *= -0.4
				# tank shooting behavior
				if t.alive and t.can_shoot and player:
					now = pygame.time.get_ticks()
					# slower firing rate for the tank
					if now - t.last_shot_time > 2200:
						t.last_shot_time = now
						dx = player_x - t.x
						dy = player_y - t.y
						dist = (dx**2 + dy**2) ** 0.5
						if dist > 0:
							dx /= dist
							dy /= dist
							# enemy bullet towards player (slower)
							self.bullets.append(level1.Bullet(t.x, t.y, dx, dy, speed=300, owner='enemy'))

		for b in self.bullets:
			b.update(dt)

		self.bullets = [b for b in self.bullets if b.alive and 0 <= b.x <= w and 0 <= b.y <= h]

		# player bullets damage targets
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
								# show hit indicator if enemy survives
								t.trigger_hit()

		self.bullets = [b for b in self.bullets if b.alive]

		# check player collisions (touch damage from soldiers 2)
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

