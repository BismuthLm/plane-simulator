#!/usr/bin/env python3

import os
os.environ['SDL_VIDEODRIVER'] = 'cocoa'  # Ensure proper video driver for macOS

import pygame
import math
import numpy as np
import random
import noise  # For improved terrain generation
import colorsys

# Initialize Pygame
pygame.init()

# Get the screen info
screen_info = pygame.display.Info()
DESKTOP_WIDTH = screen_info.current_w
DESKTOP_HEIGHT = screen_info.current_h

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 16  # Size of each tile in pixels
CHUNK_SIZE = 32  # Size of each chunk in tiles

# Colors (pixel art palette)
COLORS = {
    'sky': (140, 188, 255),
    'plane': (45, 45, 45),
    'grass': [(34, 139, 34), (40, 160, 40), (45, 180, 45)],  # Multiple shades for variation
    'tree': [(0, 100, 0), (0, 90, 0), (0, 80, 0)],
    'dense_tree': [(0, 75, 0), (0, 65, 0), (0, 55, 0)],
    'water': [(30, 144, 255), (25, 130, 230), (20, 120, 210)],
    'beach': [(238, 214, 175), (230, 206, 168), (222, 198, 160)],
    'runway': [(169, 169, 169), (160, 160, 160), (150, 150, 150)]
}

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Top-Down Plane Simulator")
clock = pygame.time.Clock()

# Fullscreen state
is_fullscreen = False

class TerrainChunk:
    def __init__(self, chunk_x, chunk_y):
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.tiles = {}  # Dictionary to store tile types
        self.features = []  # List to store special features
        self.generate()
    
    def generate(self):
        # Use noise to generate base terrain
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                world_x = self.chunk_x * CHUNK_SIZE + x
                world_y = self.chunk_y * CHUNK_SIZE + y
                
                # Generate different noise layers
                elevation = noise.pnoise2(world_x * 0.05, world_y * 0.05, octaves=6, persistence=0.5)
                moisture = noise.pnoise2(world_x * 0.03, world_y * 0.03, octaves=4, persistence=0.5)
                forest = noise.pnoise2(world_x * 0.08, world_y * 0.08, octaves=3, persistence=0.7)
                
                # Determine tile type based on noise values
                if elevation < -0.2:  # Water
                    self.tiles[(x, y)] = 'water'
                    # Add beach tiles around water
                    if elevation > -0.25:
                        self.tiles[(x, y)] = 'beach'
                else:
                    if forest > 0.2:
                        if forest > 0.4:
                            self.tiles[(x, y)] = 'dense_tree'
                        else:
                            self.tiles[(x, y)] = 'tree'
                    else:
                        self.tiles[(x, y)] = 'grass'
        
        # Generate rivers
        if random.random() < 0.3:  # 30% chance for a chunk to have a river
            self.generate_river()
    
    def generate_river(self):
        # Start river at a random edge
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge in ['top', 'bottom']:
            x = random.randint(0, CHUNK_SIZE - 1)
            y = 0 if edge == 'top' else CHUNK_SIZE - 1
        else:
            x = 0 if edge == 'left' else CHUNK_SIZE - 1
            y = random.randint(0, CHUNK_SIZE - 1)
        
        river_points = [(x, y)]
        current_x, current_y = x, y
        
        # Generate meandering river path
        for _ in range(CHUNK_SIZE):
            # Determine next direction with momentum
            if len(river_points) > 1:
                dx = current_x - river_points[-2][0]
                dy = current_y - river_points[-2][1]
            else:
                dx = dy = 0
            
            # Weighted random direction based on previous direction
            possible_dirs = []
            weights = []
            
            for new_dx, new_dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x = current_x + new_dx
                new_y = current_y + new_dy
                
                if 0 <= new_x < CHUNK_SIZE and 0 <= new_y < CHUNK_SIZE:
                    possible_dirs.append((new_dx, new_dy))
                    # Higher weight for continuing in same direction
                    weight = 3.0 if (new_dx == dx and new_dy == dy) else 1.0
                    weights.append(weight)
            
            if not possible_dirs:
                break
                
            # Normalize weights
            total = sum(weights)
            weights = [w/total for w in weights]
            
            # Choose direction
            direction = random.choices(possible_dirs, weights=weights)[0]
            current_x += direction[0]
            current_y += direction[1]
            
            river_points.append((current_x, current_y))
            
            # Add river tiles
            for px, py in river_points:
                self.tiles[(px, py)] = 'water'
                # Add beach tiles around river
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    beach_x, beach_y = px + dx, py + dy
                    if (beach_x, beach_y) in self.tiles and self.tiles[(beach_x, beach_y)] == 'grass':
                        self.tiles[(beach_x, beach_y)] = 'beach'

class Environment:
    def __init__(self):
        self.chunks = {}  # Dictionary to store loaded chunks
        self.runway_pos = (0, 0)  # World coordinates of runway
        self.generate_runway()
    
    def generate_runway(self):
        # Place runway in starting chunk
        chunk = self.get_chunk(0, 0)
        runway_width = 4
        runway_length = 20
        start_x = CHUNK_SIZE // 2 - runway_width // 2
        start_y = CHUNK_SIZE // 2 - runway_length // 2
        
        for x in range(start_x, start_x + runway_width):
            for y in range(start_y, start_y + runway_length):
                chunk.tiles[(x, y)] = 'runway'
    
    def get_chunk(self, chunk_x, chunk_y):
        chunk_key = (chunk_x, chunk_y)
        if chunk_key not in self.chunks:
            self.chunks[chunk_key] = TerrainChunk(chunk_x, chunk_y)
        return self.chunks[chunk_key]
    
    def get_tile(self, world_x, world_y):
        chunk_x = world_x // CHUNK_SIZE
        chunk_y = world_y // CHUNK_SIZE
        tile_x = world_x % CHUNK_SIZE
        tile_y = world_y % CHUNK_SIZE
        chunk = self.get_chunk(chunk_x, chunk_y)
        return chunk.tiles.get((tile_x, tile_y), 'grass')
    
    def draw(self, surface, camera_x, camera_y):
        # Calculate visible chunks
        start_chunk_x = int(camera_x // (CHUNK_SIZE * TILE_SIZE)) - 1
        start_chunk_y = int(camera_y // (CHUNK_SIZE * TILE_SIZE)) - 1
        end_chunk_x = start_chunk_x + (surface.get_width() // (CHUNK_SIZE * TILE_SIZE)) + 3
        end_chunk_y = start_chunk_y + (surface.get_height() // (CHUNK_SIZE * TILE_SIZE)) + 3
        
        # Draw visible chunks
        for chunk_x in range(start_chunk_x, end_chunk_x):
            for chunk_y in range(start_chunk_y, end_chunk_y):
                chunk = self.get_chunk(chunk_x, chunk_y)
                chunk_screen_x = chunk_x * CHUNK_SIZE * TILE_SIZE - camera_x
                chunk_screen_y = chunk_y * CHUNK_SIZE * TILE_SIZE - camera_y
                
                # Draw tiles
                for (tile_x, tile_y), tile_type in chunk.tiles.items():
                    screen_x = chunk_screen_x + tile_x * TILE_SIZE
                    screen_y = chunk_screen_y + tile_y * TILE_SIZE
                    
                    if -TILE_SIZE <= screen_x <= surface.get_width() and -TILE_SIZE <= screen_y <= surface.get_height():
                        color = random.choice(COLORS[tile_type])
                        pygame.draw.rect(surface, color, 
                                      (screen_x, screen_y, TILE_SIZE, TILE_SIZE))

class Plane:
    def __init__(self):
        self.world_x = 0
        self.world_y = 0
        self.angle = 0  # degrees
        self.speed = 5
        self.size = int(TILE_SIZE * 1.5)
    
    def move(self):
        # Convert angle to radians for math calculations
        rad = math.radians(self.angle)
        
        # Update world position based on angle and speed
        self.world_x += math.cos(rad) * self.speed
        self.world_y -= math.sin(rad) * self.speed
    
    def draw(self, surface, camera_x, camera_y):
        # Calculate screen position
        screen_x = surface.get_width() // 2
        screen_y = surface.get_height() // 2
        
        # Draw plane as pixel art style triangle
        nose_angle = math.radians(self.angle)
        wing_angle = math.radians(40)
        
        # Calculate points for isosceles triangle
        nose = (screen_x + self.size * math.cos(nose_angle),
               screen_y - self.size * math.sin(nose_angle))
        left_wing = (screen_x + self.size * math.cos(nose_angle + math.pi + wing_angle),
                    screen_y - self.size * math.sin(nose_angle + math.pi + wing_angle))
        right_wing = (screen_x + self.size * math.cos(nose_angle + math.pi - wing_angle),
                     screen_y - self.size * math.sin(nose_angle + math.pi - wing_angle))
        
        points = [nose, left_wing, right_wing]
        points = [(int(x), int(y)) for x, y in points]  # Ensure integer coordinates
        
        pygame.draw.polygon(surface, COLORS['plane'], points)
        # Draw a small circle in the center of the plane
        pygame.draw.circle(surface, (200, 0, 0), (screen_x, screen_y), 2)

def toggle_fullscreen():
    global screen, is_fullscreen, SCREEN_WIDTH, SCREEN_HEIGHT
    is_fullscreen = not is_fullscreen
    if is_fullscreen:
        # Store current window size before going fullscreen
        if not pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
            SCREEN_WIDTH = pygame.display.get_surface().get_width()
            SCREEN_HEIGHT = pygame.display.get_surface().get_height()
        screen = pygame.display.set_mode((DESKTOP_WIDTH, DESKTOP_HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

def handle_resize(event):
    global SCREEN_WIDTH, SCREEN_HEIGHT
    if not is_fullscreen:
        SCREEN_WIDTH = event.w
        SCREEN_HEIGHT = event.h

def main():
    plane = Plane()
    environment = Environment()
    running = True
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:  # F11 to toggle fullscreen
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE and is_fullscreen:  # ESC to exit fullscreen
                    toggle_fullscreen()
            elif event.type == pygame.VIDEORESIZE and not is_fullscreen:
                handle_resize(event)
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            plane.angle += 3
        if keys[pygame.K_RIGHT]:
            plane.angle -= 3
        if keys[pygame.K_UP]:
            plane.speed = min(plane.speed + 0.2, 20)
        if keys[pygame.K_DOWN]:
            plane.speed = max(plane.speed - 0.2, 1)
        
        # Update plane position
        plane.move()
        
        # Clear screen with sky color
        screen.fill(COLORS['sky'])
        
        # Draw environment (centered on plane)
        environment.draw(screen, plane.world_x - screen.get_width()//2, 
                        plane.world_y - screen.get_height()//2)
        
        # Draw plane (centered on screen)
        plane.draw(screen, plane.world_x, plane.world_y)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
