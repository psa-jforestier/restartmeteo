from sm_utils import BitField, bittoascii, encode_temp, sm_crc8, sm_crcN, debug, warning

#├ │ └

def sm_rainidx_to_proba(idx):
    return {
        0x0:0,
        0x1:5,
        0x2:10,
        0x3:20,
        0x4:25,
        0x5:30,
        0x6:40,
        0x7:50,
        0x8:60,
        0x9:70,
        0xA:75,
        0xB:80,
        0xC:90,
        0xD:95,
        0xE:98,
        0xF:99
    }.get(idx, 0xe)

def sm_proba_to_rainidx(proba):
    thresholds = [ 2.5,  7.5, 15,   22.5, 
                  27.5, 35,   45,   55, 
                  65,   72.5, 77.5, 85, 
                  92.5, 97];
    for index, threshold in enumerate(thresholds):
        if proba < threshold:
            return index
    return 0xe;
    
def sm_decode_forecast_alert(verbose, data: BitField):
    valid = True
    print("└ Decoding an alert forecast frame")    
    data.setIdx(4) # ignore first nibble (frame identifier)
    const1 = data.pullN()
    nbalert = data.pullN()
    const2 = data.pullN()
    debug(verbose, f"Const1: 0x{const1:01x}, NbAlert: {nbalert}, Const2: 0x{const2:01x}")
    i = 0 # nibble index
    while (i < nbalert):
        unkown = data.pull(5)
        level = data.pull(2)
        detail = data.pull(5)
        info = (unkown << 7) + (level << 5) + detail
        debug(verbose, f"Alert {i:2}: 0x{info:03x}")
        print(f"  │ ├ alert {i:2} - Unknown: 0x{unkown:02x} ({unkown:2}), Level: 0b{level:02b}, Detail: 0x{detail:02x}")
        i = i + 1
    expected_crc = data.pull(8)
    computed_crc = 0x07
    for i in range(0, 6 + (3 * i)):
        computed_crc = computed_crc + data.getN(i)
    computed_crc = computed_crc & 0xff
    if (computed_crc != expected_crc):
        print(f"  ├ ⚠ CRC mismatch. Recomputed CRC: 0x{computed_crc:0x}, Expected CRC: 0x{expected_crc:0x}")
        valid = False
    else:
        print(f"  ├ CRC check passed (0x{expected_crc:0x}).")
    return valid

def sm_decode_forecast_long(verbose, data: BitField):
    valid = True
    cli_forecast = [] # parameters for the cli
    print("└ Decoding an extended forecast frame")
    data.setIdx(4) # ignore first nibble (frame identifier)
    # Implementation for long forecast decoding goes here
    area = data.pull(8)
    cli_forecast.append("--area " + str(area))
    alert = data.pull(2)
    const1 = data.pull(2)
    const2 = data.pullN()
    expected_crc = data.pull(4)
    print(f"  ├ Area: {area}")
    print(f"  ├ Alert: 0b{alert:02b}")
    print(f"  ├ Const1: 0b{const1:02b}")
    if (const1 != 0):
        print("    └ ⚠ Const is not zero")
    print(f"  ├ Const2: 0x{const2:01x}")
    if (const2 != 0x4):
        print("    └ ⚠ Const is not 0x4")
    # recompute crc
    sum = sm_crcN(data, 0, 5)
    if (sum != expected_crc):
        print(f"  ├ ⚠ CRC mismatch. Recomputed CRC: 0x{sum:0x}, Expected CRC: 0x{expected_crc:0x}")
        valid = False
    else:
        print(f"  ├ CRC check passed (0x{sum:0x}).")
    # decode forecast for Day+0 to Day+5
    day = 0
    while(day < 6):
        i = 6 + (day * 15)# nibble index ├ │ └  
        print(f"  ├ Decoding forecast D + {day} at nibble index {i}")
        data.setIdx(i * 4) # set index to the start of the first block of forecast data (nibble index multiplied by 4 to get bit index)
        temp_min_tenth = data.pull(4)
        temp_min_unit = data.pull(4)
        temp_min = (temp_min_tenth * 10 + temp_min_unit) - 40
        temp_max_tenth = data.pull(4)
        temp_max_unit = data.pull(4)
        temp_max = (temp_max_tenth * 10 + temp_max_unit) - 40
        print(f"  │ ├ Temp Min: {temp_min:+03d} ; Temp Max: {temp_max:+03d}")        
        icon0 = data.pull(8) # full day
        icon1 = data.pull(8) # night (00 to 06)
        icon2 = data.pull(8) # morning (06 to 12)
        icon3 = data.pull(8) # afternoon (12 to 18)
        icon4 = data.pull(8) # evening (18 to 24)
        print(f"  │ ├ Icon Full Day: 0x{icon0:02x}")
        print(f"  │ ├ Icons per quarter: 0x{icon1:02x} 0x{icon2:02x} 0x{icon3:02x} 0x{icon4:02x}")
        expected_crc = data.pull(4)
        computed_crc = sm_crcN(data, i, 14) 
        if (computed_crc != expected_crc):
            print(f"  │ └ ⚠ CRC mismatch. Recomputed CRC: 0x{computed_crc:0x}, Expected CRC: 0x{expected_crc:0x}")
            valid = False
        else:
            print(f"  │ └ CRC check passed (0x{expected_crc:0x}).")
        # capture in advance the rain for debugging purpose
        rain_nibble_idx = 96 + ((day * 5) + 2)
        debug(verbose, f"Rain nibble index for D + {day}: {rain_nibble_idx}")
        rainidx = data.getN(rain_nibble_idx)
        rainproba = sm_rainidx_to_proba(rainidx)
        cli_forecast.append(f"--forecast {temp_min},{temp_max},0x{icon0:02x},0x{icon1:02x},0x{icon2:02x},0x{icon3:02x},0x{icon4:02x},{rainproba}")
        day += 1
    # decoding the rain probability. Nibble 96
    debug(verbose, f"Now reading nibble after forecast decoding: {data.getIdx() // 4}")
    day = 0
    while(day < 6):
        i = 96 + (day * 5) # nibble index for the rain
        print(f"  ├ Decoding rain D + {day} at nibble index {i}")
        data.setIdx(i * 4) # set index to the start of the first block of forecast data (nibble index multiplied by 4 to get bit index)
        const1 = data.pullN()
        const2 = data.pullN()
        rainidx = data.pullN()
        const3 = data.pullN()
        const4 = data.pullN()
        print(f"  │ ├ Const1: 0x{const1:01x}")
        print(f"  │ ├ Const2: 0x{const2:01x}")
        print(f"  │ ├ Rain: 0x{rainidx:01x} ({sm_rainidx_to_proba(rainidx)}%)")
        print(f"  │ ├ Const3: 0x{const3:01x}")
        print(f"  │ ├ Const4: 0x{const4:01x}")
        day+=1
    debug(verbose, f"Now reading nibble after rain decoding: {data.getIdx() // 4}")
    # End of frame, nibble 126
    expected_crc = data.pull(8) # here comes the 8 bit crc
    computed_crc = sm_crc8(data, 96, 6 * 5)
    if (computed_crc != expected_crc):
        print(f"  ├ ⚠ CRC mismatch. Recomputed CRC: 0x{computed_crc:0x}, Expected CRC: 0x{expected_crc:0x}")
        valid = False
    else:
        print(f"  ├ CRC check passed (0x{expected_crc:0x}).")
    print(f"  ├ CLI forecast parameters: {' '.join(cli_forecast)}")
    remaining_length = data.length - data.getIdx()
    if (remaining_length != 0):  
        print(f"  └ Remaining bits after CRC: {remaining_length} bits")
        remaining_bits = data.pull(remaining_length)
        print(f"    └ Remaining bits: 0b{remaining_bits:0{remaining_length}b} / 0x{remaining_bits:0{(remaining_length + 3) // 4}x}")
    else:
        print(f"    └ No remaining bits after CRC.")
    return valid

def sm_decode_forecast(verbose, data: BitField):
    valid = True
    cli_forecast = [] # parameters for the cli
    print("└ Decoding a forecast frame")
    data.setIdx(4) # ignore first nibble (frame identifier)
    area = data.pull(8)
    print(f"  ├ Area: {area}")
    cli_forecast.append("--area " + str(area))
    alert = data.pull(2)
    print(f"  ├ Alert: 0b{alert:02b}")
    const = data.pull(2)
    print(f"  ├ Const: 0b{const:02b}")
    if (const != 0):
        print("    └ ⚠ Const is not zero")
    const = data.pullN()
    print(f"  ├ Const: 0x{const:01x}")
    if (const != 0x4):
        print("    └ ⚠ Const is not 0x4")
    expected_crc = data.pull(4)

    # recompute crc
    sum = sm_crcN(data, 0, 5)

    if (sum != expected_crc):
        print(f"  ├ ⚠ CRC mismatch. Recomputed CRC: 0x{sum:0x}, Expected CRC: 0x{expected_crc:0x}")
        valid = False
    else:
        print(f"  ├ CRC check passed (0x{sum:0x}).")

    # Forecast for day D
    day = 0
    while(True):
        i = 6 + (day * 15)# nibble index ├ │ └  
        print(f"  ├ Decoding forecast D + {day} at nibble index {i}")
        data.setIdx(i * 4) # set index to the start of the first block of forecast data (nibble index multiplied by 4 to get bit index)
        temp_min_tenth = data.pull(4)
        temp_min_unit = data.pull(4)
        temp_min = (temp_min_tenth * 10 + temp_min_unit) - 40
        temp_max_tenth = data.pull(4)
        temp_max_unit = data.pull(4)
        temp_max = (temp_max_tenth * 10 + temp_max_unit) - 40
        print(f"  │ ├ Temp Min: {temp_min:+03d} ; Temp Max: {temp_max:+03d}")
        icon0 = data.pull(8) # full day
        icon1 = data.pull(8) # night (00 to 06)
        icon2 = data.pull(8) # morning (06 to 12)
        icon3 = data.pull(8) # afternoon (12 to 18)
        icon4 = data.pull(8) # evening (18 to 24)
        cli_forecast.append(f"--forecast {temp_min},{temp_max},0x{icon0:02x},0x{icon1:02x},0x{icon2:02x},0x{icon3:02x},0x{icon4:02x}")
        print(f"  │ ├ Icon Full Day: 0x{icon0:02x}")
        print(f"  │ ├ Icons per quarter: 0x{icon1:02x} 0x{icon2:02x} 0x{icon3:02x} 0x{icon4:02x}")
        expected_crc = data.pull(4)
        computed_crc = sm_crcN(data, i, 14) # first 5 nibbles starting from nibble index 6
        if (computed_crc != expected_crc):
            print(f"  │ └ ⚠ CRC mismatch. Recomputed CRC: 0x{computed_crc:0x}, Expected CRC: 0x{expected_crc:0x}")
            valid = False
        else:
            print(f"  │ └ CRC check passed (0x{expected_crc:0x}).")
        if (data.getIdx() >= data.length):
            break
        day += 1
    print(f"  ├ CLI forecast parameters: {' '.join(cli_forecast)}")
    print( "  └ Finished decoding all forecast days.")
    return valid

def get_forecast_data_from_string(fcdata):
    parts = fcdata.split(",")
    forecast_data = {
        "Tmin": int(parts[0], 0),
        "Tmax": int(parts[1], 0),
        "FullDayIcon": int(parts[2], 0),
        "NightIcon": int(parts[3], 0),
        "MorningIcon": int(parts[4], 0),
        "AfternoonIcon": int(parts[5], 0),
        "EveningIcon": int(parts[6], 0),
    }
    if len(parts) > 7:
        forecast_data["Rain"] = int(parts[7], 0)
    else:
        forecast_data["Rain"] = None
    return forecast_data
def sm_encode_forecast(forecast_values, area:int, verbose=False):
    # Placeholder implementation for encoding forecast values
    debug(verbose, f"Starting to encode forecast values: {forecast_values}")
    # check if we have to use long or short forecast frame, based
    # on the 1st forecast. It should contains Tmin,Tmax,FullDayIcon,NightIcon,MorningIcon,AfternoonIcon,EveningIcon
    # and eventually the Rain value.
    fcdata = []
    for i in forecast_values:
        fc = get_forecast_data_from_string(i)
        fcdata.append(fc)
    if (fcdata[0].get('Rain') is None):
        frametype = 0x4 # short forecast frame
    else:
        frametype = 0x0 # extended forecast frame
    debug(verbose, f"Determined frame type: 0x{frametype:1x}")
    nbdays = len(forecast_values)
    debug(verbose, f"Number of forecast entries: Day+0 to Day+{nbdays}")
    # how many bits do we need
    bitlenght = 4 * ( # computed in nibbles
        6 + # field marker, area (2 nibble), alert, const, crc
        (15 * nbdays)  # tmin (2nib), tmax (2nib), icon 0 to 4 (2 nib each), crc (one nibble)
    )
    # extended frame
    if (frametype == 0x0):
        extranib = 5 * nbdays # const, const, proba, const, const
        extranib += 4 # crc (byte), const, const
        bitlenght += 4 * extranib
    # nb if bits must also be a multiple of 6 or the
    # ascii encoding will fail
    if bitlenght % 6 != 0:
        debug(verbose, f"Bit to add to pad on 6 bits: {6 - (bitlenght % 6)}")
        bitlenght += 6 - (bitlenght % 6)
    debug(verbose, f"Total bit length for the forecast frame: {bitlenght} bits, {bitlenght // 4} nibbles")
    bitfield = BitField(bitlenght)
    bitfield.pushN(frametype)
    bitfield.pushN((area & 0xf0) >> 4) # high bits
    bitfield.pushN(area & 0x0f) # low bits
    bitfield.pushN(0x0) # alert
    bitfield.pushN(0x4) # const
    crc = sm_crcN(bitfield, 0, 5)
    bitfield.pushN(crc)
    i = 0
    # Encode each day's forecast data into the bitfield
    for d in fcdata:
        idx = bitfield.getIdx()
        debug(verbose, f"Create data for Day+{i}")
        debug(verbose, d)
        h,l = encode_temp(d['Tmin'])
        bitfield.pushN(h & 0x0f)
        bitfield.pushN(l & 0x0f)
        h,l = encode_temp(d['Tmax'])
        bitfield.pushN(h & 0x0f)
        bitfield.pushN(l & 0x0f)
            
        for j in ['FullDayIcon', 'NightIcon', 'MorningIcon', 'AfternoonIcon', 'EveningIcon']:            
            bitfield.pushB(d[j])
        crc = sm_crcN(bitfield, idx//4, 14)
        bitfield.pushN(crc)
        i = i + 1
    # rain proba    
    if (frametype == 0x0): # extended frame
        i = 0
        idx_before = bitfield.getIdx()
        for d in fcdata:
            debug(verbose, f"Create rain data for Day+{i}")
            rain = d['Rain']
            if rain is not None:
                if (rain < 0 or rain > 100):
                    warning(f"Rain value out of range for Day+{i}, using default 99")
                    rain = 99
            else:
                rain = 99
                warning(f"Rain value missing for Day+{i}, using default {rain}")
            # convert rain proba (from 0 to 100) to rain idx
            rain_idx = sm_proba_to_rainidx(rain)
            debug(verbose, f"Rain value: {rain}, idx: 0x{rain_idx:x}")
            """
            D'apres CelebWeather, on doit avoir des constantes 
            0x3c[rainidx]0x6e
            mais starmeteo.c recopie le rainidx
            """
            bitfield.pushN(rain_idx)
            bitfield.pushN(rain_idx)
            bitfield.pushN(rain_idx)
            bitfield.pushN(rain_idx)
            bitfield.pushN(rain_idx)
            #bitfield.pushB(0x3c) # cheulou const value
            #bitfield.pushN(rain_idx)
            #bitfield.pushB(0x6e) # another cheulou const avalue
            i = i + 1
        idx_after = bitfield.getIdx()
        debug(verbose, f"Rain data bitfield index before: {idx_before}, after: {idx_after}")
        crc = sm_crc8(bitfield, idx_before // 4, (idx_after - idx_before) // 4)
        bitfield.pushB(crc)
        bitfield.pushN(0x0) # const
        bitfield.pushN(0xb) # const
    debug(verbose, f"Forecast frame creation complete. Length: {bitfield.getIdx()} bits")
    debug(verbose, f"Final hexa bitfield: {bitfield.format(4, base=16)}")
    return (bittoascii(bitfield))