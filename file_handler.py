import re
from functools import wraps

# ANSI color codes for colored terminal output
COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "reset": "\033[0m"
}

# Decorator to color the output of a function
#It wraps the Function and adds any chosen color to whatever text it returns.
def color_deco(color: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Wrap the result in the specified color
            return f"{COLORS[color]}{result}{COLORS['reset']}"
        return wrapper
    return decorator

# A class to manage text files ,read them and combine them and display
#__init__ run to create objects in the file
#it sets the filename to property
class FileHandler:
    def __init__(self, filename: str):
        # Set the filename (triggers the setter for validation)
        self.filename = filename

    @property
    def filename(self):
        # Getter for filename
        return self._filename
# it reads filenames in txt if someone saved files as pdf then it displays an error
    @filename.setter
    def filename(self, value):
        # Ensure the file is a .txt file
        if not value.endswith('.txt'):
            raise ValueError("File must be a text file (.txt)")
        self._filename = value

    # Generator to read lines from the file
    def read_generator(self):
        try:
            with open(self._filename, 'r') as file:
                for line in file:
                    yield line.strip()  # Yield each line without trailing newline
        except FileNotFoundError:
            yield from []  # If file not found, yield nothing

    # String representation, it take color blue and out the formated string(Filename.txt) in blue 
    @color_deco("blue")
    def __str__(self):
        return f"FileHandler for {self._filename}"

    # Add two FileHandler objects by concatenating their contents and combines lines with newlines 
    def __add__(self, other):
        content1 = '\n'.join(list(self.read_generator()))
        content2 = '\n'.join(list(other.read_generator()))
        return content1 + '\n' + content2
    # Static method to concatenate contents of multiple FileHandler objects
    @staticmethod
    def concat_files(*files):
        return '\n'.join('\n'.join(list(f.read_generator())) for f in files)
    
    # Class method to create a filein txt from a list of strings and 
    #returns a filehandler object for that new file
    
    @classmethod
    def create_from_list(cls, data: list, filename: str):
        with open(filename, 'w') as file:
            file.write('\n'.join(data))
        return cls(filename) 
# InventoryFileHandler extends FileHandler for inventory management
#calls parental constructor and loads inventory into a dictionary

class InventoryFileHandler(FileHandler):   #child class for inventory management
    def __init__(self, filename: str):
        super().__init__(filename)  # Initialize parent class
        self.inventory = self._load_inventory()  # Load inventory from file
    # Load inventory from file into a dictionary
   
    def _load_inventory(self):
        inventory = {}
        for line in self.read_generator():
            if ':' in line:
                item, quantity = line.split(':')
                inventory[item] = int(quantity)
        return inventory
    # Add inventories of two InventoryFileHandler objects
    #combines 2 inventories :sum quantities of matching items
    
    def __add__(self, other):
        combined = self.inventory.copy()
        for item, quantity in other.inventory.items():
            combined[item] = combined.get(item, 0) + quantity
        return combined
    # Save the inventory dictionary back to the file
    def save(self):
        with open(self.filename, 'w') as file:
            for item, quantity in self.inventory.items():
                file.write(f"{item}:{quantity}\n")
