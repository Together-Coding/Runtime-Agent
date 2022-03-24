import baby_sitter
from server import app


def main():
    # Start monitoring
    baby_sitter.run()

    # Start blocking HTTP server
    app.run('0.0.0.0', port=8989)


if __name__ == '__main__':
    main()
