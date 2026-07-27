# Flashing

## Current state: PhoenixCard (Windows)

The official image `sun8iw7p1_android_h3_uart0.img` is an Allwinner LiveSuit-format image, not a raw disk image. It flashes to SD with PhoenixCard V310 (Windows only, archived from the FriendlyELEC Drive, see [SOURCES.md](SOURCES.md)), which formats the card and writes the Allwinner partition layout.

Alternative: LiveSuit (Linux, archived too) flashes over USB in FEL mode instead of writing an SD card.

## Open question: producing a dd-able image

Goal: distribute images flashable with dd / balenaEtcher / Raspberry Pi Imager like the SmartPi-armbian images, instead of requiring PhoenixCard on Windows.

Candidate approaches to investigate:

1. Flash a card with PhoenixCard once, then dump it (`dd if=/dev/sdX`) and truncate to the last used partition. Simple, but produces a card-size-dependent image and needs a Windows pass every release.
2. Unpack the LiveSuit image with `awimage` or `imgrepacker`, rebuild a raw SD layout manually: boot0 at 8 KB offset, u-boot at 16400 KB (sunxi conventions differ between boot0 era and mainline; the lichee pack scripts contain the exact offsets), then the Android partitions (nanda boot FAT with script.bin, system, data...) mapped from `sys_partition.fex`.
3. Study `lichee/tools/pack/` outputs: the pack step already produces all individual partition images before wrapping them in the LiveSuit container; a script assembling them into a raw image may be enough. This is the most promising path since it runs in CI with no Windows involved.
4. sunxi-tools ecosystem utilities for the legacy boot chain.

## dd (once a raw image exists)

```
# Identify the card first: lsblk (Linux) or diskutil list (macOS)
sudo dd if=smartpi-android.img of=/dev/sdX bs=4M status=progress conv=fsync
```
