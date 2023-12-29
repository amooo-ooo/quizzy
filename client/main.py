from src.ui import main as load_ui
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', type=str, default="http://quizzy.pythonanywhere.com", help='Set the back-end API route to a different route such as localhost.')
    args = parser.parse_args()

    if args.server == "local":
        args.server = "http://127.0.0.1:5000" 

    load_ui(args.server)

if __name__ == "__main__":
    main()