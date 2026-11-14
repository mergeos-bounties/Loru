import sys
import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(prog="loru")
    subparsers = parser.add_subparsers(dest="command")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the FastAPI server")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Bind socket to this host")
    serve_parser.add_argument("--port", type=int, default=8000, help="Bind socket to this port")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    if args.command == "serve":
        uvicorn.run("loru.api.app:app", host=args.host, port=args.port, reload=args.reload)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
