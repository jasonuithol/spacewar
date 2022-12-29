import pygame.image
import pygame.transform

from dark_math import *

def load_image(path, size):
	print(f"Loading image asset from storage {path} scaled to surface {size}")
	image = pygame.image.load(path).convert_alpha()
	image = pygame.transform.scale(image, size)
	return image

def rotate_image_circular(image, direction_degrees):
	rotated = pygame.transform.rotate(image, direction_degrees)
	offset = div2((rotated.get_rect().width - image.get_rect().width, rotated.get_rect().height - image.get_rect().height),2)

	result = pygame.Surface(image.get_rect().size)
	result.blit(rotated, mul2(offset, -1))
	return result
