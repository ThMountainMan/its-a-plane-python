from datetime import datetime

from utilities.animator import Animator
from setup import colours, fonts, frames

from rgbmatrix import graphics

# Setup
DATE_COLOUR = colours.PINK
DATE_FONT = fonts.regular
DATE_POSITION = (2, 57)


class DateScene(object):
    def __init__(self):
        super().__init__()
        self._last_date = None

    @Animator.KeyFrame.add(frames.PER_SECOND * 1)
    def date(self, count):
        if len(self._data):
            # Ensure redraw when there's new data
            self._last_date = None

        else:
            # If there's no data to display
            # then draw the date
            now = datetime.now()
            current_date = now.strftime("%-d-%-m-%Y")

            # Only draw if date needs updated
            if self._last_date != current_date:
                # Undraw last date if different from current
                if not self._last_date is None:
                    _ = graphics.DrawText(
                        self.canvas,
                        DATE_FONT,
                        DATE_POSITION[0],
                        DATE_POSITION[1],
                        colours.BLACK,
                        self._last_date,
                    )
                self._last_date = current_date

                # Draw date
                _ = graphics.DrawText(
                    self.canvas,
                    DATE_FONT,
                    DATE_POSITION[0],
                    DATE_POSITION[1],
                    DATE_COLOUR,
                    current_date,
                )
