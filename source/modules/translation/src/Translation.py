from __future__ import annotations

import copy
import json
from typing import Union, Any
import os


def read_json_file(file_path: str) -> Union[dict, list]:
    """
    Reads a JSON file and returns its contents as a Python object.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        Union[dict, list]: Python object representing the JSON content
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the JSON is invalid
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} was not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {file_path}: {str(e)}")


def save_to_json_file(data: Any, file_path: str, indent: int = 4) -> None:
    """
    Saves a Python object to a JSON file.
    
    Args:
        data (Any): Python object to save (must be JSON serializable)
        file_path (str): Path where the JSON file will be saved
        indent (int): Number of spaces to indent JSON (default: 4)
        
    Raises:
        TypeError: If data is not JSON serializable
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=indent)
    except TypeError as e:
        raise ValueError(f"Cannot serialize object to JSON: {str(e)}")


class Translation:
    def __init__(self, original_text='', original_language='en') -> None:
        self.original_text = original_text
        self.original_language = original_language

        self.translate_to = 'en'

        self.before = []
        self.after = []
        
        self.path = os.path.dirname(os.path.abspath(__file__)) + '/../translations.json'
        self.translations: dict | list = read_json_file(self.path)


    def getTranslation(self, language='en') -> str:
        self.translations: dict | list = read_json_file(self.path)

        if self.original_language in self.translations:
            if self.original_text in self.translations[self.original_language]: # type: ignore
                if language in self.translations[self.original_language][self.original_text]: # type: ignore
                    return self.translations[self.original_language][self.original_text][language] # type: ignore
                else:
                    self.translations[self.original_language][self.original_text][language] = self.original_text # type: ignore
                    save_to_json_file(self.translations, file_path=self.path)
            else:
                self.translations[self.original_language][self.original_text] = {} # type: ignore
                save_to_json_file(self.translations, file_path=self.path)
        else:
            self.translations[self.original_language] = {} # type: ignore
            save_to_json_file(self.translations, file_path=self.path)

        return self.original_text


    def __add__(self, other) -> Translation:
        n = copy.copy(self)
        n.after.append(other)
        return n
    

    def __radd__(self, other) -> Translation:
        n = copy.copy(self)
        n.before.insert(0, other)
        return n
    
    
    def __str__(self) -> str:
        raise RuntimeError('translation.Translation could not be converted to string')
    

    def translate(self, language='') -> str:
        if language == '':
            language = self.translate_to

        s = ''

        for b in self.before:
            if type(b) == Translation:
                b.translate_to = self.translate_to
                s += b.translate(language=language)

            else:
                s += str(b)

        s += self.getTranslation(language=language)

        for a in self.after:
            if type(a) == Translation:
                a.translate_to = self.translate_to
                s += a.translate(language=language)

            else:
                s += str(a)
    
        return s