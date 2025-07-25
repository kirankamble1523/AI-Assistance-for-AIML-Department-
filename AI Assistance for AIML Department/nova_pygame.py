import pygame
import sys

# Initialize pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Pygame Window")

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Exit the loop if the window is closed

    # Update the screen (fill with a color)
    screen.fill((0, 0, 255))  # Blue background

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()
