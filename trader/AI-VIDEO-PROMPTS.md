# STRATA — AI image-to-video prompt pack

Goal: turn your **exact** PNGs into premium looping clips, then I drop the video into the app.
Upload these images (in `/trader`): `bull indicator.png`, `bear indicator.png`, and `/logo.png`.

## Which tool
- **Luma Dream Machine** — has a real **Loop** toggle. Best for seamless idle loops. Start here.
- **Kling** (1.6/2.0) — best subtle, realistic motion (breathing, steam). Use "image-to-video", high "relevance".
- **Runway Gen-3/4** — use the **Motion Brush** to paint motion only on the head/nostrils/mouth so the body stays locked.
- **Pika** — quick short loops; add `-camera static` and use region controls.
- (Sora if you have access — highest quality.)

## Universal settings (use on every clip)
- Duration **5s** (4s min), **static/locked camera**, motion **low–moderate**, 24–30 fps.
- Aspect: match the image (these are portrait). 
- **Background: solid pure black (#000000)** — say it in the prompt. (That lets me composite it onto the dark UI with no ugly box: black drops out via screen-blend, the glow/steam show through.)
- Ask for a **seamless loop that returns to the starting pose**.

## Negative / avoid (paste into the "negative" field, or append "Avoid:" to the prompt)
`camera movement, zoom, pan, parallax, warping or morphing the body, changing the silhouette, extra text or watermarks, color shifts, extra limbs, distortion`

---

## BULL  (`bull indicator.png`)
> Animate this bull as a premium financial mascot on a solid black background. Idle: slow, calm breathing — the chest and nostrils gently expand and contract — with a faint emerald rim-light that softly pulses. Every few seconds the bull lowers its head slightly and snorts: thick jets of steam blast outward from BOTH nostrils, the eyes briefly glow brighter emerald-green, and the rim-light flares — then it relaxes back into slow breathing. Camera locked and static, bull centered, silhouette unchanged; only the head, steam, eyes and glow move. Cinematic, high detail, dramatic emerald lighting, seamless loop.

## BEAR  (`bear indicator.png`)
> Animate this bear as a fierce financial mascot on a solid black background. Idle: slow, heavy breathing, red eyes faintly glowing, a few tiny embers drifting upward. Every few seconds it ROARS: the mouth opens wide, the eyes flare bright red, the head pushes forward toward the camera, and a red shockwave / heat-ripple radiates outward from it — then it settles back into slow breathing. Camera locked and static, bear centered, shape and fur consistent; only the head, mouth, eyes and embers animate. Cinematic, dramatic red rim light, high detail, seamless loop.

## LOGO  (`logo.png`)
> Animate this logo as a premium brand sting on a solid black background. An upward arrow of light sweeps up through the mark and a bright emerald pulse radiates outward; the mark breathes with a subtle scale; a faint emerald eye-glow flickers; light steam wisps vent from both sides; small emerald particles drift upward. Keep the logo perfectly centered, crisp, and identical in shape — only light, glow, steam and particles move. Clean, premium, dark, seamless 3–4 second loop.

---

## Getting a clean loop
- Prefer the tool's **Loop** feature (Luma). If none, generate 5s and pick the take whose end matches the start; I can also **ping-pong** it (play forward then reverse) in the app to hide the seam.
- Generate **3–5 takes** per asset and keep the best — first try is rarely the one.

## Sending them to me
Export **MP4** (or WebM). Drop the files in `trader/app/` named `bull.mp4`, `bear.mp4`, `logo.mp4` (or send them however). I'll:
- convert to a looping, black-keyed layer (screen-blend) so there's no box,
- wire them into the **boot splash, brand header, and landing/hero** of STRATA Live.

Note: the **per-candle chart markers stay PNG** (a video per signal isn't practical) — the clips are for the brand/intro/hero chrome, which is where they'll actually shine.
