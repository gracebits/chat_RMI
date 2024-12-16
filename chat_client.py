import Pyro5.api
import Pyro5.server
import threading

# Chat client class
class ChatClient:
    def __init__(self, name, server):
        self.name = name
        self.server = server

    @Pyro5.api.expose
    def receive_message(self, sender, message):
        print(f"\n[{sender}] {message}")

    def send_public_message(self, message):
        try:
            self.server.broadcast_message(self.name, message)
        except Exception as e:
            print(f"Error sending public message: {e}")

    def send_private_message(self, to_client, message):
        try:
            self.server.private_message(self.name, to_client, message)
        except Exception as e:
            print(f"Error sending private message: {e}")


def main():
    name = input("Enter your name: ").strip()
    if not name:
        print("Name cannot be empty!")
        return

    try:
        server = Pyro5.api.Proxy("PYRONAME:chat.server")
        print("Connecting to the server...")

        client = ChatClient(name, server)
        daemon = Pyro5.server.Daemon()
        uri = daemon.register(client)
        ns = Pyro5.api.locate_ns()
        ns.register(f"chat.client.{name}", uri)

        print(f"Successfully registered as '{name}' with the server.")
        print(server.register(name, uri))

        threading.Thread(target=daemon.requestLoop, daemon=True).start()

        print("\nCommands: /msg <message>, /private <client> <message>, /list, /quit")
        while True:
            command = input("> ").strip()
            if command.startswith("/msg "):
                client.send_public_message(command[5:])
            elif command.startswith("/private "):
                parts = command.split(maxsplit=2)
                if len(parts) < 3:
                    print("Usage: /private <client> <message>")
                else:
                    to_client, message = parts[1], parts[2]
                    client.send_private_message(to_client, message)
            elif command == "/list":
                print("Online clients:", server.list_clients())
            elif command == "/quit":
                print("Exiting chat...")
                break
            else:
                print("Unknown command. Use /msg, /private, /list, or /quit.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
