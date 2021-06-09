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
                    # print(str(data[pointer:pointer+4])
                    
                    # Write the segment start marker
                    final_data.extend(b'@a@b')

                    segmentStart = pointer+4
                else:
                    # Write any bytes encountered between segments to the output buffer
                    final_data.append(data[pointer])

                    pointer += 1
            elif segmentEnd == None:
                # Need to look for a new segment end.
                if data[pointer:pointer+4] == b'@c2@':
                    segmentEnd = pointer
                    pointer = pointer+4
                else:
                    pointer += 1
            else:
                # We have a start and end to the segment.
                # Process the segment.
                segment = data[segmentStart:segmentEnd]
                segmentSize = len(segment)
                print(f'Processing segment ({segmentSize}): {segment}')

                # Write the segment end marker
                final_data.extend(b'@c2@')

                # Reset the segment start/end pointers.
                segmentStart = None
                segmentEnd = None

                break

        out_file.write(final_data)

if __name__ == "__main__":
    main()
