def convert_args(text: str):
    items = text.split(' ')

    result = {}
    for item in items:
        try:
            # Split each item into key and value at the first colon
            key, value = item.split(':', 1)
            
            # Optional: Convert value to int if possible
            try:
                value = int(value)
            except ValueError:
                pass
            
            result[key] = value
        except:
            pass
    return result