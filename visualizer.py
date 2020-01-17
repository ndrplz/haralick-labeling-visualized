from pathlib import Path
from typing import Tuple

import cv2
import numpy as np

from utils import neighborhood_idxs


class HaralickVisualizer:
    def __init__(self, index_image: np.ndarray,
                 canvas_size: Tuple[int, int],
                 output_dir: Path = None):
        assert len(index_image.shape) == 2
        self.indexed_image = index_image

        self.indexed_image_init = self.indexed_image.copy()

        self.cmap = self._get_colormap()

        self.canvas_size = canvas_size

        # If an output directory is provided, frames are saved there to be
        #  later used to compose a gif animation / movies later
        self.output_dir = None
        if output_dir is not None:
            self.output_dir = Path(output_dir)
            if not self.output_dir.exists():
                self.output_dir.mkdir()

    def _get_colormap(self):
        """
        Create the colormap to display the indexed image in RGB
        """
        n_indexes = len(np.unique(self.indexed_image))
        cmap = [self._random_color() for _ in range(n_indexes)]
        cmap[0] = np.zeros(3, dtype=np.uint8)  # make sure label `0` is drawn black
        return np.asarray(cmap)

    def draw(self, state: dict):

        color_image = self.cmap[self.indexed_image]
        color_image_init = self.cmap[self.indexed_image_init]

        _, foreground = cv2.threshold(color_image, thresh=0, maxval=255,
                                      type=cv2.THRESH_BINARY)
        foreground = cv2.resize(foreground, dsize=self.canvas_size,
                                interpolation=cv2.INTER_NEAREST)

        # Highlight the kernel in the current position
        if not state['finished']:
            cur_r, cur_c = state['pos']
            for (r, c) in neighborhood_idxs(self.indexed_image, cur_r, cur_c, state['mode']):
                color_image[r, c] = np.full(3, 224, dtype=np.uint8)
            color_image[cur_r, cur_c] = np.full(3, 255, dtype=np.uint8)

        color_image = cv2.resize(color_image, dsize=self.canvas_size,
                                 interpolation=cv2.INTER_NEAREST)

        color_image_init = cv2.resize(color_image_init, dsize=self.canvas_size,
                                      interpolation=cv2.INTER_NEAREST)
        foreground = self.add_title(foreground, 'Input Image')
        color_image_init = self.add_title(color_image_init, 'Initialization')
        color_title = 'Result' if state['finished'] else f'Iterating: {state["mode"]} pass...'
        color_image = self.add_title(color_image, color_title)

        spacing = np.full((color_image.shape[0], 10, 3), 255, dtype=np.uint8)
        return np.concatenate([spacing, foreground,
                               spacing, color_image_init,
                               spacing, color_image,
                               spacing], axis=1)

    @staticmethod
    def _random_color():
        # The min value is not zero to encourage brighter colors
        return np.random.randint(32, 256, size=(3,), dtype=np.uint8)

    @staticmethod
    def add_title(image: np.ndarray, title: str):

        # Pad top image to make space for the title
        pad_h = 50
        pad = np.full((pad_h, image.shape[1], 3), 255, dtype=np.uint8)
        image = np.concatenate([pad, image], axis=0)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        font_color = (0, 0, 0)
        line_type = 2

        text_width, text_height = cv2.getTextSize(title, font, font_scale, line_type)[0]
        bottom_left_corner = (0, int(text_height + (pad_h - text_height) // 2))

        cv2.putText(image, title,
                    bottom_left_corner,
                    font,
                    font_scale,
                    font_color,
                    line_type)  #,
                    #cv2.LINE_AA)

        return image

    def display(self, state: dict, title: str, wait: int = 0):
        """
        Display the current labeling state. If wait > 0, that number of
         millisecond is waited before closing the window. Wait = 0 means
         waiting for key pressed by the user.
        """
        image_to_display = self.draw(state)

        cv2.imshow(title, image_to_display)

        if self.output_dir is not None:
            self._save_frame(image_to_display, state['step'], self.output_dir)

            # Handle the fact that if the labeling has finished you may want to
            #  write the result many times s.t. the animation stops there a bit
            n_frames = 1 if not state['finished'] else 40
            for i in range(0, n_frames):
                self._save_frame(image_to_display, state['step'] + i,
                                 self.output_dir)
        cv2.waitKey(wait)

    @staticmethod
    def _save_frame(image: np.ndarray, cur_step: int, output_dir: Path, ext: str = 'png'):
        out_name = f'{cur_step:06d}.{ext}'
        cv2.imwrite(str(output_dir / out_name), image)
