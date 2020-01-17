from pathlib import Path

import numpy as np

from utils import neighborhood_values
from visualizer import HaralickVisualizer


def haralick_labeling(image: np.ndarray, display: bool = False) -> None:
    """
    Haralick iterative labeling
    """
    assert len(image.shape) == 2
    assert len(np.unique(image)) == 2

    # Init the image assigning a distinct label to each fg pixel
    image[image > 0] = np.arange(1, np.sum(image > 0) + 1)

    if display:
        visualizer = HaralickVisualizer(index_image=image,
                                        canvas_size=(512, 512),
                                        output_dir=Path('./output'))

    # Keep track of current state of the labeling process,
    #  only for visualization purposes
    state = {
        'iter': 0,
        'finished': False,
        'mode': 'forward',
        'pos': (0, 0),
        'step': 0
    }

    while True:

        state['iter'] += 1

        changed = False

        for scan_mode in ['forward', 'reverse']:
            state['mode'] = scan_mode

            # Top to bottom, left to right
            row_range = range(0, image.shape[0])
            col_range = range(0, image.shape[1])
            if scan_mode == 'reverse':
                # Bottom to top, right to left
                row_range = range(image.shape[0] - 1, -1, -1)
                col_range = range(image.shape[1] - 1, -1, -1)

            for r in row_range:
                for c in col_range:

                    state['pos'] = (r, c)
                    state['step'] += 1

                    if image[r, c]:  # foreground
                        neighborhood = neighborhood_values(image, r, c, state['mode'])
                        if neighborhood and image[r, c] != min(neighborhood):
                            image[r, c] = min(neighborhood)
                            changed = True

                    if display:
                        visualizer.display(state, title='Labeling...', wait=10)

        if not changed:
            state['finished'] = True
            if display:
                visualizer.display(state, title='RESULT', wait=0)
            break
