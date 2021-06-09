# Dragon Quest IV English Script Fix for JP ROM

## Prerequisites

- From Nintendo DS US DQIV ROM: English `.mpt`. files located in `data\data\MESS\en`
- From Android DQIV OBB: English Party Chat `.mpt` files `b0500000.mpt` to `b0552000.mpt` (46 files in total), located in `com.square_enix.android_googleplay.dq4\main.11100.com.square_enix.android_googleplay.dq4.obb\assets\msg\en`

## Guide

1. Copy NDS US ROM `.mpt` files to the `en` directory in this repo root
1. Copy Android OBB party chat `.mpt` files to the `en` directory

## Approach

- Seek until we find a `@a@b` start boundary. Write all bytes until the start boundary to the output file as-is.
- Seek to `@c2@` end boundary. Determine length of segment.
- Remove each `%0` and add equal number of empty spaces at end of segment.
- Change each plural-variable block e.g. `%H***%Xyou%Yyouse%Z` to plural equivalent, padding end with spaces.
    - Always pick the latter of the two options
- Change each plural-variable block e.g. `%M***%Xthem%Yit%Z` to singular equivalent, padding end with spaces.
    - Always pick the latter of the two options
- Change each gender-variable block e.g. `%A090%Xsir%Z%B090%Xlady%Z` to gender-neutral equivalent, padding end with spaces.
    - *ero/*eroine to warrior
    - *boy/*lady to you
    - *guy/*girl to person
    - he/she to they
    - man/woman to person
    - his/her to their
    - him/her to their
    - son/girl to child
    - boy/girl to child
    - sir/lady to one
    - laddie/lassie to child
- Re-layout line by first converting all newlines into spaces. Then split segment into max-42 char lines on space boundaries, changing spaces to newlines.
- Write resulting segment to output file. 

Each resulting file should be same size as the original.
