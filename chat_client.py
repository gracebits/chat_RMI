import Pyro5.api
import Pyro5.server
import threading


@Pyro5.api.expose
class ChatClient:
    def __init__(self, name, server):
        self.name = name
        self.server = server

    # Receive messages from the server or other clients
    def receive_message(self, sender, message):
        print(f"\n[{sender}] {message}")

    # Send a broadcast message
    def send_broadcast(self, message):
        try:
            self.server.broadcast_message(self.name, message)
        except Exception as e:
            print(f"Error sending broadcast message: {e}")

    # Send a private message
    def send_private_message(self, recipient, message):
        try:
            self.server.private_message(self.name, recipient, message)
        except Exception as e:
            print(f"Error sending private message: {e}")


def main():
    name = input("Enter your name: ").strip()
    if not name:
        print("Name cannot be empty!")
        return

    try:
        # Connect to the Pyro server
        server = Pyro5.api.Proxy("PYRONAME:chat.server")
        print("Connecting to the chat server...")

        # Create the client instance
        client = ChatClient(name, server)

        # Register the client with the server
        daemon = Pyro5.server.Daemon()
        uri = daemon.register(client)  # Register client object with Pyro
        ns = Pyro5.api.locate_ns()
        ns.register(f"chat.client.{name}", uri)  # Register with the name server
        print(f"Successfully registered as '{name}'.")

        print(server.register_client(name, uri))

        # Start a thread to handle incoming messages
        threading.Thread(target=daemon.requestLoop, daemon=True).start()

        # Chat commands
        print("\nCommands:")
        print("  /msg <message>          - Broadcast message to all clients")
        print("  /private <name> <msg>   - Send a private message")
        print("  /list                   - List all connected clients")
        print("  /quit                   - Exit the chat")

        while True:
            command = input("> ").strip()
            if command.startswith("/msg "):
                client.send_broadcast(command[5:])
            elif command.startswith("/private "):
                parts = command.split(maxsplit=2)
                if len(parts) < 3:
                    print("Usage: /private <client_name> <message>")
                else:
                    recipient, message = parts[1], parts[2]
                    client.send_private_message(recipient, message)
            elif command == "/list":
                print("Online clients:", server.list_clients())
            elif command == "/quit":
                print("Exiting chat...")
                print(server.unregister_client(name))
                break
            else:
                print("Unknown command. Use /msg, /private, /list, or /quit.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
