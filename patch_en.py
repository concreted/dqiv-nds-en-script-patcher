import os, shutil

def main():
    print("Patching directory 'en', writing results to 'out'")
    
    shutil.rmtree("out")
    os.mkdir("out")

    patch_file_en("b0200000.mpt")

def patch_file_en(filename):
    print(f'Patching file en/{filename}')
    with open(f'en/{filename}', "rb") as in_file, open (f'out/{filename}', "wb") as out_file:
        data = in_file.read()
        size = len(data)

        print(f'Size: {size} bytes')

        final_data = bytearray("", 'utf-8')

        pointer = 0
        segmentStart = None
        segmentEnd = None
        while pointer < size:
            if segmentStart == None:
                # Need to look for a new segment start.
                if data[pointer:pointer+4] == b'@a@b':
                    # Write the segment start marker
                    final_data.extend(b'@a@b')

                    segmentStart = pointer+4
                else:
                    # Write any bytes encountered between segments to the output buffer
                    final_data.append(data[pointer])

                    pointer += 1
            elif segmentEnd == None:
                # Need to look for a new segment end.
                if data[pointer:pointer+4] == b'@c2@' or data[pointer:pointer+4] == b'@c0@':
                    segmentEnd = pointer
                    pointer = pointer+4
                else:
                    pointer += 1
            else:
                # We have a start and end to the segment.
                segment = data[segmentStart:segmentEnd]
                segmentSize = len(segment)

                print(f'Processing segment ({segmentSize} bytes): {segment}')

                # Process the segment.
                processedSegment = bytearray("", 'utf-8')
                

                # Write the processed segment.
                processedSegment = segment[0:]
                final_data.extend(processedSegment)

                # Write the segment end marker
                final_data.extend(data[segmentEnd:segmentEnd+4])

                # Reset the segment start/end pointers.
                segmentStart = None
                segmentEnd = None

                # break

        out_file.write(final_data)

        assert(len(final_data) == size, f"ERROR: Final size ({len(final_data)}) does not match original size ({size})")

if __name__ == "__main__":
    main()
