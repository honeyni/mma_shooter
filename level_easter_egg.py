import pygame
from pathlib import Path
from level_base import Level
import level1
import random

ASSETS = Path(__file__).parent / "assets"


class LevelEasterEgg(Level):
	def __init__(self, screen):
		super().__init__(screen)
		self.background_img = pygame.image.load(str(ASSETS / "Background_easter_egg.png"))
		self.targets = []
		self.bullets = []
		self.completed = False
		# preload poing image for boss bullets if needed
		if level1.Bullet.poing_img is None:
			level1.Bullet.poing_img = pygame.image.load(str(ASSETS / "poing.png"))
			level1.Bullet.poing_img = pygame.transform.scale(level1.Bullet.poing_img, (32, 32))
		self.spawn_targets()

	def spawn_targets(self):
		w, h = self.screen.get_size()
		# Easter egg boss centered
		boss_x = w // 2
		boss_y = h // 3
		
		boss = level1.Target(
			boss_x, boss_y, 
			image_path=ASSETS / "boss_easter_egg.png", 
			hp=50, 
			radius=60, 
			seeks_player=True, 
			touch_damage=0,
			can_shoot=True
		)
		# randomize boss movement slightly
		boss.vx *= random.uniform(0.6, 0.9)
		boss.vy *= random.uniform(0.6, 0.9)
		boss.steer_strength = random.uniform(50, 70)
		# pas d'invincibilité - le joueur peut tirer immédiatement
		boss.invincible_duration = 0
		boss.shoot_cooldown = 800  # tire rapidement (toutes les 0.8 secondes)
		boss.last_shot = pygame.time.get_ticks()
		boss.first_shot_done = False  # marqueur pour le premier tir
		
		self.targets.append(boss)

	def update(self, dt, game=None):
		w, h = self.screen.get_size()
		now = pygame.time.get_ticks()
		
		# update all targets (enemies)
		for t in self.targets:
			if t.seeks_player and game:
				# simple steering towards player
				dx = game.player_rect.centerx - t.x
				dy = game.player_rect.centery - t.y
				dist = (dx**2 + dy**2)**0.5
				if dist > 1:
					t.vx += (dx / dist) * t.steer_strength * dt
					t.vy += (dy / dist) * t.steer_strength * dt
			
			# update position
			t.x += t.vx * dt
			t.y += t.vy * dt
			
			# Boss shooting
			if t.can_shoot and game:
				# Utiliser le cooldown normal
				if now - t.last_shot > t.shoot_cooldown:
					# shoot at player
					dx = game.player_rect.centerx - t.x
					dy = game.player_rect.centery - t.y
					dist = (dx**2 + dy**2)**0.5
					if dist > 1:
						bullet_vx = (dx / dist) * 250
						bullet_vy = (dy / dist) * 250
						bullet = level1.Bullet(t.x, t.y, bullet_vx, bullet_vy, speed=250, owner='enemy', custom_image=level1.Bullet.poing_img)
						self.bullets.append(bullet)
						t.first_shot_done = True  # marquer que le premier tir est fait
					t.last_shot = now
			
			# clamp to screen - boss reste dans le tiers supérieur
			t.x = max(t.radius, min(w - t.radius, t.x))
			t.y = max(t.radius, min(h // 3, t.y))  # ne descend pas plus bas que le tiers supérieur
			
			# update hit indicator
			if t.show_hit and now - t.hit_time > 400:
				t.show_hit = False
		
		# update bullets
		for b in self.bullets:
			b.x += b.dx * dt
			b.y += b.dy * dt
			if b.x < 0 or b.x > w or b.y < 0 or b.y > h:
				b.alive = False
			
			# vérifier si une balle ennemie touche le joueur (mort instantanée)
			if getattr(b, 'owner', None) == 'enemy' and game and b.alive:
				dx = b.x - game.player_rect.centerx
				dy = b.y - game.player_rect.centery
				dist = (dx**2 + dy**2)**0.5
				hit_dist = b.radius + max(game.player_rect.width, game.player_rect.height) / 4
				if dist <= hit_dist:
					game.half_lives = 0  # mort instantanée
					game.take_hit()
					b.alive = False
		
		# check bullet hits on targets (only player bullets)
		for b in list(self.bullets):
			if not b.alive or getattr(b, 'owner', None) == 'enemy':
				continue
			for t in self.targets:
				# check spawn invincibility
				if now - t.spawn_time < t.invincible_duration:
					continue
				dx = b.x - t.x
				dy = b.y - t.y
				dist = (dx**2 + dy**2)**0.5
				if dist <= b.radius + t.radius:
					b.alive = False
					t.hp -= 1
					t.trigger_hit()
					if t.hp <= 0:
						self.targets.remove(t)
					break
		
		# remove dead bullets
		self.bullets = [b for b in self.bullets if b.alive]
		
		# check if all targets are dead
		if len(self.targets) == 0:
			self.completed = True

	def shoot(self, player_rect):
		# player shoots from their position
		mouse_x, mouse_y = pygame.mouse.get_pos()
		dx = mouse_x - player_rect.centerx
		dy = mouse_y - player_rect.centery
		dist = (dx**2 + dy**2)**0.5
		if dist > 1:
			speed = 600
			vx = (dx / dist) * speed
			vy = (dy / dist) * speed
			bullet = level1.Bullet(player_rect.centerx, player_rect.centery, vx, vy, owner='player')
			self.bullets.append(bullet)

	def draw(self):
		w, h = self.screen.get_size()
		bg = pygame.transform.scale(self.background_img, (w, h))
		self.screen.blit(bg, (0, 0))
		
		# draw targets
		for t in self.targets:
			if t.image:
				img_rect = t.image.get_rect(center=(int(t.x), int(t.y)))
				self.screen.blit(t.image, img_rect)
				
				# Draw hit indicator if active
				if t.show_hit and hasattr(t, 'hit_img') and t.hit_img:
					hit_rect = t.hit_img.get_rect(center=(int(t.x), int(t.y)))
					self.screen.blit(t.hit_img, hit_rect)
		
		# draw bullets
		for b in self.bullets:
			# Use custom image if available
			if hasattr(b, 'custom_image') and b.custom_image:
				img_rect = b.custom_image.get_rect(center=(int(b.x), int(b.y)))
				self.screen.blit(b.custom_image, img_rect)
			elif hasattr(b, 'owner') and b.owner == 'player':
				# Player bullets use balle image
				if hasattr(level1.Bullet, 'bullet_img') and level1.Bullet.bullet_img:
					img_rect = level1.Bullet.bullet_img.get_rect(center=(int(b.x), int(b.y)))
					self.screen.blit(level1.Bullet.bullet_img, img_rect)
				else:
					pygame.draw.circle(self.screen, (255, 200, 0), (int(b.x), int(b.y)), b.radius)
			else:
				# Enemy bullets default
				pygame.draw.circle(self.screen, (255, 50, 50), (int(b.x), int(b.y)), b.radius)

	def handle_event(self, event):
		pass
