import pygame
import math
import numpy as np
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SKY_COLOR = (173, 216, 230)
PLANE_COLOR = (50, 50, 50)
GRASS_COLOR = (34, 139, 34)
TREE_COLOR = (0, 100, 0)
DENSE_TREE_COLOR = (0, 75, 0)
WATER_COLOR = (0, 105, 148)
RIVER_COLOR = (30, 144, 255)
RUNWAY_COLOR = (169, 169, 169)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Top-Down Plane Simulator")
clock = pygame.time.Clock()

class TerrainFeature:
    def __init__(self, x, y, feature_type):
        self.x = x
        self.y = y
        self.type = feature_type
        if feature_type == 'tree':
            self.size = random.randint(8, 15)
        elif feature_type == 'dense_tree':
            self.size = random.randint(10, 18)
        elif feature_type == 'water':
            self.size = random.randint(50, 150)
        elif feature_type == 'river':
            self.width = random.randint(20, 30)
            self.points = [(x, y)]
            # Generate river path
            current_x, current_y = x, y
            for _ in range(random.randint(5, 10)):
                angle = random.uniform(0, 2 * math.pi)
                length = random.randint(100, 200)
                current_x += math.cos(angle) * length
                current_y += math.sin(angle) * length
                self.points.append((current_x, current_y))

    def draw(self, surface, offset_x, offset_y):
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        
        if -50 <= screen_x <= SCREEN_WIDTH + 50 and \
           -50 <= screen_y <= SCREEN_HEIGHT + 50:
            
            if self.type == 'tree':
                pygame.draw.circle(surface, TREE_COLOR, 
                                (int(screen_x), int(screen_y)), self.size)
            elif self.type == 'dense_tree':
                pygame.draw.circle(surface, DENSE_TREE_COLOR, 
                                (int(screen_x), int(screen_y)), self.size)
            elif self.type == 'water':
                pygame.draw.ellipse(surface, WATER_COLOR,
                                 (int(screen_x - self.size/2), 
                                  int(screen_y - self.size/2),
                                  self.size, self.size))
            elif self.type == 'river':
                # Draw river as a series of connected segments
                points = [(x - offset_x, y - offset_y) for x, y in self.points]
                if len(points) > 1:
                    pygame.draw.lines(surface, RIVER_COLOR, False, points, self.width)

class ForestCluster:
    def __init__(self, center_x, center_y, radius, density):
        self.trees = []
        for _ in range(density):
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, radius)
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            self.trees.append(TerrainFeature(x, y, 'dense_tree'))

    def draw(self, surface, offset_x, offset_y):
        for tree in self.trees:
            tree.draw(surface, offset_x, offset_y)

class Environment:
    def __init__(self):
        self.features = []
        self.forest_clusters = []
        self.world_width = SCREEN_WIDTH * 4
        self.world_height = SCREEN_HEIGHT * 4
        
        # Generate rivers (before other features to avoid overlap)
        for _ in range(3):
            x = random.randint(0, self.world_width)
            y = random.randint(0, self.world_height)
            self.features.append(TerrainFeature(x, y, 'river'))
        
        # Generate dense forest clusters
        for _ in range(5):
            x = random.randint(0, self.world_width)
            y = random.randint(0, self.world_height)
            cluster = ForestCluster(x, y, 100, 30)  # radius 100, 30 trees per cluster
            self.forest_clusters.append(cluster)
        
        # Generate scattered trees
        for _ in range(100):
            x = random.randint(0, self.world_width)
            y = random.randint(0, self.world_height)
            self.features.append(TerrainFeature(x, y, 'tree'))
        
        # Generate water bodies
        for _ in range(10):
            x = random.randint(0, self.world_width)
            y = random.randint(0, self.world_height)
            self.features.append(TerrainFeature(x, y, 'water'))
        
        # Create runway
        self.runway_width = 60
        self.runway_length = 400
        self.runway_x = self.world_width // 2
        self.runway_y = self.world_height // 2
    
    def draw(self, surface, offset_x, offset_y):
        # Draw base grass
        surface.fill(GRASS_COLOR)
        
        # Draw runway
        runway_screen_x = self.runway_x - offset_x - self.runway_width // 2
        runway_screen_y = self.runway_y - offset_y - self.runway_length // 2
        pygame.draw.rect(surface, RUNWAY_COLOR, 
                        (runway_screen_x, runway_screen_y,
                         self.runway_width, self.runway_length))
        
        # Draw rivers first (so they appear under other features)
        for feature in self.features:
            if feature.type == 'river':
                feature.draw(surface, offset_x, offset_y)
        
        # Draw other terrain features
        for feature in self.features:
            if feature.type != 'river':
                feature.draw(surface, offset_x, offset_y)
        
        # Draw forest clusters
        for cluster in self.forest_clusters:
            cluster.draw(surface, offset_x, offset_y)

class Plane:
    def __init__(self):
        # Keep plane position fixed at center of screen
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.world_x = 0  # actual position in world coordinates
        self.world_y = 0
        self.angle = 0  # degrees
        self.speed = 5
        self.size = 20
        
    def move(self):
        # Convert angle to radians for math calculations
        rad = math.radians(self.angle)
        
        # Update world position based on angle and speed
        self.world_x += math.cos(rad) * self.speed
        self.world_y -= math.sin(rad) * self.speed
    
    def draw(self, surface):
        # Draw plane as triangle from top-down view
        nose_angle = math.radians(self.angle)
        wing_angle = math.radians(40)  # angle between wings and nose
        
        # Calculate points for isosceles triangle
        nose = (self.x + self.size * math.cos(nose_angle),
                self.y - self.size * math.sin(nose_angle))
        left_wing = (self.x + self.size * math.cos(nose_angle + math.pi + wing_angle),
                    self.y - self.size * math.sin(nose_angle + math.pi + wing_angle))
        right_wing = (self.x + self.size * math.cos(nose_angle + math.pi - wing_angle),
                     self.y - self.size * math.sin(nose_angle + math.pi - wing_angle))
        
        pygame.draw.polygon(surface, PLANE_COLOR, [nose, left_wing, right_wing])
        
        # Draw a small circle in the center of the plane
        pygame.draw.circle(surface, (200, 0, 0), (int(self.x), int(self.y)), 3)

def main():
    plane = Plane()
    environment = Environment()
    running = True
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            plane.angle += 3
        if keys[pygame.K_RIGHT]:
            plane.angle -= 3
        if keys[pygame.K_UP]:
            plane.speed = min(10, plane.speed + 0.1)
        if keys[pygame.K_DOWN]:
            plane.speed = max(1, plane.speed - 0.1)
        
        # Update
        plane.move()
        
        # Calculate camera offset (world coordinates relative to screen)
        offset_x = plane.world_x - SCREEN_WIDTH // 2
        offset_y = plane.world_y - SCREEN_HEIGHT // 2
        
        # Draw
        environment.draw(screen, offset_x, offset_y)
        plane.draw(screen)
        
        # Draw speed indicator
        speed_text = f"Speed: {plane.speed:.1f}"
        font = pygame.font.Font(None, 36)
        text_surface = font.render(speed_text, True, (0, 0, 0))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
