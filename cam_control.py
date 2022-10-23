import logging
import subprocess
import tkinter as tk

logger = logging.getLogger(__name__)


class PanAbsolute:
    def __init__(self) -> None:
        self._value = 0
        self.default = 0
        self.step = 1
        self.min = -612_000  # 2**5 * 3**2 * 5**3 * 17 ; -170° -> 3_600 / deg
        self.min_deg = -170
        self.max = 612_000  # 2**5 * 3**2 * 5**3 * 17 ; +170° -> 3_600 / deg
        self.max_deg = 170
        self.resolution = 3_600  # / deg

    def __str__(self) -> str:
        return f"pan_absolute={self._value}"

    def set(self, value: int) -> None:
        self._value = max(min(value, self.max), self.min)

    def get(self) -> int:
        return self._value


class TiltAbsolute:
    def __init__(self) -> None:
        self._value = 0
        self.default = 0
        self.step = 1
        self.min = -108_000  # 2**5 * 3**3 * 5**3 ; -30° -> 3_600 / deg
        self.min_deg = -30
        self.max = 324_000  # 2**5 * 3**4 * 5**3 ; +90° -> 3_600 / deg
        self.max_deg = 90
        self.resolution = 3_600  # / deg

    def __str__(self) -> str:
        return f"tilt_absolute={self._value}"

    def set(self, value: int) -> None:
        self._value = max(min(value, self.max), self.min)

    def get(self) -> int:
        return self._value


class ZoomAbsolute:
    def __init__(self) -> None:
        self._value = 0
        self.default = 0
        self.step = 1
        self.min = 0
        self.max = 5_680  # 2**4 * 5 * 71
        self.resolution = 5 * 71

    def __str__(self) -> str:
        return f"zoom_absolute={self._value}"

    def set(self, value: int) -> None:
        self._value = max(min(value, self.max), self.min)

    def get(self) -> int:
        return self._value


class Camera:
    def __init__(self) -> None:
        self.device = "/dev/video0"
        self.pan = PanAbsolute()
        self.tilt = TiltAbsolute()
        self.zoom = ZoomAbsolute()

    def __str__(self) -> None:
        return " ; ".join([str(self.pan), str(self.tilt), str(self.zoom)])

    def change_position(self) -> None:
        "v4l2-ctl --device /dev/video0 --set-ctrl pan_absolute=0,tilt_absolute=0,zoom_absolute=0"

        ctrl = ",".join(
            [
                str(self.pan),
                str(self.tilt),
                str(self.zoom),
            ]
        )

        logger.debug(ctrl)

        move = subprocess.run(
            [
                "v4l2-ctl",
                "--device",
                self.device,
                "--set-ctrl",
                ctrl,
            ],
            capture_output=True,
            encoding="utf_8",
        )

        logger.info(" ".join(move.args))

        if move.returncode:
            logger.error(move.stderr.strip())
        else:
            logger.info(move.stdout)


class App(tk.Frame):
    def __init__(self, master=None, camera=Camera()):
        super().__init__(master)
        self.grid()
        self.master.title("Hello!")

        self.camera = camera

        # Tilt
        self.tilt_label = tk.Label(text="Tilt")
        self.tilt_label.grid(column=3, row=0, padx=(5, 5), pady=(5, 5))

        self.tilt_value = tk.Scale(
            from_=self.camera.tilt.max_deg,
            to=self.camera.tilt.min_deg,
            orient=tk.VERTICAL,
            length=200,
            tickinterval=15,
        )
        self.tilt_value.grid(column=3, row=1, rowspan=3, padx=(5, 5), pady=(5, 5))

        # Pan
        self.pan = camera.pan

        self.pan_label = tk.Label(text="Pan")
        self.pan_label.grid(column=0, row=1, padx=(5, 5), pady=(5, 5))

        self.pan_value = tk.Scale(
            from_=self.camera.pan.min_deg,
            to=self.camera.pan.max_deg,
            orient=tk.HORIZONTAL,
            length=600,
            tickinterval=20,
        )
        self.pan_value.grid(column=1, row=1, columnspan=2, padx=(5, 5), pady=(5, 5))

        # Zoom
        self.zoom = camera.zoom

        self.zoom_label = tk.Label(text="Zoom")
        self.zoom_label.grid(column=0, row=2, padx=(5, 5), pady=(5, 5))

        self.zoom_value = tk.Scale(
            from_=self.camera.zoom.min / self.camera.zoom.resolution,
            to=self.camera.zoom.max / self.camera.zoom.resolution,
            orient=tk.HORIZONTAL,
            length=300,
        )
        self.zoom_value.grid(column=1, row=2, columnspan=2, padx=(5, 5), pady=(5, 5))

        # Go!
        self.go = tk.Button(text="Go!", command=self.change_position)
        self.go.grid(column=1, row=3, padx=(5, 5), pady=(5, 5))

        # Reset
        self.go = tk.Button(text="Reset", command=self.default_position)
        self.go.grid(column=2, row=3, padx=(5, 5), pady=(5, 5))

        # Moi
        self.go = tk.Button(text="Moi", command=self.my_position)
        self.go.grid(column=0, row=3, padx=(5, 5), pady=(5, 5))

        # Plafond
        self.go = tk.Button(text="Plafond", command=self.ceiling_position)
        self.go.grid(column=0, row=4, padx=(5, 5), pady=(5, 5))

        # Mur
        self.go = tk.Button(text="Mur", command=self.wall_position)
        self.go.grid(column=0, row=5, padx=(5, 5), pady=(5, 5))

    def change_position(self) -> None:
        self.camera.pan.set(self.pan_value.get() * self.camera.pan.resolution)
        self.camera.tilt.set(self.tilt_value.get() * self.camera.tilt.resolution)
        self.camera.zoom.set(self.zoom_value.get() * self.camera.zoom.resolution)
        logger.debug(
            "pan={pan},tilt={tilt},zoom={zoom}".format(
                pan=self.pan_value.get(),
                tilt=self.tilt_value.get(),
                zoom=self.zoom_value.get(),
            )
        )

        self.camera.change_position()

    def default_position(self) -> None:
        self.pan_value.set(self.camera.pan.default)
        self.tilt_value.set(self.camera.tilt.default)
        self.zoom_value.set(self.camera.zoom.default)

        self.change_position()

    def my_position(self) -> None:
        self.pan_value.set(0)
        self.tilt_value.set(5)
        self.zoom_value.set(4)

        self.change_position()

    def ceiling_position(self) -> None:
        self.pan_value.set(0)
        self.tilt_value.set(70)
        self.zoom_value.set(0)

        self.change_position()

    def wall_position(self) -> None:
        self.pan_value.set(60)
        self.tilt_value.set(25)
        self.zoom_value.set(15)

        self.change_position()


if __name__ == "__main__":
    # Rich traceback in the REPL:
    from rich import traceback

    _ = traceback.install()

    # Log to sys.stderr with rich text:
    from rich.logging import RichHandler

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)],
    )

    root = tk.Tk()
    myapp = App(root)

    # Call main function:
    import sys

    sys.exit(myapp.mainloop())
