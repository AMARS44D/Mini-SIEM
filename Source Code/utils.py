# utils.py
def is_int(s):
    """ Check if a string can be converted to an integer.
        Supports negative numbers as well.                  """
    try:
        int(s)
        return True
    except ValueError:
        return False
