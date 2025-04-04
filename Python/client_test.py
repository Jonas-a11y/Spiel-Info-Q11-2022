import pygame
import socket
import threading
import json
import time
import sys

TCP_PORT = 5000
UDP_PORT = 5001
BUFFER_SIZE = 1024
DISCOVERY_MESSAGE = "DISCOVER_SERVER"
DISCOVERY_TIMEOUT = 5  # Sekunden

players = {}       # Aktuelle Spielerpositionen, wie sie vom Server empfangen werden
my_player_id = None
my_x, my_y = 100, 100  # Startposition des lokalen Spielers
speed = 5             # Bewegungsgeschwindigkeit

def send_json(sock, data):
    """Sendet ein JSON-Objekt, terminiert durch einen Zeilenumbruch."""
    try:
        message = json.dumps(data) + "\n"
        sock.sendall(message.encode())
    except Exception as e:
        print("Fehler beim Senden von JSON:", e)

def discover_server(timeout=DISCOVERY_TIMEOUT):
    """Entdeckt den Server per UDP-Broadcast."""
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.settimeout(timeout)
    server_ip = None
    server_tcp_port = None

    try:
        udp_sock.sendto(DISCOVERY_MESSAGE.encode(), ('<broadcast>', UDP_PORT))
        data, addr = udp_sock.recvfrom(BUFFER_SIZE)
        response = data.decode().strip()
        if response.startswith("SERVER:"):
            server_tcp_port = int(response.split(":")[1])
            server_ip = addr[0]
            print("Server gefunden:", server_ip, "TCP Port:", server_tcp_port)
    except socket.timeout:
        print("Kein Server gefunden.")
    finally:
        udp_sock.close()

    return server_ip, server_tcp_port

def receive_messages(sock):
    """Empfängt Nachrichten vom Server und aktualisiert die Spielerpositionen."""
    global players, my_player_id
    sock_file = sock.makefile('r')
    while True:
        try:
            line = sock_file.readline()
            if not line:
                print("Verbindung zum Server verloren!")
                break
            try:
                message = json.loads(line)
            except json.JSONDecodeError as e:
                print("JSON Decode Error:", e)
                continue

            if message.get("type") == "assign":
                my_player_id = message["id"]
                print("Zugewiesene Spieler-ID:", my_player_id)
            elif message.get("type") == "players":
                players = message["players"]
        except Exception as e:
            print("Fehler beim Empfangen:", e)
            break

def send_update_loop(sock, tick_rate=30):
    """Sendet die aktuelle Position des Spielers in festen Intervallen."""
    update_interval = 1 / tick_rate
    global my_x, my_y
    while True:
        try:
            send_json(sock, {"type": "update", "x": my_x, "y": my_y})
        except Exception as e:
            print("Fehler beim Senden der Updates:", e)
            break
        time.sleep(update_interval)

def main():
    global my_x, my_y, players

    server_ip, server_tcp_port = discover_server()
    if not server_ip or not server_tcp_port:
        print("Server konnte nicht gefunden werden. Beende Client.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, server_tcp_port))
        print("Mit dem Server verbunden:", server_ip)
    except Exception as e:
        print("Verbindung fehlgeschlagen:", e)
        return

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
    threading.Thread(target=send_update_loop, args=(sock,), daemon=True).start()

    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Multiplayer Game Client")
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Bewegungsabfrage (aktualisiert my_x, my_y)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            my_x -= speed
        if keys[pygame.K_RIGHT]:
            my_x += speed
        if keys[pygame.K_UP]:
            my_y -= speed
        if keys[pygame.K_DOWN]:
            my_y += speed

        # Rendering: alle Spieler zeichnen (50x50 Rechtecke)
        screen.fill((0, 0, 0))
        for pid, pos in players.items():
            x = pos.get("x", 0)
            y = pos.get("y", 0)
            color = (0, 255, 0) if my_player_id is not None and str(my_player_id) == pid else (255, 0, 0)
            pygame.draw.rect(screen, color, (x, y, 50, 50))
        pygame.display.flip()

    pygame.quit()
    sock.close()
    sys.exit()

if __name__ == '__main__':
    main()
