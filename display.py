import time
import sys
import os
from typing import overload

from animator import Animator
from overhead import Overhead

from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

DEFAULT_INDENT_STATIC_TEXT = 4

FRAME_RATE = 0.1
FRAME_PERIOD = 1 / FRAME_RATE

COLOUR_BLACK = graphics.Color(0, 0, 0)
COLOUR_WHITE = graphics.Color(255, 255, 255)
COLOUR_YELLOW = graphics.Color(255, 255, 0)
COLOUR_BLUE = graphics.Color(55, 14, 237)
COLOUR_BLUE_LIGHT = graphics.Color(153, 204, 255)

MAX_TEXT_WIDTH = 64


class Display(Animator):
    def __init__(self):
        super().__init__(FRAME_RATE)

        # Setup Display
        options = RGBMatrixOptions()
        options.hardware_mapping = "adafruit-hat-pwm"
        options.rows = 32
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.row_address_type = 0
        options.multiplexing = 0
        options.pwm_bits = 11
        options.brightness = 100
        options.pwm_lsb_nanoseconds = 130
        options.led_rgb_sequence = "RGB"
        options.pixel_mapper_config = ""
        options.show_refresh_rate = 0
        options.gpio_slowdown = 1
        options.disable_hardware_pulsing = True
        options.drop_privileges = True
        self.matrix = RGBMatrix(options=options)

        # Setup canvas
        self.canvas = self.matrix.CreateFrameCanvas()
        self.canvas.Clear()

        # Setup fonts
        self.font_small = graphics.Font()
        self.font_regular = graphics.Font()
        self.font_large = graphics.Font()
        self.font_small.LoadFont(f"{DIR_PATH}/fonts/4x6.bdf")
        self.font_regular.LoadFont(f"{DIR_PATH}/fonts/6x12.bdf")
        self.font_large.LoadFont(f"{DIR_PATH}/fonts/8x13.bdf")

        # Element positions
        self.plane_position = MAX_TEXT_WIDTH

        # Data to render
        self._data_index = 0
        self._data_all_looped = False
        self._data = []

        # Start Looking for planes
        self.overhead = Overhead()
        self.overhead.grab_data()

    def draw_square(self, x0, y0, x1, y1, colour):
        for x in range(x0, x1):
            _ = graphics.DrawLine(self.canvas, x, y0, x, y1, colour)

    def reset_scene(self):
        self.flight_number_bar()
        self.journey()
        self.journey_arrow()

    @Animator.KeyFrame.add(0)
    def flight_number_bar(self):

        # Guard against no data
        if len(self._data) == 0:
            self.canvas.Clear()
            return

        # Clear the area
        self.draw_square(0, 14, 63, 18, COLOUR_BLACK)

        # Draw flight number if available
        flight_no_text_length = 0
        if (
            self._data[self._data_index]["callsign"] and
            self._data[self._data_index]["callsign"] != "N/A"
        ):
            flight_no = f'{self._data[self._data_index]["callsign"]}'

            flight_no_text_length = graphics.DrawText(
                self.canvas,
                self.font_small,
                2,
                19,
                COLOUR_BLUE,
                flight_no,
            )

        # Draw bar
        if len(self._data) > 1:
            # Clear are where N of M might have been
            self.draw_square(48, 14, 64, 18, COLOUR_BLACK)

            # Dividing bar
            graphics.DrawLine(self.canvas, flight_no_text_length + 2, 16, 47, 16, COLOUR_BLUE_LIGHT)

            # Draw text
            text_length = graphics.DrawText(
                self.canvas,
                self.font_small,
                51,
                19,
                COLOUR_WHITE,
                f"{self._data_index + 1}/{len(self._data)}",
            )
        else:
            # Dividing bar
            graphics.DrawLine(self.canvas, flight_no_text_length + 2, 16, 64, 16, COLOUR_BLUE_LIGHT) 

    @Animator.KeyFrame.add(0)
    def journey(self):

        # Guard against no data
        if len(self._data) == 0:
            return

        if not (
            self._data[self._data_index]["origin"]
            and self._data[self._data_index]["destination"]
        ):
            return

        journey = f"{self._data[self._data_index]['origin']}  {self._data[self._data_index]['destination']}"

        # Draw background
        self.draw_square(0, 0, 64, 13, COLOUR_BLACK)

        # Draw text
        text_length = graphics.DrawText(
            self.canvas,
            self.font_large,
            0,
            12,
            COLOUR_YELLOW,
            journey,
        )

    @Animator.KeyFrame.add(1)
    def plane(self, count):

        # Guard against no data
        if len(self._data) == 0:
            return

        MAX_STATIC_TEXT_LEN = 12

        plane = f'{self._data[self._data_index]["plane"]}'

        # Draw background
        self.draw_square(0, 20, 64, 32, COLOUR_BLACK)

        # Draw text
        text_length = graphics.DrawText(
            self.canvas,
            self.font_regular,
            self.plane_position,
            28,
            COLOUR_YELLOW,
            plane
        )

        # Handle scrolling
        self.plane_position -= 1
        if self.plane_position + text_length < 0:
            self.plane_position = MAX_TEXT_WIDTH
            if len(self._data) > 1:
                self._data_index = (self._data_index + 1) % len(self._data)
                self._data_all_looped = (
                    not self._data_index
                ) or self._data_all_looped
                self.reset_scene()


    @Animator.KeyFrame.add(0)
    def journey_arrow(self):
        # Guard against no data
        if len(self._data) == 0:
            return

        if not (
            self._data[self._data_index]["origin"]
            and self._data[self._data_index]["destination"]
        ):
            return

        self.draw_square(28, 2, 36, 12, COLOUR_BLACK)
        graphics.DrawLine(self.canvas, 29, 2, 34, 7, COLOUR_BLUE_LIGHT)
        graphics.DrawLine(self.canvas, 34, 7, 29, 12, COLOUR_BLUE_LIGHT)

    @Animator.KeyFrame.add(5)
    def loading_blink(self, count):
        graphics.DrawLine(self.canvas, 63, 0, 63, 5, COLOUR_BLACK)
        if self.overhead.processing:
            self.canvas.SetPixel(63, count % 6, 255, 255, 255)

    @Animator.KeyFrame.add(FRAME_PERIOD * 5)
    def check_for_loaded_data(self, count):
        if self.overhead.new_data:
            self._data_index = 0
            self._data_all_looped = False
            self._data = self.overhead.data
            self.reset_scene()

    @Animator.KeyFrame.add(1)
    def sync(self, count):
        _ = self.matrix.SwapOnVSync(self.canvas)

    @Animator.KeyFrame.add(FRAME_PERIOD * 20)
    def grab_new_data(self, count):
        if not (self.overhead.processing and self.overhead.new_data) and (
            self._data_all_looped or len(self._data) <= 1
        ):
            self.overhead.grab_data()

    def run(self):
        try:
            # Start loop
            print("Press CTRL-C to stop")
            self.play()

        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)
