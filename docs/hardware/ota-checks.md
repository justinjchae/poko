# OTA stage 10 checks: flash, bootloader, keys

**Written:** 2026-10-05. Checks 1, 2 and 4 of the OTA plan, the ones that touch the PCB. Checks 3 (BLE
transfer time) and 5 (power-pull drill) were then run on the XIAO the same day: see "3 and 5" below.
**How measured:** real sysbuild builds of the app (at `7574ee9`, firmware 0.1.0) with MCUboot and BLE updates (mcumgr)
turned on, on NCS v3.4.1 (Zephyr 4.4.2). Built only, nothing flashed. The configs are summarized at the bottom.

## Answers in short

| Question | Answer |
|---|---|
| App image size | **547 KiB signed** with BLE update support (534 KiB today without it) |
| Second slot inside the 1 MB? | **No.** Two internal slots get ≤ 472 KiB each, which is 75 KiB short today and gets worse as apps land |
| So the external chip holds | the second slot (**928 KiB**) + memos |
| External flash part | **16 MB stays right** (W25Q128JV). The slot costs ~2 of the ~35 memo-minutes |
| MCUboot size | 32 KiB plain; **58 KiB with USB recovery**, so give it a **64 KiB** partition |
| First image on a bare Raytac | **SWD only**, once, at assembly: a Tag-Connect TC2030 footprint (or 5 pads) |
| USB as the wired recovery path | **Yes.** MCUboot's own USB serial recovery, entered by holding select while pressing reset. No extra hardware |
| Measured on the XIAO | **≈ 34 s upload at 16.5 kB/s, 42 s swap, ~39 s boot; a battery pull mid-swap recovered (check 5 passed)** |
| RAM | ⚠ **85.6%** with BLE updates added (82.4% now). That's just over the 85% line, so it needs ~2–10 KB back (options below) |
| Signing | ECDSA P-256, private key kept offline (design below). No key in the repo |

## 1. Image size and where the second slot goes

| Build | Flash used | RAM |
|---|---|---|
| Today (UF2, no MCUboot) | 546,764 B (534 KiB) | 82.39% |
| + MCUboot + BLE update (mcumgr, NCS defaults) | 560,404 B; **560,555 B signed (547 KiB)** | **87.46%** |
| same, mcumgr buffers 4 → 2 | 560,404 B | **85.55%** |
| MCUboot alone, no USB recovery | 32,476 B | — |
| MCUboot with USB CDC serial recovery | **58,964 B** | — |

**Internal-only layout (doesn't fit):** 1024 − MCUboot (48) − settings (32) = 944 KiB, split in two = **472 KiB per slot.**
Even with MCUboot cut to 32 KiB and settings to 16 KiB, slots get 488 KiB. The image is 547 KiB now, so a
second internal slot is out, and the gap only grows (013, 011 and 006 are still to come).

**Proposed layout (built and linked):**

| Where | Partition | Size |
|---|---|---|
| internal 0x00000 | MCUboot (with USB recovery) | 64 KiB |
| internal 0x10000 | slot 0, the running app | 928 KiB (59% used today, ~380 KiB to grow) |
| internal 0xF8000 | settings (NVS, as today) | 32 KiB |
| external 0x000000 | slot 1, where a new image lands | 928 KiB |
| external 0x0E8000 | memos | the rest |

MCUboot runs in **swap-using-move** mode (NCS default): the new image is swapped in, and if it doesn't confirm itself,
the next boot swaps back. Downgrades are refused. The internal flash and the QSPI chip both have 4 KiB sectors,
which is what swap-move needs.

## 3. What size external flash

Memos are 16 kHz IMA ADPCM, 1024-byte blocks of 2041 samples, so **481,600 B per minute**.

| Chip | Memo minutes without the slot | **With a 928 KiB slot** |
|---|---|---|
| 8 MB (W25Q64JV) | 17.4 | **15.4** |
| **16 MB (W25Q128JV, current candidate)** | 34.8 | **32.9** |
| 32 MB (W25Q256JV) | 69.7 | 67.7 (needs 4-byte addressing; the nRF QSPI supports it, but not tested) |

(Raw minutes. The sector map and records take a little, which is where LOCK.md's "≈ 33" comes from; with the slot,
read it as **≈ 31**.) **Recommendation: keep the 16 MB part.** The slot is a ~6% cost. Pick 32 MB only if 008's
memo-minutes-per-day answer says 31 isn't enough. The slot can also shrink later (both slots must match), down to the
image size plus headroom, without a board change.

**Dev board caveat:** the XIAO's chip is a **2 MB** P25Q16H, not 16 MB. Today that's ~4.3 memo-minutes; with a 928 KiB
slot it drops to ~2.4. On the XIAO I'd use smaller slots (see "dev board" below).
**Firmware change this implies:** the memo store starts at offset 0 of the chip today. It must move to start after
slot 1, and memos already on a dev board must be migrated or cleared once.

## 2. MCUboot on a custom board with no UF2 bootloader

**First image load (hardware need):** a bare Raytac module ships with Raytac's test firmware and has no bootloader of
ours, so the first image (MCUboot + app, one merged hex) **must go in over SWD, once per board**. After that, everything
goes over BLE (phone) or USB (MCUboot recovery). SWD is also the only rescue if MCUboot itself is ever damaged. It's in a
protected region and never updated in the field, so that's unlikely.
- **Footprint:** a **Tag-Connect TC2030 (no-legs) footprint** with the Cortex pinout: 1 VCC, 2 SWDIO, 3 nRESET,
  4 SWCLK, 5 GND, 6 SWO (P1.00, matching `pins.md`). It's small, has no connector cost per board, and needs one
  cable for the bench. Fallback: 5 test pads (VCC, GND, SWDIO, SWCLK, nRESET) for a pogo jig. Either can sit inside
  the enclosure: SWD is for assembly and rescue. Only **reset** has to be reachable from outside (Justin's rule).
- **Probe:** something that can do an nRF52 "recover" (erase-all through the CTRL-AP), because newer nRF52840 silicon
  (build code F) can come up with debug access locked until it's erased. A J-Link or an nRF52/53 DK used as a programmer does this with
  `nrfutil device recover`. Which probe does Justin already own? I haven't priced one.
- Not checked: whether JLC can program modules at assembly. With 5–10 boards, hand-flashing is fine.

**USB as the wired recovery path: yes, on the Raytac as-is.** MCUboot's serial recovery runs over the nRF52840's own
USB (CDC ACM) and writes a signed image straight into slot 0. It works even when the app is broken, and it accepts only
images signed with our key. Measured: MCUboot grows from 32 to **58 KiB**, hence the 64 KiB partition. Ways in:
- **Hold select while pressing reset** (built and linked: select is `mcuboot-button0`). This is the user-facing
  recovery, and it needs the select button on a GPIO MCUboot can read at boot (it is: `pins.md`) plus reset reachable
  from outside (already required).
- **From the running app**, the way the `bootloader` link command works today: the app sets a retained boot-mode flag
  and reboots into recovery. The desk flow (`build.sh flash`) becomes: send `bootloader`, wait for the MCUboot USB port,
  upload with `mcumgr`/`smpmgr`. (Not built yet.)
- Rejected: entering recovery on every reset-pin press (`BOOT_SERIAL_PIN_RESET`). It was on in the measured 58 KiB
  build (it's small), but it makes reset ambiguous for users, so leave it off.
**No extra hardware** beyond what's decided: USB D+/D− and VBUS wired to the module, select on a GPIO, reset reachable,
SWD footprint.

**Dev board (XIAO), for check 2 as written:** the XIAO keeps its Adafruit UF2 bootloader, and MCUboot can
go in **as the UF2 "app" at 0x27000**, so no SWD is needed on the XIAO. Layout there: MCUboot 64 KiB at 0x27000, then
slot 0 of ~724 KiB up to the 32 KiB settings area, with slot 1 on the 2 MB chip. Smaller slots (e.g. 640 KiB) leave more
memo room. Double-tap reset still reaches UF2 as a last resort. The `bootloader` command would point to MCUboot recovery
instead. To be confirmed when stage 10 is built.

## 4. Signing key (design only)

- **Algorithm:** ECDSA P-256 (the NCS default; the nRF52840's CC310 verifies it in hardware). MCUboot holds only the
  **public** key, compiled in. The **private** key signs images on the Mac at build time.
- **Two keys, never mixed:** dev boards use MCUboot's public debug key (in NCS, so anyone can sign for it; fine for a
  bench). Production MCUboot has only the production public key, so a debug-signed image can't install on a shipped unit.
- **Where the private key lives:** generated once, offline (`imgtool keygen -t ecdsa-p256`), and kept **outside the
  repo**: a file under `~/.device-keys/` (mode 600) for builds, plus **two backups**, one in Justin's password manager
  and one on an encrypted USB stick stored away from the Mac. `build.sh` reads the path from an environment variable,
  and a release build refuses to run without it. Guards: `*.pem` in `.gitignore`, and a pre-commit check that rejects
  anything that looks like a private key.
- **If the key is lost:** shipped units can never take another update, over BLE or USB, because recovery checks the
  signature too. The only fix is reflashing MCUboot over SWD, which means opening the unit. That's why there are two
  backups.
- **If the key leaks:** someone could sign firmware our units would accept. Two mitigations:
  1. The BLE update service should require an **encrypted, bonded link** (`MCUMGR_TRANSPORT_BT_PERM_RW_ENCRYPT`). We
     already bond with the iPhone for AMS, so only the owner's phone can push an update. The NCS sample default is
     unencrypted.
  2. Key rotation would need an updatable MCUboot, which on the nRF52840 means adding Nordic's immutable first-stage
     bootloader (b0) and a second MCUboot slot: roughly 16 KiB + 64 KiB more internal flash. **Recommendation: skip it
     for 100 units** and accept that the key is fixed for this batch. Revisit before a larger run.
- **Physical access:** the key protects the wireless and USB paths only. Anyone with SWD can reflash anything unless
  debug access is locked (APPROTECT). Whether to lock shipped units (security) or leave them open (repair) is a separate
  decision for later. It doesn't change the board.

## 3 and 5. Measured on the XIAO (2026-10-05, Justin at the desk)

MCUboot was installed over USB through the XIAO's UF2 drive, with no probe (`./build.sh ec11 mcuboot flash`,
`firmware/app/mcuboot/`). Updates were sent from Justin's iPhone 16 with Nordic's **nRF Connect Device Manager** (the
same McuMgr library our app would use), with the Companion app connected at the same time. Test images 0.1.1-test and
0.1.2-test were signed with the dev key. A USB monitor timed each reboot.

| Step | Time |
|---|---|
| Upload over BLE, 561 KB | **≈ 34 s** (16.46 and 16.55 kB/s, the same as memo transfers) |
| MCUboot swap (screen dark, no USB) | **42.5 s** |
| App boot to the first link reply | **38.9 s** (the same as before MCUboot; see below) |
| Confirm (`os/ota.c`, on the phone's reconnect) | ~7 s after boot |
| **Total, upload start to running the new image** | **≈ 2 min** |

- **Check 5, power pull: passed.** With USB out, Justin uploaded 0.1.2-test, then pulled the battery a few seconds into
  the dark swap. On power-up MCUboot finished the swap and booted 0.1.2-test. All 105 memos and transcript CRCs were
  identical to the morning's baseline, and no crash was recorded.
- **"Sending the request timed out" on the phone, after every update.** Device Manager waits for the device to come
  back so it can send its own confirm, and gives up during the ~80 s of swap plus boot. Harmless here, because
  `os/ota.c` confirms on reconnect, but our own app needs a longer reconnect wait, or the boot and swap need to get
  faster.
- **The 40 s boot was already there before this work** (A/B: 7574ee9 without MCUboot took 40.8 s). It now accounts for
  half of every update. Not investigated yet; the first suspect is the boot-time scan of the memo chip.
- **The 42 s swap** is swap-using-move over 548 KB, erasing sector by sector on both the internal flash and the QSPI
  chip. A smaller image or a faster swap mode would shorten it. Not a blocker.
- iOS background limits: not measured. Both uploads ran with Device Manager in the foreground.
- Confirm: after the drill, Device Manager's image list showed slot 0 (0.1.2-test) **Active + Confirmed**. The
  confirm came from `os/ota.c` on the phone's reconnect, since the phone's own confirm timed out.
- **Board state at the end of the day:** the 0.1.0 MCUboot build (`./build.sh ec11 mcuboot flash`), flashed through
  the UF2 drive, with the 105 memos intact. A plain `./build.sh ec11 flash` still works, but it writes the app over
  MCUboot at 0x27000, so Bluetooth updates are gone until the next `mcuboot` flash. Which build is the default is open.

## RAM (heads-up)

Adding BLE updates costs ~13 KB of RAM at NCS defaults (87.5%), mostly mcumgr's receive buffers (4 × 2,475 B) and its
work-queue stack. With 2 buffers it's **85.6%**. To get back under 85% when stage 10 is built: shrink the mcumgr buffers
(smaller packets; check 3 measures what that does to transfer time), or take it from LVGL's 32 KB pool. That's a
firmware choice, not a hardware one.

## Experiment configs (for when stage 10 is built)

- Sysbuild: `SB_CONFIG_BOOTLOADER_MCUBOOT=y`, `SB_CONFIG_PARTITION_MANAGER=n` (Partition Manager is deprecated in
  NCS 3.4; the layout is in devicetree, as nrf_desktop's `memory_map_mcuboot_qspi.dtsi`).
- App: `CONFIG_NCS_SAMPLE_MCUMGR_BT_OTA_DFU=y`, `CONFIG_BUILD_OUTPUT_UF2=n`, `CONFIG_MCUMGR_TRANSPORT_NETBUF_COUNT=2`.
- MCUboot: `CONFIG_NORDIC_QSPI_NOR=y`, `CONFIG_NORDIC_QSPI_NOR_FLASH_LAYOUT_PAGE_SIZE=4096`, `CONFIG_LTO=y`,
  `CONFIG_SIZE_OPTIMIZATIONS=y`, logging off, plus `CONFIG_MCUBOOT_SERIAL=y`, `CONFIG_BOOT_SERIAL_CDC_ACM=y`,
  `CONFIG_BOOT_SERIAL_IMG_GRP_IMAGE_STATE=y`, `CONFIG_BOOT_ERASE_PROGRESSIVELY=y`, and a `mcuboot-button0` alias on select.
- Devicetree: the partition table above (`boot_partition`, `slot0_partition` also labeled `code_partition` for the
  XIAO's board files, `storage_partition`, and `slot1_partition` under the QSPI flash node).
