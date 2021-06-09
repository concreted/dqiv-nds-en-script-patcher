# Dragon Quest IV English Script Fix for JP ROM

## Prerequisites

- From Nintendo DS US DQIV ROM: English `.mpt`. files located in `data\data\MESS\en` (153 files total)
- From Android DQIV OBB: English Party Chat `.mpt` files `b0500000.mpt` to `b0552000.mpt` (46 files total), located in `com.square_enix.android_googleplay.dq4\main.11100.com.square_enix.android_googleplay.dq4.obb\assets\msg\en`

## Guide

1. Copy NDS US ROM `.mpt` files to the `en` directory in this repo root
1. Copy Android OBB party chat `.mpt` files to the `en` directory
1. Run `python patch_en.py`
1. Find output files in `out` directory. Place those files into a JP ROM of Dragon Quest IV and repack. 

## Approach

- Seek until we find a `@a` start boundary. Write all bytes until the start boundary to the output file as-is.
- Next, seek until we find a `@b` nametag end boundary. Everything between `@a` and `@b` is the speaker name of the dialogue segment.
- Seek to `@c2@` end boundary. Determine length of segment.

- Remove each `%0` and add equal number of empty spaces at end of segment.
- Change each plural-variable block e.g. `%H***%Xyou%Yyouse%Z` to plural equivalent, padding end with spaces.
    - Always pick the latter of the two options
- Change each plural-variable block e.g. `%M***%Xthem%Yit%Z` to singular equivalent, padding end with spaces.
    - Always pick the latter of the two options
- Change each context-specific block e.g. `%O***%Xthe girls'%Yyour%Z` to the first option.
- Change each gender-variable block e.g. `%A***%Xsir%Z%B090%Xlady%Z` to gender-neutral equivalent, padding end with spaces. 
    - There are some `%A180%Xhim%Z%B180%Xher%Z%C180%Xit%Z` cases. 
    - If no matching rule is found or only one option, warn and default to first item.
    - Rules:
        - his/her/its to their
        - he/she/* to they
        - man/woman to person
        - him/her/it to them
        - feen/wan to person
        - laddie/lassie to child
        - gent/wench to one
        - himself/herself/itself to themself
        - son/girl to `young one`
        - *sir/*lady to friend
        - *boy/*lady to `young one`
        - *ero/*eroine to warrior
        - *guy/*girl to person
        - monsieur/mademoiselle to friend
- Fix grammar issues caused by replacements
    - Rules:
        - `they's` to `they are`
- Re-layout line by first converting all newlines into spaces. Then split segment into max-42 char lines on space boundaries, changing spaces to newlines.
- Write resulting segment to output file. 

Each resulting file should be same size as the original.

## Known issues

## Edge cases

%N:
```
en/b0801000.mpt:@c0@▒▒▒@a@b%0%a02010 mashes up the Yggdrasil leaf and administers it to %N180%X%A010%Xhimself%Z%B010%Xherself%Z%C010%Xitself%Z%Y%a02180%Z.
en/b0802000.mpt:@c0@@a@b%0%a02010 mashes up the Yggdrasil leaf and administers it to %N180%X%A010%Xhimself%Z%B010%Xherself%Z%C010%Xitself%Z%Y%a02180%Z.

```

Nested variable blocks:
```
%H860%X%0%a02010 bangs %A010%Xhis%Z%B010%Xher%Z%C010%Xits%Z head%YThe party bang their heads%Z
```


```
(x, (his, hers))

(his, hers)

(his, hers)
theirs
```
