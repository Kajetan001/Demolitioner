import pygame
import random
import math
import pickle

PPB = 20 #pixels per block
white = (220,220,220)
gray = (140,140,140)

def negate(bool):
    if bool: return False
    else: return True

class Button():
    def __init__(self, screen, texture, position, function, picture = None):
        self.screen = screen
        self.fun = function
        self.texture = texture
        self.picture = picture
        self.rect = texture[0].get_rect(topleft = position)
        self.click = False
        self.clickable = True

    def isHovered(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            return True
        else:
            return False
        
    def getPosition(self):
        return self.rect.topleft
    
    def setPicture(self, picture):
        self.picture = picture

    def makeClickable(self):
        self.clickable = negate(self.clickable)
    
    def render(self, mouse_pos, mouse, argument = None, is_on = True):
        product = None
        if self.rect.collidepoint(mouse_pos) and self.clickable:
            self.screen.blit(self.texture[1], self.rect) if is_on else self.screen.blit(self.texture[3], self.rect)
            product = self.press(mouse, argument)
        else:
            self.screen.blit(self.texture[0], self.rect) if is_on else self.screen.blit(self.texture[2], self.rect)
        if self.picture: self.screen.blit(self.picture, (self.rect.left + self.texture[0].get_width()/2 - self.picture.get_width()/2, self.rect.top + self.texture[0].get_height()/2 - self.picture.get_height()/2 ))

        return product

    def press(self, mouse, argument):
        if mouse[0]:
            self.click = True

        elif self.click:
            self.click = False
            return self.fun() if argument == None else self.fun(argument)

class Environment():
    def __init__(self, screen, blank = False):
        self.screen = screen
        self.grid_size = (int(self.screen.get_width() / PPB), int(self.screen.get_height() / PPB))
        self.grid = []
        self.start_point = (0, self.screen.get_height())
        self.exp_timer = 0
        self.explosion_point = (0,0)
        self.font = pygame.font.Font("data/font.otf", 35)
        self.show_ui = True
        self.h_pressed = False
        self.r_pressed = False
        self.esc_pressed = False
        self.background_level = self.grid_size[1]
        self.background_grid = []
        self.key_pos = (0,0)
        self.key_gravity = 0
        self.ammo = -1
        self.level_name = 'default'
        self.show_text_box = False
        self.time = True
        
        for _ in range(self.grid_size[1]):
            level1 = []
            level2 = []
            for _ in range(self.grid_size[0]):
                level1.append('blank')
                level2.append('air')
            self.grid.append(level1)
            self.background_grid.append(level2)

        if not blank:
            self.loadLevel(self.level_name)
        self.paintBackground()
        self.loadSounds()
        self.loadTextures()
        self.placeTextures()
        self.makeButtons()
    
    def getLevelName(self):
        return self.level_name
    
    def setLevelName(self, name):
        self.level_name = name
    
    def getAmmo(self):
        return self.ammo
    
    def setAmmo(self, ammo):
        self.ammo = ammo
    
    def getGrid(self):
        return self.grid
    
    def getStartPoint(self):
        return self.start_point
    
    def paintBackground(self):
        max_depth, max_width = (self.grid_size[1], self.grid_size[0])
        surface = self.background_level
        self.ground_depth = (max_depth - surface)

        for i in range(max_depth):
            for j in range(max_width):
                if i < surface:
                    self.background_grid[i][j] = 'air'
                
                elif i >= surface and i < surface + self.ground_depth*1/3:
                    self.background_grid[i][j] = 'dirt'
                
                elif i >= surface + self.ground_depth*1/3 and i < surface + self.ground_depth*2/3:
                    value = (i - surface - self.ground_depth*1/3) / (self.ground_depth*1/3)
                    if random.random() > value:
                        self.background_grid[i][j] = 'dirt'
                    else:
                        self.background_grid[i][j] = 'stone'
                
                else:
                    self.background_grid[i][j] = 'stone'
    
    def loadSounds(self):
        self.explosion_sound = pygame.mixer.Sound('data/sounds/explode1.ogg')
        self.explosion_sound.set_volume(0.2)
    
    def loadTextures(self):
        self.air = pygame.transform.scale_by( pygame.image.load( f'data/textures/air.png' ).convert(), 10 )
        self.blank = pygame.transform.scale_by( pygame.image.load( f'data/textures/blank.png' ).convert_alpha(), 10 )
        
        self.explosion = []
        for i in range(1,7):
            self.explosion.append(pygame.transform.scale_by(pygame.image.load( f'data/textures/explosion_{i}.png' ).convert_alpha(), 5))

        self.dirt = []
        for i in range(1,7):
            self.dirt.append(pygame.transform.scale_by( pygame.image.load( f'data/textures/dirt_{i}.png' ).convert(), 10 ))

        self.stone = []
        for i in range(1,7):
            self.stone.append(pygame.transform.scale_by( pygame.image.load( f'data/textures/stone_{i}.png' ).convert(), 10 ))

        self.planks = []
        for i in range(1,7):
            self.planks.append(pygame.transform.scale_by( pygame.image.load( f'data/textures/planks_{i}.png' ).convert(), 10 ))

        self.sand = []
        for i in range(1,7):
            self.sand.append(pygame.transform.scale_by( pygame.image.load( f'data/textures/sand_{i}.png' ).convert(), 10 ))

        self.bricks = []
        for i in range(1,3):
            self.bricks.append(pygame.transform.scale_by( pygame.image.load( f'data/textures/bricks_{i}.png' ).convert(), 10 ))

        self.obsidian = []
        for i in range(1,6):
            self.obsidian.append(pygame.transform.scale_by( pygame.image.load( f'data/textures/obsidian_{i}.png' ).convert(), 10 ))

        self.ice = []
        for i in range(1,4):
            self.ice.append(pygame.transform.scale_by( pygame.image.load( f'data/textures/ice_{i}.png' ).convert(), 10 ))

        fade_height = (self.grid_size[1] - self.background_level)*PPB if (self.grid_size[1] - self.background_level)*PPB > 0 else 1
        self.background_fade = pygame.Surface((self.screen.get_width(), fade_height), pygame.SRCALPHA)
        self.background_fade.fill((10,10,15,128))

        self.key = pygame.transform.scale_by(pygame.image.load(f'data/textures/key.png').convert_alpha(),5)
        self.key_rect = self.key.get_rect(bottomleft = self.key_pos)

        self.dynamite = pygame.transform.scale_by(pygame.image.load(f'data/textures/dynamite_1.png').convert_alpha(), 8)
        self.slot = [pygame.transform.scale_by( pygame.image.load( f'data/textures/slot.png' ).convert_alpha(), 7 ), 
                     pygame.transform.scale_by( pygame.image.load( f'data/textures/slot_p.png' ).convert_alpha(), 7 )]
        
        self.button = [pygame.transform.scale_by( pygame.image.load( f'data/textures/button.png' ).convert_alpha(), 8 ), 
                       pygame.transform.scale_by( pygame.image.load( f'data/textures/button_p.png' ).convert_alpha(), 8 )]
        
        self.box = [pygame.transform.scale_by( pygame.image.load( f'data/textures/button.png' ).convert_alpha(), 12 ), 
                       pygame.transform.scale_by( pygame.image.load( f'data/textures/button_p.png' ).convert_alpha(), 12 )]
        
        self.occlusion = pygame.Surface((self.screen.get_width(),self.screen.get_height()), pygame.SRCALPHA)
        self.occlusion.fill((0,0,0,160))

    def chooseTexture(self, name, pos = (0,0), alternate=False,):
        if name == 'air': 
            return self.air
        elif name == 'blank':
            return self.blank
        elif name == 'dirt':
            return pygame.transform.rotate( random.choice(self.dirt), random.randint(0,3)*90 )
        elif name == 'stone':
            return pygame.transform.rotate( random.choice(self.stone), random.randint(0,3)*90 )
        elif name == 'planks':
            return random.choice(self.planks)
        elif name == 'sand':
            return pygame.transform.rotate( random.choice(self.sand), random.randint(0,3)*90 )
        elif name == 'obsidian':
            return pygame.transform.rotate( random.choice(self.obsidian), random.randint(0,3)*90 )
        elif name == 'ice':
            return pygame.transform.rotate( random.choice(self.ice), random.randint(0,3)*90 )
        elif name == 'bricks':
            if alternate:
                return self.bricks[0]
            else:
                return self.bricks[1]

    def placeTextures(self):
        self.textures = []
        alternate = True

        for i in self.grid:
            level = []
            for j in i:
                level.append(self.chooseTexture(j, alternate))
                alternate = negate(alternate)
            alternate = negate(alternate)
            self.textures.append(level)
        
        self.placeBackgroundTextures()

    def placeBackgroundTextures(self):
        self.background_textures = []
        alternate = True

        for i in self.background_grid:
            level = []
            for j in i:
                level.append(self.chooseTexture(j, alternate))
                alternate = negate(alternate)
            alternate = negate(alternate)
            self.background_textures.append(level)
        
    def showAmmo(self, position):
        if self.ammo > -1:
            ammount = str(self.ammo)
            number = self.font.render(ammount, True, white)
        else:
            ammount = '8'
            number = self.font.render(ammount, True, white)
            number = pygame.transform.rotate(number, -90)
            position = (position[0]-5, position[1]+10)
        
        self.screen.blit(number, position)
    
    def blowUp(self, data):
        if data[0]:
            #print("Buuuuum! Takie duże.")
            self.exp_timer = 1
            self.explosion_point = data[1]
            for y in range( int(self.explosion_point[1] / PPB) - 1,  int(self.explosion_point[1] / PPB) + 2):
                for x  in range( int(self.explosion_point[0] / PPB) - 1,  int(self.explosion_point[0] / PPB) + 2):
                    if y < len(self.grid) and x < len(self.grid[0]) and x > -1 and y > -1 and self.grid[y][x] != 'obsidian':
                        self.grid[y][x] = 'blank'
                        self.textures[y][x] = self.blank
            
            if self.sound_on:
                self.explosion_sound.play()

    def showExplosion(self):
        if self.exp_timer:
            
            self.exp_timer += 1

            if self.exp_timer < 5:
                self.screen.blit(self.explosion[0], (self.explosion_point[0] - 40, self.explosion_point[1] - 40))
            elif self.exp_timer < 10:
                self.screen.blit(self.explosion[1], (self.explosion_point[0] - 40, self.explosion_point[1] - 40))
            elif self.exp_timer < 20:
                self.screen.blit(self.explosion[2], (self.explosion_point[0] - 40, self.explosion_point[1] - 40))
            elif self.exp_timer < 30:
                self.screen.blit(self.explosion[3], (self.explosion_point[0] - 40, self.explosion_point[1] - 40))
            elif self.exp_timer < 40:
                self.screen.blit(self.explosion[4], (self.explosion_point[0] - 40, self.explosion_point[1] - 40))
            elif self.exp_timer < 50:
                self.screen.blit(self.explosion[5], (self.explosion_point[0] - 40, self.explosion_point[1] - 40))

            if self.exp_timer == 50:
                self.exp_timer = 0

    def returnSound(self):
        return self.sound_on
    
    def makeButtons(self):
        self.b_dynamite = Button(self.screen, self.slot, (15, 15), lambda : None, self.dynamite)
        self.b_dynamite.makeClickable()

    def handleButtons(self, mouse_pos, mouse):
        if self.show_ui: 
            self.b_dynamite.render(mouse_pos, mouse)
            self.showAmmo((self.b_dynamite.getPosition()[0]+100, self.b_dynamite.getPosition()[1]+30))

    def saveLevel(self, name):
        s = open(f"data/levels/{name}.dat", "wb")
        pickle.dump(self.grid, s)
        pickle.dump(self.start_point, s)
        pickle.dump(self.background_level, s)
        pickle.dump(self.key_pos, s)
        pickle.dump(self.ammo, s)
        s.close()
        return "data/levels/level.dat"

    def loadLevel(self, name):
        s = open(f"data/levels/{name}.dat", "rb")
        self.grid = pickle.load(s)
        self.start_point = pickle.load(s)
        self.background_level = pickle.load(s)
        self.key_pos = pickle.load(s)
        self.ammo = pickle.load(s)
        s.close() 

    def exitToMenu(self, keys): 
        if keys[pygame.K_ESCAPE]: 
            self.esc_pressed = True
        elif self.esc_pressed:
            self.esc_pressed = False
            self.level_name = 'default'
            if self.show_text_box:
                self.show_text_box = False
            else:
                return 'title'
        return ''
    
    def hideUi(self, keys): 
        if keys[pygame.K_h]:
            self.h_pressed = True
        elif self.h_pressed:
            self.h_pressed = False
            self.show_ui = negate(self.show_ui)

    def restart(self, keys, force = False):
        if keys[pygame.K_r]:
            self.r_pressed = True
        elif self.r_pressed or force:
            self.r_pressed = False
            self.loadLevel(self.level_name)
            self.paintBackground()
            self.key_rect.bottomleft = self.key_pos
            self.placeTextures()
            self.background_fade = pygame.transform.scale( self.background_fade, ( self.background_fade.get_width(), (self.grid_size[1] - self.background_level)*PPB) )
            return self.start_point
        return False

    def getKeyRect(self):
        return self.key_rect
    
    def startTyping(self):
        self.show_text_box = negate(self.show_text_box)

    def getGroundLevel(self, feet):
        x = int(feet[0] / PPB)
        y = int(feet[1] / PPB)
        n = 0
        for i in self.grid:
            if i[x] != 'blank' and n >= y:
                return (x*PPB, n * PPB)
            n += 1

        return (x, self.screen.get_height())
    
    def Type(self, box):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pass
                elif event.key == pygame.K_RETURN:
                    self.show_text_box = False
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.level_name = self.level_name[:-1]
                else:
                    self.level_name += event.unicode
            
        box.setPicture(self.font.render(self.level_name+'|', True, white))
        return False
    
    def keyPhysics(self):
        self.floor_pos = self.getGroundLevel(self.key_rect.midbottom)
        self.key_gravity += 0.4
        self.key_rect.bottom += self.key_gravity
        if self.key_rect.bottom >= self.floor_pos[1]:
            self.key_rect.bottom = self.floor_pos[1]
            self.key_gravity = 0
    
    def render(self, sound_on, keys):
        for i in range(self.grid_size[1]):
            for j in range(self.grid_size[0]):
                self.screen.blit(self.background_textures[i][j],(j*PPB,i*PPB))
        
        self.screen.blit(self.background_fade, (0, self.background_level*PPB) )
        
        for i in range(self.grid_size[1]):
            for j in range(self.grid_size[0]):
                self.screen.blit(self.textures[i][j],(j*PPB,i*PPB))
        
        if self.time: self.keyPhysics()
        self.screen.blit(self.key, self.key_rect)
        self.sound_on = sound_on
        self.showExplosion()
        self.hideUi(keys)

class Title(Environment):
    def __init__(self, screen, blank = False):
        super(Title, self).__init__(screen, blank)
        self.title_counter = 0
        self.sound_on = True
        self.sound_button = True
        self.click = False
        self.game_state = 'title'

    def loadTextures(self):
        super(Title, self).loadTextures()
        
        self.title = [pygame.transform.scale_by( pygame.image.load( f'data/textures/title_1.png' ).convert_alpha(), 10 ), 
                      pygame.transform.scale_by( pygame.image.load( f'data/textures/title_2.png' ).convert_alpha(), 10 )]
        self.sound = [pygame.transform.scale_by( pygame.image.load( f'data/textures/sound_on.png' ).convert_alpha(), 5 ), 
                      pygame.transform.scale_by( pygame.image.load( f'data/textures/sound_on_p.png' ).convert_alpha(), 5 ), 
                      pygame.transform.scale_by( pygame.image.load( f'data/textures/sound_off.png' ).convert_alpha(), 5 ),
                      pygame.transform.scale_by( pygame.image.load( f'data/textures/sound_off_p.png' ).convert_alpha(), 5 )]
        
        self.dirt = []
        for i in range(1,7):
            self.dirt.append(pygame.transform.scale_by( pygame.image.load( f'data/textures/dirt_{i}.png' ).convert(), 10 ))

        self.you_won = self.font.render('YOU WON!', True, white)

    def placeTextures(self):
        self.title_textures = []

        for i in self.grid:
            title_level = []

            for _ in i:
                title_level.append(pygame.transform.rotate( random.choice(self.dirt), random.randint(0,3)*90 ))

            self.title_textures.append(title_level)

    def makeButtons(self):
        self.text_box = Button(self.screen, self.box, (self.screen.get_width()/2 - self.box[0].get_width()/2, self.screen.get_height()/2 - self.box[0].get_height()/2), lambda : None)
        self.text_box.makeClickable()
        self.b_play = Button(self.screen, self.button, (self.screen.get_width()/2 - self.button[0].get_width()/2, 275), lambda : 'gameplay', self.font.render('Play', True, white))
        self.b_load = Button(self.screen, self.button, (self.screen.get_width()/2 - self.button[0].get_width()/2, 400), self.startTyping, self.font.render('Load Level', True, white))
        self.b_editor = Button(self.screen, self.button, (self.screen.get_width()/2 - self.button[0].get_width()/2, 525), lambda: 'editor', self.font.render('Level Editor', True, white))
        self.b_sound = Button(self.screen, self.sound, (15,15), lambda bool : False if bool else True)
    
    def handleButtons(self, mouse_pos, mouse):
        new_sound = self.b_sound.render(mouse_pos, mouse, self.sound_on, self.sound_on)
        if new_sound != None: self.sound_on = new_sound
        
        state = [self.b_play.render(mouse_pos, mouse), self.b_load.render(mouse_pos, mouse), self.b_editor.render(mouse_pos, mouse)]
        for i in state:
            if i: return i

        if self.show_text_box:
            self.screen.blit(self.occlusion, (0, 0) )
            self.text_box.render((0,0),(0,0,0))
            if self.Type(self.text_box): 
                return 'gameplay'

        return 'title'   
    
    def render(self, win=False):
        self.title_counter += 1
        
        for i in range(self.grid_size[1]):
            for j in range(self.grid_size[0]):
                self.screen.blit(self.title_textures[i][j],(j*PPB,i*PPB))
        
        self.screen.blit(self.occlusion, (0, 0) )

        if self.title_counter < 40: self.screen.blit(self.title[0], (self.screen.get_width()/2 - self.title[0].get_width()/2, 100))
        else: self.screen.blit(self.title[1], (self.screen.get_width()/2 - self.title[0].get_width()/2, 100))
        if self.title_counter == 80: self.title_counter = 0

        if win:
            self.screen.blit(self.you_won, (self.screen.get_width()/2 - self.you_won.get_width()/2, 400))

class Editor(Environment):
    def __init__(self, screen, blank = False):
        self.click = False
        self.mode = ''
        self.block = 'dirt'
        self.full_ui = False
        self.placing_player = False
        self.placing_key = False
        self.placing_background = False
        self.load_mode = ''

        super(Editor, self).__init__(screen, blank)
        self.time = False
    
    def loadTextures(self):
        super(Editor, self).loadTextures()
        
        self.occlusion = pygame.Surface((self.screen.get_width(),self.screen.get_height()), pygame.SRCALPHA)
        self.occlusion.fill((0,0,0,96))

        self.highlight = pygame.Surface((PPB, PPB), pygame.SRCALPHA)
        self.highlight.fill((255,255,255,64))
        
        self.small_slot = [pygame.transform.scale_by( pygame.image.load( f'data/textures/slot.png' ).convert_alpha(), 5 ), 
                     pygame.transform.scale_by( pygame.image.load( f'data/textures/slot_p.png' ).convert_alpha(), 5 )]
        self.save = [pygame.transform.scale_by( pygame.image.load( f'data/textures/save.png' ).convert_alpha(), 5 ), 
                     pygame.transform.scale_by( pygame.image.load( f'data/textures/save_p.png' ).convert_alpha(), 5 )]
        self.load = [pygame.transform.scale_by( pygame.image.load( f'data/textures/load.png' ).convert_alpha(), 5 ), 
                     pygame.transform.scale_by( pygame.image.load( f'data/textures/load_p.png' ).convert_alpha(), 5 )]
        self.tick = [pygame.transform.scale_by( pygame.image.load( f'data/textures/untick.png' ).convert_alpha(), 5 ), 
                     pygame.transform.scale_by( pygame.image.load( f'data/textures/untick_p.png' ).convert_alpha(), 5 ), 
                     pygame.transform.scale_by( pygame.image.load( f'data/textures/tick.png' ).convert_alpha(), 5 ),
                     pygame.transform.scale_by( pygame.image.load( f'data/textures/tick_p.png' ).convert_alpha(), 5 )]
        self.up = [pygame.transform.scale_by( pygame.image.load( f'data/textures/up.png' ).convert_alpha(), 5 ), 
                     pygame.transform.scale_by( pygame.image.load( f'data/textures/up_p.png' ).convert_alpha(), 5 )]
        self.down = [pygame.transform.scale_by( pygame.image.load( f'data/textures/down.png' ).convert_alpha(), 5 ), 
                     pygame.transform.scale_by( pygame.image.load( f'data/textures/down_p.png' ).convert_alpha(), 5 )]
        
        self.player_text = self.font.render('Place Player', True, white)
        self.background_text = self.font.render('Set Background Level', True, white)
        self.key_text = self.font.render('Place Objective', True, white)

        self.player = pygame.transform.scale_by(pygame.image.load(f'data/textures/char.png').convert_alpha(),5)
        self.player_rect = self.player.get_rect(midbottom = self.start_point)

    def placeBlocks(self):
        topleft = [int(self.start_block_pos[0]/PPB), int(self.start_block_pos[1]/PPB)]
        
        if self.placing_player:
            self.start_point = [topleft[0]*PPB+PPB, topleft[1]*PPB+PPB]
            self.player_rect.midbottom = self.start_point
            self.placing_player = False
        
        elif self.placing_background:
            self.background_level = topleft[1]
            self.background_fade = pygame.transform.scale( self.background_fade, ( self.background_fade.get_width(), (self.grid_size[1] - self.background_level)*PPB) )
            self.paintBackground()
            self.placeBackgroundTextures()
            self.placing_background = False

        elif self.placing_key:
            self.key_pos = [topleft[0]*PPB, topleft[1]*PPB+PPB]
            self.key_rect.bottomleft = self.key_pos
            self.placing_key = False

        else:
            for i in range(topleft[1], topleft[1]+int(self.d_y)):
                for j in range(topleft[0], topleft[0]+int(self.d_x)):
                    alternate = True if (i%2 and j%2) or (not i%2 and not j%2) else False
                    
                    if i < len(self.grid) and j < len(self.grid[0]) and j > -1 and i > -1:
                        if self.mode == 'place' and self.grid[i][j] != self.block:
                            self.grid[i][j] = self.block
                            self.textures[i][j] = self.chooseTexture(self.block, (i,j), alternate)
                        elif self.mode == 'remove':
                            self.grid[i][j] = 'blank'
                            self.textures[i][j] = self.blank
    
    def highlightBlocks(self, mouse_pos, mouse):
        curr_block = [int(mouse_pos[0]/PPB), int(mouse_pos[1]/PPB)]
        curr_block_pos = [curr_block[0]*PPB, curr_block[1]*PPB]
        if not self.click:
            self.start_block = curr_block
            self.start_block_pos = [self.start_block[0]*PPB, self.start_block[1]*PPB]

        if mouse[1]:
            block = self.grid[curr_block[1]][curr_block[0]]
            if block != 'blank': self.setBlock(block)
        
        elif mouse[0] or mouse[2]:
            self.click = True
            
            if not self.placing_player and not self.placing_key and not self.placing_background:
                self.d_x = curr_block[0] - self.start_block[0]
                if self.d_x < 1:
                    self.start_block_pos[0] = curr_block_pos[0]
                self.d_x = math.fabs(self.d_x) + 1
                
                self.d_y = curr_block[1] - self.start_block[1]
                if self.d_y < 1:
                    self.start_block_pos[1] = curr_block_pos[1]
                self.d_y = math.fabs(self.d_y) + 1

                if mouse[0]:
                    self.mode = 'place'
                elif mouse[2]:
                    self.mode = 'remove'

        elif self.click:
            self.click = False
            self.placeBlocks()
            self.d_x, self.d_y = (1, 1)

        else:
            self.d_x, self.d_y = (1, 1)      
        
        self.highlight = pygame.transform.scale( self.highlight, ( PPB*self.d_x, PPB*self.d_y) )
        self.screen.blit(self.highlight, self.start_block_pos )
        pygame.draw.rect(self.screen, white, pygame.Rect(self.start_block_pos[0]-1, self.start_block_pos[1]-1, PPB*self.d_x+2, PPB*self.d_y+2), 2)
    
    def makeButtons(self):
        self.text_box = Button(self.screen, self.button, (self.screen.get_width()/2 - self.button[0].get_width()/2, self.screen.get_height()/2 - self.button[0].get_height()/2), lambda : None)
        self.text_box.makeClickable()
        
        self.b_save = Button(self.screen, self.save, (self.screen.get_width()-self.save[0].get_width()-20, 20), self.inputLevel)
        self.b_load = Button(self.screen, self.load, (self.screen.get_width()-self.save[0].get_width()-self.load[0].get_width()-40, 20), self.inputLevel)
        
        self.b_curr_block = Button(self.screen, self.slot, (15, 15), self.expandUi, pygame.transform.scale_by(self.chooseTexture(self.block), 1.7))
        self.b_dirt = Button(self.screen, self.small_slot, (30, 120), self.setBlock, pygame.transform.scale_by(self.chooseTexture('dirt'), 1.2))
        self.b_stone = Button(self.screen, self.small_slot, (30, 85 + self.b_dirt.getPosition()[1]), self.setBlock, pygame.transform.scale_by(self.chooseTexture('stone'), 1.2))
        self.b_planks = Button(self.screen, self.small_slot, (30, 85 + self.b_stone.getPosition()[1]), self.setBlock, pygame.transform.scale_by(self.chooseTexture('planks'), 1.2))
        self.b_bricks = Button(self.screen, self.small_slot, (30, 85 + self.b_planks.getPosition()[1]), self.setBlock, pygame.transform.scale_by(self.chooseTexture('bricks'), 1.2))
        self.b_sand = Button(self.screen, self.small_slot, (30, 85 + self.b_bricks.getPosition()[1]), self.setBlock, pygame.transform.scale_by(self.chooseTexture('sand'), 1.2))
        self.b_obsidian = Button(self.screen, self.small_slot, (30, 85 + self.b_sand.getPosition()[1]), self.setBlock, pygame.transform.scale_by(self.chooseTexture('obsidian'), 1.2))
        self.b_ice = Button(self.screen, self.small_slot, (30, 85 + self.b_obsidian.getPosition()[1]), self.setBlock, pygame.transform.scale_by(self.chooseTexture('ice'), 1.2))

        self.tick_player = Button(self.screen, self.tick, (150, 30), self.placePlayer)
        self.is_player_ticked = False
        self.tick_background = Button(self.screen, self.tick, (150, 120), self.placeBackground)
        self.is_background_ticked = False
        self.tick_key = Button(self.screen, self.tick, (150, 210), self.placeKey)
        self.is_key_ticked = False

        self.b_dynamite = Button(self.screen, self.slot, (700, 60), lambda : None, self.dynamite)
        self.b_dynamite.makeClickable()
        self.b_up = Button(self.screen, self.up, (self.b_dynamite.getPosition()[0] + self.slot[0].get_width()/2 - self.up[0].get_width()/2, self.b_dynamite.getPosition()[1] - 45), self.moreAmmo)
        self.b_down = Button(self.screen, self.down, (self.b_dynamite.getPosition()[0] + self.slot[0].get_width()/2 - self.down[0].get_width()/2, self.b_dynamite.getPosition()[1] + 98), self.lessAmmo)

    def inputLevel(self, mode):
        self.startTyping()
        self.load_mode = mode
    
    def moreAmmo(self):
        self.ammo +=1

    def lessAmmo(self):
        self.ammo -=1
        if self.ammo < -1: self.ammo = -1
    
    def expandUi(self):
        self.full_ui = negate(self.full_ui)

    def setBlock(self, block):
        self.block = block
        self.b_curr_block.setPicture(pygame.transform.scale_by(self.chooseTexture(self.block), 1.7))

    def placePlayer(self):
        if not self.is_player_ticked:
            self.placing_player = True
            self.is_player_ticked = True
            self.full_ui = False
        else:
            self.is_player_ticked = False

    def placeBackground(self):
        if not self.is_background_ticked:
            self.placing_background = True
            self.is_background_ticked = True
            self.full_ui = False
        else:
            self.is_background_ticked = False
            self.background_level = self.grid_size[1]
            self.paintBackground()
            self.placeBackgroundTextures()
    
    def placeKey(self):
        if not self.is_key_ticked:
            self.placing_key = True
            self.is_key_ticked = True
            self.full_ui = False
        else:
            self.is_key_ticked = False
    
    def handleButtons(self, mouse_pos, mouse):
        if self.show_ui:
            if self.full_ui:
                self.screen.blit(self.occlusion, (0, 0) )
                
                self.b_dirt.render(mouse_pos, mouse, 'dirt')
                self.b_stone.render(mouse_pos, mouse, 'stone')
                self.b_planks.render(mouse_pos, mouse, 'planks')
                self.b_bricks.render(mouse_pos, mouse, 'bricks')
                self.b_sand.render(mouse_pos, mouse, 'sand')
                self.b_obsidian.render(mouse_pos, mouse, 'obsidian')
                self.b_ice.render(mouse_pos, mouse, 'ice')

                self.tick_player.render(mouse_pos, mouse, is_on = negate(self.is_player_ticked))
                self.screen.blit(self.player_text, (self.tick_player.getPosition()[0] + 60, self.tick_player.getPosition()[1] + 7))
                self.tick_background.render(mouse_pos, mouse, is_on = negate(self.is_background_ticked))
                self.screen.blit(self.background_text, (self.tick_background.getPosition()[0] + 60, self.tick_background.getPosition()[1] + 7))
                self.tick_key.render(mouse_pos, mouse, is_on = negate(self.is_key_ticked))
                self.screen.blit(self.key_text, (self.tick_key.getPosition()[0] + 60, self.tick_key.getPosition()[1] + 7))

                self.b_dynamite.render(mouse_pos, mouse)
                self.b_up.render(mouse_pos, mouse)
                self.b_down.render(mouse_pos, mouse)
                self.showAmmo((self.b_dynamite.getPosition()[0]+100, self.b_dynamite.getPosition()[1]+30))
            
            self.b_curr_block.render(mouse_pos, mouse)
            self.b_save.render(mouse_pos, mouse, 'save')
            self.b_load.render(mouse_pos, mouse, 'load')

        if ((not self.b_curr_block.isHovered(mouse_pos) and not self.b_save.isHovered(mouse_pos) and not self.b_load.isHovered(mouse_pos) and not self.full_ui) or not self.show_ui) and not self.show_text_box:
            self.highlightBlocks(mouse_pos, mouse)

        if self.show_text_box:
            self.screen.blit(self.occlusion, (0, 0) )
            self.text_box.render((0,0),(0,0,0))
            
            if self.Type(self.text_box): 
                if self.load_mode == 'save':
                    self.saveLevel(self.level_name)
                elif self.load_mode == 'load':
                    self.key_pos = (0,0)
                    self.loadLevel(self.level_name)
                    self.player_rect.midbottom = self.start_point
                    if self.start_point != (0, self.screen.get_height()): 
                        self.is_player_ticked = True
                    if self.background_level < self.grid_size[1]:
                        self.is_background_ticked = True
                    if self.key_pos != (0,0):
                        self.is_key_ticked = True
                    self.restart(pygame.key.get_pressed(), self.load_mode)
                self.load_mode = ''
    
    def render(self, sound_on, keys):
        super(Editor, self).render(sound_on, keys)

        if self.is_player_ticked and not self.placing_player:
            self.screen.blit(self.player, self.player_rect)
        
        if not self.is_key_ticked or self.placing_key:
            self.key_rect.bottomleft = (0,0)
            self.key_pos = (0,0)