# Hardware notes

## SmartPi One = NanoPi M1 clone

The SmartPi One is a hardware clone of the FriendlyELEC NanoPi M1: Allwinner H3 (sun8iw7p1), quad Cortex-A7, 1 GB DDR3, Mali-400 MP2, HDMI 1.4, micro-USB OTG.

Critical constraint: the DDR3 chips used on SmartPi One require `dram_clk = 576` MHz. At 408 MHz the board crashes randomly (established on the Armbian side, where 576 is enforced in a custom u-boot).

Verified stroke of luck: the official NanoPi M1 FEX `sys_config_nanopi-m1.fex` already ships `dram_clk = 576` (`dram_zq = 0x3b3bfb`), and boot0 inside the official Android image is packed with these parameters. The official image should therefore boot on SmartPi One unmodified. This must still be confirmed on hardware (roadmap step: boot test).

## FEX, not device tree

The lichee 3.4 kernel predates device trees on sunxi: all hardware description lives in `sys_config.fex` (text), compiled to `script.bin` on the FAT boot partition ("nanda"). Adapting the board means editing:

```
lichee/tools/pack/chips/sun8iw7p1/configs/nanopi-h3/board/sys_config_nanopi-m1.fex
```

then repacking. FEX reference: linux-sunxi.org/Fex_Guide (fetch through web.archive.org, the site blocks direct requests).

## Displays and rotation

| Display | Behaviour wanted |
|---------|------------------|
| SmartPad panel (800x480 HDMI, USB touch) | Panel is mounted upside down: Android must rotate 180 degrees. Candidate: `ro.sf.hwrotation=180` in build.prop (Android 4.4 supports it; to verify on this BSP). Touch axes may need inverting too. |
| 1080p monitors | Default output |
| 4K TVs | Force 720p output (H3 HDMI tops out at 4K@30 and the UI is unusable there; same policy as SmartPi-armbian) |

## Reference data from the manufacturer image (dolphin-p1)

A previous project (`xtrack33/SMARTPI-Android`, local copy in `../SmartPi-android-legacy`) extracted the manufacturer Android 7.0 image `sun8iw7p1_android_dolphin-p1_uart0` and its FEX. Useful pinout extracted there:

| Parameter | Value |
|-----------|-------|
| UART debug | PA04/PA05 at 115200 baud |
| SD card | PF00-PF05 (4-bit) |
| LED power | PL10 |
| LED status | PA15 |

Note: that dolphin-p1 image used different DRAM parameters than the FriendlyELEC FEX; the FriendlyELEC ones (576 MHz) are the ones matching our constraint.

## Branding

`branding/` carries the Yumi assets shared with SmartPi-armbian (`logo_yumi.png`, `u-boot-logo.bmp`). To integrate: Allwinner bootlogo (`bootlogo.bmp` inside the pack config) and the Android bootanimation.
