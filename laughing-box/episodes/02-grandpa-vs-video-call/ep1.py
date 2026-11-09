"""Load episode 1's modules (characters, drawing helpers, voice, SFX) by file path.

Both episodes have scripts with the same names, so episode 1's are loaded under
aliases. Its `from timeline import ...` resolves to this folder's timeline.py,
because this folder is first on sys.path.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EP1 = os.path.join(HERE, "..", "01-grandpa-vs-self-checkout")
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
    # registered as "make_video" too, so the branding helpers reuse this copy
    mod = load(os.path.join(EP1, "make_video.py"), "ep1_video")
    sys.modules.setdefault("make_video", mod)
    return mod


def audio():
    return load(os.path.join(EP1, "make_audio.py"), "ep1_audio")


def voice():
    return load(os.path.join(EP1, "make_voice.py"), "ep1_voice")


def thumb():
    video()
    load(os.path.join(BRANDING, "make_branding.py"), "make_branding")
    return load(os.path.join(EP1, "make_thumbnail.py"), "ep1_thumb")
