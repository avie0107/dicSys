import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int)
    args = parser.parse_args()

    import server
    app = server.init(server.make_app())
    app = server.init_web(app)
    app.run(debug=True, port=args.port)


if __name__ == "__main__":
    main()

