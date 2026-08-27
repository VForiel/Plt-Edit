import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def _backend_module():
    path = Path(__file__).parents[1] / "desktop" / "backend.py"
    spec = importlib.util.spec_from_file_location("pltedit_desktop_backend", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_desktop_backend_opens_updates_and_exports(tmp_path):
    backend = _backend_module()
    source = tmp_path / "source.plt"
    target = tmp_path / "edited.plt"
    png = tmp_path / "edited.png"

    figure, axis = plt.subplots()
    axis.plot([0, 1], [1, 2], label="signal")
    from pltedit._io import save

    save(figure, source)
    opened = backend.handle({"command": "open", "path": str(source)})
    assert opened["model"]["axes"][0]["artists"][0]["label"] == "signal"
    assert isinstance(backend.figure, Figure)

    updated = backend.handle({"command": "update", "changes": {"figure": {"title": "Edited"}, "axes": [{"index": 0, "grid": True}]}})
    assert updated["model"]["title"] == "Edited"
    assert updated["model"]["axes"][0]["grid"] is True

    backend.handle({"command": "save", "path": str(target)})
    backend.handle({"command": "export_png", "path": str(png)})
    assert target.exists()
    assert png.exists()