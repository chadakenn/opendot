# Roadmap

Current project stage: **offline research**. These are proposed milestones, not claims of functionality.

## Phase 0 — Archive and reproducibility (in progress)

- [x] Establish OpenDot project.
- [x] Record hardware identifier C78MP8 / Crumpet.
- [x] Hash and catalog two downloaded OTA packages.
- [x] Compare partition manifests and selected boot components.
- [ ] Reproduce the extracted-system component inventory with scripts.
- [ ] Confirm all reported architectural findings against source artifacts.

## Phase 1 — Identify stock hardware state

- [ ] Design an **internet-isolated** first-boot plan to avoid unplanned upgrades.
- [ ] Identify the currently installed firmware, rather than relying on the cached Alexa app record.
- [ ] Record read-only boot/diagnostic information, if the device exposes a supported interface.
- [ ] Document safe voltage levels and actual board revision before any physical connections.

## Phase 2 — Assess initial installation

- [ ] Determine whether stock firmware provides any authorized software-installation or diagnostic route.
- [ ] Distinguish *triggering a signed Amazon OTA* from *installing a custom OS*.
- [ ] If software installation is impossible, evaluate recoverable hardware-assisted research paths.
- [ ] Establish a tested backup and rescue plan **before writing to storage**.

## Phase 3 — Home Assistant satellite (not started)

- [ ] Establish a Linux boot path on Crumpet.
- [ ] Investigate compatibility of microphones, far-field audio DSP, speaker, buttons and LED ring.
- [ ] Implement or port wake-word/audio streaming and connect to Home Assistant Assist.
- [ ] Test reliable local playback, microphone capture and device-control latency.

## Phase 4 — Our own OTA channel (not started)

- [ ] Define an independently signed update format.
- [ ] Implement A/B or equivalent rollback-aware recovery.
- [ ] Add update controls and status visibility to the local interface.
- [ ] Test update/revert paths on a recoverable development device.

**Critical distinction:** future custom OTA updates are a *post-installation feature*. They do not solve the initial installation of unsigned firmware on a stock, verified device.
