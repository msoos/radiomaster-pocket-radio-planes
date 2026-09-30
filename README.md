# RadioMaster Pocket model backup

EdgeTX 2.12.2 backup of a RadioMaster Pocket with an internal ELRS (CRSF) module.
`backup/` is the unpacked `backup.etx`; edit the YAML there, then run
`./make_etx.sh` to rebuild the `.etx` for restoring on the radio.

## Common conventions

Unless a model is listed as an exception below:

| Switch | Function |
|---|---|
| SA | Arm (CH5, ELRS arming channel). Up = disarmed, down = armed; callouts `disarm` / `armed` |
| SB | Flaps / flight modes (up, 1, 2), callouts `flapup` / `flp1` / `flp2` |
| SC | Rates: up = high, mid = medium, down = low (`rathi` / `ratmed` / `ratlow`). Startup warning expects mid |
| SD | Vario: down = on (`vrion`), up = off (`vrioff`) |

- Low-battery warning: logical switch L1 fires when RxBt stays below the
  threshold while armed (SA down), and plays `lowbat` every 10 s.
- Names: inputs `Ail` `Ele` `Thr` `Rud` `Fla`; mix lines say what they add
  (`Ail`, `Flap`, `ThrCmp`, `FlpCmp`, ...); outputs name the servo (`AilL`/`AilR`,
  `ElvL`/`ElvR`, `AilLM`/`AilRM` (left/right middle), `FlapL`/`FlapR`, `Arm`, ...).
  On left/right channels the main mix line carries the side too (`AilL`, `AilRM`,
  `FlapR`, ...). Left/right is a guess where the model didn't say (Alula, Tanar, ASW28).
- L1 and the telemetry screen reference sensors by their index in the model's
  sensor list (`tele(N)`), which differs between models.
- Motor cut: throttle channel forced to −100 while SA is up.
- Timers: Timer 1 `thr` counts throttle-relative with minute beeps; Timer 2 `tot` runs while SA is down.
- Telemetry screen: `thr` timer | RxBt, `tot` timer | altitude, and link quality (RQly); items a model lacks are left blank.

## Overview

| # | Model | Type | Battery / low-bat | Motor cut | Vario (SD) | Flaps (SB) |
|---|---|---|---|---|---|---|
| 00 | Alula | Tailless DLG, no motor | 2S, < 7.2 V for 4 s | – | yes | – |
| 01 | air75 | Betaflight quad (**hands off**) | 1S, < 3.4 V for 2 s | via Betaflight | – | – |
| 02 | Phoenix16 | Motor glider | 3S, < 11.1 V for 0.8 s | CH3 | yes | – |
| 03 | Bixler | Plane with flight controller | – | CH3 | – | – |
| 04 | Tanar | Plane | 3S, < 11.1 V for 0.8 s | CH3 | – | – |
| 05 | Super Ray | Flying wing | 3S, < 11.1 V for 0.8 s | CH3 | – | – |
| 06 | ASW28 | Scale glider with motor, flaps | – | CH3 | yes | yes |
| 07 | F5J new | F5J glider, 6 wing servos | 3S, < 11.1 V for 0.8 s | CH10 | yes | yes |
| 08 | F5J old | F5J glider, flaps only (RES) | 3S, < 11.1 V for 0.8 s | CH10 | yes | yes |
| 09 | U-Glider | Motor glider, flaperons | 2S, < 7.2 V for 4 s | CH3 | yes | yes |

## Models

### Alula (model00)
Tailless DLG (discus launch glider) with elevons.
- CH1/CH2 are the elevons: CH3/CH4 (aileron with ±20 % differential) plus ±65 % elevator.
- No throttle, no motor cut. SA still sends the arm channel and plays the callouts.
- SE down is the launch (take-off) flight mode, with its own trims.
- Startup warning expects SD down (vario on).
- No active timers; the telemetry screen shows only RxBt, altitude and RQly.

### air75 (model01)
Betaflight whoop. Everything is done in the flight controller; do not edit.
- CH1–4 AETR, CH5 SA arm, CH6 SB mode, CH7 SE flip-over-after-crash, CH8 SD beeper.
- CH3 throttle is limited to 60 %.
- Low-battery warning like the others (L1, armed only), tuned for 1S.
- All switches must be up at startup.

### Phoenix16 (model02)
Motor glider, conventional tail.
- CH1 Ail, CH2 Ele, CH3 Motor, CH4 Rud.
- Flight modes 1 and 2 exist but have no switch.
- Startup warning expects SD down (vario on).

### Bixler (model03)
Cloned from Phoenix16; flies with a flight controller.
- CH1 Ail, CH2 Ele, CH3 Motor, CH4 Rud, CH5 flight-controller mode from SB, CH6 `Gain` (stabilization strength) from the S1 knob.
- **Arming is different:** ELRS switch arming on SA down, not a CH5 mix, because CH5 carries the mode.
- SB: up = manual (`manmod`, also forces CH6 to −100), mid = acro, down = stabilized (`stbmod`).
- CH5 has only two values on purpose: −100 on SB up and mid, +100 on SB down. Manual is acro with CH6 (gain) forced to −100.
- Startup warning expects SB down (stabilized) and S1 in the middle.

### Tanar (model04)
- **Different channel order:** CH1 Ele, CH2 Rud, CH3 Motor, CH4 and CH6 ailerons (±35 % differential).
- No altitude/vario sensor, so the altitude spot on the telemetry screen is blank. RxBt is sensor 0.

### Super Ray (model05)
Flying wing.
- CH1/CH2 elevons (50 % aileron + 50 % elevator), CH3 throttle. No rudder.
- Has Alt/VSpd sensors but no vario configured. RxBt is sensor 0.

### ASW28 (model06)
Scale glider with motor and flaps.
- CH1/CH7 ailerons (±40 % differential, camber from flaps via curve), CH2 Ele (with throttle and flap compensation), CH3 Thr, CH4 Rud (20 %), CH6 flaps (curve).
- Flight modes `flap1`/`flap2` on SB mid/down, each with its own elevator trim.

### F5J new (model07)
Six-servo F5J competition glider.
- CH1 Rud, CH2 Ele, CH3/CH4 ailerons, CH6/CH7 mid ailerons, CH8/CH9 flaps, **CH10 throttle**.
- Elevator gets throttle and flap compensation.
- Flight modes `flap1`/`flap2` on SB mid/down.

### F5J old (model08)
Earlier two-servo version of the F5J setup.
- Rudder-elevator-flaps, no ailerons: CH1 Rud, CH2 Ele, CH3/CH4 flaps, **CH10 throttle**.
- Same flight modes and callouts as F5J new.
- The flap input runs the other way (`SB w-50 off73`), so `FlpCmp` moves the elevator the opposite way from F5J new when the flaps go down. This is deliberate.

### U-Glider (model09)
Motor glider with flaperons.
- CH1/CH6 flaperons (aileron + 40 % flap), CH2 Ele (with throttle and flap compensation), CH3 Motor, CH4 Rud.
- Flaps on SB (up / mid / down) with callouts.
- Flight modes `flap1`/`flap2` on SB mid/down.
