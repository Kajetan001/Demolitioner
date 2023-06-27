import pygame
from data import env
from data import char

pygame.init()
pygame.display.set_caption('Demolitioner')
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
game_state = 'title'

main_env = env.Environment(screen)
editor_env = env.Editor(screen, blank=True)
title = env.Title(screen)

character = char.Character(main_env.getStartPoint(), screen)

theme = pygame.mixer.music.load('data/sounds/theme.mp3')
sound_on = True
pygame.mixer.music.set_volume(0)
#pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    if sound_on: pygame.mixer.music.unpause()
    else: pygame.mixer.music.pause()
    
    if game_state == 'title':
        title.render()
        sound_on = title.returnSound()
        state = title.handleButtons(mouse_pos, mouse)
        main_env.setLevelName(title.getLevelName())
        if state != game_state:
            character.restart(main_env.restart(keys, True))
            game_state = state

    elif game_state == 'gameplay':
        character.restart(main_env.restart(keys))
        
        main_env.render(sound_on, keys)
        main_env.handleButtons(mouse_pos, mouse)
        
        character.setKeyRect(main_env.getKeyRect())
        character.setAmmo(main_env.getAmmo())
        character.render(keys, mouse, main_env.getGrid())
        
        main_env.blowUp(character.blowUp())
        main_env.setAmmo(character.getAmmo())
        
        if character.checkVictory(): game_state = 'win'
        
    elif game_state == 'editor':
        editor_env.render(sound_on, keys)
        editor_env.handleButtons(mouse_pos, mouse)

    elif game_state == 'win':
        title.render(True)

    exit = editor_env.exitToMenu(keys)
    if exit: game_state = exit
    
    pygame.display.update()
    clock.tick(120)

pygame.quit()