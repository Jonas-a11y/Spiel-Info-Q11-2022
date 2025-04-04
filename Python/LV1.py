import pygame
from PIL import Image
import time
import math
import os
import main as main_script
import optionen as optionen_screen












import socket
import threading
import json
import time
import pygame

class NetworkClient:
    def __init__(self, server_ip, server_tcp_port, get_position_callback, update_callback=None):
        """
        server_ip, server_tcp_port: Server-Verbindungsdaten.
        get_position_callback: Funktion, die beim Aufruf ein Dict {"x": ..., "y": ...} zurückgibt.
        update_callback: Optionaler Callback, der bei Erhalt von Remote-Player-Daten aufgerufen wird.
        """
        self.server_ip = server_ip
        self.server_tcp_port = server_tcp_port
        self.get_position = get_position_callback
        self.update_callback = update_callback
        
        self.shot_queue = []

        self.sock = None
        self.my_id = None
        self.running = False
        self.remote_players = {}  # { "player_id": {"x": ..., "y": ...} }
        if platform == "linux" or platform == "linux2":
            pass
        elif platform == "darwin":
            self.image = pygame.image.load("Bilder/downloads/turret1.png").convert_alpha()
            self.image2 = pygame.image.load("Bilder/downloads/turret_2.png").convert_alpha()
        elif platform == "win32":
            self.image = pygame.image.load("Bilder\\downloads\\turret1.png").convert_alpha()
            self.image2 = pygame.image.load("Bilder\\downloads\\turret_2.png").convert_alpha()
        size=(130,150)
        self.image = pygame.transform.scale(self.image, size)

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_ip, self.server_tcp_port))
        self.running = True
        print("Mit dem Server verbunden:", self.server_ip)
        threading.Thread(target=self.receive_messages, daemon=True).start()
        threading.Thread(target=self.send_updates_loop, daemon=True).start()

    def send_json(self, data):
        try:
            message = json.dumps(data) + "\n"
            self.sock.sendall(message.encode())
        except Exception as e:
            print("Fehler beim Senden von JSON:", e)

    def receive_messages(self):
        sock_file = self.sock.makefile('r')
        while self.running:
            try:
                line = sock_file.readline()
                if not line:
                    print("Verbindung zum Server verloren!")
                    self.running = False
                    break
                try:
                    message = json.loads(line)
                except Exception as e:
                    print("JSON-Decode-Fehler:", e)
                    continue
                if message.get("type") == "assign":
                    self.my_id = message["id"]
                    print("Zugewiesene Spieler-ID:", self.my_id)
                elif message.get("type") == "players":
                    players = message.get("players", {})
                    # Entferne den eigenen Eintrag
                    if self.my_id is not None:
                        players.pop(str(self.my_id), None)
                    self.remote_players = players
                    if self.update_callback:
                        self.update_callback(players)
            except Exception as e:
                print("Fehler beim Empfangen von Nachrichten:", e)
                break

    def send_updates_loop(self, tick_rate=30):
        update_interval = 1 / tick_rate
        print("Update-Loop gestartet")
        while self.running:
            try:
                pos = get_player_position()  # Erwartet dict {"x":..., "y":...}
                print("Shots:",self.shot_queue)
                if len(self.shot_queue) > 0:
                    msg = {"type": "update", "x": pos["x"], "y": pos["y"], "hp": player.health, "shots": self.shot_queue[0]}
                    self.shot_queue.pop(0)
                    print(msg)
                else:
                    msg = {"type": "update", "x": pos["x"], "y": pos["y"], "hp": player.health}
                print(msg)
                self.send_json(msg)
            except Exception as e:
                print("Fehler beim Senden der Updates:", e)
            time.sleep(update_interval)

    def render(self, surface, world_offset=0, color=(0, 0, 255), size=(50, 50)):
        """
        Zeichnet die entfernten Spieler (als einfache Rechtecke) auf dem übergebenen Surface.
        world_offset wird zu den x-Koordinaten addiert.
        """
        for pid, pos in self.remote_players.items():
            if pid not in MultiplayerEnemy.multi_enemy_list:
                MultiplayerEnemy(pid, (pos.get("x", 0) + world_offset, pos.get("y", 0)))
            remote_x = pos.get("x", 0) + world_offset
            remote_y = pos.get("y", 0)
            remote_hp = pos.get("hp", 7)
            remote_shots = pos.get("shots", 0)
            if remote_shots != 0:
                shot(remote_shots["cords_target"], remote_shots["coordinates_origin"], False , remote_shots["shot_speed"])
            MultiplayerEnemy.multi_enemy_list[pid].x = remote_x
            MultiplayerEnemy.multi_enemy_list[pid].y = remote_y
            MultiplayerEnemy.multi_enemy_list[pid].hp = remote_hp
            MultiplayerEnemy.multi_enemy_list[pid].draw(surface)
            MultiplayerEnemy.multi_enemy_list[pid].display_health_bar()

    def disconnect(self):
        self.running = False
        if self.sock:
            self.sock.close()


# Beispiel: Callback, der die aktuelle Spielerposition zurückgibt
def get_player_position():
    if player:
        return {"x": player.x-world.x, "y": player.y}
    else:
        return {"x": 0, "y": 0}

# (Optional) Callback, falls du etwas bei Empfang remote Daten machen möchtest
def update_remote_players(players):
    # Hier könntest du z. B. Debug-Informationen ausgeben oder weitere Logik anstoßen.
    pass

# Definiere deine Server-IP und den Port (anpassen oder über Discovery ermitteln)
SERVER_IP = "127.0.0.1"   # z. B. für lokale Tests
SERVER_TCP_PORT = 5000




class MultiplayerEnemy():
    multi_enemy_list = {}
    def __init__(self, id, coordinates=(1200,700) , hp=7, size=(100, 150)):
        MultiplayerEnemy.multi_enemy_list[id] = self
        self.id = id
        self.hp = hp
        self.size = size
        self.coordinates = coordinates
        self.x, self.y = coordinates
        self.max_health = hp
        
        self.image = pygame.image.load("Bilder/downloads/turret1.png").convert_alpha() 
        self.image = pygame.transform.scale(self.image, size)
    
    def draw(self, surface:pygame.surface):
        if self.x > player.x:
            surface.blit(pygame.transform.flip(self.image, True, False), (self.x,self.y))
        else:
            surface.blit(self.image, (self.x,self.y))
        self.display_health_bar()
        
    def display_health_bar(self):
        """displayed the health bar"""
        color = (int(255-255*(self.hp/self.max_health)),int(255*(self.hp/self.max_health)),0)
        pygame.draw.rect(display, color,pygame.Rect(self.x,self.y-25,100,20),3)
        pygame.draw.rect(display, color,pygame.Rect(self.x,self.y-25,100*(self.hp/self.max_health),20))
    





def shot_send_to_server(cords_target, coordinates_origin, shot_by_player, shot_speed=1):
    print("Shot send to server")
    print(gs.server)
    if gs.server:
        gs.network_client.shot_queue.append({"cords_target": cords_target, "coordinates_origin": coordinates_origin, "shot_by_player": shot_by_player, "shot_speed": shot_speed})
    else:
        pass

from sys import platform


pygame.init()
# pygame.mouse.set_visible(False)
info_object = pygame.display.Info()
screen_size = (info_object.current_w, info_object.current_h)

# Geschwindigkeit zum Laufen zur Seite
SPEED_LATERAL = 10

# Geschwindigkeit des Spieles in Hz, wird angepasst um verschiedene Monitorgeschwindigkeiten zu nutzten, ohne PyGame typisches tearing bei fixer Wiederholungsrate
RUN_SPEED = 60

# Position der Spiel UI / Reload und Schussanzahl-Animation
UI_X = 30
UI_Y = screen_size[1] - 300

# zur Unterstützung verschiedener Monitorgrößen
ASPECT_RATIO = 11200//1080
LEVEL_WIDTH = screen_size[1]*ASPECT_RATIO
print(ASPECT_RATIO)

MARGIN = 20

display = pygame.display.set_mode(screen_size, pygame.FULLSCREEN | pygame.SCALED, vsync=True)

# Get the number of displays
num_displays = pygame.display.get_num_displays()
print(f"Number of displays: {num_displays}")

if platform == "darwin":
    import ctypes
    # Load SDL2 shared library
    sdl = ctypes.CDLL(None)

    # Define SDL2 structure
    class SDL_DisplayMode(ctypes.Structure):
        _fields_ = [("format", ctypes.c_uint),
                    ("w", ctypes.c_int),
                    ("h", ctypes.c_int),
                    ("refresh_rate", ctypes.c_int),
                    ("driverdata", ctypes.c_void_p)]

    # Define SDL2 functions
    SDL_GetDisplayMode = sdl.SDL_GetDisplayMode
    SDL_GetDisplayMode.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(SDL_DisplayMode)]
    SDL_GetDisplayMode.restype = ctypes.c_int

    # Iterate over each display and get its refresh rate.
    # Sets the Refreshrate to the Last detected Monitor (Wenn ein Sekundärer Monitor angeschlossen ist, wird dessen Geschwindigkeit genommen!)
    for display_index in range(num_displays):
        mode = SDL_DisplayMode()
        if SDL_GetDisplayMode(display_index, 0, ctypes.pointer(mode)) != 0:
            print(f"Could not get display mode for display {display_index}")
            continue
        
        print(f"Display {display_index}:")
        print(f"  Resolution: {mode.w}x{mode.h}")
        print(f"  Refresh rate: {mode.refresh_rate} Hz")
        RUN_SPEED = 60
        RUN_SPEED = RUN_SPEED/mode.refresh_rate

if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin":
    background = pygame.image.load('Bilder/Level 1/Level1_11200x1080_V3.1_hintergrund_1.png').convert()
    background_foreground = pygame.image.load('Bilder/Level 1/Level1_11200x1080_V3.3_vordergrund.png').convert_alpha()
    background_middle_foreground = pygame.image.load('Bilder/Level 1/Level1_11200x1080_V3.2_hintergrund_2.png').convert_alpha()

    pass
elif platform == "win32":
    background = pygame.image.load('Bilder\\Level 1\\Level1_11200x1080_V3.1_hintergrund_1.png').convert()
    background_foreground = pygame.image.load('Bilder\\Level 1\\Level1_11200x1080_V3.3_vordergrund.png').convert_alpha()
    background_middle_foreground = pygame.image.load('Bilder\\Level 1\\Level1_11200x1080_V3.2_hintergrund_2.png').convert_alpha()
    import win32api

    device = win32api.EnumDisplayDevices()
    print((device.DeviceName, device.DeviceString))
    settings = win32api.EnumDisplaySettings(device.DeviceName, -1)
    for varName in ['Color', 'BitsPerPel', 'DisplayFrequency']:
        print("%s: %s"%(varName, getattr(settings, varName)))
        if varName == 'DisplayFrequency':
            RUN_SPEED = RUN_SPEED/getattr(settings, varName)

# initialisiert die Hintergrund Bilder (Vordergrund, 2 Hintergrundbilder für Paralaxeneffekt)
background = pygame.transform.scale(background, (screen_size[1]*ASPECT_RATIO, screen_size[1]))
background_foreground = pygame.transform.scale(background_foreground, (screen_size[1]*ASPECT_RATIO, screen_size[1]))
background_middle_foreground = pygame.transform.scale(background_middle_foreground, (screen_size[1]*ASPECT_RATIO, screen_size[1]))

print("Run Speed: ", RUN_SPEED)

# Array mit Gegnerinformationen die für die Initialisierung der Gegner verwendet werden
level1_enemies_positiones = [[(LEVEL_WIDTH*0.2,0.75*screen_size[1]),1,0.5,1],[(LEVEL_WIDTH*0.25,0.605*screen_size[1]),2,1,0.5],[(LEVEL_WIDTH*0.316,0.305*screen_size[1]),5,1],[(LEVEL_WIDTH*0.511,screen_size[1]*0.115),5,3,0.4],[(LEVEL_WIDTH*0.55,screen_size[1]*0.73),5,1],[(LEVEL_WIDTH*0.675,0.36*screen_size[1]),5,1],[(LEVEL_WIDTH*0.68,screen_size[1]*0.75),5,1]]

class GameState:
    # eine Art globale variablen zu machen, ohne globale variablen zu verwenden
    def __init__(self):
        self.running = False
        self.dt_last_frame = 1
        self.dead = False
        self.shooting_enebled = False
        self.movement_enebled = False
        self.end_of_game = False
        self.server=True
        self.network_client = None
        self.Options_prototype = {
            "master volume":1,
            "jump volume":1,
            "shot volume":1,
        }
        
        try:
            # Initialisiere den Netzwerk-Client und verbinde dich
            self.network_client = NetworkClient(SERVER_IP, SERVER_TCP_PORT, get_player_position, update_remote_players)
            self.network_client.connect()
            print("Verbindung zum Server hergestellt.")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.server = False

gs = GameState()
class enemy:
    enemies = []
    def __init__(self,coordinates, hp, shots_per_seconds,shot_speed=1,size=(100,150),) -> None:
        """Initializes an Enemy Object
        
        (world)coordinates: x,y.
        
        hp: health.
        
        shots_per_second: Shots the enemy can fire per Second.
        
        shot_speed: Speed of the shots fired.
        
        size: Size of the Enemys"""
        enemy.enemies.append(self)
        self.shot_ofset = 0
        self.size = size
        self.last_shot_fired = 0
        self.shots_per_seconds = shots_per_seconds
        self.coordinates = coordinates
        self.x, self.y = coordinates
        self.max_health = hp
        self.health = hp
        self.shot_speed = shot_speed
        self.is_right = False
        if platform == "linux" or platform == "linux2":
            pass
        elif platform == "darwin":
            self.image = pygame.image.load("Bilder/downloads/turret1.png").convert_alpha()
            self.image2 = pygame.image.load("Bilder/downloads/turret_2.png").convert_alpha()
        elif platform == "win32":
            self.image = pygame.image.load("Bilder\\downloads\\turret1.png").convert_alpha()
            self.image2 = pygame.image.load("Bilder\\downloads\\turret_2.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.image2 = pygame.transform.scale(self.image2, [s/2 for s in size])


    def draw(self, surface:pygame.surface):
        """Draws this Enemy onto the Pygame Surface"""
        if -world.x + player.x > self.x: # Flippt den Gegner damit dieser immer in die Richtung des Spielers schaut.
            surface.blit(pygame.transform.flip(self.image, True, False), (self.coordinates[0] + world.x,self.coordinates[1]))
            d = self.set_direction()
            d = -get_rotation_angle(d)
            image2 = pygame.transform.flip(self.image2, False, True)
            image2 = pygame.transform.rotate(image2,d)
            surface.blit(image2, (self.coordinates[0] + world.x+40,self.coordinates[1]+20))
            self.is_right = True
        else:
            surface.blit(self.image, (self.coordinates[0] + world.x,self.coordinates[1]))
            d = self.set_direction()
            d = -get_rotation_angle(d)
            image2 = pygame.transform.rotate(self.image2,d)
            surface.blit(image2, (self.coordinates[0] + world.x-20,self.coordinates[1]+20))
            self.is_right = False
        self.display_health_bar()

    def set_direction(self):
        """Sets the x,y velocity for the shotdirection"""
        cords_target = [player.x + player.rect.w/2 - world.x, player.y + player.rect.h/2]
        coords_origin = [self.x+10, self.y+80]
        x,y = coords_origin
        v = [x - cords_target[0], y - cords_target[1]]
        v_l = math.sqrt(v[0]**2 + v[1]**2)
        v = [(i/v_l)*10 for i in v]
        return v

    def check_for_hit(self, coordinates) -> bool:
        """Takes Coordinates of the shot. If hit, returnes true."""
        x,y = coordinates
        if x > self.x and x < self.x+self.image.get_width():
            if y > self.y and y < self.y + self.image.get_height():
                return True
        return False

    
    def is_hit(self):
        """if it is hit, removes one hp. When at 0 hp, deletes the enemy"""
        self.health -= 1
        if self.health <= 0:
            enemy.enemies.remove(self)
            Collectable(self.x+self.image.get_width()//2, self.y+ self.image.get_height()//2)
        main_script.sound_hit()

    def display_health_bar(self):
        """displayed the health bar"""
        color = (int(255-255*(self.health/self.max_health)),int(255*(self.health/self.max_health)),0)
        pygame.draw.rect(display, color,pygame.Rect(self.coordinates[0] + world.x,self.coordinates[1]-25,100,20),3)
        pygame.draw.rect(display, color,pygame.Rect(self.coordinates[0] + world.x,self.coordinates[1]-25,100*(self.health/self.max_health),20))

    def fire_shot(self):
        """fires a shot from the enemy towards the player"""
        if (time.time() - self.last_shot_fired) > (1/self.shots_per_seconds) and abs(player.x + player.rect.w/2 - world.x - self.x) < 1000:
            shot([player.x + player.rect.w/2 - world.x, player.y + player.rect.h/2],[self.x if not self.is_right else self.x+self.size[0]-30, self.y+45],False,self.shot_speed)
            self.last_shot_fired = time.time()

# legt für jeden Gegner ein Gegner Objekt an
for e in level1_enemies_positiones:
    enemy(*e) 

class DialogBox:
    """Instance of the Dialogbox to be displayed."""
    boxes = []
    def __init__(self, messages, cords, font=pygame.font.SysFont('Comic Sans MS', 30), color=(255, 255, 255)):
        """defines an Instance of the DialogBox.
        
        messages: Array of Strings to display one after the other.
        
        cords: Coordinates where to display the Dialog Box.
        
        font: pygame Font.
        
        color: Color of the Dialog Box."""
        self.coordinates = cords
        self.messages = messages
        self.current_message = 0
        self.font = font
        self.color = color
        self.text_surfaces = [font.render(msg, False, self.color) for msg in messages]
        DialogBox.boxes.append(self)

    def next_message(self):
        self.current_message += 1

    def draw(self, win):
        # If we are out of messages, don't draw anything
        if self.current_message >= len(self.messages):
            gs.shooting_enebled = True
            gs.movement_enebled  = True
            DialogBox.boxes.remove(self)
            if gs.end_of_game:
                gs.running = False
            return

        text_surface = self.text_surfaces[self.current_message]
        text_rect = text_surface.get_rect(center=self.coordinates)
        bubble_rect = text_rect.inflate(2*MARGIN, MARGIN)
        pygame.draw.rect(win, self.color, bubble_rect, 2)  # Speech bubble
        pygame.draw.polygon(win, self.color, [(bubble_rect.bottomleft[0], bubble_rect.bottomleft[1]-10),
                                               (bubble_rect.bottomleft[0]-5, bubble_rect.bottomleft[1] + 5),
                                               (bubble_rect.bottomleft[0]+10, bubble_rect.bottomleft[1])])  # Little triangle
        win.blit(text_surface, text_rect)  # Text

class Collectable:
    # das ist ein Beispiel für ein collectable. Am ende sollten wahrscheinlich mehr sachen collectable sein als Münzen, und münzen werden wahrscheinlich keine collectables bleiben, aber als poc sind die wahrscheinlich ganz gut
    collectables = []
    def __init__(self, x, y):
        """Defines instance of a collectable.
        
        x,y: coordinates of the collectables animation"""
        self.x = x
        self.y = y
        self.img_frames = []
        self.load("coins")
        self.current_frame = 0
        self.last_frame_time = time.time()
        Collectable.collectables.append(self)

    def draw(self, surface):
        surface.blit(self.img_frames[self.current_frame], (self.x + world.x - self.img_frames[self.current_frame].get_width()//2,self.y))
        if time.time() - self.last_frame_time > 0.1:
            self.current_frame = (self.current_frame + 1)%len(self.img_frames)
            self.last_frame_time = time.time()
    
    def load(self, path):
        """loads the animation of the collectable.
        
        path: path to the folder of the animation."""
        filenames = sorted(os.listdir(path))
        print(filenames)
        for filename in filenames:
            filepath = os.path.join(path, filename)
            if filepath.endswith((".png")):
                # Lädt das Bild und fügt es zur Liste hinzu
                self.img_frames.append(pygame.image.load(filepath))

    def collision_with_player(self):
        """When the player collects the item"""
        if self.x > -world.x + player.x and self.x < -world.x + player.x + player.rect.width and self.y > player.y and self.y < player.y + player.rect.height:
            Collectable.collectables.remove(self)
            player.coin_count += 1
                


class ObstacleMap:
    # lädt das Bild der collision map. um Kollisionen an einem bestimmten Punkt zu überprüfen wird geschaut, ob die gegebene Koordinate auf dem Bild existiert oder nicht. existiert dort ein Pixel bedeutet das, dass dort ein Hinderniss ist.
    def __init__(self, image_path):
        """Instance of Obstacle map.
        
        image_path: path to obstacle map."""
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (screen_size[1]*ASPECT_RATIO, screen_size[1]))
        print((screen_size[1]*ASPECT_RATIO, screen_size[1]))

    def collides_horizontally_right(self, rect:pygame.Rect):
        for y in range(rect.y+25, rect.y + rect.h-25):
            try:
                if self.image.get_at((rect.x + rect.w, y)) != (0, 0, 0, 0):
                    return True
            except IndexError:
                pass
        return False
    
    def collides_horizontally_left(self, rect:pygame.Rect):
        for y in range(rect.y+25, rect.y + rect.h-25):
            try:
                if self.image.get_at((rect.x, y)) != (0, 0, 0, 0):
                    return True

            except IndexError:
                pass
        return False

    def collides_vertically_top(self, rect):
        for x in range(rect.x, rect.x + rect.w-10):
            try:
                if self.image.get_at((x, rect.y)) != (0, 0, 0, 0):
                    return True

            except IndexError:
                pass
        return False
    
    def collides_vertically_bottom(self, rect):
        for x in range(rect.x+4, rect.x + rect.w-10):
            try: 
                if self.image.get_at((x, rect.y + rect.h)) != (0, 0, 0, 0):
                    for y in range(int(rect.y+rect.h*0.5), rect.y + rect.h):
                            if self.image.get_at((rect.x+rect.w-10, y)) != (0, 0, 0, 0):
                                player.y = y-rect.h
                                break
                            if self.image.get_at((rect.x+10, y)) != (0, 0, 0, 0):
                                player.y = y-rect.h
                                break
                    return True
            except IndexError:
                pass
        return False
    
    def collides(self, rect:pygame.Rect):
        for y in range(rect.y, rect.y + rect.h):
            try:
                if self.image.get_at((rect.x, y)) != (0, 0, 0, 0):
                    return True

            except IndexError:
                pass

        for x in range(rect.x, rect.x + rect.w):
            try: 
                if self.image.get_at((x, rect.y)) != (0, 0, 0, 0):
                    return True
            except IndexError:
                pass

        return False
    

# initialisiert Obstacle Map
if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin":
    obstacle_map = ObstacleMap("Bilder/Level 1/Level1_11200x1080_V1_Collisions.png")

elif platform == "win32":
    obstacle_map = ObstacleMap("Bilder\\Level 1\\Level1_11200x1080_V1_Collisions.png")


class World:
    # initialisiert Verschiedene Welt-Aspekte, die global für dieses Level gelten sollen.
    def __init__(self):
        self.x = 0
        self.y = 0
        self.background_rect = background.get_rect()
        self.background_foreground_rect = background_foreground.get_rect()
        self.background_middle_foreground_rect = background_middle_foreground.get_rect()
        self.background = background
        self.background_foreground = background_foreground
        self.background_middle_foreground = background_middle_foreground

    def draw(self, surface):
        surface.blit(self.background, self.background_rect)
        surface.blit(self.background_middle_foreground, self.background_middle_foreground_rect)
        surface.blit(self.background_foreground, self.background_foreground_rect)

        # self.font = pygame.font.SysFont(None, 18) 
        # text = self.font.render(f"Wo bin ich? {self.x}", True, (200, 200, 200))
        # display.blit(text, (screen_size[0]-145, 80))

    def move(self, dx):
        """moves the background (so that it appeares that the player is moving).
        
        dx: how much to move the background on the x-axis."""
        if(self.x <= 0 or dx < 0):
            self.x += dx
            self.background_foreground_rect = self.background_foreground_rect.move(dx,0)
            self.background_middle_foreground_rect = self.background_middle_foreground_rect.move(dx/2,0)
            self.background_rect = self.background_rect.move(dx/4,0)


class Player:
    def __init__(self):
        """defines the instance of a player."""
        self.x, self.y = screen_size[0] // 2, screen_size[1] // 2
        self.dy = 0
        self.jump_enabled = True
        self.gravity = RUN_SPEED # Je schneller das Spiel läuft, umso geringer ist die Gravitation
        self.jump_height = 22
        self.scale = 0.15
        if platform == "linux" or platform == "linux2":
            pass
        elif platform == "darwin":
            self.animation_frames = self.load_gif("Bilder/Objekte/Test 2 Animation running 1.gif",self.scale)
            self.animation_frames_jumping_up = self.load_gif("Bilder/Objekte/Test 2 Animation running 1.gif",self.scale)
            self.health_bar_gif_folder_path = "Bilder/IO/Health_gifs"
            self.img_health = pygame.image.load("Bilder/IO/Health_gifs/Health8.png")
            self.coin_img = pygame.image.load("coins/coin_01.png")
        elif platform == "win32":
            self.animation_frames = self.load_gif("Bilder\\Objekte\\Test 2 Animation running 1.gif",self.scale)
            self.animation_frames_jumping_up = self.load_gif("Bilder\\Objekte\\Test 2 Animation running 1.gif",self.scale)
            self.health_bar_gif_folder_path = "Bilder\\IO\\Health_gifs"
            self.img_health = pygame.image.load("Bilder\\IO\\Health_gifs\\Health8.png")
            self.coin_img = pygame.image.load("coins\\coin_01.png")
        self.coin_img = pygame.transform.scale(self.coin_img, (self.coin_img.get_width(), self.coin_img.get_height()))
        self.img_health = pygame.transform.scale(self.img_health, (self.img_health.get_width() * 2, self.img_health.get_height() * 2))
        self.animation_frames.pop(0)
        self.current_frame = 0
        self.rect = self.animation_frames[0].get_rect()
        self.walking_right = False
        self.walking_left = False
        self.crouch = False
        self.last_jump = time.time()

        self.coin_count = 0
        self.health = 7
        self.health_bar_current_frame = 0
        self.haelth_bar_gifs = self.load_gifs(self.health_bar_gif_folder_path)

    @staticmethod
    def load_gif(path, scale):
        """loads a animation, returns the single animation frames.
        
        path: path to GIF / Animation.
        
        scale: how to scale the animationframes."""
        img = Image.open(path)
        frames = []
        try:
            while True:
                frame = pygame.image.fromstring(img.tobytes(), img.size, img.mode).convert_alpha()
                frame = pygame.transform.scale(frame, (frame.get_width() * scale, frame.get_height() * scale))
                frame.set_colorkey((255,255,255))  # Make white (also the default) color transparent
                frames.append(frame)
                img.seek(len(frames))
        except EOFError:
            pass
        return frames

    def draw(self, surface):
        image = self.animation_frames[int(self.current_frame)]
        if self.dy < 0: # wenn der Spieler nach oben springt
            image = self.animation_frames_jumping_up[1]
            image = pygame.transform.scale(image, (image.get_width(), image.get_height()))
            image.set_colorkey((255,255,255))
        current_width, current_height = image.get_size()
        if self.walking_left:
            image = pygame.transform.flip(image, True, False)
            image.set_colorkey((255,255,255))
        if self.crouch:
            image = pygame.transform.scale(image, (current_width, current_height*0.5))
            image.set_colorkey((255,255,255))  # Make white (also the default) color transparent
        self.rect = image.get_rect()

        surface.blit(image, (self.x, self.y))  

    def jump(self):
        """lets the player jump"""
        test_rect = pygame.Rect(player.x - world.x, player.y, player.rect.w, player.rect.h).move(0, 2*self.dy)
        if obstacle_map.collides_vertically_bottom(test_rect) and self.jump_enabled:
            self.dy -= self.jump_height
            if (time.time() - self.last_jump) > 0.3:
                self.last_jump = time.time()
                main_script.sound_jump()

    def damage(self, damage):
        """deducts damage from players health.
        
        damage: how much to deduct from player hp"""
        godemode = False
        pygame.draw.rect(display, (255,0,0),pygame.Rect(0,0,screen_size[0],screen_size[1]),4)
        if not godemode:
            self.health -= damage
            if self.health < 0:
                self.health = 0
                gs.dead = True
                world.__init__()
                gs.dead = False
                self.health = 7

    def display_health(self, surface):
        """displayes the players health on the given surface."""
        if self.health == 7:
            surface.blit(self.img_health, (UI_X+170, UI_Y+50))
        else: 
            surface.blit(self.haelth_bar_gifs[self.health][int(self.health_bar_current_frame)], (UI_X+170, UI_Y+50))
            self.health_bar_current_frame = (self.health_bar_current_frame + 0.25) % 7
    
    def display_coins(self, surface,font=pygame.font.SysFont('Comic Sans MS', 30)):
        """display the players coin count."""
        surface.blit(self.coin_img, (screen_size[0]-190, 50))
        text_surface = font.render("X", False, (255,255,255))
        text_rect = text_surface.get_rect(center=(screen_size[0]-120, 70))
        surface.blit(text_surface, text_rect)
        text_surface = font.render(str(self.coin_count), False, (255,255,255))
        text_rect = text_surface.get_rect(center=(screen_size[0]-80, 70))
        surface.blit(text_surface, text_rect)
       
    def load_gifs(self, path):
        all_gifs = []
        filenames = sorted(os.listdir(path))
        print(filenames)
        for filename in filenames:
            filepath = os.path.join(path, filename)
            if filepath.endswith((".gif")):
                # Lädt das Bild und fügt es zur Liste hinzu
                gif = self.load_gif(filepath,2)
                gif.pop(0)
                all_gifs.append(gif)
        return all_gifs
    
    def check_for_hit(self, coordinates) -> bool:
        """checkes if the player is hit"""
        image = self.animation_frames[1]
        x,y = coordinates
        if x > self.x-world.x and x < self.x - world.x + image.get_width():
            if y > self.y and y < self.y + image.get_height():
                return True
        return False
                

    def update(self):
        """updates position of the player, checks for obstacles"""
        self.prev_x, self.prev_y = self.x, self.y  # Remember previous position
        self.dy += self.gravity
        test_rect = pygame.Rect(self.x - world.x, self.y, self.rect.w, self.rect.h).move(0, self.dy)
        
        if obstacle_map.collides_vertically_top(test_rect) and self.dy < 0:
            self.dy = 0

        if not obstacle_map.collides_vertically_bottom(test_rect):
            self.y += self.dy 
        elif not self.dy < 0:
            self.dy = 0

        # Laufgeschwindigkeit der Animation wird an die Geschwindigkeit des Monitors angepasst.
        if(self.walking_right):
            self.current_frame = (self.current_frame + gs.dt_last_frame/4 * 1) % (len(self.animation_frames))
        elif(self.walking_left):
            self.current_frame = (self.current_frame + gs.dt_last_frame/4 * 1) % (len(self.animation_frames))
        else:
            self.current_frame = 3
        if -world.x + self.x >= screen_size[1]*11200/1080 - screen_size[0]//2:
            gs.movement_enebled = False
            if DialogBox.boxes == []:
                gs.end_of_game = True
                DialogBox(["Wow, du hast es geschafft!", "Bist du bereit weiter zu gehen?"],(player.x+100, 700))

def get_rotation_angle(velocity):
    """get rotation angles so that something faces the correct direction.
    
    velocity: [x velocity, y velocity]"""
    # velocity[0] is horizontal speed
    # velocity[1] is vertical speed
    if velocity[0]==0: # this conditional logic is done in order to handle the case whenever horizontal speed becomes zero to avoid zero division error
        return 90 if velocity[1]>0 else 270
    angle_in_radians = math.atan(velocity[1]/velocity[0])
    # convert radian to degree
    angle_in_degree = math.degrees(angle_in_radians)
    #Finding appropriate quadrant of angle
    if velocity[0]>0 and velocity[1]>0:
        final_angle = angle_in_degree
    elif velocity[0]<0 and velocity[1]>0:
        final_angle = 180 + angle_in_degree
    elif velocity[0]<0 and velocity[1]<0:
        final_angle = 180 + angle_in_degree
    elif velocity[0]>0 and velocity[1]<0:
        final_angle = 360 + angle_in_degree
    else:
        final_angle = angle_in_degree
    return final_angle

class shot:
    """defines the shot class"""
    shots_list = []
    last_shot_fired = 0
    shots_left = 4
    is_reloading = False
    if platform == "linux" or platform == "linux2":
        pass
    elif platform == "darwin":
        animation_frames = Player.load_gif("Bilder/IO/reload.webp",0.1)
        image = pygame.image.load("Bilder/downloads/rocket_enemy.png")
    elif platform == "win32":
        animation_frames = Player.load_gif("Bilder\\IO\\reload.webp",0.1)
        image = pygame.image.load("Bilder\\downloads\\rocket_enemy.png")
    current_frame = 0
    last_frame_time = 0
        
    def __init__(self, cords_target, coordinates_origin, shot_by_player, shot_speed=1):
        """initializes a new shot.
        
        cords_target: target coordinates (to where the shot should fly).
        
        coordinates origin: where to spawn the shot, x,y position, to figure out angle.
        
        shot_by_player: if the shot is shot by a player.
        
        shot speed: speed of the bullet."""
        self.shot_speed = shot_speed
        if (time.time() - shot.last_shot_fired) > 0.2 and shot.shots_left > 0 and shot_by_player and gs.shooting_enebled:
            shot.shots_list.append(self)
            self.shot_by_player = shot_by_player
            self.image = pygame.transform.scale(self.image, (50,10))
            self.velocity = self.set_velocities(cords_target, coordinates_origin)
            v = -get_rotation_angle(self.velocity)
            self.image = pygame.transform.rotate(self.image,v)
            self.coordinates = coordinates_origin
            shot.last_shot_fired = time.time()
            shot.shots_left -= 1
            shot_send_to_server(cords_target, coordinates_origin, shot_by_player, shot_speed=1)
            main_script.sound_shot()
        elif not shot_by_player and gs.shooting_enebled:
            shot.shots_list.append(self)
            self.shot_by_player = shot_by_player
            if platform == "linux" or platform == "linux2":
                pass
            elif platform == "darwin":
                self.image = pygame.image.load("Bilder/downloads/rocket_enemy.png")
            elif platform == "win32":
                self.image = pygame.image.load("Bilder\\downloads\\rocket_enemy.png")
            self.image = pygame.transform.scale(self.image, (35,20))
            self.velocity = self.set_velocities(cords_target, coordinates_origin)
            v = -get_rotation_angle(self.velocity)
            self.image = pygame.transform.rotate(self.image,v)
            self.coordinates = coordinates_origin
        elif shot.shots_left <= 0 and shot.is_reloading == False and (time.time() - shot.last_shot_fired) > 0.2:
            shot.is_reloading = True
    
    def move(self):
        """moves the shot one frame. If it hits the player / enemy it deals damage. if it exits the bounds or hits an obstacle, the shot despawns."""
        self.coordinates[0] += self.velocity[0]*RUN_SPEED*self.shot_speed
        self.coordinates[1] += self.velocity[1]*RUN_SPEED*self.shot_speed

        test_rect = pygame.Rect(self.coordinates[0], self.coordinates[1], 5, 5)
        for enem in enemy.enemies:
            if enem.check_for_hit(self.coordinates) and self.shot_by_player:
                shot.shots_list.remove(self)
                enem.is_hit()
        if obstacle_map.collides(test_rect):
            shot.shots_list.remove(self)
        if abs(self.coordinates[1]) > screen_size[1]:
            shot.shots_list.remove(self)
        if player.check_for_hit(self.coordinates) and not self.shot_by_player:
            player.damage(1)
            shot.shots_list.remove(self)

    def reload_animation(surface):
        """initializes the reloading animation."""
        surface.blit(shot.animation_frames[shot.current_frame], (UI_X, UI_Y))
        if time.time() - shot.last_frame_time > 0.2:
            shot.current_frame = (shot.current_frame + 1)%len(shot.animation_frames)
            if shot.current_frame % 3 == 0:
                main_script.sound_reloading
            if shot.current_frame % len(shot.animation_frames) == 0:
                shot.is_reloading = False
                shot.shots_left = 4
            shot.last_frame_time = time.time()

    def display_magazine(surface):
        """displayes the current number of shots remaining"""
        if shot.shots_left > 0:
            surface.blit(shot.animation_frames[int(shot.shots_left * 3)-2], (UI_X, UI_Y))
        elif shot.is_reloading == False:
            surface.blit(shot.animation_frames[0], (UI_X, UI_Y))
            if (time.time() - shot.last_shot_fired) > 0.5:
                shot.is_reloading = True
        else:
            shot.reload_animation(surface)


    def set_velocities_mouse(self) -> list:
        
        x,y = pygame.mouse.get_pos()
        v = [x - (player.x + player.rect.w/2), y - (player.y + player.rect.h/2)]
        v_l = math.sqrt(v[0]**2 + v[1]**2)
        v = [(i/v_l)*10 for i in v]
        return v
    
    def set_velocities(self, coords_origin, cords_target) -> list:
        x,y = coords_origin
        v = [x - cords_target[0], y - cords_target[1]]
        v_l = math.sqrt(v[0]**2 + v[1]**2)
        if self.shot_by_player:
            v = [(i/v_l)*15 for i in v]
        else:
            v = [(i/v_l)*10 for i in v]
        return v
    
    def draw(self,surface):
        surface.blit(self.image, (self.coordinates[0] + world.x, self.coordinates[1]))


# initialisiert die Welt, den Spieler und die Dialogboxen
world = World()
player = Player()
FPS = pygame.time.Clock()
DialogBox(["Hello!", "How are you?", "Good Luck!"], (screen_size[0]//2 + 200,580))

#Haupt Game loop, wird aus main.py gestartet
def main(optionen): 
    gs.Options_prototype = optionen
    gs.running = True
    while gs.running:

        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.QUIT:
                gs.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    optionen = optionen_screen.main(optionen)
                    if optionen_screen.gs_optionen.level == 'exit':
                        gs.running = False
                if event.key == pygame.K_SPACE:
                    dialog.next_message()

            if event.type == pygame.MOUSEBUTTONUP:
                cords = pygame.mouse.get_pos()
                shot([cords[0] - world.x, cords[1]],[player.x + player.rect.w/2 - world.x, player.y + player.rect.h/2],True)

        # man kann sich nur bewegen wenn die Bewegung freigegeben ist (nach den Dialognachrichten), springen nur wenn man gerade auf dem Boden ist.
        if keys[pygame.K_SPACE] and gs.movement_enebled:
            if not player.dy < 0:
                player.jump()

        if keys[pygame.K_d] and gs.movement_enebled:
                test_rect = pygame.Rect((player.x - world.x), player.y, player.rect.w, player.rect.h).move(1, 0)
                if not obstacle_map.collides_horizontally_right(test_rect):
                    world.move(-SPEED_LATERAL*RUN_SPEED)
                    player.walking_right = True
        else:
            player.walking_right = False

        if keys[pygame.K_a] and gs.movement_enebled:

                test_rect = pygame.Rect(player.x - world.x, player.y, player.rect.w, player.rect.h).move(-1, 0)
                if not obstacle_map.collides_horizontally_left(test_rect):
                    world.move(SPEED_LATERAL*RUN_SPEED)
                    player.walking_left = True
        else:
            player.walking_left = False

        #Spieler kriecht. Sprünge sind dann deaktiviert
        if keys[pygame.K_LSHIFT] and gs.movement_enebled:
            player.crouch = True
            player.jump_enabled = False
        elif player.crouch == True:
            player.jump_enabled = True
            player.y -= player.rect.size[1]
            player.crouch = False


        display.fill((0,0,0))
        player.update()
        world.draw(display)
        player.draw(display)
        if gs.server:
            # Zeichne die entfernten Spieler (z. B. als blaue Rechtecke)
            gs.network_client.render(display, world_offset=world.x)
        
        shot.display_magazine(display)
        player.display_health(display)
        player.display_coins(display)
        for dialog in DialogBox.boxes:
            dialog.draw(display)
        for item in Collectable.collectables:
            item.collision_with_player()
            item.draw(display)
        for shots in shot.shots_list:
            shots.move()
            shots.draw(display)
        
        for e in enemy.enemies:
            e.fire_shot()
            e.draw(display)

        pygame.display.flip()
        gs.dt_last_frame = FPS.tick()/17
    # Falls nötig, beim Beenden die Verbindung sauber trennen
    gs.network_client.disconnect()
    return (player.coin_count, gs.end_of_game)

if __name__ == "__main__":
    main([gs.Options_prototype])
