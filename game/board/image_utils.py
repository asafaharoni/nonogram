from typing import List

from PIL import Image as im
import numpy as np

from game.board.cell import CellState


def image_to_array(image_path: str):
    image_file = im.open(image_path)
    bool_matrix = np.invert(np.array(image_file.convert('1'))).tolist()
    return bool_to_state_matrix(bool_matrix)


def bool_to_state_matrix(bool_matrix: List[List[bool]]):
    return list(map(
        lambda row: list(map(lambda x: CellState(x),
                             row)),
        bool_matrix))


def array_to_image(array, image_path: str):
    data = np.invert(np.array(array))
    data_bytes = np.packbits(data, axis=1)
    image = im.frombytes(mode='1', size=data.shape[::-1], data=data_bytes)
    image.save(image_path)
