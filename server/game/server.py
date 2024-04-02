import socket
import threading

# Global variables
HOST = '127.0.0.1'  # Localhost
PORT = 5555
MAX_PLAYERS = 2
clients = []

# Function to handle client connections


def handle_client(client_socket):
    while True:
        try:
            # Receive data from client
            result = client_socket.recv(1024).decode('utf-8')
            if not result:
                remove_client(client_socket)
                break
            handle_game_action(result, client_socket)

        except:
            continue

# Function to handle game actions


def handle_game_action(action, client_socket):
    player_id = clients.index(client_socket)
    other_player_id = 1 - player_id
    other_player_socket = clients[other_player_id]

    if action == "True":
        winning_message = "You won!"
        losing_message = "Player A won, you lost. Game over."
    elif action == "False":
        winning_message = "You lost. Game over."
        losing_message = "Player A lost, you can keep playing for fun >_<!"

    send_message_to_client(winning_message, client_socket)
    send_message_to_client(losing_message, other_player_socket)
    remove_client(client_socket)
    remove_client(other_player_socket)

# Function to send message to a client


def send_message_to_client(message, client_socket):
    try:
        client_socket.send(message.encode('utf-8'))
    except:
        remove_client(client_socket)

# Function to remove client from list


def remove_client(client_socket):
    if client_socket in clients:
        clients.remove(client_socket)

# Main server function


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_PLAYERS)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()
        print(f"New connection from {client_address}")
        clients.append(client_socket)
        if len(clients) == MAX_PLAYERS:
            break

    for client_socket in clients:
        handle_client_thread = threading.Thread(
            target=handle_client, args=(client_socket,))
        handle_client_thread.start()


# Start the server
start_server()
