import os

def open_file_list(lst):
    for f in lst:
        if os.path.isfile(f):
            return f
    return 0

def hex_to_rgba(value):
    """Convierte hexadecimal a RGBA tal y como Gdk lo requiere"""
    value = value.lstrip('#')
    if len(value) == 3:
        value = ''.join([v*2 for v in list(value)])
    (r1, g1, b1, a1)=tuple(int(value[i:i+2], 16) for i in range(0, 6, 2))+(1, )
    (r1, g1, b1, a1)=(r1/255.00000, g1/255.00000, b1/255.00000, a1)

    return (r1, g1, b1, a1)