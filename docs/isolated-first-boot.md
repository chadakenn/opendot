# Preserving the original C78MP8 firmware: first-boot plan

_2026-10-17 · Planning only. The physical Echo Dot remains unplugged._

## Goal

Establish the firmware *actually installed* on the retail Echo Dot C78MP8 and document its boot behavior without allowing a surprise Amazon OTA download, reset, or flash write.

## Current known state

- Model physically identified as **C78MP8**, Crumpet family.
- Alexa app showed software version **8624646532** after roughly three years unplugged; this could be cached.
- The former Wi-Fi SSID and password are unknown. A new isolated SSID **will not automatically be trusted or remembered** by the Dot.
- The public [Crumpet firmware catalog](https://ftvdb.com/echo/firmware/com.amazon.crumpet.android.os/) does not list `8624646532` in its current 13 captured records. The build is visible in the public [Biscuit firmware catalog](https://ftvdb.com/echo/firmware/com.amazon.biscuit.android.os/), which **does not** establish that the cached Dot version belongs to Biscuit, nor that Crumpet could not share the same numeric software code. The catalog may be incomplete.

## Recommended order

1. **Keep it unplugged** while preparing documentation and a safe observation method.
2. Preserve screenshots of the Alexa app version and the label identifying the model; avoid publicly sharing serial numbers.
3. Avoid factory reset or normal Internet-connected Alexa setup until firmware version/recovery options are understood.
4. For a *power-on-only* observation, ensure all possible remembered Wi-Fi paths lack Internet access first. The reliable method is to physically isolate the network uplink(s) during the observation, but this may disrupt other users. Merely adding a new isolated SSID does **not** prevent the Dot from joining another remembered network.
5. Record time, LED behavior, audible prompts, and whether the Dot advertises a setup network. A boot without WAN may reveal **no firmware build number at all**; do not reset simply to force provisioning.
6. The next useful technical milestone is **read-only UART boot logging**, but only *after* verifying board revision, actual test-point pinout, GND, UART voltage level, and availability of a correctly leveled serial adapter. Start with just GND and board TX → adapter RX, leaving adapter TX and VCC disconnected.
7. If the device does not expose the installed build on an authenticated supported interface, static firmware images from other builds alone cannot establish the device's version.

## Stop conditions

- Unexpected registration/update prompt, provisioning changes, or request to reset.
- Unsure whether any remembered access point still has Internet access.
- Unknown UART logic voltage, unidentified test points, or signs of short circuit.
- Any proposed operation that erases storage, writes partitions, changes boot flags, or requires a blind recovery step.

## Research milestones from the first safe physical session

- [ ] Capture board identification photos without disclosing its serial number.
- [ ] Document actual power-on/boot observations.
- [ ] Determine whether read-only diagnostic interface is safely accessible.
- [ ] Capture verified firmware / boot information if possible.
- [ ] Preserve the results in OpenDot without device identifiers.

**Reminder:** Neither checksum spoofing nor a copied Amazon OTA gives OpenDot an initial custom-firmware installer. A tested installation and recovery path is still missing.
