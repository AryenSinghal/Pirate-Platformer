import pygame
from support import import_folder
from math import sin
from sounds import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, jump_particles):
        super().__init__()
        self.initialise_animations()
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        self.import_dust_run_particles()
        self.dust_frame_index = 0
        self.dust_animation_speed = 0.15
        self.screen = surface
        
        self.direction = pygame.math.Vector2(0,0)
        self.speed = 8
        self.gravity = 0.8
        self.jump_speed = -16
        self.collision_rect = pygame.Rect(self.rect.topleft, (50, self.rect.height))

        self.state = 'idle'
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_right = False
        self.on_left = False

        self.jump_particles = jump_particles

        self.invincible = False
        self.invincibility_duration = 600
        self.hurt_time = 0

    def initialise_animations(self):
        self.animations = {'idle':[], 'run': [], 'jump':[], 'fall':[]}
        self.frame_index = 0
        self.animation_speed = 0.15
        character_path = '../graphics/character'
        for state in self.animations:
            self.animations[state] = import_folder(character_path + '/' + state)
    
    def import_dust_run_particles(self):
        self.dust_run_particles = import_folder('../graphics/character/dust_particles/run')

    def animate(self):
        self.get_status()
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0
        
        image = self.animations[self.state][int(self.frame_index)]
        if self.facing_right:
            self.image = image
            self.rect.bottomleft = self.collision_rect.bottomleft
        else:
            self.image = pygame.transform.flip(image, True, False)
            self.rect.bottomright = self.collision_rect.bottomright
        
        if self.invincible:
            wave_value = sin(pygame.time.get_ticks())
            alpha_value = 255 if wave_value >= 0 else 0
            self.image.set_alpha(alpha_value)
        else:
            self.image.set_alpha(255)
        
        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
        
    def dust_run_animation(self):
        if self.state == 'run':
            self.dust_frame_index += self.dust_animation_speed
            if self.dust_frame_index >= len(self.dust_run_particles):
                self.dust_frame_index = 0
            
            dust_particle = self.dust_run_particles[int(self.dust_frame_index)]
            if self.facing_right:
                pos = self.rect.bottomleft - pygame.math.Vector2(6,10)
                self.screen.blit(dust_particle, pos)
            else:
                pos = self.rect.bottomright - pygame.math.Vector2(6,10)
                self.screen.blit(pygame.transform.flip(dust_particle, True, False), pos)

    def get_input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False
        else:
            self.direction.x = 0
        
        if keys[pygame.K_SPACE] and self.on_ground:
            self.direction.y = self.jump_speed
            self.jump_particles(self.rect.midbottom)
            jump_sound.play()
    
    def get_status(self):
        if self.direction.y < 0:
            self.state = 'jump'
        elif self.direction.y > 1:
            self.state = 'fall'
        else:
            if self.direction.x != 0:
                self.state = 'run'
            else:
                self.state = 'idle'

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.collision_rect.y += self.direction.y
    
    def invincibility_timer(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.invincible = False

    def update(self):
        self.get_input()
        self.animate()
        self.dust_run_animation()
        self.invincibility_timer()