from skimage import io


def get_image(path_to_image: str):

    return io.imread(path_to_image)
