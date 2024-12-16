import Pyro5.api
import Pyro5.server


@Pyro5.api.expose
class ChatServer:
    def __init__(self):
        self.clients = {}  # Dictionary to store client_name: client_uri

    # Register a new client
    def register_client(self, name, uri):
        if name in self.clients:
            return f"Error: Client name '{name}' already exists."
        self.clients[name] = uri
        print(f"Client '{name}' registered with URI: {uri}")
        return f"Client '{name}' registered successfully."

    # Unregister a client
    def unregister_client(self, name):
        if name in self.clients:
            del self.clients[name]
            print(f"Client '{name}' unregistered.")
            return f"Client '{name}' unregistered successfully."
        else:
            return f"Error: Client '{name}' not found."

    # List all connected clients
    def list_clients(self):
        return list(self.clients.keys())

    # Broadcast a message to all clients
    def broadcast_message(self, sender, message):
        print(f"[Broadcast] {sender}: {message}")
        for name, uri in self.clients.items():
            if name != sender:
                client = Pyro5.api.Proxy(uri)
                client.receive_message(sender, message)

    # Send a private message
    def private_message(self, sender, recipient, message):
        if recipient in self.clients:
            client = Pyro5.api.Proxy(self.clients[recipient])
            client.receive_message(sender, f"[Private] {message}")
            print(f"[Private] {sender} to {recipient}: {message}")
        else:
            print(f"Private message failed: Client '{recipient}' not found.")
            raise ValueError(f"Client '{recipient}' not found.")


def main():
    # Create a Pyro server instance
    server = ChatServer()
    daemon = Pyro5.server.Daemon()
    ns = Pyro5.api.locate_ns()  # Locate the Pyro name server
    uri = daemon.register(server)  # Register the server object
    ns.register("chat.server", uri)  # Register with the name server
    print("Chat server is ready.")
    print(f"URI: {uri}")
    daemon.requestLoop()  # Start the server loop


if __name__ == "__main__":
    main()
