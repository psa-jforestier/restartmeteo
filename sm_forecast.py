from sm_utils import BitField, sm_crcN

#├ │ └
def sm_decode_forecast(verbose, data: BitField):
    print("└ Decoding a forecast frame")
    data.setIdx(4) # ignore first nibble (frame identifier)
    area = data.pull(8)
    print(f"  ├ Area: {area}")
    alert = data.pull(2)
    print(f"  ├ Alert: 0b{alert:02b}")
    const = data.pull(2)
    print(f"  ├ Const: 0b{const:02b}")
    if (const != 0):
        print("    └ ⚠ Const is not zero")
    const = data.pullN()
    print(f"  ├ Const: 0x{const:01x}")
    if (const != 0x4):
        print("    └ ⚠ Const is not zero")
    expected_crc = data.pull(4)

    # recompute crc
    sum = sm_crcN(data, 0, 5)

    if (sum != expected_crc):
        print(f"  ├ ⚠ CRC mismatch. Recomputed CRC: 0x{sum:0x}, Expected CRC: 0x{expected_crc:0x}")
    else:
        print(f"  ├ CRC check passed (0x{sum:0x}).")

    # Forecast for day D
    day = 0
    while(True):
        i = 6 + (day * 15)# nibble index ├ │ └  
        print(f"  ├ Decoding forecast D + {day} at nibble index {i}")
        data.setIdx(i * 4) # set index to the start of the first block of forecast data (nibble index multiplied by 4 to get bit index)
        temp_max_tenth = data.pull(4)
        temp_max_unit = data.pull(4)
        temp_max = (temp_max_tenth * 10 + temp_max_unit) - 40
        temp_min_tenth = data.pull(4)
        temp_min_unit = data.pull(4)
        temp_min = (temp_min_tenth * 10 + temp_min_unit) - 40
        print(f"  │ ├ Temp Min: {temp_min:+03d} ; Temp Max: {temp_max:+03d}")
        icon0 = data.pull(8) # full day
        icon1 = data.pull(8) # night (00 to 06)
        icon2 = data.pull(8) # morning (06 to 12)
        icon3 = data.pull(8) # afternoon (12 to 18)
        icon4 = data.pull(8) # evening (18 to 24)
        print(f"  │ ├ Icon Full Day: 0x{icon0:02x}")
        print(f"  │ ├ Icons per quarter: 0x{icon1:02x} 0x{icon2:02x} 0x{icon3:02x} 0x{icon4:02x}")
        expected_crc = data.pull(4)
        computed_crc = sm_crcN(data, i, 14) # first 5 nibbles starting from nibble index 6
        if (computed_crc != expected_crc):
            print(f"  │ └ ⚠ CRC mismatch. Recomputed CRC: 0x{computed_crc:0x}, Expected CRC: 0x{expected_crc:0x}")
        else:
            print(f"  │ └ CRC check passed (0x{expected_crc:0x}).")
        if (data.getIdx() >= data.length):
            break
        day += 1
    print("  └ Finished decoding all forecast days.")