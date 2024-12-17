import Pyro5.api

@Pyro5.api.expose
class ChatServer:
    def __init__(self):
        self.clients = {}  # {normalized_name: (actual_name, uri)}

    def register_client(self, name, uri):
        """Register a client with the server."""
        normalized_name = name.lower()  # Store names in lowercase
        if normalized_name not in self.clients:
            self.clients[normalized_name] = (name, uri)  # Store both actual name and URI
            print(f"[SERVER] {name} has joined the chat. Active clients: {self.get_active_client_names()}")
            return f"Welcome {name}! Type 'send <message>' to chat or 'invite <client>' to private chat."
        return "Name already taken. Try another name."

    def get_active_client_names(self):
        """Return the list of actual active client names."""
        return [info[0] for info in self.clients.values()]

    def broadcast_message(self, sender, message):
        """Broadcast a message to all clients."""
        print(f"[BROADCAST] {sender}: {message}")
        for normalized_name, (actual_name, uri) in self.clients.items():
            if actual_name != sender:  # Avoid sending the message back to the sender
                try:
                    client = Pyro5.api.Proxy(uri)
                    client.receive_message(sender, message)
                except Exception as e:
                    print(f"[ERROR] Could not send message to {actual_name}: {e}")

    def invite_to_private_chat(self, sender, target):
        """Invite another client to a private chat."""
        target_normalized = target.lower()
        sender_normalized = sender.lower()

        if target_normalized in self.clients:
            actual_target_name, target_uri = self.clients[target_normalized]
            try:
                target_client = Pyro5.api.Proxy(target_uri)
                response = target_client.receive_invitation(sender)
                return f"{actual_target_name} responded: {response}"
            except Exception as e:
                print(f"[ERROR] Failed to send invitation to {actual_target_name}: {e}")
                return f"Could not reach {actual_target_name}."
        return f"{target} is not online."

    def unregister_client(self, name):
        """Remove a client from the active list."""
        normalized_name = name.lower()
        if normalized_name in self.clients:
            del self.clients[normalized_name]
            print(f"[SERVER] {name} has disconnected. Active clients: {self.get_active_client_names()}")

# Start the server
def main():
    daemon = Pyro5.server.Daemon()  # Pyro5 Daemon
    ns = Pyro5.api.locate_ns()  # Locate Pyro5 name server
    uri = daemon.register(ChatServer)  # Register the server object
    ns.register("chat.server", uri)  # Register with name server
    print("[SERVER] Chat server is running...")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
