import pygame
pygame.init()

#effects
coin_sound = pygame.mixer.Sound('../audio/effects/coin.wav')
stomp_sound = pygame.mixer.Sound('../audio/effects/stomp.wav')

jump_sound = pygame.mixer.Sound('../audio/effects/jump.wav')
jump_sound.set_volume(0.5)
hit_sound = pygame.mixer.Sound('../audio/effects/hit.wav')

#bg music
level_music = pygame.mixer.Sound('../audio/level_music.wav')
overworld_music = pygame.mixer.Sound('../audio/overworld_music.wav')