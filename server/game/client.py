# Client code
import socket
import threading
import time
import wumpus_world
import os

# Global variables
HOST = '127.0.0.1'  # Localhost
PORT = 5555

# Function to receive messages from server


def send_message_to_server(message, client_socket):
    try:
        client_socket.send(message.encode('utf-8'))
    except:
        print("An error occurred while sending the message.")
        client_socket.close()


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print("\n")
            print(message)
            if "Game over" in message:
                time.sleep(1)
                os._exit(0)
        except:
            print("An error occurred while receiving messages.")
            client_socket.close()
            break

# Main client function


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()
    while True:
        try:
            result = wumpus_world.run_game_with_human()
            client.send(str(result).encode('utf-8'))
            # end the program after 2 seconds
            time.sleep(3)
            os._exit(0)
        except:
            print("An error occurred while sending the message.")
            client.close()
            break


# Start the client
start_client()
