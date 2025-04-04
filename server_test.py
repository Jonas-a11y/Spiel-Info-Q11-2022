import socket
import threading
import json
import time

TCP_PORT = 5000      # TCP-Port für Spielupdates
UDP_PORT = 5001      # UDP-Port für die Server-Discovery
BUFFER_SIZE = 1024

players = {}         # { "player_id": {"x": value, "y": value} }
clients = {}         # { player_id: client_socket }
lock = threading.Lock()
next_player_id = 1   # Laufende Spieler-ID

def send_json(sock, data):
    """Sendet ein JSON-Objekt mit Zeilenende."""
    try:
        message = json.dumps(data) + "\n"
        sock.sendall(message.encode())
    except Exception as e:
        print("Fehler beim Senden von JSON:", e)

def broadcast_players():
    """Schickt an alle Clients die aktuelle Spielerübersicht."""
    with lock:
        message_data = {"type": "players", "players": players}
        to_remove = []
        for pid, client_sock in clients.items():
            try:
                send_json(client_sock, message_data)
            except Exception as e:
                print(f"Fehler beim Senden an Client {pid}: {e}")
                to_remove.append(pid)
        for pid in to_remove:
            if str(pid) in players:
                del players[str(pid)]
            if pid in clients:
                del clients[pid]

def broadcast_loop(tick_rate=30):
    """Broadcastet die Spielerpositionen in festen Intervallen."""
    tick_interval = 1 / tick_rate
    while True:
        broadcast_players()
        time.sleep(tick_interval)

def handle_client(client_sock, addr, player_id):
    """Verarbeitet eingehende Nachrichten eines Clients."""
    global players, clients
    try:
        send_json(client_sock, {"type": "assign", "id": player_id})
    except Exception as e:
        print("Fehler beim Senden der ID an den Client:", e)
        return

    # Lese Nachrichten zeilenweise (jede Zeile = ein JSON-Objekt)
    client_file = client_sock.makefile('r')
    while True:
        try:
            line = client_file.readline()
            if not line:
                print(f"Client {player_id} hat die Verbindung geschlossen.")
                break
            try:
                message = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"JSON-Decode-Fehler bei Client {player_id}: {e}")
                continue

            if message.get("type") == "update":
                x = message.get("x", 0)
                y = message.get("y", 0)
                hp = message.get("hp", 14)
                shots = message.get("shots", 0)
                if shots != 0:
                    print(f"Client {player_id} hat {shots} Schüsse abgegeben.")
                with lock:
                    players[str(player_id)] = {"x": x, "y": y, "hp": hp, "shots": shots}
        except Exception as e:
            print(f"Fehler bei Client {player_id}: {e}")
            break

    with lock:
        if str(player_id) in players:
            del players[str(player_id)]
        if player_id in clients:
            del clients[player_id]
    client_sock.close()

def tcp_server():
    """Startet den TCP-Server, der Verbindungen für Spielupdates entgegennimmt."""
    global next_player_id
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('', TCP_PORT))
    server_sock.listen(5)
    print(f"Game-Server (TCP) läuft auf Port {TCP_PORT}")

    while True:
        client_sock, addr = server_sock.accept()
        print(time.localtime(), "Neue Verbindung von:", addr)
        with lock:
            player_id = next_player_id
            next_player_id += 1
            clients[player_id] = client_sock
        threading.Thread(target=handle_client, args=(client_sock, addr, player_id), daemon=True).start()

def udp_discovery():
    """Hört auf UDP-Discovery-Anfragen und antwortet mit dem TCP-Port."""
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_sock.bind(('', UDP_PORT))
    print(f"UDP Discovery Server läuft auf Port {UDP_PORT}")
    
    while True:
        try:
            data, addr = udp_sock.recvfrom(BUFFER_SIZE)
            message = data.decode().strip()
            if message == "DISCOVER_SERVER":
                print("Discovery-Anfrage von:", addr)
                response = f"SERVER:{TCP_PORT}"
                udp_sock.sendto(response.encode(), addr)
        except Exception as e:
            print("Fehler im UDP Discovery:", e)

if __name__ == '__main__':
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=udp_discovery, daemon=True).start()
    threading.Thread(target=broadcast_loop, daemon=True).start()
    print("Game-Server ist bereit und wartet auf Verbindungen...")
    while True:
        time.sleep(1)
