# updated

import Pyro5.api
import threading

class ChatClient:
    def __init__(self, name):
        self.name = name
        self.server = Pyro5.api.Proxy("PYRONAME:chat.server")  # Connect to the server
        self.uri = None
        self.daemon = Pyro5.server.Daemon()  # Create a client daemon

    @Pyro5.api.expose
    def receive_message(self, sender, message):
        """Receive a broadcast message."""
        print(f"\n{sender}: {message}")

    @Pyro5.api.expose
    def receive_invitation(self, sender):
        """Handle a private chat invitation."""
        print(f"\n[INVITE] {sender} invites you to a private chat.")
        choice = input("Accept invitation? (yes/no): ").strip().lower()
        return "accepted" if choice == "yes" else "rejected"

    def register_with_server(self):
        """Register this client with the server."""
        self.uri = self.daemon.register(self)  # Register client object with daemon
        response = self.server.register_client(self.name, self.uri)
        print(response)

    def user_input_loop(self):
        """Handle user commands."""
        while True:
            try:
                user_input = input("\n> ").strip()
                if user_input.startswith("send "):
                    message = user_input[5:]
                    self.server.broadcast_message(self.name, message)
                elif user_input.startswith("invite "):
                    target = user_input[7:].strip()
                    response = self.server.invite_to_private_chat(self.name, target)
                    print(f"[SERVER RESPONSE] {response}")
                elif user_input == "exit":
                    self.server.unregister_client(self.name)
                    print("Disconnected from server. Goodbye!")
                    break
                else:
                    print("Invalid command. Use 'send <message>' or 'invite <client>'. Type 'exit' to leave.")
            except KeyboardInterrupt:
                self.server.unregister_client(self.name)
                print("\nDisconnected. Goodbye!")
                break

    def start(self):
        """Start the chat client."""
        threading.Thread(target=self.daemon.requestLoop, daemon=True).start()
        self.register_with_server()
        print("Available commands:\n - send <message>\n - invite <client>\n - exit")
        self.user_input_loop()

# Start the client
def main():
    name = input("Enter your name: ").strip()
    if not name:
        print("Name cannot be empty. Restart the client.")
        return
    client = ChatClient(name)
    client.start()

if __name__ == "__main__":
    main()
