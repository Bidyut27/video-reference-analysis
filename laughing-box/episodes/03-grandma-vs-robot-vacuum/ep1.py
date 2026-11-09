"""Load earlier episodes' modules (characters, sets, props, voice, SFX) by file path.

The episodes' scripts share names, so earlier ones are loaded under aliases.
Their `from timeline import ...` resolves to this folder's timeline.py, because
this folder is first on sys.path.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EP1 = os.path.join(HERE, "..", "01-grandpa-vs-self-checkout")
EP2 = os.path.join(HERE, "..", "02-grandpa-vs-video-call")
BRANDING = os.path.join(HERE, "..", "..", "brand-kit")
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def load(path, alias):
    if alias in sys.modules:
        return sys.modules[alias]
    spec = importlib.util.spec_from_file_location(alias, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


def video():
    mod = load(os.path.join(EP1, "make_video.py"), "ep1_video")
    sys.modules.setdefault("make_video", mod)
    return mod


def ep2_video():
    video()
    return load(os.path.join(EP2, "make_video.py"), "ep2_video")


def audio():
    return load(os.path.join(EP1, "make_audio.py"), "ep1_audio")


def ep2_audio():
    return load(os.path.join(EP2, "make_audio.py"), "ep2_audio")


def voice():
    return load(os.path.join(EP1, "make_voice.py"), "ep1_voice")


def thumb():
    video()
    load(os.path.join(BRANDING, "make_branding.py"), "make_branding")
    return load(os.path.join(EP1, "make_thumbnail.py"), "ep1_thumb")
