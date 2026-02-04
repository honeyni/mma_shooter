import pygame
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"


class Menu:
	def __init__(self, screen, levels, completed_levels):
		self.screen = screen
		self.levels = levels
		self.completed_levels = completed_levels
		self.selected = 0
		self.font = pygame.font.Font(str(ASSETS / "ARCADECLASSIC.TTF"), 40)
		self.big_font = pygame.font.Font(str(ASSETS / "ARCADECLASSIC.TTF"), 60)
		self.control_font = pygame.font.Font(str(ASSETS / "ARCADECLASSIC.TTF"), 30)
		
		self.background_img = pygame.image.load(str(ASSETS / "fondmenu.png"))
		
		pygame.mixer.music.load(str(ASSETS / "menu.mp3"))
		pygame.mixer.music.set_volume(0.3)
		pygame.mixer.music.play(-1)

	def handle_event(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP or event.key == pygame.K_z:
				self.selected = (self.selected - 1) % len(self.levels)
			elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
				self.selected = (self.selected + 1) % len(self.levels)
			elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
				return self.selected
		return None

	def draw(self):
		w, h = self.screen.get_size()
		
		scaled_bg = pygame.transform.scale(self.background_img, (w, h))
		self.screen.blit(scaled_bg, (0, 0))
		
		# Left side: Mission list
		left_x = w // 4
		mission_names = ["MISSION  1", "MISSION  2", "MISSION  3"]
		
		# Draw missions
		for i in range(len(self.levels)):
			if i == self.selected:
				color = (255, 255, 0)
				size_font = self.big_font
			else:
				color = (200, 200, 200)
				size_font = self.font
			
			text = size_font.render(mission_names[i], True, color)
			y = h // 3 + 50 + i * 100
			self.screen.blit(text, (left_x - text.get_width() // 2, y))
		
		# Right side: Controls
		right_x = 3 * w // 4
		
		# Draw controls
		controls = [
			"CONTROLES",
			"",
			"   :  DEPLACER",
			"",
			"R  :  RECHARGER",
			"",
			"ESPACE  :  COUP  SPECIAL"
		]
		
		y_offset = h // 3 + 30
		for control in controls:
			if control == "CONTROLES":
				text = self.font.render(control, True, (255, 200, 100))
			elif control == "":
				y_offset += 10
				continue
			else:
				text = self.control_font.render(control, True, (200, 200, 200))
			self.screen.blit(text, (right_x - text.get_width() // 2, y_offset))
			y_offset += 45
		
		# Bottom instruction
		instr = self.control_font.render("ENTREE  :  JOUER", True, (150, 150, 150))
		self.screen.blit(instr, (w // 2 - instr.get_width() // 2, h - 60))
