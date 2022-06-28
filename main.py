import pygame
import random
import os
from pygame import mixer



mixer.init()
pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('ANGRY REDPANDA')

clock = pygame.time.Clock()
FPS = 60

jump_fx = pygame.mixer.Sound('jump.mp3')
jump_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('death.mp3')
death_fx.set_volume(0.3)


SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

if os.path.exists('score.txt'):
	with open('score.txt', 'r') as file:
		high_score = int(file.read())
else:
	high_score = 0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PANEL = (153, 217, 234)

font_small = pygame.font.SysFont('Pacifico', 20)
font_big = pygame.font.SysFont('Pacifico', 24)

red_image = pygame.image.load('redpanda.png').convert_alpha()
bg_image = pygame.image.load('bg.png').convert_alpha()
tiles_image = pygame.image.load('tiles.png').convert_alpha()



def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_panel():
	pygame.draw.rect(screen, PANEL, (0, 0, SCREEN_WIDTH, 30))
	pygame.draw.line(screen, WHITE, (0, 30), (SCREEN_WIDTH, 30), 2)
	draw_text('SCORE: ' + str(score), font_small, WHITE, 0, 0)


def draw_bg(bg_scroll):
	screen.blit(bg_image, (0, 0 + bg_scroll))
	screen.blit(bg_image, (0, -600 + bg_scroll))


class Player():
	def __init__(self, x, y):
		self.image = pygame.transform.scale(red_image, (60, 65))
		self.width = 25
		self.height = 40
		self.rect = pygame.Rect(0, 0, self.width, self.height)
		self.rect.center = (x, y)
		self.vel_y = 0
		self.flip = False

	def move(self):
		scroll = 0
		dx = 0
		dy = 0

		key = pygame.key.get_pressed()
		if key[pygame.K_a]:
			dx = -10
			self.flip = True
		if key[pygame.K_d]:
			dx = 10
			self.flip = False


		self.vel_y += GRAVITY
		dy += self.vel_y

		if self.rect.left + dx < 0:
			dx = -self.rect.left
		if self.rect.right + dx > SCREEN_WIDTH:
			dx = SCREEN_WIDTH - self.rect.right

		for platform in platform_group:
			if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				if self.rect.bottom < platform.rect.centery:
					if self.vel_y > 0:
						self.rect.bottom = platform.rect.top
						dy = 0
						self.vel_y = -20
						jump_fx.play()

		if self.rect.top <= SCROLL_THRESH:
			if self.vel_y < 0:
				scroll = -dy

		self.rect.x += dx
		self.rect.y += dy + scroll


		self.mask = pygame.mask.from_surface(self.image)

		return scroll

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))

class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, width, moving):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(tiles_image, (width, 10))
		self.moving = moving
		self.move_counter = random.randint(0, 50)
		self.direction = random.choice([-1, 1])
		self.speed = random.randint(1, 2)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self, scroll):
		if self.moving == True:
			self.move_counter += 1
			self.rect.x += self.direction * self.speed

		if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
			self.direction *= -1
			self.move_counter = 0


		self.rect.y += scroll

		if self.rect.top > SCREEN_HEIGHT:
			self.kill()
red = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

platform_group = pygame.sprite.Group()

platform = Platform(SCREEN_WIDTH // 2 , SCREEN_HEIGHT -50, 100, False)
platform_group.add(platform)

run = True
while run:

	clock.tick(FPS)

	if game_over == False:
		scroll = red.move()

		
		bg_scroll += scroll
		if bg_scroll >= 600:
			bg_scroll = 0
		draw_bg(bg_scroll)

		
		if len(platform_group) < MAX_PLATFORMS:
			p_w = random.randint(40, 60)
			p_x = random.randint(0, SCREEN_WIDTH - p_w)
			p_y = platform.rect.y - random.randint(80, 120)
			p_type = random.randint(1, 2)
			if p_type == 1 and score > 500:
				p_moving = True
			else:
				p_moving = False
			platform = Platform(p_x, p_y, p_w, p_moving)
			platform_group.add(platform)

		
		platform_group.update(scroll)

		if scroll > 0:
			score += scroll

		pygame.draw.line(screen, WHITE, (0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 3)
		draw_text('HIGH SCORE', font_small, WHITE, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH)

		platform_group.draw(screen)
		red.draw()

		draw_panel()

		if red.rect.top > SCREEN_HEIGHT:
			game_over = True
			death_fx.play()
			game_over = True
			death_fx.play()
	else:
		if fade_counter < SCREEN_WIDTH:
			fade_counter += 5
			for y in range(0, 6, 2):
				pygame.draw.rect(screen, BLACK, (0, y * 100, fade_counter, 100))
				pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - fade_counter, (y + 1) * 100, SCREEN_WIDTH, 100))
		else:
			draw_text('GAME OVER!', font_big, WHITE, 130, 200)
			draw_text('SCORE: ' + str(score), font_big, WHITE, 130, 250)
			draw_text('PRESS SPACE TO PLAY AGAIN', font_big, WHITE, 40, 300)
			if score > high_score:
				high_score = score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE]:
				game_over = False
				score = 0
				scroll = 0
				fade_counter = 0
				red.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
				platform_group.empty()
				platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT -50, 300, False)
				platform_group.add(platform)


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			
			if score > high_score:
				high_score = score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))
			run = False

	pygame.display.update()



pygame.quit()