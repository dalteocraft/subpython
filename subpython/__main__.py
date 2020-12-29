import argparse


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action")
    connect_parser = subparsers.add_parser("connect")
    connect_parser.add_argument("--endpoint", "-E", default="tcp://127.0.0.1:5555", help="Connection endpoint.")
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--endpoint", "-E", default="tcp://127.0.0.1:5555", help="Connection endpoint.")

    args = parser.parse_args()

    if args.action == "connect":
        from .client import Client
        client = Client(args.endpoint)
        client.spImportModule("os")
        print(client.os.getcwd())
    elif args.action == "run":
        from .server import Server
        server = Server(args.endpoint)
        server.start()


if __name__ == "__main__":
    main()