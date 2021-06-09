import os, shutil, sys

mode_gender = 'n'
mode_lang = 'en'

def main():
    print("Patching directory 'en', writing results to 'out'")
    
    shutil.rmtree("out", ignore_errors=True)
    os.mkdir("out")
    os.mkdir(f"out/{mode_lang}")

    # patch_file_en("b0200000.mpt")

    # Plurals
    # patch_file_en("b0803000.mpt")

    # Nested
    patch_file_en("b0802000.mpt")

    # Party-specific
    patch_file_en("b0018000.mpt")

def is_control_char(bytes):
    return bytes == b'%H' or bytes == b'%M' or bytes == b'%O' or bytes == b'%A'

def is_regular_control_char(bytes):
    return bytes == b'%H' or bytes == b'%M' or bytes == b'%O'

def is_regular_secondary_control_char(bytes):
    return bytes == b'%Y'

def is_gender_control_char(bytes):
    return bytes == b'%A'

def is_gender_secondary_control_char(bytes):
    return bytes == b'%B' or bytes == b'%C'

def replace_control_segment(control_char, options):
    assert is_control_char(control_char), f'Attempted to replace non-control-char: {control_char}'

    if control_char == b'%H':
        return options[len(options)-1]
    elif control_char == b'%M':
        return options[len(options)-1]
    elif control_char == b'%O':
        return options[0]
    elif control_char == b'%A':
        if mode_gender == 'b':
            return bytearray('/', 'utf-8').join(options)
        elif mode_gender == 'm':
            return options[0]
        elif mode_gender == 'f':
            if len(options) > 1:
                return options[1]
            return options[0]

        # Rule-based replacement
        if len(options) == 1:
            return options[0]
        else:
            if options[0] == b'his':
                return b'their'
            
            print(f'WARNING: Unhandled gender replacement, falling back to first: {options[0]}')
            return options[0]
    raise

def reduce_control_segment(segment):
    is_regular = is_regular_control_char(segment[0:2])
    is_gender = is_gender_control_char(segment[0:2])
    assert is_regular or is_gender, f'Attempted to reduce non-control segment: {segment}'
    if is_gender:
        return reduce_gender_control_segment(segment)
    return reduce_regular_control_segment(segment)

def reduce_regular_control_segment(segment):
    size = len(segment)

    pointer = 0
    # Control segment starts appear to always be 7 bytes
    pointer = pointer + 7

    options = [bytearray("", 'utf-8')]
    options_index = 0

    while pointer < size:
        if is_control_char(segment[pointer:pointer+2]):
            rcs, cs = reduce_control_segment(segment[pointer:])
            pointer += len(cs)
        elif is_regular_secondary_control_char(segment[pointer:pointer+2]):
            options.append(bytearray("", 'utf-8'))
            options_index += 1
            pointer += 2
        elif segment[pointer:pointer+2] == b'%Z':
            pointer += 2
            break
        else:
            options[options_index].append(segment[pointer])
            pointer += 1

    control_segment = segment[0:pointer]
    reduced_control_segment = replace_control_segment(segment[0:2], options)

    # print(f'***Found control segment: {control_segment}***')
    # print(f'***Reduced control segment: {reduced_control_segment}***')
    # print(f'Regular options: {options}')

    return reduced_control_segment, control_segment

def reduce_gender_control_segment(segment):
    size = len(segment)

    pointer = 0
    # Control segment starts appear to always be 7 bytes
    pointer = pointer + 7

    options = [bytearray("", 'utf-8')]
    options_index = 0

    while pointer < size:
        if is_control_char(segment[pointer:pointer+2]):
            rcs, cs = reduce_control_segment(segment[pointer:])
            pointer += len(cs)
        elif is_gender_secondary_control_char(segment[pointer:pointer+2]):
            options.append(bytearray("", 'utf-8'))
            options_index += 1
            pointer += 7
        elif segment[pointer:pointer+2] == b'%Z':
            pointer += 2
            # Check if we have any further gender options after this one.
            # If not, we can end.
            if not is_gender_secondary_control_char(segment[pointer:pointer+2]):
                break
        else:
            options[options_index].append(segment[pointer])
            pointer += 1

    control_segment = segment[0:pointer]
    reduced_control_segment = replace_control_segment(segment[0:2], options)

    # TODO: Implement. Should return the reduced form of the control segment. 
    # print(f'***Found gender control segment: {control_segment}***')
    # print(f'***Reduced gender control segment: {reduced_control_segment}***')
    # print(f'Gender options: {options}')

    return reduced_control_segment, control_segment

def process_control_chars(segment):
    size = len(segment)
    # Step through segment 
    processed_segment = bytearray("", 'utf-8')

    pointer = 0
    while pointer < size:
        if is_control_char(segment[pointer:pointer+2]):
            reduced_control_segment, control_segment = reduce_control_segment(segment[pointer:])
            processed_segment.extend(reduced_control_segment)
            pointer += len(control_segment)
        else:
            # Write the current byte as-is
            processed_segment.append(segment[pointer])
            pointer += 1

    return processed_segment

# Process a single "segment" of dialogue.
# The resulting segment should be the exact same length as the original segment.
def process_segment(segment):
    size = len(segment)

    # Strip all %0 control characters.
    segment = segment.replace(b'%0', b'')

    processed_segment = process_control_chars(segment)

    # Rewrite %H***%X<singular>%Y<plural>%Z blocks. Use the plural variant for these blocks.

    # Rewrite %M***%X<plural>%Y<singular>%Z blocks. Use the singular variant for these blocks.

    # Rewrite %O***%X<leader>%Y<specific party member>%Z blocks. Use the first variant.

    # Rewrite %A***%X<masculine>%Z%B***%X<feminine>%Z%C***%X<non-gendered>%Z blocks using rule-based replacement.

    # Fix grammar issues caused by replacements.

    # Re-layout lines with max 42-char lines.

    # Pad the processed segment to the same length as the original.
    print(f'Processed segment: {processed_segment}')
    while len(processed_segment) < size:
        processed_segment.extend(b' ')

    assert len(processed_segment) == size, f"ERROR: Processed segment size ({len(processed_segment)}) does not match original size ({size})"

    return processed_segment

def patch_file_en(filename):
    print(f'Patching file en/{filename}')
    with open(f'en/{filename}', "rb") as in_file, open (f'out/en/{filename}', "wb") as out_file:
        data = in_file.read()
        size = len(data)

        print(f'Size: {size} bytes')

        final_data = bytearray("", 'utf-8')

        pointer = 0
        segment_start = None
        segment_end = None
        nametag = b''
        while pointer <= size:
            if segment_start == None:
                # Need to look for a new segment start.
                if data[pointer:pointer+2] == b'@a':
                    # Look for the nametag end marker
                    pointer = pointer+2
                    nametag_start = pointer
                    nametag_len = 0
                    while data[pointer:pointer+2] != b'@b':
                        nametag_len += 1
                        pointer += 1
                    nametag = data[nametag_start:nametag_start + nametag_len]

                    # Write the segment start marker
                    final_data.extend(b'@a')
                    final_data.extend(nametag)
                    final_data.extend(b'@b')

                    # TODO: Support jp-compatible segments where nametags are inside the regular segment text.

                    segment_start = pointer+2
                elif pointer < size:
                    # Write any bytes encountered between segments to the output buffer
                    final_data.append(data[pointer])

                pointer += 1
            elif segment_end == None:
                # Need to look for a new segment end.
                if data[pointer:pointer+4] == b'@c3@' or data[pointer:pointer+4] == b'@c2@' or data[pointer:pointer+4] == b'@c1@' or data[pointer:pointer+4] == b'@c0@':
                    segment_end = pointer
                    pointer = pointer+4
                else:
                    pointer += 1
            else:
                # We have a start and end to the segment.
                segment = data[segment_start:segment_end]
                segmentSize = len(segment)

                nametag_print = f' [{nametag}]' if len(nametag) > 0 else ''
                print(f'Processing segment ({segmentSize} bytes):{nametag_print} {segment}')

                # Process the segment.
                processedSegment = process_segment(segment)
                
                # Write the processed segment.
                final_data.extend(processedSegment)

                # Write the segment end marker
                final_data.extend(data[segment_end:segment_end+4])

                # Reset the segment start/end pointers.
                segment_start = None
                segment_end = None
                nametag = b''

                # break

        out_file.write(final_data)

        assert len(final_data) == size, f"Final size ({len(final_data)}) does not match original size ({size})"

        print(f'Successfully patched file en/{filename}')

if __name__ == "__main__":
    main()
