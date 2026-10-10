'''
starmeteo reverse engeneering project

This tool generate a StarMeteo compatible message for time synchronization.
'''

import argparse
from sm_utils import *
from datetime import datetime

import sm_utils
import sys
sys.stdout.reconfigure(encoding="utf-8")


'''
Time frame
Nibble  .-----0-----.   .-----1-----.   .-----2-----.   .-----3-----.   .-----4-----.   .-----5-----.   .-----6-----.   .-----7-----.   .-----8-----.
Bits    0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25  26  27  28  29  30  31  32  33  34  35  
        `--- 0xf ---'   `-- hour  --'   `-min.tenth-'   `-min.unit--'   `-- month --'   `-d10'  `--day.unit--'  `------- year -------'  `--- crc ---'
        frameidentifier
6bits pack
        ^   ^   ^   ^   ^   ^ | ^   ^   ^   ^   ^   ^ | ^   ^   ^   ^   ^   ^ | ^   ^   ^   ^   ^   ^ | ^   ^   ^   ^   ^   ^ | ^   ^   ^   ^   ^   ^ | 


'''
def sm_encode_datetime(dt, area=[75], interval=12, verbose=False):
  hour = dt.hour
  minute = dt.minute
  year = dt.year
  month = dt.month # 1..12
  day = dt.day # 1..31
  nbarea = len(area)

  bits = BitField(36) # At least 36 bits are needed at the beginning for the date time
  bits.setN(0, 0xf) # frame identifier
  # Hour
  if (hour < 10):
      bits.setN(1, hour)
      bits.setN(2, minute // 10)
      bits.setN(3, minute % 10)
  elif (hour >= 10 and hour <= 19):
      bits.setN(1, hour - 10)
      bits.setN(2, (minute // 10) + 10)
      bits.setN(3, minute % 10)
  else: # 20..23
      bits.setN(1, hour - 10)
      bits.setN(2, (minute // 10))
      bits.setN(3, minute % 10)
  # Month
  bits.setN(4, month)
  # day tenths in bits 0 and 1 of nibble 5
  day_t = day // 10 
  day_u = day % 10
  # day tenths in bits 0 and 1 of nibble 5
  bits.set(5*4, day_t, 2)
  # day unit in the next 4 bits
  bits.set((5*4) + 2, day_u, 4)
  yearoffset = year - 2000
  # year in the next 6 bits
  bits.set((5*4) + 2 + 4, yearoffset, 6)
  
  # crc
  sum = 0x07
  for i in range(0,8): # on first 8 nibbles (from 0 to 7)
    sum = sum + bits.getN(i)
  bits.setN(8, sum & 0x0f)
  # convert every 6 bits pack to an ascii char following the starmeteo encoding
  ascii_datetime = bittoascii(bits)
  if (verbose):
    debug(verbose, f"BitField nibbles representation: {bits.format(4)}")
    debug(verbose, f"Encoded datetime ASCII string: <<{ascii_datetime}>>")

  bits_area_length = 4 + 4 + 4 + 5 + 5 + (7 * nbarea) 
  debug(verbose, f"Area stored in {bits_area_length} bits")
  align = (4 - (bits_area_length % 4)) % 4
  debug(verbose, f"Alignment needed to bound on nibble: add {align} bits")
  bits_area_length += align
  bits_area_length += 4 + 8 # add const , checksum
  debug(verbose, f"Final bit array needed: {bits_area_length} bits")
  align6bits = (6 - (bits_area_length % 6)) % 6
  debug(verbose, f"Alignment needed to bound on 6 bits: add {align6bits} bits")
  bits_area_length += align6bits
  areabits = BitField(bits_area_length)
  areabits.pushN(0x0) # 3 padding nibbles
  areabits.pushN(0x0)
  areabits.pushN(0x0)
  areabits.push(interval, 5) # interval (5 bits)
  areabits.push(nbarea, 5) # number of areas (5 bits)
  for i in range(nbarea):
      areabits.push(area[i], 7) # each area takes 7 bits
  areabits.push(0, align) # add alignment bits (0 to 3 bits added) to be bound to a nibble
  areabits.push(0x5, 4) # push 4 bits for a magic constant (/!\ doc differs on this. starmeteo.c says it is 0x01, CelebWeather says it works with 1, 5, 7). Original capture use 5
  # crc, again
  crc = 0x07
  for i in range(0, areabits.getIdx() // 4): # on all nibbles up to the alignment including the 0x5 const
    crc = crc + areabits.getN(i)
  areabits.push(crc & 0xff, 8) # 8-bit CRC
  areabits.push(0x00, align6bits) # const

  debug(verbose, f"Nb of bits pushed: {areabits.getIdx()}, nb of bits allocated {bits_area_length}")

  return ascii_datetime + bittoascii(areabits)

def sm_decode_datetime(verbose, data: BitField, fast):
    valid = True
    if not fast:
        print("└ Decoding a time frame")
    debug(verbose, f"Bit pos | bit length | value")
    n1 = data.getN(1) # hour
    n2 = data.getN(2) # minute tens
    n3 = data.getN(3) # minute units
    debug(verbose, f"0       | 4          | 0x{data.getN(0):01x} : frame identifier")
    debug(verbose, f"4       | 4          | {n1} : hour (encoded)")
    debug(verbose, f"8       | 4          | {n2} : minute tens (encoded)")
    debug(verbose, f"12      | 4          | {n3} : minute units (encoded)")
    if (n1 < 10):
        if (n2 >= 10):
            hours = n1 + 10
            minutes = ((n2 - 10) * 10) + n3
        else:
            hours = n1
            minutes = (n2 * 10) + n3
    else:
        hours = n1 + 10
        minutes = (n2 * 10) + n3
    month = data.getN(4) #month
    day = ( data.get(20, 2) * 10) + data.get(22, 4) #day
    year = 2000 + data.get(26, 6) #year
    debug(verbose, f"16      | 4          | {month} : month")
    debug(verbose, f"20      | 2          | {day // 10} : day tens")
    debug(verbose, f"22      | 4          | {day % 10} : day units")
    debug(verbose, f"26      | 6          | {year - 2000} : year")
    debug(verbose, f"Decoded time: {hours:02d}:{minutes:02d}")
    debug(verbose, f"Decoded date: {year:04d}-{month:02d}-{day:02d}")
    # recompute crc
    sum = 0x07
    for i in range(0,8): # on first 8 nibbles (from 0 to 7)
      sum = sum + data.getN(i)
    sum = sum & 0x0f
    expected_crc = data.getN(8)
    debug(verbose, f"32      | 4          | 0x{expected_crc:01x} : CRC")
    debug(verbose, f"Recomputed CRC: 0x{sum:0x}")
    debug(verbose, f"Expected CRC:   0x{expected_crc:0x}")
    if not fast:
        print(f"  ├ Date time: {year:04d}-{month:02d}-{day:02d} {hours:02d}:{minutes:02d}")
        if sum != expected_crc:
            print(f"  │ └ ⚠ CRC mismatch. Recomputed CRC: 0x{sum:0x}, Expected CRC: 0x{expected_crc:0x}")
            valid = False
        else:
            print(f"  │ └ CRC check passed (0x{sum:0x}).")
    else:
        print(f" ; Date time: {year:04d}-{month:02d}-{day:02d} {hours:02d}:{minutes:02d}", end="") 
        if sum != expected_crc:
            print(f" ; ⚠ CRC mismatch. Recomputed CRC: 0x{sum:0x}, Expected CRC: 0x{expected_crc:0x}", end="")
            valid = False
        else:
            print(f" ; CRC check passed (0x{sum:0x}).", end="")

    # Continue decoding other parts of the time frame if necessary
    pad1 = data.getN(9) # some nibble padding
    pad2 = data.getN(10) # 
    pad3 = data.getN(11) #
    debug(verbose, f"36      | 12          | 0x{pad1:01x}{pad2:01x}{pad3:01x} : padding nibbles")
    if not fast:
        print(f"  ├ Padding nibbles: 0x{pad1:01x}{pad2:01x}{pad3:01x}")
        print(f"  └ Area block :")
    idx = data.setIdx(12*4) # set the index to the start of the area block
    interval = data.pull(5)
    debug(verbose, f"48      | 5           | {interval} : interval")
    nbarea = data.pull(5)
    if not fast:
        print(f"    ├ Interval: {interval}")
        print(f"    ├ Number of areas: {nbarea}")
    debug(verbose, f"53      | 5           | {nbarea} : number of areas")
    debug(verbose, f"58      | {nbarea}*7={nbarea*7}    | area codes")
    for i in range(nbarea):
        area = data.pull(7)
        if not fast:
            print(f"    │ ├ Area {i:2}: {area:2}")
        else:
            print(f" {area:2}", end="")
    # find alignment
    pos = 58 + (nbarea * 7)
    debug(verbose, f"Position after area : {pos}")
    align = (4 - (pos % 4)) % 4    
    debug(verbose, f"Alignment needed: {align} bits")
    for i in range(align):
        alignvalue = data.pull(1)
        debug(verbose, f"{i+pos:3}     | 1           | {alignvalue} : alignment bit")
    const = data.pull(4)
    if not fast:
        print(f"    ├ Const: 0x{const:01x}")
    debug(verbose, f"{pos+align:3}     | 4           | 0x{const} : const")
    crc = data.pull(8) # this crc is in 8 bits
    debug(verbose, f"{pos+align+4:3}     | 8           | 0x{crc:02x} : 8b area CRC")
    # recompute crc for the area block. 
    sum = 0x07
    for i in range(12, (pos+align+4) // 4): # on the nibbles of the area block
        v = data.getN(i)
        sum = sum + data.getN(i)
    sum = sum & 0xFF  # ensure the CRC is 8 bits
    debug(verbose, f"Recomputed area CRC: 0x{sum:02x}")
    if sum != crc:
        print(f"    ├ ⚠ Area CRC mismatch. Recomputed CRC: 0x{sum:02x}, Expected CRC: 0x{crc:02x}")
        valid = False
    else:
        print(f"    ├ Area CRC check passed (0x{sum:02x}).")
    remaining_length = data.length - data.getIdx()
    if (remaining_length != 0):  
        print(f"    └ Remaining bits after CRC: {remaining_length} bits")
        remaining_bits = data.pull(remaining_length)
        print(f"      └ Remaining bits: 0b{remaining_bits:0{remaining_length}b} / 0x{remaining_bits:0{(remaining_length + 3) // 4}x}")
    else:
        print(f"    └ No remaining bits after CRC.")
    return valid