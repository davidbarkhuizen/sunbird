# The sungate transmitter circuit

Reconstructed on 2026-11-17 from photographs of the breadboard as built in
2020, with the owner confirming the points the photos couldn't show. Items
not yet confirmed are marked **unconfirmed**.

## Schematic

```
 Nano 5V ──────────────── + rail
                            │
          ┌─────────┬───────┴─┬─────────┐
          │         │         │         │
         LED1      LED2      LED3      LED4      anode up (to + rail)
          │         │         │         │
         220Ω      220Ω      220Ω      220Ω
          │         │         │         │
          └─────────┴────┬────┴─────────┘
                         │  LED return rail
                         │
                         C
 Nano D3 ──── 220Ω ──── B    TIP122 (NPN Darlington)
                         E
                         │
 Nano GND ───────────────┘
```

When D3 is high the TIP122 conducts and pulls the LED return to ground, so
all four LEDs light together. The firmware switches D3 with the 38 kHz
carrier (timer 2's OC2B output, which is fixed to D3) during each pulse of
the IR command.

## Parts

part|value|notes
----|-----|-----
controller|Arduino Nano (ATmega328P clone)|same chip as the Uno; D3 is OC2B on both
transistor|TIP122|NPN Darlington, TO-220, 100 V, 5 A, gain >= 1000; legs B, C, E reading the printed face left to right
base resistor|220 Ω|owner's recollection: same value as the LED resistors (bands not readable in the photos)
LED resistors|4 x 220 Ω|red-red-brown, read from the photos
LEDs|4 x clear 5 mm|**unconfirmed:** part number; assumed 940 nm infrared
wiring|male-male jumpers on a split-rail breadboard|

## Connections

from|to|wire
----|---|----
Nano 5V|top + rail|orange
Nano GND|TIP122 emitter|black (one wire, confirmed)
Nano D3|base resistor|green
base resistor|TIP122 base|resistor lead, across the centre gap
top + rail|each LED's anode (long leg)|4 x red
each LED's cathode|its 220 Ω resistor|LED leg, across the centre gap
4 x LED resistor|bottom-left rail section (the LED return)|resistor leads
TIP122 collector|LED return rail|blue

The rails on this breadboard are split in the middle. The LED return is the
left section of the bottom rail, where the four LED resistors land. Nothing
else uses that section, so its printed + or − marking doesn't matter. The
blue wire's rail end was found loose on 2026-11-17; it must be in that
section or no LED lights.

## Layout

```
 top + rail     ═══ red x4 ══════ orange (5V) ═══════════════════════════════
 rows A-E       [red][red][red][red]                [E C B] TIP122   Nano top row
                 LED  LED  LED  LED                black blue          (VIN GND RST 5V ...)
 ── centre gap ── LED legs cross ──────────── base resistor crosses ── Nano ──
 rows F-J       220Ω x4 down to the rail       green from D3          Nano bottom row
 bottom rail    ═══ LED return (left section) ═══ | (split) | ════════ (D12 ... D3 D2 GND RST RX0 TX1)
```

LEDs at one end of the board, the TIP122 in the middle, the Nano at the
other end. The transistor's printed face points away from the centre gap.

## Numbers

These are estimates from typical datasheet values, not measurements.

- LED current, per LED while on: (5 V − LED drop ≈ 1.3 V − TIP122 drop
  ≈ 0.8 V) / 220 Ω ≈ 13 mA. All four: about 50 mA. The 38 kHz carrier has
  a 50% duty cycle, so the average during a pulse is half that.
- Base current while D3 is high: (5 V − TIP122 base-emitter drop ≈ 1.3 V)
  / 220 Ω ≈ 17 mA. That's within the ATmega328P's 20 mA recommended per
  pin (40 mA absolute maximum), but far more than needed: with a gain of
  at least 1000, 50 mA of LED current needs about 0.05 mA of base current.
  A 1 kΩ to 10 kΩ base resistor would also switch it fully and spare the
  pin; that's optional and not yet tried.
- The LED current is modest for IR LEDs, which typically take 20-100 mA
  continuous and more in short pulses. If range is short, lower the LED
  resistors after checking the LED's datasheet.

## Notes

- Nano clones often ship with the old bootloader. If an upload fails, pick
  "ATmega328P (Old Bootloader)" in the IDE, or with arduino-cli use
  `--fqbn arduino:avr:nano:cpu=atmega328old`.
- `reference/arduino-drive-external-voltage-circuit.png` is a generic
  MOSFET-and-lamp tutorial picture, not this circuit.
  `reference/ir protocol analysis - kerry d wong/ir_sensor_circuit.png` is
  Wong's photodiode receiver for capturing the remote's signal, not part of
  the transmitter.
