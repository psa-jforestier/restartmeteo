#!/usr/bin/env python3
'''
starmeteo reverse engeneering project

This tool generate a StarMeteo compatible message for time synchronization.
'''

import argparse
from sm_utils import *
from datetime import datetime



    
def sm_encode_datetime(dt):
  # TODO
  return dt.strftime("%Y-%m-%d_%H:%M:%S")
  

    
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
