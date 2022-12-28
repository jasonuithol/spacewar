import ctypes
import pygame
import pygame.locals
import pygame.math

from dark_math import *

def load_image(path, size):
	print(f"Loading image asset from storage {path} scaled to surface {size}")
	image = pygame.image.load(path).convert_alpha()
	image = pygame.transform.scale(image, size)
	return image

def rotate_image(image, direction_degrees):
	return pygame.transform.rotate(image, direction_degrees)

class Sprite:
	def __init__(self, image, position):
		self.image = image
		self.position = position

	def draw(self, surface):
		surface.blit(self.image, self.position)

	def get_rect(self):
		rect = self.image.get_rect()
		rect.x, rect.y = self.position
		return rect

class SpaceObject(Sprite):
	def __init__(self, position, velocity, direction, image, image_rotation_offset):
		super().__init__(image, position)
		self.velocity = velocity
		self.direction = direction
		self.unrotated_image = image
		self.image_rotation_offset = image_rotation_offset

		# force various properties to exist
		self.tick()

	def accelerate(self, force):
		self.velocity = add2(self.velocity, force)

	def tick(self):
		self.position = add2(self.position, self.velocity)
		self.image = rotate_image(self.unrotated_image, self.direction + self.image_rotation_offset)

class Fighter(SpaceObject):
	def __init__(self, position, velocity, direction, fighter_image, fighter_rotation_offset, bullet_image, bullet_rotation_offset):
		super().__init__(position, velocity, direction, fighter_image, fighter_rotation_offset)
		self.bullet_image = bullet_image
		self.bullet_rotation_offset = bullet_rotation_offset
		self.rotation_speed = 5

	def fire_bullet(self):
		# TODO: Adjust these
		position = add2(self.position, mul2((20, 20), degrees_to_normal2(self.direction)))
		velocity = add2(self.velocity, mul2((5, 5), degrees_to_normal2(self.direction)))

		bullet = Bullet(self, position, velocity, self.direction, self.bullet_image, self.bullet_rotation_offset)
		return bullet

	def fire_thrusters(self):
		# TODO: Adjust these
		force = mul2((10,10), degrees_to_normal2(self.direction))

		self.accelerate(force)

	def rotate_clockwise(self):
		self.direction = self.direction - self.rotation_speed

	def rotate_anticlockwise(self):
		self.direction = self.direction + self.rotation_speed


class Bullet(SpaceObject):
	def __init__(self, owner, position, velocity, direction, image, image_rotation_offset):
		super().__init__(position, velocity, direction, image, image_rotation_offset)
		self.owner = owner

class Planet(Sprite):
	def __init__(self, planet_image, position):
		super().__init__(planet_image, position)
		self.gravity_strength = 0.10

	def assert_gravity_force(self, space_object):
		force = mul2(normal2(sub2(self.get_rect().center, space_object.get_rect().center)), self.gravity_strength)
		space_object.accelerate(force)

class Arena:
	def __init__(self, screen):

		self.screen = screen
		self.text = ['Loaded arena']

		#
		# Load images
		#

		fighter_size = (100,100)
		bullet_size = (20,20)
		planet_size = (200,200)

		fighter_image_alliance = load_image('images/fighter_alliance.png', fighter_size)
		bullet_image_alliance = load_image('images/bullet_alliance.png', bullet_size)

		fighter_image_federation = load_image('images/fighter_federation.png', fighter_size)
		bullet_image_federation = load_image('images/bullet_federation.png', bullet_size)

		planet_image = load_image('images/planet.png', planet_size)

		#
		# Create fighters
		#

		fighter_position_alliance = fighter_size
		fighter_direction_alliance = normal_to_degrees2(normal2((+3,+2)))

		fighter_position_federation = sub2(screen.get_size(), mul2((2,2), fighter_size))
		fighter_direction_federation = normal_to_degrees2(normal2((-3,-2)))

		velocity_none = (0,0)
		image_rotation_offset = -90

		self.fighter_alliance = Fighter(
			fighter_position_alliance,
			velocity_none,
			fighter_direction_alliance,
			fighter_image_alliance, 
			image_rotation_offset,
			bullet_image_alliance,
			image_rotation_offset
		)

		self.text.append(f"Alliance Rect: {self.fighter_alliance.get_rect()}")
		self.fighter_federation = Fighter(
			fighter_position_federation,
			velocity_none,
			fighter_direction_federation,
			fighter_image_federation, 
			image_rotation_offset,
			bullet_image_federation,
			image_rotation_offset
		)

		self.text.append(f"Federation Rect: {self.fighter_federation.get_rect()}")
		'''
		self.fighter_federation = Planet(fighter_image_federation, fighter_position_federation)

		self.text.append(f"Federation Rect: {self.fighter_federation.get_rect()}")
		'''
		#
		# Create planet
		#
		planet_position = sub2(div2(screen.get_size(), 2), div2(planet_size, 2))
		self.planet = Planet(planet_image, planet_position)

		self.text.append(f"Planet Rect: {self.planet.get_rect()}")

		#
		# Create collections
		#
		self.collidable = [self.fighter_alliance, self.fighter_federation, self.planet]
		self.drawable = [self.fighter_alliance, self.fighter_federation, self.planet]
		self.moveable = [self.fighter_alliance, self.fighter_federation]

	def tick(self):

		for moveable in self.moveable:
			self.planet.assert_gravity_force(moveable)
			moveable.tick()

		'''
		# TODO: Remove groups by calling individual sprite collision detection
		alliance_collide = spritecollide(self.fighter_alliance, Group(self.collidable), True)
		federation_collide = spritecollide(self.fighter_federation, Group(self.collidable), True)

		if len(alliance_collide) > 0 and len(federation_collide) > 0:
			# TODO: Game over: draw
			return (0,0)

		if len(alliance_collide) > 0:
			# TODO: Game over: federation win
			return (0,1)

		if len(federation_collide) > 0:
			# TODO: Game over: alliance win
			return (1,0)

		return None
		'''

	def draw(self):
		for drawable in [self.fighter_alliance, self.fighter_federation, self.planet]: #self.drawable
			drawable.draw(self.screen)

def start_round(screen_handle):
	font = pygame.font.SysFont('arial', 32)
	arena = Arena(screen_handle)
	clock = pygame.time.Clock()
	while True:
		for event in pygame.event.get():
			if event.type == pygame.locals.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				pygame.quit()
				quit()
			else:
				# event handler. for updating game state based on user input.
				pass

		arena.tick()
		screen_handle.fill((0,0,0))
		arena.draw()

		if len(arena.text) > 0:
			text_to_render = '; '.join(arena.text)
			textimage = font.render(text_to_render,True,(255,255,255),(0,0,0))
			screen_handle.blit(textimage, (0,0))
			print(text_to_render)
		
		'''
		# debug rectangles
		for drawable in [arena.fighter_alliance, arena.fighter_federation, arena.planet]:
			pygame.draw.rect(screen_handle, (255,0,0), drawable.get_rect(), 3)
		'''

		pygame.display.flip()
		clock.tick(60)

def init():
	pygame.init()
	ctypes.windll.user32.SetProcessDPIAware()
	system_resolution = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
	screen_handle = pygame.display.set_mode(system_resolution, pygame.FULLSCREEN, display=0)
	return screen_handle

#
# Execution starts here.
#
screen_handle = init()
start_round(screen_handle)
