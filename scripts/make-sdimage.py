#!/usr/bin/env python3
"""Build a raw, dd-able SD image from the Allwinner pack output.

The BSP only produces a LiveSuit image (IMAGEWTY), which needs PhoenixCard on
Windows. PhoenixCard itself just writes a handful of blobs at fixed sector
offsets, and those offsets are described by cardscript.fex inside the image.
This reassembles the same card as a plain file, so it can be written with dd,
balenaEtcher or Raspberry Pi Imager from any OS.

Layout (from cardscript.fex, sector = 512 bytes):

    sector    16   boot0        [boot_0_0] start
    sector 38192   u-boot       [boot_1_0] start
    sector 40960   sunxi MBR    [card_boot] start, also the origin the
                                partition addresses in the MBR are relative to

Input is either the pack output directory (lichee/tools/pack/out) or a
directory produced by awutils' awimage; file names are resolved for both.
"""

import argparse
import os
import re
import struct
import sys

SECTOR = 512

# Fallbacks used only when cardscript.fex is missing; the values are the ones
# every sun8iw7p1 (H3) card script ships with.
DEFAULT_BOOT0_SECTOR = 16
DEFAULT_UBOOT_SECTOR = 38192
DEFAULT_CARD_SECTOR = 40960

# Candidate file names: pack out/ layout first, then awimage dump layout.
CANDIDATES = {
    "boot0": ["boot0_sdcard.fex", "12345678_1234567890BOOT_0"],
    "uboot": ["u-boot.fex", "12345678_UBOOT_0000000000"],
    "mbr": ["sunxi_mbr.fex", "12345678_1234567890___MBR"],
    "cardscript": ["cardscript.fex", "12345678_1234567890SCRIPT"],
    "sys_partition": ["sys_partition.fex"],
}


def resolve(directory, key, required=True):
    for name in CANDIDATES[key]:
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            return path
    if required:
        sys.exit(f"error: none of {CANDIDATES[key]} found in {directory}")
    return None


def partition_payload(directory, name):
    """Locate the .fex holding a partition's content, if it has one."""
    for candidate in (f"{name}.fex", f"RFSFAT16_{name.upper()}_FEX00000000"):
        path = os.path.join(directory, candidate)
        if os.path.isfile(path):
            return path
    # awimage pads the subtype to 16 chars, so the suffix length varies
    prefix = f"RFSFAT16_{name.upper()}_FEX"
    for entry in sorted(os.listdir(directory)):
        if entry.startswith(prefix) and not entry.endswith(".hdr"):
            return os.path.join(directory, entry)
    return None


def parse_cardscript(path):
    """Read the three start sectors PhoenixCard uses."""
    starts = {}
    section = None
    # the file is GBK-commented and CRLF terminated
    with open(path, "r", encoding="latin-1") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("["):
                section = line.strip("[]")
            elif "=" in line and section:
                key, _, value = line.partition("=")
                if key.strip() == "start":
                    try:
                        starts[section] = int(value.strip())
                    except ValueError:
                        pass
    return (
        starts.get("boot_0_0", DEFAULT_BOOT0_SECTOR),
        starts.get("boot_1_0", DEFAULT_UBOOT_SECTOR),
        starts.get("card_boot", DEFAULT_CARD_SECTOR),
    )


def parse_mbr(path):
    """Extract the partition table from sunxi_mbr.fex.

    struct: crc32, version, "softw411", copies, ..., count at 0x18, then
    128-byte entries of {addrhi, addrlo, lenhi, lenlo, class[16], name[16],
    user_type, ...} with addresses relative to the card_boot sector.
    """
    with open(path, "rb") as handle:
        data = handle.read()
    if data[8:16] != b"softw411":
        sys.exit(f"error: {path} is not a sunxi MBR (bad magic)")
    count = struct.unpack_from("<I", data, 0x18)[0]
    partitions = []
    offset = 0x20
    for _ in range(count):
        addr, length = struct.unpack_from("<I", data, offset + 4)[0], struct.unpack_from("<I", data, offset + 12)[0]
        name = data[offset + 0x20 : offset + 0x30].split(b"\x00")[0].decode("ascii", "replace")
        partitions.append((name, addr, length))
        offset += 0x80
    return partitions


SPARSE_MAGIC = 0xED26FF3A
CHUNK_RAW, CHUNK_FILL, CHUNK_DONT_CARE, CHUNK_CRC32 = 0xCAC1, 0xCAC2, 0xCAC3, 0xCAC4


def expand_sparse(image, sector, handle):
    """Expand an Android sparse image in place.

    system.fex is a sparse image, not a raw filesystem. PhoenixCard expands it
    while flashing, so a plain copy would leave an unmountable partition.
    """
    (_magic, _major, _minor, file_hdr_sz, chunk_hdr_sz,
     blk_sz, _total_blks, total_chunks, _checksum) = struct.unpack("<IHHHHIIII", handle.read(28))
    if file_hdr_sz > 28:
        handle.seek(file_hdr_sz - 28, os.SEEK_CUR)

    base = sector * SECTOR
    written = 0
    for _ in range(total_chunks):
        chunk_type, _reserved, chunk_blocks, chunk_total = struct.unpack("<HHII", handle.read(12))
        if chunk_hdr_sz > 12:
            handle.seek(chunk_hdr_sz - 12, os.SEEK_CUR)
        payload = chunk_total - chunk_hdr_sz
        span = chunk_blocks * blk_sz

        if chunk_type == CHUNK_RAW:
            image.seek(base + written)
            remaining = payload
            while remaining:
                data = handle.read(min(4 << 20, remaining))
                if not data:
                    sys.exit("error: truncated sparse image")
                image.write(data)
                remaining -= len(data)
        elif chunk_type == CHUNK_FILL:
            fill = handle.read(payload)[:4]
            if fill and fill != b"\x00\x00\x00\x00":
                image.seek(base + written)
                image.write(fill * (span // 4))
        elif chunk_type == CHUNK_DONT_CARE:
            handle.seek(payload, os.SEEK_CUR)
        elif chunk_type == CHUNK_CRC32:
            handle.seek(payload, os.SEEK_CUR)
            span = 0
        else:
            sys.exit(f"error: unknown sparse chunk type 0x{chunk_type:04x}")
        written += span
    return written


def write_at(image, sector, path, label):
    with open(path, "rb") as handle:
        head = handle.read(4)
        handle.seek(0)
        if len(head) == 4 and struct.unpack("<I", head)[0] == SPARSE_MAGIC:
            size = expand_sparse(image, sector, handle)
            note = f"{os.path.basename(path)} (sparse, expanded)"
        else:
            size = os.path.getsize(path)
            image.seek(sector * SECTOR)
            while True:
                chunk = handle.read(4 << 20)
                if not chunk:
                    break
                image.write(chunk)
            note = os.path.basename(path)
    print(f"  {label:<14} sector {sector:>9}  {size / (1 << 20):>8.1f} MiB  {note}")
    return size


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pack_dir", help="pack output dir (lichee/tools/pack/out) or an awimage dump dir")
    parser.add_argument("-o", "--output", required=True, help="raw image to create")
    parser.add_argument("--slack-mib", type=int, default=16,
                        help="space kept past the last written partition (default 16)")
    args = parser.parse_args()

    boot0 = resolve(args.pack_dir, "boot0")
    uboot = resolve(args.pack_dir, "uboot")
    mbr = resolve(args.pack_dir, "mbr")
    cardscript = resolve(args.pack_dir, "cardscript", required=False)

    if cardscript:
        boot0_sector, uboot_sector, card_sector = parse_cardscript(cardscript)
        print(f"layout from {os.path.basename(cardscript)}")
    else:
        boot0_sector, uboot_sector, card_sector = (
            DEFAULT_BOOT0_SECTOR, DEFAULT_UBOOT_SECTOR, DEFAULT_CARD_SECTOR)
        print("layout from built-in defaults (no cardscript found)")

    partitions = parse_mbr(mbr)
    print(f"{len(partitions)} partitions in the sunxi MBR\n")

    with open(args.output, "wb") as image:
        write_at(image, boot0_sector, boot0, "boot0")
        write_at(image, uboot_sector, uboot, "u-boot")
        write_at(image, card_sector, mbr, "sunxi MBR")

        end_sector = card_sector + 0
        for name, addr, length in partitions:
            payload = partition_payload(args.pack_dir, name)
            absolute = card_sector + addr
            if payload:
                written = write_at(image, absolute, payload, name)
                if length and written > length * SECTOR:
                    sys.exit(f"error: {name} payload ({written} B) exceeds its "
                             f"partition ({length * SECTOR} B)")
            else:
                print(f"  {name:<14} sector {absolute:>9}  {'':>8}      (empty)")
            # a zero length means "use whatever is left on the card"
            end_sector = max(end_sector, absolute + (length or 0))

        total = (end_sector + args.slack_mib * (1 << 20) // SECTOR) * SECTOR
        image.truncate(total)

    print(f"\nwrote {args.output}: {total / (1 << 30):.2f} GiB "
          f"(sparse, mostly zeros - compresses well)")


if __name__ == "__main__":
    main()
