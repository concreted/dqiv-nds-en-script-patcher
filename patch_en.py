import os, shutil

def main():
    print("Patching directory 'en', writing results to 'out'")
    
    shutil.rmtree("out", ignore_errors=True)
    os.mkdir("out")
    os.mkdir("out/en")

    patch_file_en("b0200000.mpt")

# Process a single "segment" of dialogue.
# The resulting segment should be the exact same length as the original segment.
def process_segment(segment):
    size = len(segment)
    # Strip all %0 control characters.
    s = segment.replace(b'%0', b'')

    processed_segment = bytearray(s)
    print(processed_segment)
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
        while pointer < size:
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
                else:
                    # Write any bytes encountered between segments to the output buffer
                    final_data.append(data[pointer])

                    pointer += 1
            elif segment_end == None:
                # Need to look for a new segment end.
                if data[pointer:pointer+4] == b'@c2@' or data[pointer:pointer+4] == b'@c1@' or data[pointer:pointer+4] == b'@c0@':
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

if __name__ == "__main__":
    main()
