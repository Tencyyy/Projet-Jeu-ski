import math
import random
import pygame


class Player:
    def __init__(self, x, y, frames):
        # ca c'est pour le perso principal (bouger/afficher)
        self.x = x
        self.y = y
        self.w = frames[0].get_width()
        self.h = frames[0].get_height()
        self.base_speed = 4
        self.speed = self.base_speed
        self.boost_timer = 0.0
        self.slow_timer = 0.0
        self.frames = frames
        self.frame_index = 0
        self.frame_timer = 0.0
        self.moonwalk = 0.0

    def rect(self):
        # ca fonction est de donner le rectangle de collision
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, keys, screen_w):
        # ca c'est pour gerer la vitesse (boost / ralentit) puis le deplacement
        if self.boost_timer > 0:
            self.boost_timer = max(0.0, self.boost_timer - dt)
        if self.slow_timer > 0:
            self.slow_timer = max(0.0, self.slow_timer - dt)

        speed_mult = 1.8 if self.boost_timer > 0 else 1.0
        if self.slow_timer > 0:
            speed_mult *= 0.6
        self.speed = self.base_speed * speed_mult

        move = 0
        if keys[pygame.K_LEFT]:
            move -= 1
        if keys[pygame.K_RIGHT]:
            move += 1

        if self.moonwalk > 0:
            # ca c'est pour l'effet "clavier inverser" pendant un petit moment
            move *= -1
            sway = math.sin(pygame.time.get_ticks() * 0.02) * 1.5
            self.x += sway
            self.moonwalk = max(0.0, self.moonwalk - dt)

        self.x += move * self.speed
        self.x = max(10, min(screen_w - self.w - 10, self.x))

        self.frame_timer += dt
        if self.frame_timer >= 0.1:
            self.frame_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, screen):
        # ca c'est pour dessiner la frame courante
        screen.blit(self.frames[self.frame_index], (int(self.x), int(self.y)))


class Obstacle:
    def __init__(self, x, y, kind, speed, image):
        # ca c'est pour un rocher / obstacle qui descend
        self.x = x
        self.y = y
        self.kind = kind
        self.speed = speed
        self.image = image
        self.w = image.get_width()
        self.h = image.get_height()

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt):
        self.y += self.speed * dt

    def draw(self, screen):
        screen.blit(self.image, (int(self.x), int(self.y)))


class Gate:
    def __init__(self, y, gap_x, gap_w, speed, tree_image, screen_w):
        # ca c'est pour une porte = rangee de sapins avec un trou (gap)
        self.y = y
        self.gap_x = gap_x
        self.gap_w = gap_w
        self.speed = speed
        self.tree_image = tree_image
        self.tree_w = tree_image.get_width()
        self.tree_h = tree_image.get_height()
        self.screen_w = screen_w
        self.passed = False

    def update(self, dt):
        self.y += self.speed * dt

    def _tree_positions(self):
        # ca c'est pour placer des sapins partout sauf dans le trou
        positions = []
        x = 0
        gap_left = int(self.gap_x)
        gap_right = int(self.gap_x + self.gap_w)
        while x < self.screen_w:
            if x + self.tree_w <= gap_left or x >= gap_right:
                positions.append(x)
            x += self.tree_w
        return positions

    def tree_rects(self):
        y = int(self.y)
        return [pygame.Rect(x, y, self.tree_w, self.tree_h) for x in self._tree_positions()]

    def draw(self, screen):
        y = int(self.y)
        for x in self._tree_positions():
            screen.blit(self.tree_image, (x, y))


class Bonus:
    def __init__(self, x, y, image, speed, kind):
        # ca c'est pour un bonus = danse ou boost
        self.x = x
        self.y = y
        self.image = image
        self.w = image.get_width()
        self.h = image.get_height()
        self.speed = speed
        self.kind = kind

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt):
        self.y += self.speed * dt

    def draw(self, screen):
        screen.blit(self.image, (int(self.x), int(self.y)))


class Drone:
    def __init__(self, x, image):
        # ca c'est pour le drone qui lache parfois un objet
        self.x = x
        self.y = 60
        self.cooldown = 0.0
        self.image = image

    def update(self, dt, target_x):
        self.x += (target_x - self.x) * 0.05
        self.cooldown = max(0.0, self.cooldown - dt)

    def try_drop(self, obstacles, speed, drop_image):
        if self.cooldown == 0.0 and random.random() < 0.02:
            obstacles.append(Obstacle(self.x - 10, self.y + 10, "drone_drop", speed + 50, drop_image))
            self.cooldown = 1.5

    def draw(self, screen):
        screen.blit(self.image, (int(self.x - self.image.get_width() / 2), int(self.y - 8)))


class Yeti:
    def __init__(self, x, y, image):
        # ca c'est pour le yeti qui poursuit le joueur (il commence derriere)
        self.x = x
        self.y = y
        self.image = image
        self.w = image.get_width()
        self.h = image.get_height()
        self.knockback = 0.0
        self.slow_timer = 0.0
        self.moonwalk_timer = 0.0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, target_x, target_y, speed, speed_bonus, screen_h, screen_w):
        # ca c'est pour l'IA simple: aller vers le joueur + un peu de logic
        if self.slow_timer > 0:
            self.slow_timer = max(0.0, self.slow_timer - dt)
        if self.moonwalk_timer > 0:
            self.moonwalk_timer = max(0.0, self.moonwalk_timer - dt)

        if self.moonwalk_timer > 0:
            # ca c'est pour quand le joueur a le moonwalk, le yeti se trompe de direction
            target_x = screen_w - target_x

        slow_mult = 0.7 if self.slow_timer > 0 else 1.0
        chase_speed = ((speed + speed_bonus) * 0.42 + 28) * slow_mult
        self.y -= chase_speed * dt * 0.9
        self.x += (target_x - (self.x + self.w / 2)) * 0.04
        self.x = max(0, min(screen_w - self.w, self.x))

        desired_y = target_y + 190
        if self.y < desired_y:
            self.y = min(desired_y, self.y + chase_speed * dt * 0.8)
        if self.knockback > 0:
            self.y += 200 * dt
            self.knockback = max(0.0, self.knockback - dt)
        if self.y < -self.h - 60:
            self.y = screen_h + 140
            self.x = random.randint(0, screen_w - self.w)

    def draw(self, screen):
        screen.blit(self.image, (int(self.x), int(self.y)))
