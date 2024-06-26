import pygame
import math
import optionen

from sys import platform



pygame.init()
# pygame.mouse.set_visible(False)
info_object = pygame.display.Info()
screen_size = (info_object.current_w, info_object.current_h)

display = pygame.display.set_mode(screen_size, pygame.FULLSCREEN | pygame.SCALED, vsync=True)

class gamestate:
    def __init__(self):
        self.running = False
        self.level = "exit"
        self.coin_count = 0
        gs.Options_prototype = {
            "master volume":1,
            "jump volume":1,
            "shot volume":1,
        }


class PulsatingText:

    Texts = []
    def __init__(self, display, text, center, font_size=36):
        """defines a new pulsating text.
        
        display: pygame instance of the display to draw on.
        text: text the pulsating text should display in game.
        center: list(x-position, y-positio).
        fint_size: default = 36px."""
        self.display = display
        self.text = text
        self.center = center
        self.font_size = font_size
        self.phase = 0
        PulsatingText.Texts.append(self)

    def update(self):
        """updates the phase of the blink."""
        self.phase = (self.phase + 0.04) % (2 * math.pi)

    def draw(self):
        """draws the Text on the display"""
        pulse_val = abs(math.sin(self.phase)) 
        pulse_color = (pulse_val * 255, pulse_val * 255, pulse_val * 255)
        font = pygame.font.SysFont(None, self.font_size) 
        rendered_text = font.render(self.text, True, pulse_color)
        text_rect = rendered_text.get_rect(center=self.center)
        self.display.blit(rendered_text, text_rect)



class Startmenu():
    def __init__(self, display):
        """defines a new startmenu.

        display: instance of the display to draw on."""
        self.display = display
        self.font_size = 18
        self.font = pygame.font.SysFont(None, self.font_size) 
        self.color_l = (0,0,0)
        self.color_r = (0,0,0)
        y = 200
        x = screen_size[0]//2
        PulsatingText(display, "Wähle dein Level", (x, 100), 36)

        Level(1, x-100, y,enebled=True)
        Level(2,x,y)
        


    def draw(self):
        """draws the startmenue to the display"""

        pygame.draw.rect(self.display, (150, 0, 0), (screen_size[0]-150, 70, 70, 30), 0)
        text = self.font.render(f"Beenden", True, (200, 200, 200))
        self.display.blit(text, (screen_size[0]-145, 80))

        for level in Level.levels:
            level.draw(self.display)
        

        
    def check_input(self, events):
        """checks input to the startmenue.
        events: pygame.event"""
        for level in Level.levels:
            level.check_input(events)

        options.check_input(events)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if pygame.Rect(screen_size[0]-150, 70, 70, 30).collidepoint(mouse_pos): 
                    print('click')
                    gs.level = "exit"
                    gs.running = False


class Options():
    def __init__(self) -> None:
        self.x = screen_size[0] - 100
        self.y = screen_size[1] - 100
        self.w = 90
        self.h = 35
        self.font_size = 24
        self.font = pygame.font.SysFont(None, self.font_size) 

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y, self.w, self.h))
        text = self.font.render(f"Optionen", True, (255, 255, 255))
        surface.blit(text, (self.x+10, self.y+10))

    def check_input(self, events):
        """checks input to the startmenue.
        events: pygame.event"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if pygame.Rect(self.x-5, self.y-5, self.w+10, self.h+10).collidepoint(mouse_pos): 
                    print('click')
                    optionen.main([gs.Options_prototype])
                    

class Level():
    levels = []
    def __init__(self, level_id, x, y, font_size=24,enebled=False):
        self.font_size = font_size
        self.font = pygame.font.SysFont(None, self.font_size) 
        self.x = x
        self.y = y
        self.level_id = level_id
        self.enebled = enebled

        Level.levels.append(self)

    def draw(self, surface):
        if self.enebled:
            pygame.draw.rect(surface, (100, 255, 0), (self.x-35, self.y-30, 70, 60), 4)
        else:
            pygame.draw.rect(surface, (255, 0, 0), (self.x-35, self.y-30, 70, 60), 0)
        text = self.font.render(f"Level: {self.level_id}", True, (255, 255, 255))
        surface.blit(text, (self.x-30, self.y-5))
    
    def check_input(self, events):
        """checks input to the startmenue.
        events: pygame.event"""
        if self.enebled:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if pygame.Rect(self.x-35, self.y-30, 70, 60).collidepoint(mouse_pos): 
                        print('click')
                        gs.level = self.level_id
                        gs.running = False
if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin":
    coin_img = pygame.image.load("coins/coin_01.png")
elif platform == "win32":
    coin_img = pygame.image.load("coins\\coin_01.png")
def display_coins(surface,font=pygame.font.SysFont('Comic Sans MS', 30)):
        COIN_X = 300
        img = pygame.transform.scale(coin_img, (coin_img.get_width(), coin_img.get_height()))
        surface.blit(img, (COIN_X-190, 50))
        text_surface = font.render("X", False, (255,255,255))
        text_rect = text_surface.get_rect(center=(COIN_X-120, 70))
        surface.blit(text_surface, text_rect)
        text_surface = font.render(str(gs.coin_count), False, (255,255,255))
        text_rect = text_surface.get_rect(center=(COIN_X-80, 70))
        surface.blit(text_surface, text_rect)


start_menu = Startmenu(display)
options = Options()


gs = gamestate
def main(coins,game_options,level_count):

    for index, l in enumerate(Level.levels):
        if index <= level_count:
            l.enebled = True
        else:
            l.enebled = False

    gs.Options_prototype = game_options
    gs.coin_count = coins
    gs.running = True
    while gs.running:
        display.fill((0,0,0))

        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.QUIT:
                gs.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    gs.running = False
                    gs.level = "exit"
        options.draw(display)
        start_menu.check_input(events)
        for texts in PulsatingText.Texts:
            texts.update()
            texts.draw()
        start_menu.draw()
        display_coins(display)
        pygame.display.flip()
    if not gs.level == "exit" and gs.level < len(Level.levels):
        Level.levels[gs.level].enebled = True
    return (gs.level,gs.Options_prototype)

if __name__ == '__main__':
    main(0,gs.Options_prototype)