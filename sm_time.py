#!/usr/bin/env python3
'''
starmeteo reverse engeneering project

This tool generate a StarMeteo compatible message for time synchronization.
'''

import argparse
from sm_utils import *
from datetime import datetime

import sm_utils



    
def sm_encode_datetime(dt, area=["75"], verbose=False):
  hour = dt.hour
  minute = dt.minute
  year = dt.year
  month = dt.month # 1..12
  day = dt.day # 1..31

  # Prepare nibble array. At least 11 nibbles are needed.

  nibbles = [0x00] * 9
  nibbles[0] = 0x0f # frame identifier
  # Hour
  if (hour < 10):
      nibbles[1] = hour
      nibbles[2] = minute // 10
      nibbles[3] = minute % 10
  elif (hour >= 10 and hour <= 19):
      nibbles[1] = hour - 10
      nibbles[2] = (minute // 10) + 10
      nibbles[3] = minute % 10
  else: # 20..23
      nibbles[1] = hour - 10
      nibbles[2] = (minute // 10)
      nibbles[3] = minute % 10
  # Minute tenth
  #nibbles[2] = minute // 10
  # Minute unit
  #nibbles[3] = minute % 10 
  # Month
  nibbles[4] = month
  # day tenths in bits 0 and 1 of nibble 5
  day_t = day // 10 
  day_u = day % 10
  nibbles[5] = ((day_t & 0x03) << 2 ) | ((day_u >> 2) &0x03)
  nibbles[6] = (day_u & 0x03) << 2
  yearoffset = year - 2000
  nibbles[6] |= ((yearoffset) >> 4 ) &0x03
  nibbles[7] = yearoffset & 0x0F
  # crc
  sum = 0x07
  for i in range(0,8):
    sum = sum + nibbles[i]
  nibbles[8] = sum & 0x0f
  
  if (verbose) :
   sm_utils.debug(verbose, f"Nibbles: {nibbles}")
   sm_utils.dumphex(nibbles, 16)
   sm_utils.dumpbin(nibbles, 16, 8)
  # We now have 9 nibbles representing the encoded datetime
  # 9 x 4 = 36 bits.
  # Convert them into 6 bits (36 / 6 = 6 bytes)
  bytes = [0x00] * 6
  for i in range(0,36): # browse all 36 bits of the nibbles
    byte_index = i // 6
    bit_index = i % 6
    nibble_index = i // 4
    bit_in_nibble = i % 4
    bit_value = (nibbles[nibble_index] >> (3 - bit_in_nibble)) & 0x01
    bytes[byte_index] |= bit_value << (5 - bit_index)
     
  if (verbose):
    sm_utils.debug(verbose, f"Encoded 6bits: {bytes}")
    sm_utils.dumphex(bytes, 16)
    sm_utils.dumpbin(bytes, 16, 8)
  # Encode bytes by using the StarMeteo ASCII encoding
  ascii = ''.join(raw2char(b) for b in bytes)
  sm_utils.debug(verbose,f"Encoded ASCII: {ascii}")
  return ascii

    
def decode(verbose, data):
  debug(verbose, "Decoding "+data)
  # convert data to a byte array
  if isinstance(data, str):
      data = data.encode("latin1")
  else:
      data = bytes(data)
  if (verbose):
    debug(verbose, "Dump before decoding :")
    dumphex(data,16)
    dumpbin(data, 16, 8)
  converted = bytearray()
  for b in data:
    converted.append(char2raw(b))
  converted = bytes(converted)
  if (verbose):
    debug(verbose, "Dump after  decoding :")
    dumphex(converted,16)
    dumpbin(converted, 16, 8)
    debug(verbose, "Dump after  decoding -6 bits packing) :")
    dumpbin(converted, 16, 6)
  # convert to binary string
  bitstring = ''.join(f'{b:08b}' for b in converted)
  
  if (verbose):
    debug(verbose, "8 bits dump :")
    for i in range(0, len(converted), 8):    
      print(' '.join(f'{b:08b}' for b in converted[i:i+8]))
    #debug(verbose, "6 bits dump :")   
    #print(' '.join(bitstring[i:i+6] for i in range(0, len(bitstring), 6)))
    
  # regroup by 6 bit
  bitstring6 = bytearray()
  for i in range(0, len(bitstring), 6):
    chunk = bitstring[i:i+6]

    # pad the last chunk with zeros if it is shorter than 6 bits
    if len(chunk) < 6:
        chunk = chunk.ljust(6, '0')

    bitstring6.append(int(chunk, 2))
  if (verbose):
    debug(verbose, "6 bits dump :")
    for i in range(0, len(bitstring6), 8):    
      print(' '.join(f'{b:06b}' for b in bitstring6[i:i+6]))
      
      
      
      
      
  newconv = bytearray()

  # Flux binaire continu
  bitstream = ''.join(f'{b:08b}' for b in converted)

  # Extraction par paquets de 6 bits
  for i in range(0, len(bitstream), 6):
      chunk = bitstream[i:i+6]

      # Complète avec des 0 à droite si nécessaire
      chunk = chunk.ljust(6, '0')

      newconv.append(int(chunk, 2))
  dumphex(newconv,16)
      
      
  return ""

def main():
    parser = argparse.ArgumentParser(description="This tool generate or decode a StarMeteo compatible message for time synchronization.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug output")
    parser.add_argument("--time", dest="time", required=False, 
      type=str, 
      help="Time & date value as a string")
    parser.add_argument("--timeformat", dest="timeformat", required=False, 
      type=str, 
      default="%Y-%m-%d_%H:%M:%S",
      help="Time & date format. Use Python datetime.strptime format. Default is %%Y-%%m-%%d_%%H:%%M:%%S. If you use the \"date -R\" Linux command, use format \"%%a, %%d %%b %%Y %%H:%%M:%%S %%z\" (do not forget the \")")
    parser.add_argument("--decode", dest="decode", required=False,
      type=str,
      help="Decode the frame"
    )
    args = parser.parse_args()
    
    if (args.decode != None):
      decode(args.verbose, args.decode)
      quit()

    dt = args.time
    if (dt == None):
      dt = datetime.now()      
    else:
      dt = datetime.strptime(args.time, args.timeformat)
    debug(args.verbose, f"Time is : {dt}")
    encoded_dt = sm_encode_datetime(dt)
    if (dt == None):
      error("Unable to convert date time to StarMeteo")
      return(1)
    else:
      print(encoded_dt)

if __name__ == "__main__":
    main()
