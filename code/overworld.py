import pygame
from decorations import Sky
from game_data import levels
from support import *

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, status, marker_speed, path):
        super().__init__()
        self.frames = import_folder(path)
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.frames[self.frame_index]
        self.status = status
        self.rect = self.image.get_rect(center = pos)

        self.detection_zone = pygame.Rect(self.rect.centerx-(marker_speed/2), self.rect.centery-(marker_speed/2), marker_speed, marker_speed)
    
    def animate(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
    
    def update(self):
        if self.status == 'unlocked':
            self.animate()
        else:
            tint_surf = self.image.copy()
            tint_surf.fill('black', None, pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surf, (0,0))

class Marker(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load('../graphics/overworld/hat.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.pos = pos
    
    def update(self):
        self.rect.center = self.pos

class Overworld:
    def __init__(self, start_level, max_level, surface, create_level):
        #setup
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.create_level = create_level

        #movement logic
        self.move_direction = pygame.math.Vector2(0,0)
        self.speed = 8
        self.moving = False

        #sprites
        self.setup_nodes()
        self.setup_marker()
        self.sky = Sky(8, 'overworld')

        #timer
        self.start_time = pygame.time.get_ticks()
        self.allow_input = False
        self.timer_duration = 300
    
    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()
        for index, node_data in enumerate(levels.values()):
            if index <= self.max_level:
                node_sprite = Node(node_data['node_pos'], 'unlocked', self.speed, node_data['node_graphics'])
            else:
                node_sprite = Node(node_data['node_pos'], 'locked', self.speed, node_data['node_graphics'])
            self.nodes.add(node_sprite)
    
    def draw_paths(self):
        if self.max_level:
            points = [x['node_pos'] for i, x in enumerate(levels.values()) if i <= self.max_level]
            pygame.draw.lines(self.display_surface, '#a04f45', False, points, 6)
    
    def setup_marker(self):
        self.marker = pygame.sprite.GroupSingle()
        marker_sprite = Marker(self.nodes.sprites()[self.current_level].rect.center)
        self.marker.add(marker_sprite)

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.moving and self.allow_input:
            if keys[pygame.K_RIGHT] and self.current_level < self.max_level:
                self.move_direction = self.get_movement_data(1)
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_LEFT] and self.current_level > 0:
                self.move_direction = self.get_movement_data(-1)
                self.current_level -= 1
                self.moving = True
            elif keys[pygame.K_SPACE]:
                self.create_level(self.current_level)
    
    def get_movement_data(self, step):
        start = pygame.math.Vector2(self.nodes.sprites()[self.current_level].rect.center)
        end = pygame.math.Vector2(self.nodes.sprites()[self.current_level + step].rect.center)
        return (end - start).normalize()

    def update_marker_pos(self):
        if self.moving:
            self.marker.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.detection_zone.collidepoint(self.marker.sprite.pos):
                self.move_direction = pygame.math.Vector2(0,0)
                self.moving = False

    def input_timer(self):
        if not self.allow_input:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.timer_duration:
                self.allow_input = True

    def run(self):
        self.input()
        self.update_marker_pos()
        self.marker.update()
        self.nodes.update()
        
        self.sky.draw(self.display_surface)
        self.draw_paths()
        self.nodes.draw(self.display_surface)
        self.marker.draw(self.display_surface)

        self.input_timer()