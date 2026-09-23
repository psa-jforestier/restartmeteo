import sys

def debug(verbose: bool, msg: str):
    if verbose:
        print(f"[DEBUG] {msg}")

def error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)

def char2raw(c):
    """
    Convert a POCSAG character to its 6-bit raw value.
    `c` can be a character string of length 1 or an integer.
    """
    if isinstance(c, str):
        c = ord(c)

    if ord('k') <= c <= ord('o'):
        return 59 + (c - ord('k'))

    if c == ord('p'):
        return 0x20

    if c == ord('s'):
        return 0x03

    return c - 0x20

def dumpbin(data, blocksize=16, bitpack=8):
    """
    data      : bytes, bytearray, or iterable of integers
    blocksize : number of bytes per output line
    bitpack   : insert a space every bitpack bits
    """

    for i in range(0, len(data), blocksize):
        chunk = data[i:i + blocksize]

        # Continuous bit stream for the line
        bits = ''.join(f'{b:08b}' for b in chunk)

        if bitpack > 0:
            bits = ' '.join(
                bits[j:j + bitpack]
                for j in range(0, len(bits), bitpack)
            )

        print(bits)

  
def dumphex(data, blocksize=16):
    if isinstance(data, str):
        raw = data.encode("latin1")
    else:
        raw = bytes(data)

    for offset in range(0, len(raw), blocksize):
        chunk = raw[offset:offset + blocksize]

        ascii_part = ''.join(
            chr(b) if 32 <= b <= 126 else '.'
            for b in chunk
        )

        hex_part = ' '.join(f'{b:02X}' for b in chunk)

        print(f"{ascii_part:<{blocksize}} | {offset:04X} | {hex_part}")
  