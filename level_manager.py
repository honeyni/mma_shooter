from level1 import Level1
from level2 import Level2
from level3 import Level3


class LevelManager:
	def __init__(self, screen):
		self.screen = screen
		self.levels = [Level1, Level2, Level3]
		self.completed_levels = []
		self.current_index = 0
		self.current = None
		self.load(self.current_index)

	def load(self, index):
		if index < 0 or index >= len(self.levels):
			return
		self.current_index = index
		level_cls = self.levels[index]
		self.current = level_cls(self.screen)

	def mark_completed(self):
		if self.current_index not in self.completed_levels:
			self.completed_levels.append(self.current_index)

	def handle_event(self, event):
		if self.current:
			self.current.handle_event(event)

	def update(self, dt):
		if self.current:
			self.current.update(dt)

	def draw(self):
		if self.current:
			self.current.draw()
