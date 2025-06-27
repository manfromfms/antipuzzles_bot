from typing import Any
from telegram import Update

class CommandDecorator:
    name = ''
    h = ''
    help = ''

    async def __call__(self):
        pass


    def __repr__(self) -> str:
        return f'telegram.CommandDecorator(name=\'{self.name}\', h=\'{self.h}\')'



def command(n, params_spec, h=''):
    """
    Decorator for parsing command parameters from message.text.
    
    Parses a command string in the format:
        `/command param1:value1 param2 param3:value3 ...`
    
    Args:
        n (str): Name of this command
        params_spec (list[dict]): List of parameter specifications. Each spec is a dict with:
            - 'name' (str): Parameter name
            - 'type' (type): Python type (str, int, float, bool, etc.)
            - 'required' (bool): Whether parameter is required
            - 'help' (str): Context for help command
        h (str): Information about this command
    
    Returns:
        function: Decorated function that receives (message, params)
        
    Raises:
        ValueError: For various parsing errors with detailed messages
        
    Features:
        - Handles required parameters
        - Type conversion
        - Boolean flags (presence = True, absence = False)
        - Missing optional parameters default to None (or False for booleans)
        - Comprehensive error reporting
    """

    def decorator(func):
        class Command(CommandDecorator):
            async def __call__(self, update: Update, context):
                message = update.message

                tokens = message.text.strip().split()
                tokens = tokens[1:]  # Skip the command part
                
                provided = {}
                for token in tokens:
                    if ':' in token:
                        key, value = token.split(':', 1)
                        provided[key] = value
                    else:
                        provided[token] = True
                
                parsed_params = {}
                errors = []
                
                for spec in params_spec:
                    n = spec['name']
                    param_type = spec['type']
                    required = spec['required']
                    
                    if n in provided:
                        if param_type is bool:
                            if isinstance(provided[n], str):
                                errors.append(f"Parameter '{n}' is a flag and should not have a value")
                            else:
                                parsed_params[n] = True
                        else:
                            if isinstance(provided[n], bool):
                                errors.append(f"Parameter '{n}' requires a value")
                            else:
                                try:
                                    parsed_params[n] = param_type(provided[n])
                                except (ValueError, TypeError) as e:
                                    errors.append(f"Invalid value for '{n}': {e}")
                    else:
                        if param_type is bool:
                            parsed_params[n] = False
                        else:
                            if required:
                                errors.append(f"Missing required parameter: '{n}'")
                            else:
                                parsed_params[n] = None
                
                if errors:
                    raise ValueError("\n".join(errors))
                
                return await func(message, parsed_params)
            
        cmd = Command()

        cmd.name = n
        cmd.h = h
        cmd.help = f'*/{n}*: {h}\n'

        for spec in params_spec:
            name = spec['name']
            param_type = spec['type']
            required = spec['required']
            hh = spec['help']

            cmd.help += f'    - *{name}* _({param_type}{', required' if required else ''})_{(': ' + hh) if hh is not None else ''}'

        return cmd
    return decorator