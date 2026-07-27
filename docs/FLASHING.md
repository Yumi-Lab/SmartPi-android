# Flashing

Two formats are produced for every Android build.

| Format | File | Flash with | OS |
|--------|------|-----------|-----|
| Raw SD image | `smartpi-one-android-4.4-sd.img.gz` | dd, balenaEtcher, Raspberry Pi Imager | macOS, Linux, Windows |
| LiveSuit image | `sun8iw7p1_android_nanopi-m1_uart0.img` | PhoenixCard V310 | Windows only |

The raw image is the recommended one; the LiveSuit image is kept because it is the format upstream produces and the only one validated by FriendlyELEC.

## Raw image (macOS and Linux)

```
# macOS: find the card, unmount it but keep the device
diskutil list
diskutil unmountDisk /dev/disk4

# rdisk is the raw device and is much faster than disk
gunzip -c smartpi-one-android-4.4-sd.img.gz | sudo dd of=/dev/rdisk4 bs=4m
sync
```

On Linux use `/dev/sdX` and `bs=4M`. With balenaEtcher or Raspberry Pi Imager, select the `.gz` directly, no decompression needed.

The image is 2.36 GiB uncompressed, so the card must be at least 4 GB. The last partition (UDISK, Android internal storage) is declared with size 0, which means the BSP grows it to whatever is left on the card at runtime.

After writing, the card will look unreadable to macOS or Windows: it carries the Allwinner partition table, not a DOS one. That is expected.

## How the raw image is built

`scripts/make-sdimage.py` reproduces what PhoenixCard does. PhoenixCard is not magic: it writes a few blobs at fixed sector offsets, and those offsets are described by `cardscript.fex`, which ships inside the LiveSuit image itself:

| Sector | Offset | Content | Source |
|--------|--------|---------|--------|
| 16 | 8 KiB | boot0 (`eGON.BT0`), what the H3 boot ROM looks for | `[boot_0_0] start` |
| 38192 | 18.6 MiB | u-boot | `[boot_1_0] start` |
| 40960 | 20 MiB | sunxi MBR (`softw411`), 4 copies | `[card_boot] start` |
| 40960 + partition address | | each partition's payload | addresses read from the sunxi MBR |

The sunxi MBR is the authoritative partition table: 128-byte entries holding a start sector and a length, both relative to sector 40960. The script parses it rather than recomputing offsets from `sys_partition.fex`.

One trap worth knowing: `system.fex` is an **Android sparse image** (magic `0xed26ff3a`), not a raw filesystem. PhoenixCard expands it while flashing, so copying it verbatim would leave an unmountable partition. The script expands the sparse chunks itself (no `simg2img` dependency), producing the expected 768 MiB ext4.

The script also runs on a directory produced by [awutils](https://github.com/Ithamar/awutils)' `awimage`, so it can turn any existing Allwinner LiveSuit image into a raw one, including the official FriendlyELEC release:

```
awimage -u sun8iw7p1_android_h3_uart0.img          # creates <name>.img.dump/
python3 scripts/make-sdimage.py <name>.img.dump -o card.img
```

## Verifying an image without a board

Structure can be checked offline, which is how the builder was validated:

```
dd if=card.img bs=512 skip=16      count=1 | xxd | head -1   # eGON.BT0
dd if=card.img bs=512 skip=38192   count=1 | xxd | head -1   # uboot
dd if=card.img bs=512 skip=40960   count=1 | xxd | head -1   # softw411
dd if=card.img bs=512 skip=139264  count=1 | head -c 8       # ANDROID!
dd if=card.img bs=512 skip=172032  count=1 | xxd | head -1   # ext4 (0xEF53 at 0x438)
```

## PhoenixCard (reference method)

Per the FriendlyELEC wiki: low-level format the card with HDDLLF 4.40, format it FAT32, then write the LiveSuit image with PhoenixCard V310 as administrator. Both tools are archived on the `sources-archive` release.

## Status

The raw image is structurally verified but **has not been booted on hardware**. If it fails while the LiveSuit image works, the difference is in this layout and the first things to question are the u-boot sector and whether PhoenixCard writes anything else the card script does not mention.
