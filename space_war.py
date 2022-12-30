import ctypes
import pygame
import pygame.locals
import pygame.math
import pygame.joystick

from dark_math import *
from dark_image import *

# set dark_image default transparency
set_color_key((0,0,0))

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

class RotatableImage():
	def __init__(self, image, rotation_offset_degrees):
		self.image = image
		self.rotation_offset_degrees = rotation_offset_degrees

# TODO: In the future, an object should be able to be multiple sprites.
class SpaceObject(Sprite):
	def __init__(self, position, velocity, direction, rotatable_image):
		super().__init__(rotatable_image.image, position)
		self.velocity = velocity
		self.direction = direction
		self.set_rotatable_image(rotatable_image)

		# force various properties to exist
		# NOTE: This has already caused a bug.  Bad idea.
		self.tick()

	def set_rotatable_image(self, rotatable_image):
		self.rotatable_image = rotatable_image

	def accelerate(self, force):
		self.velocity = add2(self.velocity, force)

	def tick(self):
		self.position = add2(self.position, self.velocity)
		self.image = rotate_image_circular(
			self.rotatable_image.image, 
			self.direction + self.rotatable_image.rotation_offset_degrees
		)

class Bullet(SpaceObject):
	def __init__(self, position, velocity, direction, bullet_rot_image):
		self.lifetime_tick_count = 0
		super().__init__(
			position, 
			velocity, 
			direction, 
			bullet_rot_image
		)

	def tick(self):
		self.lifetime_tick_count += 1
		super().tick()

	def get_lifetime_tick_count(self):
		return self.lifetime_tick_count


class Fighter(SpaceObject):
	def __init__(self, position, direction, fighter_rot_image, bullet_rot_image, thrusters_rot_image):
		self.fighter_rot_image = fighter_rot_image
		self.bullet_rot_image = bullet_rot_image
		self.thrusters_rot_image = thrusters_rot_image
		self.rotation_speed = 5
		self.thruster_power = 0.15
		self.show_thrusters = False

		super().__init__(
			position, 
			(0,0), 
			direction, 
			fighter_rot_image
		)

	def fire_bullet(self):
		# TODO: Adjust these
		position = add2(self.position, mul2((20, 20), degrees_to_normal2(self.direction)))
		velocity = add2(self.velocity, mul2((5, 5), degrees_to_normal2(self.direction)))

		bullet = Bullet(
			position, 
			velocity, 
			self.direction, 
			self.bullet_rot_image
		)

		return bullet

	def __fire_thrusters__(self):
		# TODO: Adjust these
		force = mul2(degrees_to_normal2(self.direction), self.thruster_power)
		self.accelerate(force)

	def thrusters_on(self):
		self.show_thrusters = True

	def thrusters_off(self):
		self.show_thrusters = False

	def rotate_clockwise(self):
		self.direction = (self.direction - self.rotation_speed) % 360

	def rotate_anticlockwise(self):
		self.direction = (self.direction + self.rotation_speed) % 360
	
	def tick(self):
		super().tick()
		if self.show_thrusters == True:
			self.__fire_thrusters__()

	def draw(self, surface):
		if self.show_thrusters == True:
			self.set_rotatable_image(self.thrusters_rot_image)
		else:
			self.set_rotatable_image(self.fighter_rot_image)
		super().draw(surface)

'''
class Bullet(SpaceObject):
	def __init__(self, owner, position, velocity, direction, image, image_rotation_offset):
		super().__init__(position, velocity, direction, image, image_rotation_offset)
		self.owner = owner
'''

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
		self.bullet_maximum = 5
		self.alliance_bullets = []
		self.federation_bullets = []

		# About 3 seconds * 60 fps = 180 ticks.
		self.maximum_bullet_lifetime_ticks = 180

		#
		# Create fighters
		#
		fighter_offset = (100,100)

		fighter_position_alliance = fighter_offset
		fighter_direction_alliance = normal_to_degrees2(normal2((+3,+2)))

		self.fighter_alliance = self.__load_fighter_team__(
			'alliance', 
			fighter_position_alliance, 
			fighter_direction_alliance
		)

		fighter_position_federation = sub2(screen.get_size(), mul2((2,2), fighter_offset))
		fighter_direction_federation = normal_to_degrees2(normal2((-3,-2)))

		self.fighter_federation = self.__load_fighter_team__(
			'federation', 
			fighter_position_federation, 
			fighter_direction_federation
		)

		#
		# Create planet
		#
		planet_size = (200,200)
		planet_image = load_image('images/planet.png', planet_size)
		planet_position = sub2(div2(screen.get_size(), 2), div2(planet_size, 2))

		self.planet = Planet(planet_image, planet_position)

	def __load_fighter_team__(self, team_name, fighter_position, fighter_direction):

		fighter_size = (100,100)
		bullet_size = (20,20)
		image_rotation_offset = -90

		fighter_image = RotatableImage(
			load_image(f"images/fighter_{team_name}.png", fighter_size),
			image_rotation_offset
		)

		thrusters_image = RotatableImage(
			load_image(f"images/fighter_{team_name}_thrusters.png", fighter_size),
			image_rotation_offset
		)

		bullet_image = RotatableImage(
			load_image(f"images/bullet_{team_name}.png", bullet_size),
			image_rotation_offset
		)

		return Fighter(
			fighter_position,
			fighter_direction,
			fighter_image, 
			bullet_image,
			thrusters_image
		)

	def __space_objects__(self):
		return [self.fighter_alliance, self.fighter_federation] + self.alliance_bullets + self.federation_bullets

	def collidable(self):
		return self.__space_objects__() + [self.planet]

	def drawable(self):
		return self.__space_objects__() + [self.planet]

	def moveable(self):
		return self.__space_objects__()

	def limited_lifespan(self):
		return self.alliance_bullets + self.federation_bullets

	def add_alliance_bullet(self):
		if len(self.alliance_bullets) >= self.bullet_maximum:
			return
		bullet = self.fighter_alliance.fire_bullet()
		self.alliance_bullets.append(bullet)

	def remove_alliance_bullet(self, bullet):
		if not bullet in self.alliance_bullets:
			return
		self.alliance_bullets.remove(bullet)

	def tick(self):

		for moveable in self.moveable():
			self.planet.assert_gravity_force(moveable)
			# TODO: dangerous - should really make "tickable"
			moveable.tick()

		for limited in self.limited_lifespan():
			if limited.get_lifetime_tick_count() > self.maximum_bullet_lifetime_ticks:
				# we don't know which collection it's in but these methods check that for us.
				self.remove_alliance_bullet(limited)
				#self.remove_federation_bullet(limited)

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
		for drawable in self.drawable():
			drawable.draw(self.screen)

def start_round(screen_handle):
	font = pygame.font.SysFont('arial', 32)
	arena = Arena(screen_handle)
	clock = pygame.time.Clock()

	joysticks = {}
	joystick = None

	alliance_axis_rotate = 0
	alliance_axis_thruster = 0

	while True:
		for event in pygame.event.get():
			if event.type == pygame.locals.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				pygame.quit()
				quit()
			else:

				if event.type == pygame.JOYAXISMOTION:
					joystick = joysticks[event.instance_id]
					alliance_axis_rotate = joystick.get_axis(0)
					alliance_axis_thruster = joystick.get_axis(5)

				if event.type == pygame.JOYBUTTONDOWN:
					if event.button == 0:
						arena.add_alliance_bullet()
						#arena.fighter_alliance.fire_thrusters()
						#joystick = joysticks[event.instance_id]

				if event.type == pygame.JOYBUTTONUP:
					pass

				# Handle hotplugging
				if event.type == pygame.JOYDEVICEADDED:
					# This event will be generated when the program starts for every
					# joystick, filling up the list without needing to create them manually.
					joy = pygame.joystick.Joystick(event.device_index)
					joysticks[joy.get_instance_id()] = joy
					print(f"Joystick {joy.get_instance_id()} connencted")

				if event.type == pygame.JOYDEVICEREMOVED:
					del joysticks[event.instance_id]
					print(f"Joystick {event.instance_id} disconnected")

		#
		# Tick helpers for rotation and thrusters.
		#
		# Basically, axis movement events don't "repeat", they only fire if the axis value changes.
		# So, we remember the last axis value in case there's no event, and then keep firing off
		# tick level methods based on that remembered value, simulating a "repeat" style input.
		#
		if alliance_axis_rotate < -0.1:
			arena.fighter_alliance.rotate_anticlockwise()
		if alliance_axis_rotate > +0.1:
			arena.fighter_alliance.rotate_clockwise()
		if alliance_axis_thruster > +0.1:
			arena.fighter_alliance.thrusters_on()
		else:
			arena.fighter_alliance.thrusters_off()

		arena.tick()
		screen_handle.fill((0,0,0))
		arena.draw()

		'''
		arena.text.clear()
		for directional in [arena.fighter_alliance, arena.fighter_federation]:
			arena.text.append(f"Degrees {directional.direction}")
		'''

		if len(arena.text) > 0:
			text_to_render = '; '.join(arena.text)
			textimage = font.render(text_to_render,True,(255,255,255),(0,0,0))
			screen_handle.blit(textimage, (0,0))
		
		'''
		# debug rectangles
		for drawable in [arena.fighter_alliance, arena.fighter_federation, arena.planet]:
			pygame.draw.rect(screen_handle, (255,0,0), drawable.get_rect(), 3)
		'''
		for directional in [arena.fighter_alliance, arena.fighter_federation]:
			startpoint = directional.get_rect().center
			endpoint = add2(startpoint, mul2(degrees_to_normal2(directional.direction), 100))
			pygame.draw.line(screen_handle, (255,0,0), startpoint, endpoint, 3)

		pygame.display.flip()
		clock.tick(60)

def init():
	pygame.init()
	pygame.joystick.init()
	ctypes.windll.user32.SetProcessDPIAware()
	system_resolution = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
	screen_handle = pygame.display.set_mode(system_resolution, pygame.FULLSCREEN, display=0)
	return screen_handle

#
# Execution starts here.
#
screen_handle = init()
start_round(screen_handle)
