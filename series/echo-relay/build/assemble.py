"""Assemble ECHO RELAY EP01: zoompan on stills + captions + score -> ep01.mp4."""
import subprocess
import tempfile
from pathlib import Path

from imageio_ffmpeg import get_ffmpeg_exe

FF = get_ffmpeg_exe()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STILLS = ROOT / "stills"
OUT = ROOT / "ep01.mp4"
FPS = 30
SIZES = [1080, 1920]

DURS = [4.5, 4.5, 4.5, 5.0, 4.5, 5.0, 5.0, 5.0, 5.0, 5.0, 4.0]  # = 52.5 s
SCALES = [(120, 111), (0, 121), (140, 131), (0, 141), (120, 151), (0, 161),
          (140, 171), (0, 181), (120, 191), (0, 201), (100, 211)]

UP = 2160  # supersample width for smooth zoompan


def chop(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    f.write(text)
    f.close()
    return f.name


def clip(i, dur):
    src = STILLS / f"s{i:02d}.png"
    n = int(dur * FPS) + 1
    zmax = 1.10 if i % 2 else 1.09
    zoom = f"1+{zmax - 1:.2f}*on/{n}"
    fade = 0.5
    cap_file = chop(CAPS[i]) if i <= 10 else None
    vf = (
        f"scale={UP}:-2,"
        f"zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={n}:s={SIZES[0]}x{SIZES[1]}:fps={FPS},"
        f"format=yuv420p"
    )
    vf = vf.replace(",format=yuv420p", "")
    if cap_file:
        a = (
            f"if(lt(t,{fade}),t/{fade},"
            f"if(gt(t,{dur - fade}),({dur}-t)/{fade},1))"
        )
        vf += (
            f",drawtext=fontfile={FONT_BOLD}:textfile={cap_file}"
            f":fontsize=50:fontcolor=white:borderw=2:bordercolor=black@0.9"
            f":shadowx=3:shadowy=4:shadowcolor=black@0.5"
            f":line_spacing=16:x=(w-text_w)/2:y=h*0.855-text_h/2"
            f":alpha='{a}'"
        )
    vf += ",fade=t=in:st=0:d=0.5,fade=t=out:st=%.2f:d=0.5,format=yuv420p" % (dur - 0.5)
    dst = HERE / f"clip{i:02d}.mp4"
    cmd = [
        FF, "-y", "-i", str(src), "-vf", vf, "-frames:v", str(n),
        "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", str(dst),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return dst


from matplotlib import __file__ as _mpl
FONT_BOLD = str(Path(_mpl).parent / "mpl-data" / "fonts" / "ttf" / "DejaVuSans-Bold.ttf")

CAPS = {}


def load_caps():
    caps = {
        1: "THIS STATION RELAYS\nEVERY SIGNAL PAST SATURN",
        2: "ONE CREW.  HER.",
        3: "TONIGHT ONE SIGNAL STOPS",
        4: "A DISTRESS BEACON",
        5: "BUT IT KNOWS HER NAME",
        6: "LOGGED: FOURTEEN DAYS FROM NOW",
        7: "THE VOICE IS HERS",
        8: '"DO NOT OPEN THE AIRLOCK"',
        9: "SHE HAS A CHOICE",
        10: "THE COUNTDOWN IS ON",
    }
    caps.update({i: None for i in caps if not caps[i]})
    CAPS.update({k: v for k, v in caps.items() if v})


def main():
    load_caps()
    clips = []
    for i, dur in enumerate(DURS, start=1):
        clips.append(clip(i, dur))
        print(f"clip{i:02d} ok")

    lst = HERE / "concat.txt"
    with open(lst, "w") as f:
        for c in clips:
            f.write(f"file '{c}'\n")
    silent = HERE / "video.mp4"
    subprocess.run(
        [FF, "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)],
        check=True, capture_output=True,
    )

    score = ROOT / "ep01_score.wav"
    subprocess.run(
        [FF, "-y", "-i", str(silent), "-i", str(score),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(OUT)],
        check=True, capture_output=True,
    )
    print("wrote", OUT)


if __name__ == "__main__":
    main()
