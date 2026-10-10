import sys




def debug(verbose: bool, msg: str):
    if verbose:
        print(f"[DEBUG] {msg}")

def warning(msg: str):
    print(f"[WARN ] {msg}", file=sys.stderr)

def error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)
class BitField:
    """
    A class representing a continuous bitfield, 
    allowing for bit-level manipulation.
    Provides methods to set, get, push, and pull bits (one by one) and nibbles (4 bits per 4 bits).
    """
    def __init__(self, length: int):
        """
        Initialize a BitField with the specified length in bits.
        """
        self.length = length
        self.data = bytearray((length + 7) // 8)
        self.idx = 0 #used to push values into the bitfield
        # we allocated more
        # but the length of the bitfield is still 'length'
    
    def setIdx(self, idx: int) -> None:
        """
        Set the current bit index to 'idx'. Used when pushing or pulling bits.
        Raises ValueError if 'idx' is out of range.
        """
        if idx < 0 or idx >= self.length:
            raise ValueError("index out of range")
        self.idx = idx        
    def getIdx(self) -> int:
        """
        Get the current bit index. Used when pushing or pulling bits.
        """
        return self.idx    
    def resize(self, new_length: int) -> None:
        """
        Shrink or extend the existing bitfield.
        Push/pull idx not modified (so it may be out of range)
        """
        if new_length <= self.length:
            self.length = new_length
            return
        new_data = bytearray((new_length + 7) // 8)
        for i in range(len(self.data)):
            new_data[i] = self.data[i]
        self.data = new_data
        self.length = new_length

    def push(self, value: int, length: int) -> None:
        """
        Push the value (made of length bits) and update the idx
        """
        self.set(self.idx, value, length)
        self.idx += length
        """
        Push a nibble (4 bits) and update the idx.
        """
    def pushN(self, nibblevalue:int) -> None:
        self.push(nibblevalue, 4)        
    def pushB(self, bytevalue:int) -> None:
        self.push(bytevalue, 8)
    def pull(self, length: int) -> int:
        """
        Pull 'length' bits from the current idx and update the idx.
        Returns the pulled value as an integer.
        """
        value = self.get(self.idx, length)
        self.idx += length
        return value
    def pullN(self) -> int:
        """
        Pull a nibble (4 bits) from the current idx and update the idx.
        Returns the pulled value as an integer.
        """
        return self.pull(4)
    
    def setN(self, nibbleposition:int, value:int) -> None:
        """
        Set the value of a nibble (4 bits) at the specified nibble position.
        Nibble positions are numbered from 0.
        """
        if nibbleposition < 0:
            raise ValueError("index out of range")
        if nibbleposition * 4 + 4 > self.length:
            raise ValueError("index out of range")
        bit_position = nibbleposition * 4
        self.set(bit_position, value & 0x0F, 4)

    def getN(self, nibbleposition:int) -> int:
        """
        Get the value of a nibble (4 bits) at the specified nibble position.
        Nibble positions are numbered from 0.
        """
        if nibbleposition < 0:
            raise ValueError("index out of range")
        if nibbleposition * 4 + 4 > self.length:
            raise ValueError("index out of rangeh")
        bit_position = nibbleposition * 4
        return self.get(bit_position, 4)
    def set(self, position: int, value: int, length: int) -> None:
        """
        Set 'length' bits of 'value' starting at bit 'position'.

        Bits are numbered from 0.
        Bit 0 is the leftmost bit of the bitfield.
        """

        if position < 0:
            raise ValueError("index out of range")

        if position + length > self.length:
            raise ValueError("index out of rangeh")

        for i in range(length):
            field_pos = position + i

            byte_index = field_pos // 8
            bit_index = 7 - (field_pos % 8)

            bit_value = (value >> (length - 1 - i)) & 1

            if bit_value:
                self.data[byte_index] |= (1 << bit_index)
            else:
                self.data[byte_index] &= ~(1 << bit_index)

    def get(self, position: int, length: int) -> int:
        """
        Read 'length' bits starting at 'position'.
        Bits are numbered from 0.
        Bit 0 is the leftmost bit of the bitfield.
        """
        if position < 0:
            raise ValueError("index out of range")

        if position + length > self.length:
            raise ValueError("index out of range")

        value = 0

        for i in range(length):
            field_pos = position + i

            byte_index = field_pos // 8
            bit_index = 7 - (field_pos % 8)

            bit = (self.data[byte_index] >> bit_index) & 1

            value = (value << 1) | bit

        return value

    def format(self, packed:int, base=2) -> str:
        # return a string of bits (if base = 2) or hex digits (if base = 16) with a separator on 
        # each packed.
        result = []

        if (base == 16):
            for i in range(0, self.length // 4):
                if i>0 and i % packed == 0:
                    result.append(' ')
                if ((i*4)<= self.length):
                    result.append(f"{self.get(i*4, 4):x}")
                else:
                    result.append("?")
            if ((i*4) + 4 != self.length):
                result.append("?")
            
        elif (base == 2):
            for i in range(0, self.length):
                if i>0 and i % packed == 0:
                    result.append(' ')
                result.append(str(self.get(i, 1)))
        return ''.join(result)
    
        for i in range(0, self.length, packed):
            if i > 0:
                result.append(' ')
            for j in range(packed):
                if i + j < self.length:
                    if base == 2:
                        result.append(str(self.get(i + j, 1)))
                    elif base == 16:
                        if j % 4 == 0 and j > 0:
                            result.append(' ')
                        if (i+j+4 < self.length):
                            result.append(f"{self.get(i + j, 4):x}")
                        else:
                            result.append("?")
                    else:
                        raise ValueError("Unsupported base")
        return ''.join(result)
        
    def __str__(self) -> str:
        return ''.join(
            str(self.get(i, 1))
            for i in range(0, self.length)
        )
def sm_crc8(data: BitField, idxN:int, lengthN:int) -> int:
    """
    Compute the Starmeteo 8 bits crc for the given nibble index and length in nibbles.
    """
    crc = 0x07
    for i in range(0,lengthN):
        crc = crc + data.getN(idxN + i)
    crc = crc & 0xff
    return crc
def sm_crcN(data: BitField, idxN:int, lengthN:int) -> int:
    """
    Compute the Starmeteo 4 bits crc for the given nibble index and length in nibbles.
    """
    crc = 0x07
    for i in range(0,lengthN):
        crc = crc + data.getN(idxN + i)
    crc = crc & 0x0f
    return crc

def encode_temp(temp:int):
    """
    return the temperature nibbles (high, low)
    """
    temp = temp + 40
    tenth = temp // 10
    unit = temp % 10
    return (tenth, unit)
def asciitobit(ascii: str) -> BitField:
    """
    Convert a StarMeteo ASCII encoded string into a BitField.
    Each ASCII character is converted to its corresponding 6-bit value.
    """
    bits = BitField((len(ascii) * 6))
    for i, c in enumerate(ascii):
        six_bits = char2raw(c)
        bits.set(i * 6, six_bits, 6)
    return bits
def bittoascii(bits: BitField) -> str:
    """
    Convert a BitField into a StarMeteo ASCII encoded string.
    Each 6-bit pack is converted to a corresponding ASCII character.
    If the bitfield length is not a multiple of 6, will raise an exception
    """
    ascii_chars = []
    if bits.length % 6 != 0:
        # Zero pad the last few bits to make it a multiple of 6
        padding = 6 - (bits.length % 6)
        raise ValueError("BitField length is not a multiple of 6.")
    for i in range(0, bits.length, 6):
        six_bits = bits.get(i, 6)
        ascii_chars.append(raw2char(six_bits))
    encoded_string = ''.join(ascii_chars)
    return encoded_string
def bitset(data:bytearray , position: int, value: int, bitlenght:int) -> None:
    # copy bitlenght bit from value at position position in the data array of bytes
    # modify data in place
    mask = (1 << bitlenght) - 1
    value &= mask
    for i in range(bitlenght):
        if position + i < len(data) * 8:
            byte_index = (position + i) // 8
            bit_index = 7 - ((position + i) % 8)
            data[byte_index] &= ~(1 << bit_index)
            data[byte_index] |= ((value >> (bitlenght - 1 - i)) & 1) << bit_index

"""
Implementation of the strange StarMeteo ASCII encoding.
It is not base 64, not base 85, it is a custom 6-bit encoding.
"""
def raw2char(r:int) -> str:
    """
    Convert a 6-bit raw value to its corresponding POCSAG character.
    """
    if 59 <= r <= 63:
        return chr(ord('k') + (r - 59))
    if r == 0x20:
        return 'p'
    if r == 0x03:
        return 's'
    return chr(r + 0x20)
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


def decode(verbose, data, fast=False):
    
    l = len(data)

    bits= asciitobit(data)
    print("Hexa bitfield: ", bits.format(4, base=16))
    debug(verbose, f"BitField nibbles representation: {bits.format(4)}")
    frame_identifier = bits.getN(0)
    if (fast):
        print(f"Frame identifier: 0x{frame_identifier:0x}", end="")
        if (frame_identifier == 0xf):
            print(": time frame", end="")
            import sm_time
            sm_time.sm_decode_datetime(verbose, bits, True)
        elif (frame_identifier == 0x4):
            print(": forecast frame", end="")
        elif (frame_identifier == 0x0):
            print(": long forecast frame", end="")
        else:
            print(": unknown frame", end="")
        print()
    else:
        print("Length of ascii characters: ", l)
        print("Expected number of bits: ", l * 6)
            
        print(f"Frame identifier: 0x{frame_identifier:0x}")
        if (frame_identifier == 0xf):
            import sm_time
            sm_time.sm_decode_datetime(verbose, bits, False)
        elif (frame_identifier == 0x4):
            import sm_forecast
            sm_forecast.sm_decode_forecast(verbose, bits)
            pass
        elif (frame_identifier == 0x0):
            import sm_forecast
            sm_forecast.sm_decode_forecast_long(verbose, bits)
        elif (frame_identifier == 0xe):
            import sm_forecast
            sm_forecast.sm_decode_forecast_alert(verbose, bits)
        else:
            print(" └ Unknown frame identifier. Attempt decoding (after frame identifier)")
            print("   ├ Bit stream: "+str(bits)[4:])
            print("   └ Per nibbles:")
            # print bit data, after the identifier, by nibbles
            for i in range(1, (bits.length + 3) // 4):
                nibble = bits.getN(i)
                print(f"Nibble {i:02}: 0x{nibble:01x} 0b{nibble:04b}")
            print("   └ Per bytes :")
            nb_bytes = (bits.length - 4 ) // 8
            for i in range(nb_bytes):
                b = bits.get(4 + i*8, 8)
                print(f"Byte {i:02}: 0x{b:02x} 0b{b:08b}")
    return
    