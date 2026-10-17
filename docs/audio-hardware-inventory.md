# Crumpet audio hardware: firmware inventory

_2026-10-17 · Read-only examination of selected vendor audio configuration and libraries extracted from the 2022 and 2023 Crumpet system images._

## Why this matters

The OpenDot goal is **Home Assistant Assist on the original Echo Dot C78MP8 hardware**. Even with a custom boot path, the firmware must support microphone capture, speaker output, gain/mixer controls, audio preprocessing and possibly LED/button interfaces. None of these functions has been tested on the physical unit.

## Physical hardware references (no-alexa research)

The [no-alexa Hardware wiki](https://github.com/jvandewiel/no-alexa/wiki/Hardware) identifies four MEMS microphones (MK1–MK4), **two TLV320ADC3101** stereo ADC devices, **IS31FL3236** LED controller, **12 RGB LEDs**, and a **TI TAS2770** amplifier on the author's tested 3rd-gen boards. These are hardware-research observations, **not** direct inspection of our device. See [no-alexa reference notes](no-alexa-hardware-reference.md).

## Verified cross-release comparisons

The following extracted file SHA-256 hashes were independently matched against both full system inventories before comparing their bytes.

| File under `/system/vendor/` | 2022 → 2023 |
|---|---|
| `etc/audio_policy.conf` | Identical |
| `etc/audio_device.xml` | Identical |
| `etc/mixer_paths.xml` | Identical |
| `etc/audio-algorithms/AFE.cfg` | Changed |
| `lib/libalexaaudiocomponent.so` | Changed |
| `lib/libalexaaudiohal.so` | Changed |
| `lib/libspeech_enh_lib.so` | Identical |

The **audio policy** advertises these profile options for the primary module:

- Output sampling rates: **8,000 / 16,000 / 44,100 Hz**, mono or stereo, PCM 16-bit or 32-bit.
- Input sampling rates: **8,000 / 16,000 / 32,000 / 44,100 / 48,000 Hz**, mono or stereo (plus voice-call masks), PCM 16-bit.
- An attached speaker and built-in mic are listed.
- Mixer settings reference speaker amplification, mic ADC switches, gain settings and capture/playback routes.

**Caution:** The policy file begins with a *generic device/emulator* comment and contains numerous broadly supported device types. Those advertised profiles are configuration data, **not verified microphone-array specifications** or proof that all routes are usable on the Echo. The Android audio HAL and kernel drivers still need live testing.

The vendor directory also contains audio-front-end configurations and beamforming-related coefficient tables. Their presence supports continued investigation of far-field audio processing but does not prove which portions could be reused under custom Linux.

## What remains unknown

1. Number and wiring of physically available microphone channels on C78MP8.
2. Whether the microphones and amplifier work via standard ALSA under an independently booted Linux kernel.
3. Whether Alexa audio DSP/beamforming is implemented entirely in reusable userspace libraries or depends on unavailable proprietary runtime services and firmware.
4. Whether 16 kHz mono PCM can be captured with acceptable latency while playing a response.
5. Wake-word processing CPU budget and audio echo cancellation.
6. Buttons, mute behavior, ring LED interfaces and safe recovery/power-off behavior.

## Proposed non-destructive tests after authorized code execution exists

- Enumerate sound cards and ALSA controls.
- Record a short local audio sample without uploading any recordings.
- Play an audio test signal at conservative volume.
- Verify hardware mute switch behavior.
- Check capture/response latency for a Home Assistant Assist pipeline.
- Preserve required proprietary licenses and avoid committing Amazon libraries or coefficient files to this public repository.

**Status:** a firmware audio inventory, **not** a working Home Assistant satellite or demonstration of a custom firmware installer.
