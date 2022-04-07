import uvicorn
import baby_sitter
from server import sio_app as app


# Start monitoring
# baby_sitter.run()

def main():
    # Start blocking HTTP server
    uvicorn.run(app)


if __name__ == '__main__':
    main()
