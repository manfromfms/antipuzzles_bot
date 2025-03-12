import sys
from src.Generator import Generator
from src.Database import Database


def g():
    # Check if a file was dropped
    if len(sys.argv) != 2:
        print("Usage: Drag and drop a file onto the batch file")
        return

    # Get the dropped file path
    file_path = sys.argv[1]

    # Process the file here
    print(f"Processing file: {file_path}")

    db = Database('./database.db')

    gen = Generator(db=db)

    gen.generate(open(file_path))

g()