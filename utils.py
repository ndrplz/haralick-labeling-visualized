import numpy as np


def neighborhood_idxs(image: np.ndarray, r: int, c: int, mode: str):
    """
    Get indexes of the current position neighbors
    """
    assert mode in {'forward', 'reverse'}

    if mode == 'forward':
        offsets = [(0, -1), (-1, -1), (-1, 0), (-1, 1)]
    else:
        offsets = [(0, 1), (1, -1), (1, 0), (1, 1)]

    support_idxs = []
    h, w = image.shape
    for offset in offsets:
        new_r = r + offset[0]
        new_c = c + offset[1]
        if 0 <= new_r < h and 0 <= new_c < w:
            support_idxs.append((new_r, new_c))

    return support_idxs


def neighborhood_values(image: np.ndarray, r: int, c: int, mode: str):
    """
    Get values of pixels in the neighborhood of the current position
    """
    assert mode in {'forward', 'reverse'}

    neighborhood = []

    for (supp_r, supp_c) in neighborhood_idxs(image, r, c, mode):
        if image[supp_r, supp_c]:  # is foreground
            neighborhood.append(image[supp_r, supp_c])

    return neighborhood
