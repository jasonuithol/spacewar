import ctypes
import pygame
import pygame.image
import pygame.draw
import pygame.gfxdraw
from dark_math import *
from dark_image import *

grid_size = 100
def grid(screen):
	global grid_size
	grid_color = (100,100,100)

	screen.fill((50,50,50))

	for x in range(0, system_resolution[0], grid_size):
		pygame.draw.line(screen, grid_color, (x,0), (x,system_resolution[1]), 1)

	for y in range(0, system_resolution[1], grid_size):
		pygame.draw.line(screen, grid_color, (0,y), (system_resolution[0],y), 1)

def show():
	pygame.display.flip()
	pygame.event.clear()
	while True:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				return

# Init
pygame.init()
ctypes.windll.user32.SetProcessDPIAware()
system_resolution = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
screen = pygame.display.set_mode(system_resolution, pygame.FULLSCREEN, display=0)

# Test 1: rotating images

grid(screen)
image = pygame.image.load('images/fighter_alliance.png').convert_alpha()

screen.blit(image, (0,0))
screen.blit(pygame.transform.rotate(image, 90), (400,0))
screen.blit(pygame.transform.rotate(image, 45), (800,0))
pygame.draw.rect(screen,(255,0,0), pygame.transform.rotate(image, 45).get_rect().move(800,0),3)

rotated = rotate_image_circular(image, 30)
screen.blit(rotated, (1300,0))
pygame.draw.rect(screen,(255,0,0), rotated.get_rect().move(1300,0),3)

show()

# Test 2: normals and degrees

def test_angles(origin, normal):
	global grid_size
	global screen
	line_color = (255,0,0)
	arc_color = (0,255,0)
	pygame.draw.line(screen, line_color, origin, add2(origin, mul2(normal, grid_size)), 3)
	pygame.gfxdraw.arc(screen, origin[0], origin[1], 100, 0, int(normal_to_degrees2(normal)), arc_color)

grid(screen)

test_angles((100,100), (1,0))
test_angles((300,100), (1,1))
test_angles((500,100), normal2((3,2)))

print(f"(1,0) -> expecting 0: {normal_to_degrees2((1,0))}")
print(f"(1,1) -> expecting -45: {normal_to_degrees2((1,1))}")
print(f"(3,2) -> expecting -30ish: {normal_to_degrees2((3,2))}")

print(f"0 -> expecting (1,0): {degrees_to_normal2(0)}")
print(f"-45 -> expecting (1,1): {degrees_to_normal2(-45)}")
print(f"-30 -> expecting (0.5,0.3)ish: {degrees_to_normal2(-30)}")

show()

# Finished
pygame.quit()
