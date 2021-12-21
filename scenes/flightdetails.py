from animator import Animator
from setup import colours, fonts, screen

from rgbmatrix import graphics

# Setup
BAR_STARTING_POSITION = (0, 18)
BAR_PADDING = 2

FLIGHT_NO_POSITION = (1, 21)
FLIGHT_NO_TEXT_HEIGHT = 8  # based on font size
FLIGHT_NO_FONT = fonts.font_small

FLIGHT_NUMBER_ALPHA_COLOUR = colours.COLOUR_BLUE
FLIGHT_NUMBER_NUMERIC_COLOUR = colours.COLOUR_BLUE_LIGHT

DATA_INDEX_POSITION = (52, 21)
DATA_INDEX_TEXT_HEIGHT = 6
DATA_INDEX_FONT = fonts.font_extrasmall

DIVIDING_BAR_COLOUR = colours.COLOUR_GREEN
DATA_INDEX_COLOUR = colours.COLOUR_GREY


class FlightDetailsScene(object):

    def __init__(self):
        super().__init__()

    @Animator.KeyFrame.add(0)
    def flight_details(self):

        # Guard against no data
        if len(self._data) == 0:
            return

        # Clear the whole area
        self.draw_square(
            0,
            BAR_STARTING_POSITION[1] - (FLIGHT_NO_TEXT_HEIGHT // 2),
            screen.WIDTH - 1,
            BAR_STARTING_POSITION[1] + (FLIGHT_NO_TEXT_HEIGHT // 2),
            colours.COLOUR_BLACK,
        )

        # Draw flight number if available
        flight_no_text_length = 0
        if (
            self._data[self._data_index]["callsign"]
            and self._data[self._data_index]["callsign"] != "N/A"
        ):
            flight_no = f'{self._data[self._data_index]["callsign"]}'

            for ch in flight_no:
                ch_length = graphics.DrawText(
                    self.canvas,
                    FLIGHT_NO_FONT,
                    FLIGHT_NO_POSITION[0] + flight_no_text_length,
                    FLIGHT_NO_POSITION[1],
                    FLIGHT_NUMBER_NUMERIC_COLOUR
                    if ch.isnumeric()
                    else FLIGHT_NUMBER_ALPHA_COLOUR,
                    ch,
                )
                flight_no_text_length += ch_length

        # Draw bar
        if len(self._data) > 1:
            # Clear are where N of M might have been
            self.draw_square(
                DATA_INDEX_POSITION[0] - BAR_PADDING,
                BAR_STARTING_POSITION[1] - (FLIGHT_NO_TEXT_HEIGHT // 2),
                screen.WIDTH,
                BAR_STARTING_POSITION[1] + (FLIGHT_NO_TEXT_HEIGHT // 2),
                colours.COLOUR_BLACK,
            )

            # Dividing bar
            graphics.DrawLine(
                self.canvas,
                flight_no_text_length + BAR_PADDING,
                BAR_STARTING_POSITION[1],
                DATA_INDEX_POSITION[0] - BAR_PADDING - 1,
                BAR_STARTING_POSITION[1],
                DIVIDING_BAR_COLOUR,
            )

            # Draw text
            text_length = graphics.DrawText(
                self.canvas,
                fonts.font_extrasmall,
                DATA_INDEX_POSITION[0],
                DATA_INDEX_POSITION[1],
                DATA_INDEX_COLOUR,
                f"{self._data_index + 1}/{len(self._data)}",
            )
        else:
            # Dividing bar
            graphics.DrawLine(
                self.canvas,
                flight_no_text_length + BAR_PADDING if flight_no_text_length else 0,
                BAR_STARTING_POSITION[1],
                screen.WIDTH,
                BAR_STARTING_POSITION[1],
                DIVIDING_BAR_COLOUR,
            )
