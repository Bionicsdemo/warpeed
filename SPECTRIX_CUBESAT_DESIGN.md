# SPECTRIX CUBESAT - TECHNICAL DESIGN SPECIFICATION

**Mission:** Pluto & Oort Cloud Exploration via Laser Propulsion
**Version:** 1.0
**Date:** October 17, 2025

---

## CUBESAT CONFIGURATION

### Platform: 6U CubeSat

**Dimensions:**
- Stowed: 10 cm × 20 cm × 30 cm (6U form factor)
- Mass: 250 grams total
  - CubeSat bus: 150 grams
  - Lightsail (folded): 100 grams
  - Payload: Included in bus mass

**Power:**
- Solar panels: 4× deployable (2W each = 8W total)
- Battery: 20 Wh Li-ion
- Power budget: 5W average, 8W peak

---

## LIGHTSAIL SYSTEM

### Sail Specifications

**Deployed Configuration:**
- Shape: Square sail
- Area: 100 m² (10m × 10m)
- Areal Density: 1 g/m²
- Total Sail Mass: 100 grams
- Material: Multi-layer metamaterial
  - Layer 1: Al₂O₃ (50 nm) - protective layer
  - Layer 2: SiO₂ (100 nm) - dielectric reflector
  - Layer 3: TiO₂ (75 nm) - structural layer
  - Substrate: Ultra-thin Kapton (2 μm)
- Reflectivity: >99% @ 1064 nm
- Thickness: <1 μm total

**Deployment Mechanism:**

**Type:** Z-fold with deployable booms

**Components:**
1. **Storage Canister** (integrated in 6U body)
   - 4× compartments for sail quadrants
   - Pyrotechnic release mechanism
   - Hermetically sealed until deployment

2. **Deployable Booms** (4× carbon fiber)
   - Length: 5 meters each (deployed)
   - Diameter: 8 mm
   - Mass: 5 grams each (20 grams total)
   - Material: Ultra-thin carbon fiber composite
   - Deployment: Rolled storage → spring deployment

3. **Deployment Sequence:**
   - T+0s: Pyrotechnic release fires
   - T+2s: Booms begin deployment (spring-loaded)
   - T+10s: Booms fully extended (5m each)
   - T+12s: Sail unfolds (Z-fold pattern)
   - T+30s: Sail fully deployed (10m × 10m)
   - T+35s: Tension check & stabilization

---

## CUBESAT BUS DESIGN

### Physical Layout (6U Configuration)

```
┌─────────────────────────────────┐
│         TOP (Solar Panel)       │ ← Z+ face (nadir pointing)
├─────────────────────────────────┤
│                                 │
│  ┌───────────────────────────┐  │
│  │  SAIL STORAGE CANISTER    │  │ ← Units 1-4 (sail + booms)
│  │  (4 quadrants, Z-folded)  │  │
│  │                           │  │
│  │  ┌─────────────────────┐  │  │
│  │  │ Boom 1 (NW) Rolled  │  │  │
│  │  │ Boom 2 (NE) Rolled  │  │  │
│  │  │ Boom 3 (SE) Rolled  │  │  │
│  │  │ Boom 4 (SW) Rolled  │  │  │
│  │  └─────────────────────┘  │  │
│  └───────────────────────────┘  │
│                                 │
├─────────────────────────────────┤
│  ┌─────────────────────────┐   │
│  │  AVIONICS STACK (U5-U6) │   │ ← Units 5-6
│  │                         │   │
│  │  • Flight Computer      │   │
│  │  • Radio (S-band)       │   │
│  │  • Attitude Control     │   │
│  │  • Power Management     │   │
│  │  • GPS Receiver         │   │
│  │  • Battery              │   │
│  │  • Payload Instruments  │   │
│  └─────────────────────────┘   │
├─────────────────────────────────┤
│       BOTTOM (Solar Panel)      │ ← Z- face (zenith pointing)
└─────────────────────────────────┘

SIDE FACES:
X+/X- faces: Solar panels (deployable, 2 per side)
Y+/Y- faces: Radio antennas + sensors
```

---

## SUBSYSTEMS

### 1. Attitude Determination & Control System (ADCS)

**Components:**
- 3× Reaction wheels (micro-sized, 2g each)
- 3× Magnetorquers (1g each)
- Star tracker (miniature, 10g)
- Sun sensors (4×, 1g each)
- GPS receiver (5g)

**Performance:**
- Pointing accuracy: ±0.1° (required for laser tracking)
- Slew rate: 5°/second
- Stabilization time: <30 seconds after deployment

**Purpose:**
- Maintain sail orientation perpendicular to laser beam
- Precision pointing during acceleration phase
- Attitude control during coast phase

### 2. Communications System

**Radio:**
- S-band transceiver (2.2-2.3 GHz)
- Data rate: 1 Mbps downlink, 1 kbps uplink
- Antenna: Deployable patch antenna (gain: 6 dBi)
- Power: 2W transmit, 0.5W receive

**Ground Stations:**
- NASA Deep Space Network (DSN)
- ESA Estrack Network
- Backup: Amateur radio ground stations

### 3. Power System

**Solar Panels:**
- 4× deployable panels (10 cm × 20 cm each)
- Triple-junction GaAs cells (30% efficiency)
- Total area: 800 cm²
- Power generation: 8W @ 1 AU, 0.02W @ 30 AU (Pluto)

**Battery:**
- Li-ion (20 Wh capacity)
- Charge/discharge management
- Temperature control (10-30°C)

**Power Budget:**
- Cruise mode: 3W (radio beacon, housekeeping)
- Science mode: 8W (instruments active)
- Deployment: 5W (motors + pyrotechnics)

### 4. Scientific Payload

**Instruments:**

**A) Navigation Camera** (10g)
- Resolution: 1280×960 pixels
- FOV: 40°
- Purpose: Star tracking, navigation, mission documentation

**B) Miniature Spectrometer** (15g)
- Wavelength range: 200-1000 nm
- Resolution: 2 nm
- Purpose: Analyze interstellar medium, Oort Cloud composition

**C) Particle Detector** (20g)
- Detects: Cosmic rays, solar wind particles
- Purpose: Map particle density in outer solar system

**D) Magnetometer** (8g)
- Range: ±1000 nT
- Purpose: Measure magnetic fields in deep space

**Total Payload Mass:** 53 grams

---

## DEPLOYMENT SEQUENCE (DETAILED)

### Phase 1: Launch & Deployment from Rocket (T+0)
- Deployed from secondary payload adapter
- Altitude: 400-500 km LEO
- Initial orbit: Circular, equatorial

### Phase 2: System Checkout (T+0 to T+2 weeks)
- Deploy solar panels (T+10 min)
- Boot flight computer (T+15 min)
- Establish radio contact (T+30 min)
- Test all subsystems (2 weeks)
- Calibrate instruments
- Test ADCS (reaction wheels, magnetorquers)

### Phase 3: Sail Deployment (T+2 weeks)
**Pre-deployment:**
- Orient CubeSat (sail deployment axis toward open space)
- Spin stabilization (0.5 RPM)
- Final system check

**Deployment (30 seconds):**
- T+0s: Fire pyrotechnic release
- T+2s: Booms begin deployment (spring-loaded)
- T+5s: Boom 1 (NW) locked at 5m
- T+7s: Boom 2 (NE) locked at 5m
- T+9s: Boom 3 (SE) locked at 5m
- T+10s: Boom 4 (SW) locked at 5m
- T+12s: Sail unfolds (Z-fold pattern)
- T+20s: Sail 50% deployed
- T+30s: Sail 100% deployed (10m × 10m)

**Post-deployment:**
- Camera images to verify sail shape
- Tension monitoring (strain gauges on booms)
- Reflectivity test (measure solar radiation pressure)
- ADCS recalibration (new mass properties)

### Phase 4: Earth-Laser Alignment (T+3 weeks)
- Ground laser facility begins tracking
- CubeSat orients sail perpendicular to laser beam
- ADCS maintains ±0.1° pointing accuracy
- GPS provides real-time position updates

### Phase 5: Laser Acceleration (T+4 weeks, Duration: 15 minutes)
- 50 GW laser illuminates sail
- Acceleration: 1,332,000 m/s² (135,900 g)
- ΔV: 45,000 km/s (0.15c)
- Final velocity: 0.15c relative to Sun
- Trajectory: Hyperbolic escape, target Pluto → Oort Cloud

### Phase 6: Coast Phase (Years 1-30+)
- Power: Solar panels (until ~5 AU), then battery rationing
- Communications: Periodic beacons (daily → weekly → monthly)
- Science: Continuous data collection
- Navigation: Star tracker + doppler ranging

---

## MISSION PROFILE

### Key Milestones

| Event | Time | Distance | Velocity | Notes |
|-------|------|----------|----------|-------|
| **Launch** | T+0 | LEO (500 km) | 7.8 km/s (orbital) | Secondary payload on commercial launch |
| **Sail Deployment** | T+2 weeks | LEO | 7.8 km/s | 30-second deployment sequence |
| **Laser Ignition** | T+4 weeks | LEO | 7.8 km/s | Ground laser acquires target |
| **Laser Acceleration** | T+4 weeks | LEO → 6,700 km altitude | 7.8 → 45,000 km/s | 15 minutes, 0.15c final velocity |
| **Moon Flyby** | T+8 seconds | 384,400 km | 45,000 km/s | 8.5 sec after acceleration ends |
| **Earth Escape** | T+3 minutes | 1.5 million km | 45,000 km/s | Beyond Earth's gravitational influence |
| **Mars Orbit Cross** | T+1.7 hours | 228 million km | 45,000 km/s | No Mars encounter (wrong alignment) |
| **Jupiter Orbit Cross** | T+9.6 hours | 778 million km | 45,000 km/s | Possible magnetosphere data |
| **Saturn Orbit Cross** | T+17.5 hours | 1.4 billion km | 45,000 km/s | Possible ring system imaging |
| **Uranus Orbit Cross** | T+1.3 days | 2.9 billion km | 45,000 km/s | Outer solar system entry |
| **Neptune Orbit Cross** | T+1.85 days | 4.5 billion km | 45,000 km/s | Last gas giant |
| **Pluto Encounter** | T+36 hours | 5.9 billion km | 45,000 km/s | PRIMARY SCIENCE TARGET |
| **Kuiper Belt** | T+3-7 days | 30-50 AU | 45,000 km/s | Extended scattered disk |
| **Heliopause** | T+10 days | 120 AU | 45,000 km/s | Exit solar system |
| **Oort Cloud Inner Edge** | T+138 days | 2,000 AU | 45,000 km/s | SECONDARY SCIENCE TARGET |
| **Oort Cloud Outer Edge** | T+2.7 years | 100,000 AU | 45,000 km/s | Interstellar transition zone |
| **1 Light-Year** | T+7.3 years | 63,241 AU | 45,000 km/s | Deep interstellar space |

---

## VISUAL DESCRIPTION FOR IMAGE GENERATION

### Stowed Configuration (In Rocket)
- Compact 6U CubeSat (10×20×30 cm rectangular prism)
- Metallic silver body with black solar panels (folded)
- Small antennas visible on Y faces
- Warpeed logo on X+ face
- Clean, modern aerospace aesthetic
- Mounted in P-POD deployer (standard CubeSat launch canister)

### Deployment Sequence
1. **Solar Panel Deployment** (T+10 min after launch)
   - 4× panels unfold like wings (2 per side on X+/X-)
   - Blue solar cells visible
   - CubeSat in LEO with Earth in background

2. **Sail Deployment Begin** (T+2 weeks)
   - 4× carbon fiber booms extending from top (Z+) face
   - Booms are thin, black, extending radially
   - Sail beginning to unfold (still crumpled, silver/iridescent)
   - Earth in background, orbital sunrise lighting

3. **Sail Deployment Complete** (T+2 weeks + 30 sec)
   - Massive 10m × 10m square sail fully deployed
   - Sail is ultra-thin, mirror-like, iridescent (rainbow sheen)
   - Perfectly flat, tensioned by 4 booms at corners
   - Tiny 6U CubeSat in center for scale
   - Sun illuminating sail from behind (transmission glow at edges)

### Laser Acceleration Phase
- Ground-based view: 500-element phased array laser facility in desert
- Brilliant green/near-IR beam (1064 nm) shooting upward
- Beam converging on tiny point of light (CubeSat) in night sky
- Star trails in background (long exposure effect)

### Space View During Acceleration
- Close-up of sail being illuminated by laser
- Intense bright spot in center of sail (laser illumination)
- Sail glowing with transmitted/reflected 1064 nm light
- Slight curvature distortion from radiation pressure
- CubeSat bus silhouetted against bright sail
- Attitude thrusters firing to maintain orientation

### Post-Acceleration Coast
- CubeSat receding from Earth at 0.15c
- Sail edge-on view (appears as thin line due to extreme thinness)
- Earth shrinking rapidly in background
- Star field beginning to show relativistic aberration
- Doppler shift visualization (stars ahead blue-shifted, behind red-shifted)

### Pluto Flyby (T+36 hours)
- CubeSat approaching Pluto at 45,000 km/s
- Sail fully deployed, edge-on to flight direction (minimal drag)
- Pluto and Charon visible, sunlit (distant Sun as bright star)
- Camera capturing images during flyby (few seconds of encounter)
- Motion blur effect showing extreme speed

### Oort Cloud (T+138 days)
- Deep space scene, Sun is just a bright star
- Sail illuminated only by starlight (faint glow)
- Comet nuclei in background (primordial icy bodies)
- CubeSat's navigation lights/beacon visible
- Cosmic dust illuminated by sail's passing

---

## TECHNICAL CHALLENGES & SOLUTIONS

### Challenge 1: Extreme Acceleration (135,900 g)
**Solution:**
- No moving parts during acceleration
- All components epoxied/bolted in place
- Sail booms locked in rigid configuration
- Electronics potted in epoxy
- No deployables during acceleration phase

### Challenge 2: Sail Deployment Reliability
**Solution:**
- Redundant pyrotechnic release (2× charges)
- Spring-loaded booms (passive deployment, no motors)
- Z-fold pattern (proven on LightSail-2, IKAROS)
- Ground testing in thermal-vacuum chamber
- Vibration testing to 20g (launch loads)

### Challenge 3: Laser Pointing Accuracy
**Solution:**
- GPS real-time position (accuracy: ±1 meter)
- ADCS precision pointing (±0.1°)
- Retro-reflector on sail (laser ranging)
- Ground tracking radar (backup)
- Predictive trajectory modeling

### Challenge 4: Power @ Pluto & Beyond
**Solution:**
- Li-ion battery (20 Wh capacity)
- Ultra-low power instruments (<1W)
- Duty cycling (10% active, 90% sleep)
- Radioisotope heater units (RHUs) for warmth
- No solar power expected beyond 5 AU

### Challenge 5: Communication at 0.15c
**Solution:**
- Doppler compensation (frequency shift: +15%)
- High-gain antenna pointed at Earth
- S-band (robust, DSN compatible)
- Store-and-forward data (no real-time)
- Pre-programmed science sequences

---

## MASS BUDGET

| Subsystem | Mass (grams) | % of Total |
|-----------|--------------|------------|
| **Lightsail** | 100 | 40% |
| - Metamaterial film (100 m²) | 80 | 32% |
| - Carbon fiber booms (4×) | 20 | 8% |
| **CubeSat Structure** | 35 | 14% |
| **ADCS** | 20 | 8% |
| **Communications** | 15 | 6% |
| **Power (solar + battery)** | 18 | 7% |
| **Flight Computer** | 8 | 3% |
| **Scientific Payload** | 53 | 21% |
| **Harness + Misc** | 1 | 0.4% |
| **TOTAL** | **250** | **100%** |

---

## TECHNOLOGY READINESS

### Current Status (2025)
- **CubeSat bus:** TRL 9 (flight-proven, hundreds launched)
- **Deployable booms:** TRL 8 (LightSail-2, NEA Scout heritage)
- **Z-fold deployment:** TRL 8 (IKAROS, LightSail-2)
- **Metamaterial sail:** TRL 3 (quantum-optimized, not yet fabricated)
- **50 GW laser:** TRL 3 (scaled from 10 GW demo concept)
- **ADCS for lightsail:** TRL 7 (LightSail-2 demonstrated)

### Development Path to TRL 9
1. **2026-2027:** Fabricate 10cm samples of metamaterial (TRL 4)
2. **2027-2028:** 1m² prototype sail, ground testing (TRL 5)
3. **2028-2030:** 3U CubeSat demo with 1m² sail @ 10 GW (TRL 6)
4. **2035-2040:** Full-scale SPECTRIX mission (TRL 9)

---

## COMPARISON WITH HERITAGE MISSIONS

| Mission | Type | Sail Area | Mass | Propulsion | Max Velocity | Status |
|---------|------|-----------|------|------------|--------------|--------|
| **LightSail-2** | 3U CubeSat | 32 m² | 5 kg | Solar pressure | +Δorbit | SUCCESS (2019) |
| **IKAROS** | Smallsat | 200 m² | 310 kg | Solar pressure | +ΔV (small) | SUCCESS (2010) |
| **NEA Scout** | 6U CubeSat | 86 m² | 14 kg | Solar pressure | +ΔV (small) | FAILED (2022) |
| **New Horizons** | Flagship | N/A | 478 kg | Chemical+gravity assist | 16.26 km/s | SUCCESS (2006) |
| **Voyager 1** | Flagship | N/A | 825 kg | Chemical+gravity assist | 17.0 km/s | SUCCESS (1977) |
| **Starshot (concept)** | Wafersat | 16 m² | 1 gram | 100 GW laser | 0.20c | Concept |
| **SPECTRIX (proposed)** | 6U CubeSat | 100 m² | 250 g | 50 GW laser | 0.15c | THIS MISSION |

---

**Status:** Conceptual Design Complete
**Next Steps:** Metamaterial fabrication, laser facility construction, mission proposal to NASA/ESA
**Target Launch:** 2040+ (after technology validation)

**Document:** WRP-SPECTRIX-001
**Version:** 1.0
**Date:** October 17, 2025
