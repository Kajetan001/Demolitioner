import pygame
import math

PPB = 20 #pixels per block

class Dynamite():
    def __init__(self, screen):
        self.on_screen = False
        self.screen = screen
        self.timer = 0
        self.texture_1 = pygame.transform.scale_by(pygame.image.load(f'data/textures/dynamite_1.png').convert_alpha(),5)
        self.texture_2 = pygame.transform.scale_by(pygame.image.load(f'data/textures/dynamite_2.png').convert_alpha(),5)
        self.dyn = self.texture_1
        self.dir = 1
        self.rect = self.dyn.get_rect(topleft = (0,0))
        self.gravity = 0
        self.flying = False
        self.sticky = False
        self.detonate = False
        self.grid = []
        
    def appear_held(self, pos, dir):
        self.on_screen = True
        self.flying = False
        self.gravity = 0
        self.vel = [0,0]
        self.dir = 1
        self.dyn = self.texture_1

        pos[1] -= 10
        if self.dir != dir:
            self.dyn = pygame.transform.flip(self.dyn, True, False)
            self.dir = dir
        if not self.dir + 1: pos[0] -= 50
        self.rect.midleft = pos
        
        y = self.rect.bottom
        if self.dir + 1: x = self.rect.right
        else: x = self.rect.left
        self.start = (x,y)

    def getMidPoint(self):
        point = list(self.rect.midright) if self.dir + 1 else list(self.rect.midleft)
        point[0] -= 9 if self.dir + 1 else -6
        return point
    
    def drop(self):
        self.flying = True
        self.timer = 0

    def position(self):    
        if self.flying:  

            x = self.rect.right if self.dir + 1 else self.rect.left
            y = self.rect.bottom

            if self.vel[0]:
                next_x = x + self.vel[0]*0.2*self.dir
                next_y = self.start[1] - (next_x-self.start[0]) * (-self.vel[1]*self.dir)/self.vel[0] + (10*(next_x-self.start[0])**2)/(2*self.vel[0]*self.vel[0])
            else:
                self.gravity += 0.4
                next_x = x
                next_y = y + self.gravity
            
            if x > (len(self.grid[0]))*PPB: 
                x = (len(self.grid[0]))*PPB - 1
                self.vel[0] = 0
            
            if next_y < 0: 
                next_y = 0
                self.gravity = 0
                self.vel[0] = 0
            if next_y > (len(self.grid))*PPB: 
                next_y = (len(self.grid))*PPB - 2
                self.gravity = 0
                self.vel[0] = 0
                
            if self.grid[int(next_y / PPB)][int(x / PPB)] != 'blank':
                self.gravity = 0
                if self.grid[int((next_y + 0.4) / PPB)][int(x / PPB)] != 'blank':
                    self.vel[0] = 0
                next_y = y

            if next_x < 0: 
                next_x = 0
                self.vel[0] = 0
            if next_x > (len(self.grid[0]))*PPB: 
                next_x = (len(self.grid[0]))*PPB - 1
                self.vel[0] = 0

            if self.grid[int(y / PPB)][int(next_x / PPB)] != 'blank':
                self.vel[0] = 0
                next_x = x 
            
            self.rect.bottom = next_y
            if self.dir + 1: self.rect.right = next_x
            else: self.rect.left = next_x

            self.flicker()

    def render(self):
        if self.on_screen:    
            self.position()
            self.screen.blit(self.dyn, self.rect)
        else:
            self.detonate = False

    def ready(self, velocity = [0,0]):
        self.vel = velocity
    
    def flicker(self):
        self.timer +=1
        if not self.timer % 50:
            self.dyn = self.texture_2
            if self.dir - 1:
                self.dyn = pygame.transform.flip(self.dyn, True, False)
        elif not self.timer % 25:
            self.dyn = self.texture_1
            if self.dir - 1:
                self.dyn = pygame.transform.flip(self.dyn, True, False)

        if self.timer == 300:
            self.detonate = True
            self.flying = False
            self.on_screen = False
    
    def isBooming(self):
        return self.detonate

class Character():
    def __init__(self, floor_pos, screen):
        self.char = pygame.transform.scale_by(pygame.image.load(f'data/textures/char.png').convert_alpha(),5)
        self.rect = self.char.get_rect(midbottom = floor_pos)
        self.gravity = 0
        self.fatigue = 0
        self.dir = 1
        self.floor_pos = floor_pos
        self.level_size = pygame.display.get_window_size()
        self.screen = screen
        self.click = False
        self.dynamite = Dynamite(self.screen)
        self.cooldown = False
        self.key_rect = None
        self.win_countdown = 20
        self.ammo = -1

    def setKeyRect(self, rect):
        self.key_rect = rect

    def checkVictory(self):
        if self.rect.colliderect(self.key_rect):
            self.win_countdown -= 1
        if self.win_countdown == 0: 
            self.win_countdown = 20
            return True
        else: return False
   
    def handleKeys(self, keys, mouse):
        if mouse[0]:
            if not self.click:
                self.mouse_start = pygame.mouse.get_pos()
            
            if not self.cooldown and not mouse[2] and self.ammo != 0:
                self.click = True
                    
                self.dynamite.appear_held(list(self.rect.midright), self.dir)
                self.prepare_throw()
            
            elif not self.cooldown and mouse[2]:
                self.click = False
                self.dynamite.on_screen = False

        else:
            if self.click: 
                self.dynamite.drop()
                if self.ammo > 0: self.ammo -=1
                self.cooldown = True
            self.click = False

            if keys[pygame.K_SPACE] and self.rect.bottom == self.floor_pos[1] and self.fatigue < 1:
                self.jump()
        
            if keys[pygame.K_a]:
                self.moveLeft()
        
            if keys[pygame.K_d]:
                self.moveRight()

    def isFacingWall(self):
        if not self.dir + 1: #patrzymy w lewo
            if self.walls[0] != ['blank','blank','blank']:
                return True
        
        elif self.dir + 1: #patrzymy w prawo
            if self.walls[1] != ['blank','blank','blank']:
                return True
        
        else:
            return False
    
    def drawTrajectory(self, origin):
        mouse_curr = pygame.mouse.get_pos()

        if (mouse_curr[0] - self.mouse_start[0]) * self.dir > 0:
            floor = self.getGroundLevel(self.rect.bottomright)
            
            for i in range(origin[1], floor[1]):
                if i % 11 == 0:
                    pygame.draw.rect(self.screen, 'White', pygame.Rect(origin[0], i, 3, 3))
            
            self.dynamite.ready()
            
        else:
            vel_ver = math.sqrt(math.fabs(self.mouse_start[1] - mouse_curr[1]))*3
            if mouse_curr[1] > self.mouse_start[1]:
                vel_ver *= -1
            vel_hor = math.sqrt(math.fabs(self.mouse_start[0] - mouse_curr[0]))*3
                
            x,y = (0,0)
            if not origin[0]/PPB < 0 and not origin[0]/PPB > len(self.grid[0]) and not origin[1]/PPB < 0 and not origin[1]/PPB > len(self.grid):
                while self.grid[int((origin[1] + y)/PPB)][int((origin[0] + x)/PPB)] == 'blank' and vel_hor:
                        
                    pygame.draw.rect(self.screen, 'White', pygame.Rect(origin[0] + x, origin[1] + y, 3, 3))
                    self.dynamite.ready([vel_hor, vel_ver])
                    x += vel_hor*0.2*self.dir
                    y = -x * (-vel_ver*self.dir)/vel_hor + (10*x*x)/(2*vel_hor*vel_hor)

                    if (origin[0] + x)/PPB < 0 or (origin[0] + x)/PPB > len(self.grid[0]) or (origin[1] + y)/PPB < 0 or (origin[1] + y)/PPB > len(self.grid):
                        break
    
    def prepare_throw(self):
        origin = self.dynamite.getMidPoint()
        self.drawTrajectory(origin)

    def jump(self):
        self.gravity = -11
        self.fatigue = 6

    def moveLeft(self):
        if self.dir + 1: 
            self.char = pygame.transform.flip(self.char, True, False)
        self.dir = -1
        
        if not self.isFacingWall():
            self.rect.left -= 5 if self.rect.bottom < self.floor_pos[1] else 4.5

    def moveRight(self):
        if not self.dir + 1: 
            self.char = pygame.transform.flip(self.char, True, False)
        self.dir = 1

        if not self.isFacingWall():
            self.rect.left += 5 if self.rect.bottom < self.floor_pos[1] else 4.5
    
    def getFeet(self):
        return self.rect.midbottom
    
    def getGroundLevel(self, feet):
        x = int(feet[0] / PPB)
        y = int(feet[1] / PPB)
        n = 0
        for i in self.grid:
            if i[x] != 'blank' and n >= y:
                return (x*PPB, n * PPB)
            n += 1

        return (x, self.screen.get_height())
    
    def getWalls(self, feet):
        x = int(feet[0] / PPB)
        y = int(feet[1] / PPB)
        if y < 3: y = 3
        
        wall1 = [self.grid[y-1][x-1], self.grid[y-2][x-1], self.grid[y-3][x-1]] if x > 0 else ['void','void','void']
        wall2 = [self.grid[y-1][x+1], self.grid[y-2][x+1], self.grid[y-3][x+1]] if x + 1 < len(self.grid[1]) else ['void','void','void']
        ceiling = self.grid[y-4][x] if y > 3 else 'void'

        return (wall1, wall2, ceiling)
    
    def handleEnvironment(self):
        if not self.click: 
            self.gravity += 0.4
            self.rect.bottom += self.gravity
        
        if self.walls[2] != 'blank' and self.gravity < 0:
            self.gravity = 0

        if self.rect.bottom >= self.floor_pos[1]:
            self.rect.bottom = self.floor_pos[1]
            self.fatigue -= 1
            self.gravity = 0

    def blowUp(self):
        if self.dynamite.isBooming():
            self.cooldown = False
        return (self.dynamite.isBooming(), self.dynamite.getMidPoint())
    
    def setAmmo(self, ammo):
        self.ammo = ammo

    def getAmmo(self):
        return self.ammo
    
    def restart(self, start_point):
        if start_point:
            self.rect.midbottom = start_point
            self.dynamite.on_screen = False
            self.cooldown = False
    
    def render(self, keys, mouse, grid):
        self.grid = grid
        self.dynamite.grid = grid
        self.walls = self.getWalls(self.rect.midbottom)
        self.floor_pos = self.getGroundLevel(self.rect.midbottom)
        self.dynamite.render()

        self.handleKeys(keys, mouse)
        self.handleEnvironment()
        self.screen.blit(self.char, self.rect)
