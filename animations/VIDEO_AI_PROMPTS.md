# VIDEO AI ANIMATION PROMPTS - SPECTRIX MISSION

**Date:** October 17, 2025
**Purpose:** Generate high-quality video animations for SPECTRIX lightsail mission using AI tools

---

## TABLE OF CONTENTS

1. [Runway ML Gen-3 Prompts](#runway-ml-gen-3)
2. [Pika Labs Prompts](#pika-labs)
3. [Luma AI Dream Machine](#luma-ai-dream-machine)
4. [Stable Diffusion Video](#stable-diffusion-video)
5. [Technical Settings Guide](#technical-settings)

---

## RUNWAY ML GEN-3

### Video 1: CubeSat Solar Panel Deployment

**Prompt:**
```
A 6U CubeSat satellite deploying its solar panels in low Earth orbit. Camera slowly orbits around the satellite. Four blue photovoltaic panels unfold symmetrically from the metallic silver body. Earth's curved blue atmosphere visible in background with orbital sunrise creating dramatic golden rim lighting. Panels deploy in 3 seconds with smooth mechanical precision. Ultra-realistic space photography, 8K quality, cinematic lighting. Camera movement: slow orbital dolly 360 degrees around subject.
```

**Settings:**
- Duration: 5 seconds
- Motion: Medium (orbital camera movement)
- Camera: Orbital dolly shot
- Style: Photorealistic
- Resolution: 1920x1080

---

### Video 2: Lightsail Deployment Sequence

**Prompt:**
```
Extreme close-up of a compact CubeSat in space as a massive 100 square meter lightsail rapidly unfolds in 30 seconds. Four carbon fiber booms extend from corners. Ultra-thin iridescent mirror sail catches sunlight creating rainbow shimmer effect. Camera pulls back to reveal full sail deployed - tiny CubeSat in center dwarfed by enormous square sail. Earth rotating slowly in background. Sail fabric has metallic sheen with subtle wave motion. Photorealistic space documentary style, NASA quality, dramatic lighting from Sun behind sail creating glow at edges.
```

**Settings:**
- Duration: 10 seconds
- Motion: High (sail deployment + camera pullback)
- Camera: Start extreme close-up, pull back to wide shot
- Style: Photorealistic documentary
- Resolution: 3840x2160 (4K)

---

### Video 3: Ground Laser Firing Sequence

**Prompt:**
```
Night shot in Atacama Desert. 500-element phased array laser facility arranged in hexagonal pattern on ground. Camera starts at ground level showing individual laser emitters. Brilliant green-yellow laser beams (1064nm near-infrared) fire upward converging into single powerful beam shooting straight up into starry night sky. Milky Way visible. Beam reaches tiny bright point of light (satellite) thousands of kilometers above. Long exposure star trails in background. Atmospheric distortion visible around beam. Cinematic sci-fi realism, Interstellar movie quality, dramatic nighttime photography.
```

**Settings:**
- Duration: 8 seconds
- Motion: Medium (camera crane up from ground to sky)
- Camera: Ground to sky crane shot
- Style: Cinematic sci-fi
- Resolution: 3840x2160 (4K)

---

### Video 4: Acceleration Phase Space View

**Prompt:**
```
Space view of lightsail being illuminated by powerful 50 GW laser from Earth. Intense bright green spot in center of 100m² sail where laser hits. Sail glowing brilliantly with transmitted light. Visible curvature from radiation pressure pushing sail. Tiny 6U CubeSat silhouette visible at center. Earth below with laser beam shooting upward. Sail begins accelerating away from Earth, motion blur on edges showing extreme speed. Stars beginning to show Doppler aberration. Ultra-realistic space photography, dramatic lighting, sense of incredible power and speed.
```

**Settings:**
- Duration: 10 seconds
- Motion: Very High (acceleration effect)
- Camera: Fixed space camera watching sail accelerate away
- Style: Photorealistic with motion blur
- Resolution: 3840x2160 (4K)

---

## PIKA LABS

### Video 5: Pluto Flyby

**Base Image:** cubestat.png (your existing image)

**Motion Prompt:**
```
Camera tracking shot following CubeSat with deployed lightsail as it approaches Pluto at 45,000 km/s. Pluto's heart-shaped Tombaugh Regio growing larger. Charon moon rising on horizon. Motion blur on edges indicating extreme speed. Sail edge-on to flight direction (minimal drag). Sun as bright star in background. 3 second flyby, dramatic space documentary style.
```

**Settings:**
- Seed Image: cubestat.png
- Motion Strength: 0.8
- Camera Movement: Tracking shot
- Duration: 3 seconds
- FPS: 24

---

### Video 6: Deep Space Journey

**Base Image:** cubestat2.png

**Motion Prompt:**
```
Slow rotation of CubeSat lightsail in deep space. Milky Way galaxy slowly rotating in background. Sail catching faint starlight with subtle iridescent shimmer. Gentle tumbling motion showing different angles of sail. Sense of vast distance and isolation. No planets visible - pure interstellar space. Contemplative mood, deep space documentary style.
```

**Settings:**
- Seed Image: cubestat2.png
- Motion Strength: 0.3 (slow gentle movement)
- Camera Movement: Slow orbit
- Duration: 5 seconds
- FPS: 24

---

## LUMA AI DREAM MACHINE

### Video 7: Oort Cloud Journey

**Text-to-Video Prompt:**
```
A lightsail spacecraft sailing through the Oort Cloud 2000 AU from Sun. Massive square sail illuminated only by faint starlight. Primordial icy comet nuclei floating in background - dark irregular shapes. Milky Way galaxy prominent across sky. Sun visible as just a bright star (no longer a disk). Cosmic dust particles illuminated by spacecraft's passing. Extreme deep space isolation. Sail has subtle rainbow iridescence. Ultra-realistic space photography, sense of vast distance, contemplative mood. Camera: slow dolly forward following spacecraft deeper into cloud.
```

**Settings:**
- Mode: Text-to-Video
- Duration: 5 seconds (extend to 10 seconds)
- Style: Photorealistic
- Motion: Slow forward dolly

**Enhancement Prompt (for extension):**
```
Continue motion. More comet nuclei appear. Spacecraft getting smaller as it moves deeper into Oort Cloud. Increasing sense of scale and distance.
```

---

### Video 8: Launch Sequence

**Text-to-Video Prompt:**
```
Rocket launch at night from Cape Canaveral. Camera at launchpad showing rocket on pad. T-10 countdown visible on screen. Engines ignite with brilliant orange flames. Rocket lifts off slowly, then accelerates upward trailing fire and smoke. Camera tilts up following rocket. Transitions to view of rocket from space as it deploys 6U CubeSat. Satellite tumbles gently in orbit with Earth rotating below. Orbital sunrise. Photorealistic launch footage, NASA documentary quality.
```

**Settings:**
- Mode: Text-to-Video
- Duration: 10 seconds
- Style: Documentary photorealism
- Motion: High (rocket launch)

---

## STABLE DIFFUSION VIDEO

### Video 9: Deployment Animation (Technical)

**Base Image Prompt (Generate First):**
```
Technical diagram of 6U CubeSat lightsail deployment sequence. White background. Clean engineering illustration showing 5 stages: 1) Stowed configuration 2) Solar panels deployed 3) Sail canister opening 4) Booms extending 5) Sail fully deployed. Blueprint style with measurements and labels. Top view and side view. Professional aerospace engineering diagram.
```

**Video Motion Prompt:**
```
Animate deployment sequence. Panels deploy first (0-2s). Booms extend next (2-5s). Sail unfolds last (5-8s). Smooth mechanical motion. Technical animation style.
```

**Settings:**
- Model: SVD (Stable Video Diffusion)
- Motion Bucket ID: 127 (medium motion)
- Frames: 120 (5 seconds at 24fps)
- Noise Aug: 0.02

---

### Video 10: Physics Simulation

**Base Image Prompt:**
```
Side view scientific visualization of lightsail being pushed by laser. Sail shown as thin reflective surface. Laser beam shown as ray diagram with photons bouncing off sail. Force vectors labeled. Equations visible: F=2P/c. Clean scientific diagram style, white background, educational physics visualization.
```

**Video Motion Prompt:**
```
Animate photons hitting sail and reflecting. Show force vectors pulsing. Sail slowly accelerating to right. Equations updating in real-time. Scientific animation style, educational physics video.
```

**Settings:**
- Model: SVD-XT (extended frames)
- Motion Bucket ID: 100 (controlled motion)
- Frames: 240 (10 seconds at 24fps)
- Cond Aug: 0.0 (preserve details)

---

## TECHNICAL SETTINGS GUIDE

### Optimal Settings by Tool

#### Runway ML Gen-3
```
Resolution: 1920x1080 or 3840x2160
Duration: 5-10 seconds
Motion Level:
  - Low (0-0.3): Subtle camera movement, gentle object motion
  - Medium (0.4-0.7): Active camera work, normal object motion
  - High (0.8-1.0): Fast action, rapid camera movement

Camera Movements:
  - Dolly: Moving toward/away from subject
  - Orbit: Circular movement around subject
  - Crane: Vertical movement
  - Tracking: Following moving subject
  - Static: Fixed camera position
```

#### Pika Labs
```
Resolution: 1920x1080 (upscale to 4K available)
Duration: 3 seconds (extendable to 9 seconds)
Motion Strength: 0.1-1.0
  - 0.1-0.3: Minimal motion (ambient, atmospheric)
  - 0.4-0.7: Moderate motion (standard camera movement)
  - 0.8-1.0: High motion (action sequences)

Best Practices:
  - Use seed images for consistency
  - Lower motion strength for complex scenes
  - Higher motion strength for simple scenes
```

#### Luma AI Dream Machine
```
Resolution: 1920x1080
Duration: 5 seconds (extendable to 10 seconds via extension)
Modes:
  - Text-to-Video: Best for scenes without existing images
  - Image-to-Video: Best for animating specific images
  - Video-to-Video: Best for style transfers

Tips:
  - Detailed prompts work better
  - Specify camera movement explicitly
  - Mention lighting conditions
```

#### Stable Diffusion Video (SVD)
```
Model Types:
  - SVD: 14 frames (stable, fast)
  - SVD-XT: 25 frames (extended, more motion)

Key Parameters:
  - motion_bucket_id: 1-255 (motion amount)
    - 1-50: Minimal motion
    - 50-127: Moderate motion
    - 128-255: High motion
  - fps: 6, 12, 24 (frame rate)
  - noise_aug_strength: 0.0-0.3 (variation)
```

---

## POST-PRODUCTION WORKFLOW

### Recommended Tools

1. **Upscaling:**
   - Topaz Video AI (for upscaling to 4K/8K)
   - Settings: Proteus model, High Quality, 4x upscale

2. **Stabilization:**
   - After Effects: Warp Stabilizer VFX
   - DaVinci Resolve: Stabilization

3. **Color Grading:**
   - DaVinci Resolve: Color page
   - Preset: Cinematic space (increase contrast, add blue/purple tint)

4. **Audio:**
   - Background: Deep space ambience
   - SFX: Mechanical deployment sounds, laser firing
   - Music: Sci-fi orchestral (for presentation videos)

---

## BATCH GENERATION STRATEGY

### Priority Order (Budget-Conscious)

1. **Essential Videos (Generate First):**
   - Video 2: Lightsail Deployment (flagship animation)
   - Video 4: Acceleration Phase (shows technology in action)
   - Video 5: Pluto Flyby (mission objective visualization)

2. **Supporting Videos:**
   - Video 1: Solar Panel Deployment
   - Video 6: Deep Space Journey
   - Video 7: Oort Cloud

3. **Optional/Advanced:**
   - Video 3: Ground Laser Facility
   - Video 8: Launch Sequence
   - Video 9-10: Technical diagrams

### Cost Estimates (2025 Pricing)

- Runway ML Gen-3: ~$0.05/second → $1-2 per video
- Pika Labs: ~$0.08/second → $0.25-0.75 per video
- Luma AI: Free tier available, Pro ~$30/month unlimited
- Stable Diffusion: Free (self-hosted) or $0.01/video (API)

**Total Budget for All 10 Videos:** ~$20-50

---

## INTEGRATION INTO WEBSITE

### Embedding Video

```html
<video autoplay loop muted playsinline style="width: 100%;">
    <source src="deployment_animation.mp4" type="video/mp4">
    Your browser does not support video.
</video>
```

### Background Video (Hero Section)

```html
<div class="hero" style="position: relative;">
    <video autoplay loop muted playsinline
           style="position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0.3;">
        <source src="deep_space_journey.mp4" type="video/mp4">
    </video>
    <div class="hero-content" style="position: relative; z-index: 2;">
        <!-- Your content here -->
    </div>
</div>
```

### Video Gallery

```html
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
    <div class="video-card">
        <video controls style="width: 100%; border-radius: 12px;">
            <source src="solar_deployment.mp4" type="video/mp4">
        </video>
        <p>Solar Panel Deployment (T+10 min)</p>
    </div>
    <!-- More videos -->
</div>
```

---

## OPTIMIZATION FOR WEB

### Video Compression Settings

```bash
# Using FFmpeg
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset slow -c:a aac -b:a 128k output.mp4

# For background videos (higher compression)
ffmpeg -i input.mp4 -c:v libx264 -crf 28 -preset slow -vf scale=1280:720 output.mp4
```

### Recommended Formats
- **Primary:** MP4 (H.264) - Best compatibility
- **Fallback:** WebM (VP9) - Better compression for modern browsers
- **Poster Frame:** JPG (for preview before video loads)

---

**Document Version:** 1.0
**Created:** October 17, 2025
**Usage:** Generate professional video animations for SPECTRIX mission website and presentations
