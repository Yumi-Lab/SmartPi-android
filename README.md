# SmartPi-android

Android 4.4.2 (KitKat) build pipeline for the Yumi Lab SmartPi One, based on the FriendlyELEC NanoPi M1 BSP (lichee kernel 3.4.39).

The SmartPi One is a hardware clone of the FriendlyELEC NanoPi M1, which makes the official NanoPi M1 Android BSP the most direct path to a bootable, reconstructible Android image.

## Hardware

| Component | Specification |
|-----------|---------------|
| SoC | Allwinner H3 (sun8iw7p1), quad Cortex-A7, 32-bit |
| RAM | 1 GB DDR3 - dram_clk must be 576 MHz (408 MHz causes random crashes) |
| GPU | Mali-400 MP2 |
| Video | HDMI 1.4 (max 4K at 30 Hz) |
| USB | micro-USB OTG + host ports |

The official NanoPi M1 FEX (`sys_config_nanopi-m1.fex`) already sets `dram_clk = 576`, matching the SmartPi One DRAM requirement. Direct boot of the official image on SmartPi One is therefore expected to work without modification. See [docs/HARDWARE.md](docs/HARDWARE.md).

Target displays: SmartPad (800x480 HDMI panel with USB touch, mounted upside down, needs 180 degree rotation), 1080p monitors, 4K TVs (720p output recommended).

## Approach

- BSP: FriendlyELEC `h3_lichee` (u-boot + linux 3.4.39 + Allwinner pack tools) plus `h3_android-4.4` (Android 4.4.2 tree). Kernel 3.4 uses FEX files compiled to `script.bin`, not device trees.
- Build environment: Docker image based on Debian wheezy (`debian/eol:wheezy` + `archive.debian.org`, the durable stand-in for the historically recommended Ubuntu 14.04, which Canonical purged from old-releases) with Oracle JDK 1.6.0_45. The Allwinner pack tools are 32-bit i386 binaries, so builds require an x86_64 Linux host. Apple Silicon Macs cannot build this, even through Rosetta (Rosetta does not translate i386).
- CI: GitHub Actions on the free runner first (public repo: 4 vCPU, 16 GB RAM, roughly 45-60 GB disk after cleanup, 6 h job limit). See [docs/BUILD.md](docs/BUILD.md).

## Repository layout

```
docker/            Build container (Ubuntu 14.04 + JDK6 + i386 libs)
scripts/           fetch-sources.sh (host side), build.sh (inside container)
.github/workflows/ build.yml (BSP build), mirror-sources.yml (source archival)
branding/          Yumi logo assets shared with SmartPi-armbian
docs/              SOURCES, BUILD, HARDWARE, FLASHING
```

## Build

Through CI: run the `Build` workflow and pick the target (`lichee` for u-boot + kernel only, fast; `android` for the full image).

Locally on an x86_64 Linux host:

```
./scripts/fetch-sources.sh
docker build --platform linux/amd64 -t smartpi-android-build docker/
docker run --rm --platform linux/amd64 -v "$PWD:/work" smartpi-android-build /work/scripts/build.sh android
```

Output: `sources/lichee/tools/pack/sun8iw7p1_android_nanopi-m1_uart0.img`

Resource needs for a full Android build: about 8 GB RAM, 40 GB disk, 2-4 h on 4 cores.

## Roadmap

- [x] Locate and verify all upstream sources (see [docs/SOURCES.md](docs/SOURCES.md))
- [ ] Archive sources and official image on Yumi infrastructure (`mirror-sources` workflow, upstream files can disappear)
- [ ] Boot test of the official `sun8iw7p1_android_h3_uart0.img` on SmartPi One hardware
- [ ] Reproducible Docker build, first green CI build
- [ ] SmartPi One customization: FEX, Yumi branding (bootlogo, bootanimation), SmartPad rotation
- [ ] Release with flashable image and procedure (PhoenixCard and/or dd)

Open questions are tracked in [docs/FLASHING.md](docs/FLASHING.md) (dd-able image production) and [docs/HARDWARE.md](docs/HARDWARE.md) (rotation).

## Related projects

- [SmartPi-armbian](https://github.com/Yumi-Lab/SmartPi-armbian): Linux images (Debian, Ubuntu, DietPi) for the same hardware. Branding assets are shared from there.
- A previous exploration (Android 10 / GloDroid, abandoned as not viable on 1 GB RAM) lives at `xtrack33/SMARTPI-Android`. Its extraction of the manufacturer dolphin-p1 image remains useful as hardware reference.
