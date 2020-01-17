import numpy as np

from haralick import haralick_labeling


def main():
    np.random.seed(123)

    # Create a random binary image to test the labeling process
    img_h, img_w = 8, 8
    image = np.random.choice((0, 0, 1), size=(img_h, img_w)).astype(np.uint8)

    haralick_labeling(image, display=True)


if __name__ == '__main__':
    main()
