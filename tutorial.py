import os  # Import the OS module for file and directory operations
import random  # Import the random module
import math  # Import the math module
import pygame  # Import the pygame module for game development
from os import listdir  # Import listdir function from os module
from os.path import isfile, join  # Import isfile and join functions from os.path module

pygame.init()  # Initialize all imported pygame modules

pygame.display.set_caption("Platformer")  # Set the window caption
# BG_COLOR = (255, 255, 255)  # Default Background color
WIDTH, HEIGHT = 800, 600  # Default window size
FPS = 60  # Frames per second
PLAYER_VEL = 5  # Player velocity

window = pygame.display.set_mode((WIDTH, HEIGHT))  # Create a window with specified dimensions

def flip(sprites):  # Function to flip sprites horizontally
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):  # Function to load sprite sheets
    path = join("assets", dir1, dir2)  # Construct the path to the sprite sheets
    images = [f for f in listdir(path) if isfile(join(path, f))]  # List all files in the directory
    
    all_sprites = {}  # Dictionary to hold all sprites
    
    for image in images:  # Loop through each image file
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()  # Load the sprite sheet
        
        sprites = []  # List to hold individual sprites
        for i in range(sprite_sheet.get_width() // width):  # Loop through each sprite in the sheet
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)  # Create a surface for the sprite
            rect = pygame.Rect(i * width, 0, width, height)  # Define the rectangle for the sprite
            surface.blit(sprite_sheet, (0, 0), rect)  # Blit the sprite onto the surface
            sprites.append(pygame.transform.scale2x(surface))  # Scale the sprite and add to the list
            
        if direction:  # If direction is True, add sprites for both left and right directions
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:  # Otherwise, add the sprites without direction
            all_sprites[image.replace(".png", "")] = sprites
    
    return all_sprites  # Return the dictionary of sprites

def get_block(size):  # Function to get a block sprite
    path = join("assets", "Terrain", "Terrain.png")  # Construct the path to the terrain image
    image = pygame.image.load(path).convert_alpha()  # Load the terrain image
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)  # Create a surface for the block
    rect = pygame.Rect(96, 0, size, size)  # Define the rectangle for the block
    surface.blit(image, (0, 0), rect)  # Blit the block onto the surface
    return pygame.transform.scale2x(surface)  # Scale the block and return it

class Player(pygame.sprite.Sprite):  # Player class, inheriting from pygame.sprite.Sprite
    COLOR = (255, 0, 0)  # Define the player's color
    GRAVITY = 1  # Define the gravity affecting the player
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)  # Load player sprites
    ANIMATION_DELAY = 3  # Define the delay between animation frames
    
    def __init__(self, x, y, width, height):  # Initialize the player
        self.rect = pygame.Rect(x, y, width, height)  # Define the player's rectangle
        self.x_vel = 0  # Player's horizontal velocity
        self.y_vel = 0  # Player's vertical velocity
        self.mask = None  # Collision mask for the player
        self.direction = "left"  # Initial direction of the player
        self.animation_count = 0  # Animation frame counter
        self.fall_count = 0  # Falling frame counter
        self.jump_count = 0  # Jumping frame counter
        
    def jump(self):  # Function to make the player jump
        self.y_vel = -self.GRAVITY * 8  # Set vertical velocity to negative value
        self.animation_count = 0  # Reset animation counter
        self.jump_count += 1  # Increment jump count
        if self.jump_count == 1:  # If it's the first jump
            self.fall_count = 0  # Reset jump count
        
    
    def move(self, dx, dy):  # Function to move the player
        self.rect.x += dx  # Move horizontally by dx
        self.rect.y += dy  # Move vertically by dy
        
    def move_left(self, vel):  # Function to move the player left
        self.x_vel = -vel  # Set horizontal velocity to negative value
        if self.direction != "left":  # If player is not already facing left
            self.direction = "left"  # Change direction to left
            self.animation_count = 0  # Reset animation counter
            
    def move_right(self, vel):  # Function to move the player right
        self.x_vel = vel  # Set horizontal velocity to positive value
        if self.direction != "right":  # If player is not already facing right
            self.direction = "right"  # Change direction to right
            self.animation_count = 0  # Reset animation counter
    
    def loop(self, fps):  # Function to update the player each frame
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)  # Move the player by current velocities
    
        self.fall_count += 1  # Increment fall count
        self.update_sprite()  # Update the player's sprite
    
    def landed(self):
        self.fall_count = 0  # Reset fall count
        self.y_vel = 0  # Reverse vertical velocity
        self.jump_count = 0  # Reset jump count
        
    def hit_head(self):
        self.count = 0  # Reset hit count
        self.y_vel *= -1  # Reverse vertical velocity
    
    def update_sprite(self):  # Function to update the player's sprite based on movement
        sprite_sheet = "idle"  # Default sprite sheet
        if self.y_vel != 0:  # If player is jumping or falling
            if self.jump_count == 1:  # If it's the first jump
                sprite_sheet = "jump"  # Change to jumping sprite sheet
            elif self.jump_count == 2:  # If it's the second jump
                sprite_sheet = "double_jump"  # Change to double jumping sprite sheet
        elif self.y_vel > self.GRAVITY * 2: # If player is falling
            sprite_sheet = "fall"  # Change to falling sprite sheet
        elif self.x_vel != 0:
            sprite_sheet = "run"  # Change to running sprite sheet
                
        if self.x_vel != 0:  # If player is moving
            sprite_sheet = "run"  # Change to running sprite sheet
            
        sprite_sheet_name = sprite_sheet + "_" + self.direction  # Construct the sprite sheet name
        sprites = self.SPRITES[sprite_sheet_name]  # Get the sprites from the sprite sheet
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)  # Calculate sprite index
        self.sprite = sprites[sprite_index]  # Set the current sprite
        self.animation_count += 1  # Increment animation counter
        self.update()  # Update the player's rectangle and mask
        
    def update(self):  # Function to update the player's rectangle and mask
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))  # Update rectangle position
        self.mask = pygame.mask.from_surface(self.sprite)  # Update collision mask
      
    def draw(self, win, offset_x):  # Function to draw the player on the window
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))  # Draw the player's sprite

class Object(pygame.sprite.Sprite):  # Object class, inheriting from pygame.sprite.Sprite
    def __init__(self, x, y, width, height, name=None):  # Initialize the object
        super().__init__()  # Call the parent class constructor
        self.rect = pygame.Rect(x, y, width, height)  # Define the object's rectangle
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  # Create a surface for the object
        self.width = width  # Set the object's width
        self.height = height  # Set the object's height
        self.name = name  # Set the object's name
        
    def draw(self, win, offset_x):  # Function to draw the object on the window
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))  # Draw the object's image

class Block(Object):  # Block class, inheriting from Object
    def __init__(self, x, y, size):  # Initialize the block
        super().__init__(x, y, size, size)  # Call the parent class constructor
        block = get_block(size)  # Get the block image
        self.image.blit(block, (0, 0))  # Blit the block image onto the surface
        self.mask = pygame.mask.from_surface(self.image)  # Create a collision mask for the block

def get_background(name):  # Function to get the background image
    image = pygame.image.load(join("assets", "Background", name))  # Load the background image
    _, _, width, height = image.get_rect()  # Get the dimensions of the image
    tiles = []  # List to hold the background tiles
    
    for i in range((WIDTH // width) + 1):  # Loop through the width of the window
        for j in range((HEIGHT // height) + 1):  # Loop through the height of the window
            pos = [i * width, j * height]  # Calculate the position of each tile
            tiles.append(pos)  # Add the tile position to the list
            
    return tiles, image  # Return the list of tile positions and the background image

def draw(window, background, bg_image, player, objects, offset_x):  # Function to draw the game elements on the window
    for tile in background:  # Loop through each background tile
        window.blit(bg_image, tile)  # Draw the background tile
    
    for obj in objects:
        obj.draw(window, offset_x)  # Draw each object on the window
    
    player.draw(window, offset_x)  # Draw the player
    
    pygame.display.update()  # Update the display


def handle_vertical_collision(player, objects, dy):  # Function to handle vertical collision
    collided_objects = []  # List to hold the collided objects
    for obj in objects:  # Loop through all objects
        if pygame.sprite.collide_mask(player, obj):  # Check for collision
            if dy > 0:  # If moving down
                player.rect.bottom = obj.rect.top  # Move player to the top of the object
                player.landed()
            if dy < 0:  # If moving up
                player.rect.top = obj.rect.bottom  # Move player to the bottom of the object
                player.hit.head()
        
        collided_objects.append(obj)  # Add the collided object to the list
    
    return collided_objects  # Return the list of collided objects



def handle_move(player, objects):  # Function to handle player movement
    keys = pygame.key.get_pressed()  # Get the current state of all keyboard keys
    
    player.x_vel = 0  # Reset player's horizontal velocity
    if keys[pygame.K_a]:  # If 'A' key is pressed
        player.move_left(PLAYER_VEL)  # Move player left
    if keys[pygame.K_d]:  # If 'D' key is pressed
        player.move_right(PLAYER_VEL)  # Move player right
        
    handle_vertical_collision(player, objects, player.y_vel)  # Handle vertical collision
    


def main(window):  # Main function to run the game
    clock = pygame.time.Clock()  # Create a clock object to manage the frame rate
    background, bg_image = get_background("Pink.png")  # Get the background image and tile positions
    
    block_size = 96  # Set the size of each block
    
    player = Player(100, 100, 50, 50)  # Create a player object
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, WIDTH * 2// block_size)] # Create a floor
    
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size)]
    
    offset_x = 0
    scroll_area_width = 200
    
    run = True  # Set the run flag to True
    while run:  # Main game loop
        clock.tick(FPS)  # Cap the frame rate to FPS
        
        for event in pygame.event.get():  # Loop through all events
            if event.type == pygame.QUIT:  # If the QUIT event is triggered
                run = False  # Set the run flag to False
                break
            
            if event.type == pygame.KEYDOWN:  # If a key is pressed
                if event.key == pygame.K_SPACE and player.jump_count < 2:  # If the space bar is pressed and the player has not reached the maximum jump count
                    player.jump()  # Jump the player
        
        player.loop(FPS)  # Update the player
        handle_move(player, objects)  # Handle player movement
        draw(window, background, bg_image, player, objects, offset_x)  # Draw the game elements on the window
        
        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        
    pygame.quit()  # Quit pygame
    quit()  # Quit the program

if __name__ == "__main__":  # If this script is run directly
    main(window)  # Call the main function
