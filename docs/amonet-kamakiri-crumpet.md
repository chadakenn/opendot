# Crumpet initial-access research: amonet, kamakiri, and amonet-koboreru

_2026-10-17. Documentation and source review only. **No exploit executed, no flash write, and no confirmation of exploit support on the user's Echo Dot.**_

## Summary

The Amazon Echo Dot 3rd Gen **C78MP8 / Crumpet** uses a **MediaTek MT8516** SoC (the supplied Amazon OS image also uses the `mt8167` software platform name). A newer public exploit project, [R0rt1z2/amonet-koboreru](https://github.com/R0rt1z2/amonet-koboreru), contains **explicit Crumpet configuration** under `devices/crumpet.c` and `include/devices/crumpet.h` using platform `mt8516`.

This is **better evidence of targeting this board family** than generic MT8163/kamakiri support, **but is not proof of successful exploitation on our retail board or currently installed preloader**. The project's README warns that Amazon patched the affected preloader issue around 2022 and that older vulnerable preloaders are needed. Its documented approach writes boot-critical images, potentially hard-bricking the target.

## Distinguish the projects

| Project | Technology and scope | Specific Crumpet support? |
|---|---|---|
| [R0rt1z2/amonet](https://github.com/R0rt1z2/amonet) | Older combined MediaTek boot ROM/preloader/LK research for selected Echo Show models | **Not listed** in its supported-device table |
| [bkerler/mtkclient](https://github.com/bkerler/mtkclient) / kamakiri | USB BootROM tooling, supports multiple chipset families and exploit variants | **Not demonstrated on our unit** |
| [R0rt1z2/amonet-koboreru](https://github.com/R0rt1z2/amonet-koboreru) | Preloader-stage vulnerability and device-specific runtime patches; persistent installation requires writing TEE-related partitions | **Yes, contains Crumpet-specific source code**, but version compatibility unknown |

The project's specific sources are [`devices/crumpet.c`](https://github.com/R0rt1z2/amonet-koboreru/blob/main/devices/crumpet.c) and [`include/devices/crumpet.h`](https://github.com/R0rt1z2/amonet-koboreru/blob/main/include/devices/crumpet.h). The embedded patch addresses and structures are **version-dependent**, so mixing firmware generations, flashing a Donut preloader, or relying on generic MT8163 instructions is unsafe.

## What older Crumpet research actually confirms

The [jvandewiel/no-alexa fastboot log](https://github.com/jvandewiel/no-alexa/blob/main/logicanalyzer/uart_logs/fastboot_stuff.txt) from the author's device reports:

- `product: CRUMPET`;
- `secure: yes`, `prod: 1`, `unlock_status: false`;
- preloader build descriptor `eb725ec-20210326_040236` (March 26, 2021);
- LK build descriptor `8f885ae-20210414_064357` (April 14, 2021);
- `version-preloader: 0.1.00`, anti-rollback PL level `0x0001`.

The author's [normal boot log](https://github.com/jvandewiel/no-alexa/blob/main/logicanalyzer/uart_logs/normal_boot.txt) also carries the 2021 preloader and LK descriptors.

**These are the other researcher's values, not readings from our Dot.** A 2021 *build date* predating a reported ~2022 patch is encouraging but not sufficient evidence of compatibility.

The [no-alexa repository](https://github.com/jvandewiel/no-alexa) contains `preloader_donut.bin`, which is **for Donut**, not an independently verified Crumpet preloader. Do not write it to Crumpet.

## What we need from our original device

The user has already opened their Dot and photographed a matching **`30-004397 REV 01`** logic board; UART pads `TM44` (TX) and `TM45` (RX) were identified via the [no-alexa interfacing wiki](https://github.com/jvandewiel/no-alexa/wiki/Interfacing).

**First, complete a safe, read-only UART capture** (verified common ground, voltage compatibility, and a USB serial RX input). Capture boot messages at **115200 baud** preloader and **921600 baud** later. Watch for these fields, which no-alexa shows in the output:

- `PL_VERSION` and `pl_build_desc` / `androidboot.pl_build_desc`;
- `lk_build_desc`;
- anti-rollback PL/TEE/LK versions;
- `androidboot.verifiedbootstate` / `androidboot.unlocked_kernel`;
- storage/NAND identity.

**Don't publish unredacted serials, challenge/unlock codes or tokens.**

The 2022 and 2023 OTA packages OpenDot compared **do not contain the installed preloader**. A dated firmware version in the Alexa app is not a reliable substitute for read-only device measurement. The Crumpet exploit's README mentions a specific preloader code signature as a compatibility clue, but an exact determination requires **the correct extracted preloader bytes**, not just a version label, and should avoid writing a blind downgrade.

## Safety / blockers

1. A custom preloader and LK path could still fail because of version-specific patch addresses, signature checks, anti-rollback and hardware differences.
2. The Crumpet-specific exploit uses a TEE-image modification; **a successful NAND write is not a confirmed unlock or boot**.
3. Never run exploit, flashing, downgrade, `Set Feature`, or erase commands just to identify version compatibility. The original device's bootability is more valuable than an unverified installation attempt.
4. The current project's objective remains **local Home Assistant Assist**. No Wi-Fi-only initial custom firmware method has been demonstrated by this research.
5. The next safe milestone is a **boot log from the actual board**. If it cannot be obtained, investigate another read-only diagnostic method instead of flashing anything.

## Research conclusion

**Promising first-install hardware lead, unverified on this unit.** The 2026 project explicitly targets Crumpet; the 2021 preloader reported by no-alexa is a *lead*, not proof. Capture the original Dot's bootloader version and compare it with the exact supported preloader before any further action.
