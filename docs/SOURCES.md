# Upstream sources

All locations verified on 2026-07-27. Upstream is unmaintained (last pushes 2018-2019), so everything must be archived: run the `mirror-sources` workflow, which stores the files on the `sources-archive` GitHub release of this repository.

## Git repositories

| What | Location | Notes |
|------|----------|-------|
| lichee SDK (u-boot + linux 3.4.39 + pack tools) | https://github.com/friendlyarm/h3_lichee | branch `master`, ~345 MB, last push 2019-05. Fork kept at `Yumi-Lab/h3_lichee`. Clone it as directory name `lichee`. |
| Android 4.4.2 tree | https://gitlab.com/friendlyelec/h3_android-4.4 | branch `master`, last activity 2018-11. Large. Clone as directory name `android`, sibling of `lichee`. Snapshot archived by `mirror-sources`. |

## Google Drive (FriendlyELEC official mirror)

`https://dl.friendlyelec.com/nanopim1` is only a redirect page pointing to Baidu and to the public Google Drive folder `H3-FriendlyElec`, id `1ZvaUcfgR_uFoupmtFFnTzBH4cQqweE-E`.

Warning: these Drive files intermittently return "quota exceeded" (too many downloads). Retry later or use gdown with retries; once mirrored, always prefer the `sources-archive` release.

File ids (fetch with `gdown <id>`):

| File | Drive id | Purpose |
|------|----------|---------|
| `sun8iw7p1_android_h3_uart0.img.zip` | `18_7bcI5-IhfDa1M1iVT3-KPa7w7X5Nug` | Official Android 4.4.2 SD image. Step one of the project: flash and boot-test on SmartPi One. In `01_Official images/01_SD card images`. |
| `sha256sum.txt` | `1eGKfQKYhI4fZaTdqShj4Ev9kCpvYrdqZ` | Checksums for the SD card images folder |
| `gcc-linaro-arm.tar.xz` | `1QdloBW9YaTyqRVAjbpoGCadAhDL_koVH` | Cross toolchain from `04_SDK and toolchain`. The lichee tree is expected to bundle its own toolchain (brandy); this one is archived in case it is needed. |
| `fa-toolchain.tgz` | `1Nzug_j2J1xT7O6Gt3ujSWzhJdGy0_ZVF` | From `04_SDK and toolchain/build-env-on-ubuntu` (with `install.sh` id `1MLuXFSKvm-ottnj3XhZ0BKfuqW2M5MPp`) |
| `PhoenixCard_V310.rar` | `18_LzRJoRRINBFTCYs48aBqbTqAIgXVog` | Windows SD flashing tool for Allwinner images |
| `LiveSuitV306_For_Linux64.zip` | `1wt88Qcp_Pv0JswFfQp8YP0TcPxJcgh8C` | Linux USB (FEL) flashing tool |

Drive folder ids for reference: `01_Official images` `1JHCClssLh54d0dtHU88mr4uN4gkmr0vO`, `01_SD card images` `1PV6NnJrgtbiNEX72R9hcKlulFshvwpNV`, `04_SDK and toolchain` `1aOvVXViuT4ajVP3OZT0c39k-yqtLllkk`, `05_Tools` `1XKd6_d4sUnKqBYyarWSPgGz58dydHvd6`, `07_Source codes` `1zJRx4MaSIg1JFhFVhvebkWVW0-nfo7G0`.

## Build environment

| What | Location | Notes |
|------|----------|-------|
| Oracle JDK 1.6.0_45 x64 | https://repo.huaweicloud.com/java/jdk/6u45-b06/jdk-6u45-linux-x64.bin | sha256 `6b493aeab16c940cae9e3d07ad2a5c5684fb49cf06c5d44c400c7993db0d12e8` (72087592 bytes, verified 2026-07-27). Pinned in the Dockerfile. |
| Debian wheezy apt archive | http://archive.debian.org/debian | Permanent. Used instead of Ubuntu 14.04: Canonical purged trusty from old-releases.ubuntu.com (verified 2026-07-27, only precise and older remain). |

## Reference documentation

- FEX format: linux-sunxi.org/Fex_Guide - the site blocks direct fetches, use web.archive.org
- Docker AOSP references: `tedwang/aosp-v4`, `Praqma/AndroidAospInDocker`
- Possible Android 7.0 phase 2: Orange Pi H3 Android 7 beta SDK (about 14 GB in 14 parts on the Orange Pi Google Drive, Orange Pi PC support page). Requires a DRAM repack (their parameters are not 576 MHz) and has no git history (DMCA takedown in 2015).
