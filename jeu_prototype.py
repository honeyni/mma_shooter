import pygame
import random
from dataclasses import dataclass

# =========================
# CONFIG
# =========================
W, H = 960, 540
FPS = 60

BLACK = (15, 15, 18)
WHITE = (240, 240, 245)
GREY = (140, 140, 150)
GREEN = (80, 220, 140)
RED = (230, 70, 70)
YELLOW = (250, 220, 80)
BLUE = (80, 150, 255)

HUD_H = 72

# Initialize mixer for sound
pygame.mixer.init()


# =========================
# UTILS
# =========================
def clamp(v, a, b):
    return max(a, min(b, v))


def circle_hit(mx, my, x, y, r):
    return (mx - x) ** 2 + (my - y) ** 2 <= r ** 2


# =========================
# DATA STRUCTURES
# =========================
@dataclass
class GameConfig:
    width: int = W
    height: int = H
    fps: int = FPS


# =========================
# UI
# =========================
class UI:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 22)
        self.big = pygame.font.SysFont("consolas", 42, bold=True)

    def draw_text(self, surf, text, x, y, color=WHITE, big=False):
        f = self.big if big else self.font
        img = f.render(text, True, color)
        surf.blit(img, (x, y))

    def draw_hud(self, surf, level_label, score, shots, focus_unlocked, focus_active, focus_time):
        pygame.draw.rect(surf, (25, 27, 33), (0, 0, W, HUD_H))
        self.draw_text(surf, f"LEVEL: {level_label}", 18, 18)
        self.draw_text(surf, f"SCORE: {score}", 220, 18)
        self.draw_text(surf, f"SHOTS: {shots}", 380, 18)

        if focus_unlocked:
            status = "READY (press 1)" if not focus_active else f"ACTIVE {focus_time:.1f}s"
            self.draw_text(surf, f"FOCUS: {status}", 540, 18, BLUE)

    def draw_center_title(self, surf, title, y=86):
        img = self.big.render(title, True, WHITE)
        surf.blit(img, (W // 2 - img.get_width() // 2, y))


# =========================
# STORY / TRANSITION SCREEN
# =========================
class StoryScreen:
    """Simple écran texte entre niveaux (arcade, facile)."""
    def __init__(self, ui: UI):
        self.ui = ui
        self.active = False
        self.lines = []
        self.timer = 0.0  # seconds

    def show(self, lines, duration=2.0):
        self.active = True
        self.lines = lines
        self.timer = duration

    def update(self, dt):
        if not self.active:
            return
        self.timer -= dt
        if self.timer <= 0:
            self.active = False

    def draw(self, surf):
        if not self.active:
            return
        # overlay
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surf.blit(overlay, (0, 0))

        y = 170
        for i, line in enumerate(self.lines):
            self.ui.draw_text(surf, line, 80, y + i * 34, WHITE)
        self.ui.draw_text(surf, "—", 80, y + len(self.lines) * 34 + 12, GREY)


# =========================
# PLAYER (viseur / crosshair)
# =========================
class Player:
    def __init__(self):
        self.shots = 0
        self.x = W // 2
        self.y = H - 40
        self.bullets = []
        
        # Charger l'image
        try:
            self.image = pygame.image.load("content.png")
            self.image = pygame.transform.scale(self.image, (80, 60))
        except:
            self.image = None
        
        # Charger le son
        try:
            self.shoot_sound = pygame.mixer.Sound("GUNPis_Coup de feu de 357 magnum 9 mm (ID 0438)_LaSonotheque.fr.mp3")
        except:
            self.shoot_sound = None

    def shoot(self):
        self.shots += 1
        
        # Jouer le son à chaque tir
        if self.shoot_sound:
            self.shoot_sound.play()
        
        mx, my = pygame.mouse.get_pos()
        # direction vers la souris
        dx = mx - self.x
        dy = my - self.y
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            dx /= dist
            dy /= dist
        self.bullets.append(Bullet(self.x, self.y, dx, dy))

    def update(self, dt):
        # Enlever les balles qui sortent de l'écran
        self.bullets = [b for b in self.bullets if b.alive]
        for b in self.bullets:
            b.update(dt)

    def draw_crosshair(self, surf):
        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(surf, WHITE, (mx, my), 14, 2)
        pygame.draw.line(surf, WHITE, (mx - 18, my), (mx + 18, my), 1)
        pygame.draw.line(surf, WHITE, (mx, my - 18), (mx, my + 18), 1)

    def draw(self, surf):
        # Dessiner l'arme avec l'image
        if self.image:
            surf.blit(self.image, (self.x - 40, self.y - 30))
        else:
            pygame.draw.rect(surf, YELLOW, (self.x - 20, self.y - 15, 40, 30), border_radius=4)
            pygame.draw.circle(surf, RED, (self.x, self.y - 20), 6)
        
        # Dessiner les balles
        for b in self.bullets:
            b.draw(surf)


class Bullet:
    def __init__(self, x, y, dx, dy, speed=600):
        self.x = float(x)
        self.y = float(y)
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.alive = True
        self.r = 4

    def update(self, dt):
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt
        
        # Si la balle sort de l'écran
        if self.x < -50 or self.x > W + 50 or self.y < -50 or self.y > H + 50:
            self.alive = False

    def hit_test(self, x, y, r):
        return (self.x - x)**2 + (self.y - y)**2 <= (self.r + r)**2

    def draw(self, surf):
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), self.r)


# =========================
# ENTITIES
# =========================
class Target:
    def __init__(self, x, y, r=20, speed=220, color=GREEN, hp=1, decoy=False):
        self.x = float(x)
        self.y = float(y)
        self.r = r
        self.speed = speed
        self.vx = random.choice([-1, 1]) * speed
        self.vy = random.choice([-1, 1]) * speed
        self.color = color
        self.hp = hp
        self.decoy = decoy
        self.alive = True

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x - self.r < 0:
            self.x = self.r
            self.vx *= -1
        if self.x + self.r > W:
            self.x = W - self.r
            self.vx *= -1
        if self.y - self.r < HUD_H:
            self.y = HUD_H + self.r
            self.vy *= -1
        if self.y + self.r > H:
            self.y = H - self.r
            self.vy *= -1

    def hit_test(self, mx, my):
        return circle_hit(mx, my, self.x, self.y, self.r)

    def damage(self, d=1):
        self.hp -= d
        if self.hp <= 0:
            self.alive = False

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), self.r, 3)
        if self.decoy:
            pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), 6)


class BossDrone(Target):
    """Boss du niveau mystère : plus de PV et un look différent."""
    def __init__(self, x, y):
        super().__init__(x, y, r=34, speed=320, color=RED, hp=8, decoy=False)

    def draw(self, surf):
        super().draw(surf)
        # anneau supplémentaire pour le style "boss"
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), self.r + 6, 2)


class PoirierBoss(Target):
    """Boss Poirier : affiche l'image du poirier en mâchant."""
    def __init__(self, x, y):
        super().__init__(x, y, r=50, speed=280, color=RED, hp=10, decoy=False)
        try:
            self.image = pygame.image.load("poirier.png")
            self.image = pygame.transform.scale(self.image, (100, 100))
        except:
            self.image = None

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, (int(self.x - 50), int(self.y - 50)))
        else:
            super().draw(surf)
        # anneau pour le style "boss"
        pygame.draw.circle(surf, YELLOW, (int(self.x), int(self.y)), self.r + 6, 2)


class ItemPickup:
    """Clique dessus pour débloquer un item. Ici : Focus."""
    def __init__(self, x, y, kind="focus"):
        self.x = int(x)
        self.y = int(y)
        self.kind = kind
        self.r = 16
        self.alive = True

    def hit_test(self, mx, my):
        return circle_hit(mx, my, self.x, self.y, self.r)

    def draw(self, surf, ui: UI):
        pygame.draw.rect(surf, BLUE, (self.x - 14, self.y - 14, 28, 28), border_radius=6)
        pygame.draw.rect(surf, BLACK, (self.x - 14, self.y - 14, 28, 28), 3, border_radius=6)
        ui.draw_text(surf, "F", self.x - 7, self.y - 11, WHITE)


# =========================
# LEVEL MANAGER
# =========================


class Soldier(Target):
    """Enemy soldier graphic: uses provided image 'soldat.jpg'."""
    def __init__(self, x, y):
        super().__init__(x, y, r=20, speed=200, color=GREEN, hp=1)
        try:
            # prefer jpg if that's provided
            self.image = pygame.image.load("soldat.jpg")
            self.image = pygame.transform.scale(self.image, (44, 44))
        except:
            self.image = None

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, (int(self.x - 22), int(self.y - 22)))
            pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), self.r, 2)
        else:
            super().draw(surf)


class LevelManager:
    def __init__(self):
        self.level = 1
        self.targets = []
        self.pickups = []

        # Mystery mechanics
        self.decoy_cd = 0.0
        self.item_dropped = False
        
        # Charger le son du début de niveau
        try:
            self.level_start_sound = pygame.mixer.Sound("ssstik.io_1770039077153.mp3")
        except:
            self.level_start_sound = None

    def label(self):
        return "MYSTERY" if self.level == 99 else str(self.level)

    def load(self, level):
        self.level = level
        self.targets = []
        self.pickups = []
        self.decoy_cd = 1.0
        self.item_dropped = False
        
        # Arrêter le son précédent et jouer le nouveau
        pygame.mixer.stop()
        if self.level_start_sound:
            self.level_start_sound.play()

        if level == 1:
            for _ in range(5):
                self.targets.append(Soldier(random.randint(90, W-90), random.randint(HUD_H+60, H-80)))

        elif level == 2:
            for _ in range(6):
                self.targets.append(Target(random.randint(90, W-90), random.randint(HUD_H+60, H-80),
                                           r=18, speed=240, color=GREEN, hp=1))
            # 1 leurre
            self.targets.append(Target(random.randint(90, W-90), random.randint(HUD_H+60, H-80),
                                       r=20, speed=260, color=GREY, hp=1, decoy=True))

        elif level == 3:
            for _ in range(4):
                self.targets.append(Target(random.randint(90, W-90), random.randint(HUD_H+60, H-80),
                                           r=18, speed=270, color=GREEN, hp=1))
            # Boss Poirier
            self.targets.append(PoirierBoss(random.randint(130, W-130), random.randint(HUD_H+80, H-120)))

        elif level == 99:
            # OPÉRATION MIROIR - Boss Poirier
            self.targets.append(PoirierBoss(W//2, H//2))

    def all_cleared(self):
        return all(not t.alive for t in self.targets)

    def update(self, dt, score_ref):
        """Retourne score mis à jour (car pénalités possibles)."""
        # Update targets
        for t in self.targets:
            if t.alive:
                t.update(dt)

        # Mystery spawns
        if self.level == 99:
            score_ref = self._update_mystery(dt, score_ref)

        return score_ref

    def _update_mystery(self, dt, score_ref):
        # spawn decoys
        self.decoy_cd -= dt
        if self.decoy_cd <= 0:
            self.decoy_cd = random.uniform(0.8, 1.3)
            self.targets.append(Target(
                random.randint(90, W-90),
                random.randint(HUD_H+60, H-80),
                r=18, speed=300, color=GREY, hp=1, decoy=True
            ))

        # drop focus item when boss hp low
        boss = self.targets[0]
        if (not self.item_dropped) and boss.alive and boss.hp <= 4:
            self.pickups.append(ItemPickup(
                random.randint(120, W-120),
                random.randint(HUD_H+90, H-120),
                kind="focus"
            ))
            self.item_dropped = True

        # cap decoys count (avoid too many entities)
        alive_targets = [t for t in self.targets if t.alive]
        if len(alive_targets) > 14:
            # keep boss + some others
            boss = alive_targets[0]
            non_decoys = [t for t in alive_targets[1:] if not t.decoy][:6]
            decoys = [t for t in alive_targets[1:] if t.decoy][:7]
            self.targets = [boss] + non_decoys + decoys

        return score_ref

    def draw(self, surf, ui: UI):
        for t in self.targets:
            if t.alive:
                t.draw(surf)
        for p in self.pickups:
            if p.alive:
                p.draw(surf, ui)

    def handle_click(self, mx, my, score):
        """Gestion clic: pickups puis targets. Renvoie (score, hit_any)."""
        # pickups
        for p in self.pickups:
            if p.alive and p.hit_test(mx, my):
                p.alive = False
                return score, True, ("pickup", p.kind)

        # targets
        for t in self.targets:
            if t.alive and t.hit_test(mx, my):
                if t.decoy:
                    score = max(0, score - 2)
                    t.alive = False
                    return score, True, ("decoy", None)
                else:
                    t.damage(1)
                    score += 1
                    return score, True, ("target", None)

        return score, False, (None, None)


# =========================
# ITEMS / POWERUPS
# =========================
class Powerups:
    def __init__(self):
        self.focus_unlocked = False
        self.focus_active = False
        self.focus_time = 0.0

    def activate_focus(self):
        if self.focus_unlocked and not self.focus_active:
            self.focus_active = True
            self.focus_time = 2.0

    def update(self, dt):
        if self.focus_active:
            self.focus_time -= dt
            if self.focus_time <= 0:
                self.focus_active = False
                self.focus_time = 0.0

    def time_scale(self):
        return 0.55 if self.focus_active else 1.0


# =========================
# GAME (main loop)
# =========================
class Game:
    def __init__(self):
        pygame.init()
        self.cfg = GameConfig()
        self.screen = pygame.display.set_mode((self.cfg.width, self.cfg.height))
        pygame.display.set_caption("Mission Saint Denis - Arcade")
        self.clock = pygame.time.Clock()

        self.ui = UI()
        self.story = StoryScreen(self.ui)
        self.player = Player()
        self.levels = LevelManager()
        self.powerups = Powerups()
        
        # Charger le fond
        try:
            self.background = pygame.image.load("fond.png")
            self.background = pygame.transform.scale(self.background, (self.cfg.width, self.cfg.height))
        except:
            self.background = None

        self.score = 0
        self.running = True
        
        # Level selection
        self.selected_level = 1
        self.level_selected = False

        # Select level at start
        self.select_level_screen()
        self.story.show([
            "Base d'entraînement — Zone classifiée",
            f"PHASE {self.selected_level} : Initiation",
            "Objectif : précision avant vitesse."
        ], duration=2.2)

    def select_level_screen(self):
        """Écran de sélection de niveau au démarrage."""
        self.level_selected = False
        while not self.level_selected and self.running:
            dt = self.clock.tick(self.cfg.fps) / 1000.0
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                    return
                    
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_LEFT or e.key == pygame.K_a or e.key == pygame.K_q:
                        self.selected_level = max(1, self.selected_level - 1)
                    elif e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                        self.selected_level = min(3, self.selected_level + 1)
                    elif e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                        self.level_selected = True
                        self.levels.load(self.selected_level)
            
            # Draw level selection screen
            self.screen.fill(BLACK)
            
            # Title
            title = self.ui.big.render("CHOISIR LE NIVEAU", True, WHITE)
            self.screen.blit(title, (W//2 - title.get_width()//2, 80))
            
            # Display levels
            for i in range(1, 4):
                color = YELLOW if i == self.selected_level else GREY
                level_text = self.ui.font.render(f"PHASE {i}", True, color)
                x = W//2 - 150 + (i-1) * 150
                y = 250
                pygame.draw.rect(self.screen, color if i == self.selected_level else BLACK, 
                               (x - 50, y - 40, 100, 80), border_radius=10,
                               width=3 if i == self.selected_level else 1)
                self.screen.blit(level_text, (x - level_text.get_width()//2, y))
            
            # Instructions
            instr = self.ui.font.render("Flèches: Sélectionner | ENTRÉE: Commencer", True, GREY)
            self.screen.blit(instr, (W//2 - instr.get_width()//2, 420))
            
            pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(self.cfg.fps) / 1000.0

            self._handle_events()
            self._update(dt)
            self._draw()

        pygame.quit()

    def _handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False
                if e.key == pygame.K_1:
                    self.powerups.activate_focus()

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = pygame.mouse.get_pos()
                self.player.shoot()

                # if story screen on top, ignore shooting (optional)
                if self.story.active:
                    return

                # Vérifier les pickups seulement (pas les targets)
                for p in self.levels.pickups:
                    if p.alive and p.hit_test(mx, my):
                        p.alive = False
                        self.powerups.focus_unlocked = True
                        self.story.show([
                            "ITEM DÉBLOQUÉ : FOCUS",
                            "Appuie sur 1 pour ralentir le temps (2s)."
                        ], duration=2.0)
                        break

    def _update(self, dt):
        self.player.update(dt)
        self.story.update(dt)
        self.powerups.update(dt)

        dt_scaled = dt * self.powerups.time_scale()

        # update level
        self.score = self.levels.update(dt_scaled, self.score)
        
        # check collisions entre balles et cibles
        for b in self.player.bullets:
            for t in self.levels.targets:
                if t.alive and b.hit_test(t.x, t.y, t.r):
                    b.alive = False
                    t.damage(1)
                    if not t.alive:
                        self.score += 1

        # level progression
        if self.levels.all_cleared() and not self.story.active:
            self._go_next_level()

    def _draw(self):
        # Afficher le fond ou la couleur de base
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)
        
        # Draw level
        self.levels.draw(self.screen, self.ui)
        
        # Draw player (arme + balles)
        self.player.draw(self.screen)
        
        # Draw player crosshair
        self.player.draw_crosshair(self.screen)
        
        # Draw HUD
        self.ui.draw_hud(
            self.screen, 
            f"PHASE {self.levels.level}", 
            self.score, 
            self.player.shots,
            self.powerups.focus_unlocked,
            self.powerups.focus_active,
            self.powerups.focus_time
        )
        
        # Draw story
        self.story.draw(self.screen)
        
        pygame.display.flip()

    def _go_next_level(self):
        # Transitions
        if self.levels.level == 1:
            self.levels.load(2)
            self.story.show([
                "PHASE 2 : Stress & pression",
                "Certaines cibles sont des leurres.",
                "Reste lucide."
            ], duration=2.2)

        elif self.levels.level == 2:
            self.levels.load(3)
            self.story.show([
                "PHASE 3 : Maîtrise totale",
                "Tu es prêt."
            ], duration=2.0)


if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
