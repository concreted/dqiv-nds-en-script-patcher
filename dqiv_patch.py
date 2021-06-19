import os, shutil, argparse, logging, sys

logging.basicConfig(format='%(message)s', stream=sys.stdout, level=logging.INFO)

mode_gender = 'n'
mode_lang = 'en'

def main():
    global mode_gender
    global mode_lang

    parser = argparse.ArgumentParser(description='Patch English script files for JP Dragon Quest VI ROM.')
    parser.add_argument('--file', help='file to be patched. must be present in the ./en directory', default=None)
    parser.add_argument('--gender', help='[(n)|m|f|b] player character gender. options are neutral, male, female, both', default='n')
    parser.add_argument('--lang', help='[(en)|ja] rom language mode to target. en uses nametags, ja embeds the speaker name in text', default='en')
    parser.add_argument('--debug', dest='debug', action='store_true', help='enable debug logs')

    args = parser.parse_args()

    if args.gender not in ['n', 'm', 'f', 'b']:
        logging.error(f'Unsupported --gender: {args.gender}')
        exit(1)
    if args.lang not in ['en', 'ja']:
        logging.error(f'Unsupported --lang: {args.lang}')
        exit(1)
    if args.debug:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
    mode_gender = args.gender
    mode_lang = args.lang
    logging.info(f"Patching directory en, writing results to 'out/{mode_lang}'")
    
    shutil.rmtree("out", ignore_errors=True)
    os.mkdir("out")
    os.mkdir(f"out/{mode_lang}")

    if args.file is not None:
        patch_file_en(args.file)
    else:
        files = os.listdir('en')
        for file in files:
            patch_file_en(f'{file}')

    # Prologue
    # patch_file_en("b0200000.mpt")

    # Plurals
    # patch_file_en("b0803000.mpt")

    # Nested
    # patch_file_en("b0802000.mpt")

    # Party-specific
    # patch_file_en("b0018000.mpt")

    # Chapter titles (special case)
    # patch_file_en("b1007000.mpt")

    # Battle text
    # patch_file_en('b0801000.mpt')

def is_control_char(bytes):
    return is_regular_control_char(bytes) or is_gender_control_char(bytes)

def is_regular_control_char(bytes):
    return bytes == b'%H' or bytes == b'%M' or bytes == b'%O' or bytes == b'%L'

def is_regular_secondary_control_char(bytes):
    return bytes == b'%Y'

def is_gender_control_char(bytes):
    return bytes == b'%A'

def is_gender_secondary_control_char(bytes):
    return bytes == b'%B' or bytes == b'%C'

def replace_control_segment(control_char, options):
    assert is_control_char(control_char), f'Attempted to replace non-control-char: {control_char}'

    if control_char == b'%H':
        # Rewrite %H***%X<singular>%Y<plural>%Z blocks. Use the plural variant for these blocks.
        return options[len(options)-1]
    elif control_char == b'%M':
        # Rewrite %M***%X<plural>%Y<singular>%Z blocks. Use the singular variant for these blocks.
        return options[len(options)-1]
    elif control_char == b'%O':
        # Rewrite %O***%X<leader>%Y<specific party member>%Z blocks. Use the first variant.
        return options[0]
    elif control_char == b'%L':
        # Rewrite %L***%X<both sisters>%Y<one sister>%Z blocks. Use the second variant.
        return options[1]
    elif control_char == b'%A':
        # Rewrite %A***%X<masculine>%Z%B***%X<feminine>%Z%C***%X<non-gendered>%Z blocks 
        # using specific gender mode or rule-based replacement.
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
            logging.warning(f'**** WARNING ****: Gender block has only one choice: {options[0]}')
            return options[0]
        else:
            if options[0] == b'his':
                return b'their'
            if options[0] == b'he':
                return b'they'
            if options[0] == b'man':
                return b'person'
            if options[0] == b'him':
                return b'them'
            if options[0] == b'himself':
                return b'themself'
            if options[0] == b'feen':
                return b'person' 
            if options[0] == b'laddie':
                return b'child'
            if options[0] == b'his':
                return b'their'
            if options[0] == b'gent':
                return b'one'
            if options[0] == b'monsieur':
                return b'friend'
            if options[0] == b'son':
                return b'young one'
            if options[0] == b'o mighty hero':
                return b'o mighty warrior'
            if options[0].find(b'guy') >= 0:
                return b'person'
            if options[0].find(b'sir') >= 0:
                return b'friend'
            if options[0].find(b'boy') >= 0:
                return b'young one'
            if options[0].find(b'ero') >= 0 and options[1].find(b'eroine') >= 0:
                return b'warrior'
            logging.warning(f'**** WARNING ****: Unhandled gender replacement, falling back to first: {options[0]}')
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

    logging.debug(f'***Found control segment: {control_segment}***')
    logging.debug(f'***Reduced control segment: {reduced_control_segment}***')
    logging.debug(f'Regular options: {options}')

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

    logging.debug(f'***Found gender control segment: {control_segment}***')
    logging.debug(f'***Reduced gender control segment: {reduced_control_segment}***')
    logging.debug(f'Gender options: {options}')

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

def fix_grammar(segment):
    fixed_segment = segment
    fixed_segment = fixed_segment.replace(b"they's", b"they are")
    fixed_segment = fixed_segment.replace(b"What luck!", b"Found")
    return bytearray(fixed_segment)

def reflow_segment(segment, force=False, reflow_limit=43, newline_end=True):
    # Check if we need to reflow at all. If not, return the original segment.
    needs_reflow = force
    lines = segment.split(b'\n')
    for line in lines:
        if len(line) > reflow_limit:
            needs_reflow = True
            break
    if not needs_reflow:
        return bytearray(segment)

    # Convert all newlines to spaces.
    reflowed_segment = bytearray(segment.replace(b'\n', b' '))

    # Break segment into lines of max reflow_limit chars.
    size = len(segment)
    pointer = 0
    current_line_size = 0
    last_space_index = None
    while pointer < size:
        if reflowed_segment[pointer] == ord(' '):
            last_space_index = pointer
        if current_line_size > reflow_limit and last_space_index is not None:
            reflowed_segment[last_space_index] = ord('\n')
            last_space_index = None
            current_line_size = 0
        else:
            current_line_size += 1 
        pointer += 1

    reflowed_size = len(reflowed_segment)
    if newline_end:
        if reflowed_segment[reflowed_size-1] == ord(' '):
            reflowed_segment[reflowed_size-1] = ord('\n')
    else:
        if reflowed_segment[reflowed_size-1] == ord('\n'):
            reflowed_segment[reflowed_size-1] = ord(' ')

    return reflowed_segment

# Process a single "segment" of dialogue.
# The resulting segment should be the exact same length as the original segment.
def process_segment(filename, segment):
    size = len(segment)

    # Strip all %0 control characters.
    segment = segment.replace(b'%0', b'')

    processed_segment = process_control_chars(segment)

    # Fix grammar issues caused by replacements.
    processed_segment = fix_grammar(processed_segment)

    # Reflow lines.
    if (filename == 'b0801000.mpt'):
        processed_segment = reflow_segment(processed_segment, True, 45, False)
        # Special case logic: 
        if processed_segment.find(b'appears!') >= 0 or processed_segment.find(b'appear!') >= 0:
            # Enemy name announcements should end with newline.
            processed_segment[len(processed_segment)-1] = ord('\n')
        if processed_segment.find(b'Each party member receives') >= 0:
            # Experience points message should not have any newlines.
            processed_segment = bytearray(processed_segment.replace(b'\n', b' '))
    else:
        processed_segment = reflow_segment(processed_segment, True, 43, False)

    # Pad the processed segment to the same length as the original.
    logging.info(f'Processed segment: {bytes(processed_segment)}')
    while len(processed_segment) < size:
        processed_segment.extend(b' ')

    assert len(processed_segment) == size, f"ERROR: Processed segment size ({len(processed_segment)}) does not match original size ({size})"

    return processed_segment

def special_case_patch(filename, data):
    patched_data = data
    patched = False
    if filename == 'b1007000.mpt':
        patched_data = patched_data.replace(b'@1Chapter 1: Ragnar McRyan and the Case of the Missing Children@', b'@1Chapter 1: Ragnar McRyan\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE@')
        patched_data = patched_data.replace(b'@1Chapter 2: Alena and the Journey to the Tourney@', b'@1Chapter 2: Alena\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE@')
        patched_data = patched_data.replace(b'@1Chapter 3: Torneko and the Extravagant Excavation@', b'@1Chapter 3: Torneko\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE@')
        patched_data = patched_data.replace(b'@1Chapter 4: Meena and Maya and the Mahabala Mystery@', b'@1Chapter 4: Meena and Maya\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE\xFE@')
        patched = True
    return patched_data, patched

def patch_file_en(filename):
    logging.info(f'Patching file {filename}')
    with open(f'en/{filename}', "rb") as in_file, open (f'out/{mode_lang}/{filename}', "wb") as out_file:
        data = in_file.read()
        size = len(data)

        logging.info(f'Size: {size} bytes')

        data, patched = special_case_patch(filename, data)
        if (patched):
            out_file.write(data)
            assert len(data) == size, f"Final size ({len(data)}) does not match original size ({size})"
            logging.info(f'Successfully applied special case patch file en/{filename}')
            return

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
                    if mode_lang == 'en':
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
                if mode_lang == 'ja' and len(nametag) > 0:
                    # Strip off last char and add nametag*
                    segment_strip_last_char = segment[:len(segment)-1]
                    nametag_part = bytearray(nametag)
                    nametag_part.extend(b'*')
                    segment = nametag_part
                    segment.extend(segment_strip_last_char)
                segmentSize = len(segment)

                nametag_print = f' [{nametag}]' if len(nametag) > 0 else ''
                logging.info(f'Processing segment ({segmentSize} bytes):{nametag_print} {segment}')

                # Process the segment.
                processedSegment = process_segment(filename, segment)
                
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

        logging.info(f'Successfully patched file en/{filename}')

if __name__ == "__main__":
    main()
