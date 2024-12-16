import Pyro5.api
import Pyro5.server

# Chat server class
@Pyro5.api.expose
class ChatServer:
    def __init__(self):
        self.clients = {}  # Dictionary to store client_name: client_uri

    # Register a new client
    def register(self, name, uri):
        if name in self.clients:
            return f"Error: Client name '{name}' already exists."
        self.clients[name] = uri
        print(f"Client '{name}' registered with URI: {uri}")
        return f"Client '{name}' registered successfully."

    # Broadcast a public message to all clients
    def broadcast_message(self, sender, message):
        print(f"Broadcast from {sender}: {message}")
        for name, uri in self.clients.items():
            if name != sender:  # Don't send the message back to the sender
                client = Pyro5.api.Proxy(uri)
                client.receive_message(sender, message)

    # Send a private message to a specific client
    def private_message(self, sender, to_client, message):
        if to_client in self.clients:
            client = Pyro5.api.Proxy(self.clients[to_client])
            client.receive_message(sender, f"[Private] {message}")
            print(f"Private message from {sender} to {to_client}: {message}")
        else:
            print(f"Private message failed: Client '{to_client}' not found.")
            raise ValueError(f"Client '{to_client}' not found.")

    # List all connected clients
    def list_clients(self):
        return list(self.clients.keys())

    # Server sends a public message to all clients
    def send_public_message(self, sender, message):
        print(f"Server sending public message: {message}")
        for name, uri in self.clients.items():
            if name != sender:
                client = Pyro5.api.Proxy(uri)
                client.receive_message("Server", message)

# Main server function
def main():
    server = ChatServer()
    daemon = Pyro5.server.Daemon()
    ns = Pyro5.api.locate_ns()  # Locate the name server
    uri = daemon.register(server)  # Register the server object
    ns.register("chat.server", uri)  # Register server in the NameServer
    print("Chat server is ready.")
    print(f"URI: {uri}")
    daemon.requestLoop()  # Start server event loop


if __name__ == "__main__":
    main()
