import argparse
import h5py
from PIL import Image


def convert(filepath, duration=100):
    """
    Convert images in an HDF5 file into a gif and save to cwd.

    This will take as input the path to an hdf5 file containing
    images and convert those images into a gif which will be saved
    to the current workng directory. You can also specify how long
    each frame of the gif should be in milliseconds.

    Parameters
    ----------
    filepath: string
        Path to the hdf5 file containing the images, where the images can be
        found going from the group `entry` to `data` to `data` (again), stored
        as an NxHxW array. Using h5_img_collect will create hdf5 files
        with the expected structure for this function to work.
    duration: int
        The amount of time in milliseconds each frame of the gif should last.
    """

    # Getting images from HDF5 file
    h5_file = h5py.File(filepath, 'r')
    images = h5_file['entry']['data']['data']
    # Converting to PIL.Image
    images = [Image.fromarray(i).convert() for i in images]
    # Saving as GIF
    images[0].save(filepath.split('/')[-1] + '.gif',
                   save_all=True, append_images=images[1:],
                   duration=duration, loop=0)
    return


if __name__ == "__main__":
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filepath', required=True,
                        help='path to hdf5 file containing images')
    parser.add_argument('-d', '--duration', type=int, nargs='?', default=100,
                        help="how long each frame is displayed in milliseconds"
                        ", default is 100")
    args = parser.parse_args()
    convert(args.filepath, args.duration)
