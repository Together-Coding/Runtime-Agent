import uvicorn
import baby_sitter
from server import app


def main():
    # Start monitoring
    baby_sitter.run()

    # Start blocking HTTP server
    uvicorn.run(app)


if __name__ == '__main__':
    main()
