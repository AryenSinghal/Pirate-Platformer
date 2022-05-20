import pygame, sys
from settings import *
from level import Level
from overworld import Overworld
from ui import UI
from sounds import *

class Game:
    def __init__(self):
        #game attributes
        self.max_level = 0
        self.max_health = 100
        self.current_health = 100
        self.coins = 0

        #overworld creation
        self.overworld = Overworld(0, self.max_level, screen, self.create_level)
        self.state = 'overworld'
        overworld_music.play(loops = -1)

        #UI
        self.ui = UI(screen)
    
    def create_level(self, current_level):
        self.level = Level(current_level, screen, game)
        self.state = 'level'
        overworld_music.stop()
        level_music.play(loops = -1)
    
    def create_overworld(self, current_level, max_level):
        if max_level > self.max_level: self.max_level = max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
        self.state = 'overworld'
        level_music.stop()
        overworld_music.play(loops = -1)
    
    def check_game_over(self):
        if self.current_health <= 0:
            level_music.stop()
            self.__init__()

    def run(self):
        if self.state == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.ui.display_health(self.current_health, self.max_health)
            self.ui.display_coins(self.coins)
            self.check_game_over()


pygame.init()
pygame.display.set_caption('Pirate Platformer')
pygame.display.set_icon(pygame.image.load('../graphics/character/hat.png'))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    game.run()

    pygame.display.update()
    clock.tick(60)