import pygame

class UI:
    def __init__(self, surface):
        #setup
        self.display_surface = surface

        #health
        self.health_bar = pygame.image.load('../graphics/ui/health_bar.png').convert_alpha()
        self.health_bar_topleft = (54,39)
        self.bar_max_width = 152
        self.bar_height = 4
        
        #coins
        self.coin = pygame.image.load('../graphics/ui/coin.png').convert_alpha()
        self.coin_rect = self.coin.get_rect(topleft = (50,61))
        self.font = pygame.font.Font('../graphics/ui/ARCADEPI.ttf', 30)
    
    def display_health(self, current, max):
        self.display_surface.blit(self.health_bar, (20,10))
        bar_width = (current / max) * self.bar_max_width
        health_bar_rect = pygame.Rect((self.health_bar_topleft), (bar_width, self.bar_height))
        pygame.draw.rect(self.display_surface, '#dc4949', health_bar_rect)

    def display_coins(self, amount):
        coin_amount_surf = self.font.render(str(amount), False, '#33323d')
        coin_amount_rect = coin_amount_surf.get_rect(midleft = (self.coin_rect.right + 4, self.coin_rect.centery))
        self.display_surface.blit(self.coin, self.coin_rect)
        self.display_surface.blit(coin_amount_surf, coin_amount_rect)