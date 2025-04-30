import carla

# import os
import os

# import pygame & more
import pygame
from pygame.locals import *

import ctypes

# sets window in top left center
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"

# initialize holding variables
r = 0
m = ""
ti = "title"
cX = 0
cY = 0
cZ = 0


# initializing pygame
pygame.font.init()
 
# creates the display surface
display_surface = pygame.display.set_mode((250, 600), pygame.NOFRAME)

# Get the window handle
hwnd = pygame.display.get_wm_info()['window']

def keep_top_window(hwnd):
	# Use ctypes to call the Windows API to set the window as topmost
	ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0003)

def get_Ana(vehicle):
	ti = vehicle.id
	m = vehicle.type_id 
	cX = vehicle.get_location().x
	cY= vehicle.get_location().y
	cZ = vehicle.get_location().z
	spLim = vehicle.get_speed_limit()
	velocity = vehicle.get_velocity()
	r = math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2)


# creates font variables with font file and size
font1 = pygame.font.SysFont('chalkduster.ttf', 40)
font2 = pygame.font.SysFont('freesanbold.ttf', 30)
 
# renders the text displays
title = font1.render(f'{ti}', True, (0, 255, 0))
rmp = font2.render(f'RMP: {r}', True, (0, 255, 0))
model = font2.render(f'Car Model: {m}', True, (0, 255, 0))
location = font2.render(f'Location: {cX}, {cY}, {cZ}', True, (0, 255, 0))
 
# creates text surface objects
tRect = title.get_rect()
mRect = model.get_rect()
rRect = rmp.get_rect()
lRect = location.get_rect()

 
# setting the tilte center
tRect.center = (125, 15)
 
# setting the model midleft
mRect.midleft = (5, 75)

# setting the speed midleft
rRect.midleft = (5, 125)
 
# setting the throttle midleft
lRect.midleft = (5, 175)

while True:
 
    # add background color using RGB values
    display_surface.set_alpha(0)
 
    # copying the text surface objects
    # to the display surface objects
   


    display_surface.blit(title, textRect1)
    display_surface.blit(model, textRect2)
    display_surface.blit(speed, textRect3)
    display_surface.blit(throttle, textRect4) 
    display_surface.blit(location, textRect5)
    display_surface.blit(vStatus, textRect6) 

    # iterate over the list of Event objects
    # that was returned by pygame.event.get()
    # method.
    for event in pygame.event.get():
 
        if event.type == pygame.QUIT:
           
            # deactivating the pygame library
            pygame.quit()
 
            # quitting the program.
            quit()
 
    keep_top_window(hwnd)
    get_Ana(vehicle)
    
    # update the display
    pygame.display.flip()