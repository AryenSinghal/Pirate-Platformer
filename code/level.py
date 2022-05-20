import pygame
from particles import ParticleEffect
from player import Player
from settings import *
from support import *
from tiles import *
from enemy import *
from decorations import *
from game_data import levels
from sounds import *

class Level:
    def __init__(self, current_level, surface, game):
        self.display_surface = surface
        self.world_shift = 0
        self.game = game

        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)
        self.dust = pygame.sprite.GroupSingle()
        self.player_landing_check = False

        self.explosion_sprites = pygame.sprite.Group()

        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        crates_layout = import_csv_layout(level_data['crates'])
        self.crates_sprites = self.create_tile_group(crates_layout, 'crates')

        coins_layout = import_csv_layout(level_data['coins'])
        self.coins_sprites = self.create_tile_group(coins_layout, 'coins')

        fg_palms_layout = import_csv_layout(level_data['fg palms'])
        self.fg_palms_sprites = self.create_tile_group(fg_palms_layout, 'fg palms')

        bg_palms_layout = import_csv_layout(level_data['bg palms'])
        self.bg_palms_sprites = self.create_tile_group(bg_palms_layout, 'bg palms')

        enemies_layout = import_csv_layout(level_data['enemies'])
        self.enemies_sprites = self.create_tile_group(enemies_layout, 'enemies')

        constraints_layout = import_csv_layout(level_data['constraints'])
        self.constraints_sprites = self.create_tile_group(constraints_layout, 'constraints')

        self.sky = Sky(8)
        level_width = len(terrain_layout[0])*tile_size
        self.water = Water(HEIGHT-30, level_width)
        self.clouds = Clouds(400, level_width, 20)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_ind, row in enumerate(layout):
            for col_ind, val in enumerate(row):
                if val != '-1':
                    x = col_ind * tile_size
                    y = row_ind * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('../graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    elif type == 'grass':
                        grass_tile_list = import_cut_graphics('../graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    elif type == 'crates':
                        sprite = Crate(tile_size, x, y)
                    elif type == 'coins':
                        if val == '0': sprite = Coin(tile_size, x, y, '../graphics/coins/gold', 5)
                        else: sprite = Coin(tile_size, x, y, '../graphics/coins/silver', 1)
                    elif type == 'fg palms':
                        if val == '4': sprite = Palm(tile_size, x, y, '../graphics/terrain/palm_small', 38)
                        else: sprite = Palm(tile_size, x, y, '../graphics/terrain/palm_large', 64)
                    elif type == 'bg palms':
                        sprite = Palm(tile_size, x, y, '../graphics/terrain/palm_bg', 64)
                    elif type == 'enemies':
                        sprite = Enemy(tile_size, x, y)
                    elif type == 'constraints':
                        sprite = Tile(tile_size, x, y)
                    
                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout):
        for row_ind, row in enumerate(layout):
            for col_ind, val in enumerate(row):
                x = col_ind * tile_size
                y = row_ind * tile_size
                if val == '0':
                    sprite = Player((x,y), self.display_surface, self.jump_particles)
                    self.player.add(sprite)
                elif val == '1':
                    hat_surf = pygame.image.load('../graphics/character/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, hat_surf)
                    self.goal.add(sprite)

    def jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,5)
        else:
            pos += pygame.math.Vector2(10,-5)
        self.dust.add(ParticleEffect(pos, 'jump'))

    def land_particles(self):
        if not self.player_landing_check and self.player.sprite.on_ground and not self.dust.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10,15)
            else:
                offset = pygame.math.Vector2(-10,15)
            self.dust.add(ParticleEffect(self.player.sprite.rect.midbottom-offset, 'land'))

    def player_horizontal(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed

        collideable_sprites = self.terrain_sprites.sprites() + self.crates_sprites.sprites() + self.fg_palms_sprites.sprites()
        for tile in collideable_sprites:
            if tile.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = tile.rect.right
                    player.on_left = True
                elif player.direction.x > 0:
                    player.collision_rect.right = tile.rect.left
                    player.on_right = True
        
        if player.on_left and player.direction.x > 0:
            player.on_left = False
        if player.on_right and player.direction.x < 0:
            player.on_right = False
    
    def player_vertical(self):
        player = self.player.sprite
        player.apply_gravity()

        collideable_sprites = self.terrain_sprites.sprites() + self.crates_sprites.sprites() + self.fg_palms_sprites.sprites()
        for tile in collideable_sprites:
            if tile.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = tile.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.collision_rect.top = tile.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
        
        if player.on_ground and (player.direction.y < 0 or player.direction.y > 1):
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 1:
            player.on_ceiling = False

    def enemy_constraint_collision(self):
        for enemy in self.enemies_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraints_sprites, False):
                enemy.reverse_speed()

    def world_scroll(self):
        player_x = self.player.sprite.rect.centerx
        player_direction = self.player.sprite.direction.x

        if player_x < (WIDTH/4) and player_direction < 0:
            self.world_shift = 8
            self.player.sprite.speed = 0
        elif player_x > (WIDTH*3/4) and player_direction > 0:
            self.world_shift = -8
            self.player.sprite.speed = 0
        else:
            self.world_shift = 0
            self.player.sprite.speed = 8

    def check_death(self):
        if self.player.sprite.rect.top > HEIGHT:
            self.game.create_overworld(self.current_level, self.current_level)
    
    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.game.create_overworld(self.current_level, self.new_max_level)

    def check_coin_collisions(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coins_sprites, True)
        if collided_coins:
            for coin in collided_coins:
                self.game.coins += coin.value
                coin_sound.play()

    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemies_sprites, False)
        player = self.player.sprite
        for enemy in enemy_collisions:
            enemy_center = enemy.rect.centery
            enemy_top = enemy.rect.top
            player_bottom = self.player.sprite.rect.bottom
            if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                self.player.sprite.direction.y = -15
                explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion')
                self.explosion_sprites.add(explosion_sprite)
                enemy.kill()
                stomp_sound.play()
            else:
                if not player.invincible:
                    self.game.current_health -= 10
                    player.invincible = True
                    player.hurt_time = pygame.time.get_ticks()
                    hit_sound.play()

    def run(self):
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        self.bg_palms_sprites.update(self.world_shift)
        self.bg_palms_sprites.draw(self.display_surface)

        self.dust.update(self.world_shift)
        self.dust.draw(self.display_surface)

        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        self.constraints_sprites.update(self.world_shift)
        self.enemies_sprites.update(self.world_shift)
        self.enemy_constraint_collision()
        self.enemies_sprites.draw(self.display_surface)
        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)

        self.crates_sprites.update(self.world_shift)
        self.crates_sprites.draw(self.display_surface)

        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)

        self.coins_sprites.update(self.world_shift)
        self.coins_sprites.draw(self.display_surface)

        self.fg_palms_sprites.update(self.world_shift)
        self.fg_palms_sprites.draw(self.display_surface)

        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        
        self.player.update()
        self.player_horizontal()
        self.player_landing_check = self.player.sprite.on_ground
        self.player_vertical()
        self.land_particles()
        self.player.draw(self.display_surface)

        self.water.draw(self.display_surface, self.world_shift)

        self.world_scroll()

        self.check_death()
        self.check_win()
        
        self.check_coin_collisions()
        self.check_enemy_collisions()