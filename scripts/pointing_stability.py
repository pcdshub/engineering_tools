"""
Ported from Matt Bain's working example in chemRIXS, generalized for the Basler gigecams and applied ISO
positional & pointing stability standards.
"""

import argparse
import os
import sys
import time
from functools import partial

import matplotlib.pyplot as plt
import numpy as np
from colorama import Fore, Style
from epics import PV

PIXEL_DICT = {'Manta_G046B': 8.3,
              'Manta_G146B': 4.65,
              'Manta_G146C': 4.65,
              'Manta_G2460B': 2.74,
              'acA1300-22gm': 3.75,
              'acA1300-30gm': 3.75,
              'acA1300-60gmNIR': 5.3,
              'acA1440-73gm': 3.45,
              'acA1600-60gm': 4.5,
              'acA2500-20gm': 4.8,
              'FLIR_A65': 17.0,
              'FLIR_AX5': 50.0,
              'JAI_AM-201GE': 5.5,
              'PyrocamIIIHR': 80.0,
              'Mako G-030B': 7.4,
              'Mako G-032B': 7.4,
              'Mako G-040B': 6.9,
              'Mako G-125B': 3.75,
              'Mako G-125C': 3.75,
              'Mako G-158B': 3.45,
              'Mako G-192B': 4.5,
              'Mako G-234B': 5.86,
              'Mako G-319B': 3.45,
              'Mako G-319C': 3.45,
              'Mako G-419B': 5.5,
              'Manta G-033B': 9.9,
              'Manta_G-046B': 8.3,
              'Manta_G-125B': 3.75,
              'Manta_G-145B': 6.45,
              'Manta_G-145C': 6.45,
              'Manta_G-146B': 4.65,
              'Manta_G-146C': 4.65,
              'Manta_G-158B': 3.45,
              'Manta_G-201B': 4.4,
              'Manta G-2460B': 2.74,
              'Manta_G-282B': 3.69,
              'Manta G-419B': 5.5,
              'Manta G-419B-NIR': 5.5,
              'Manta_G-419C': 5.5,
              'Manta_G-504B': 3.45,
              'Manta_G-504C': 3.45,
              'Manta_G-917B': 3.69,
              'Manta G-917C': 3.69,
              'ProsilicaGC1350C': 4.65}


def build_parser():
    """
    Constructs the parser for the script.
    Returns:
        parser: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog='pointing_stability',
        formatter_class=argparse.RawTextHelpFormatter,
        description='Collect centroids from the camera then'
        ' determine the positional stability using ISO 11145:2018',
        epilog='For more information on subcommands, use: '
               'pointing_stability --help')

    parser.add_argument('cam', type=str,
                        help='PV prefix for the camera using ECS naming convention')
    parser.add_argument('-l', '--focal_length', type=float,
                        default=10.,
                        help='Focal lenght of the imaging lens in cm as a float. Defaults to 10 cm.')
    parser.add_argument('-d', '--dir', type=str,
                        help='Set directory for the output data. Defaults to $PWD')
    parser.add_argument('-f', '--filename', type=str,
                        help='Set the base filename for the output data.')
    parser.add_argument('-p', '--pixel_size', type=float,
                        help='Set the pixel size if you have a special snowflake camera.')
    parser.add_argument('-q', '--quiet', action='store_true',
                        default=False,
                        help='Supress the progressbar and graphs from printing to terminal')
    parser.add_argument('-r', '--near_field', action='store_true',
                        default=False,
                        help='Whether to perform calculations assuming near field imaging.'
                        ' Default is to use far-field calculations and a 10 cm focal length.')
    parser.add_argument('-s', '--size', type=int,
                        default=5000,
                        help='Total number of centroids to acquire before calculating'
                        ' the pointing stability. Defaults to 5000 counts')
    return parser


def build_data(data: list, value, **kw):
    """Simple callback for appending camonitor output to a list"""
    data.append(value)


def print_progress_bar(iteration: int, total: int,
                       prefix: str = '', suffix: str = '', decimals: int = 1,
                       length: int = 100, fill: str = '\u2588',
                       end: str = "\r") -> None:
    """
    Print the progressbar to terminal
    Parameters
    -----------
    iteration (int):
        iterator
    total (int):
        total number of iterations
    prefix (str, optional):
        Prefix to progress bar. Defaults to ''.
    suffix (str, optional):
        Suffix to progress bar. Defaults to ''.
    decimals (int, optional):
        Number of decimals to display in percentage. Defaults to 1.
    length (int, optional):
        Length of the progressbar. Defaults to 100.
    fill (str, optional):
        Progressbar fill symbol. Defaults to '\u2588' █.
    end (str, optional):
        Progressbar terminator. Defaults to "\r".
    """

    percent = ('{0:.' + f'{decimals}' + 'f}').format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    color = Fore.LIGHTYELLOW_EX if round(filledLength / length, 1) < 1 else Fore.GREEN

    print(color + f'\r{prefix} |{bar}| {percent}% {suffix}' + Style.RESET_ALL, end=end)


def connect_centroids(cam_prefix: str) -> list[PV]:
    """
    Connect to the centroid PVs and wait for the PV objects to connect.
    Parameters
    -----------
    cam_prefix (str):
        Camera PV prefix.
    Returns
    -----------
    list[epics.PV]:
        list of the PV objects
    """
    centroid_x = PV(f'{cam_prefix}Stats2:CentroidX_RBV', connection_timeout=5)
    centroid_y = PV(f'{cam_prefix}Stats2:CentroidY_RBV', connection_timeout=5)

    centroid_x.wait_for_connection()
    centroid_y.wait_for_connection()

    return centroid_x, centroid_y


def main():
    # Build parser and initialize lists
    parser = build_parser()
    args = parser.parse_args()

    # Make sure the prefix matches AD standard
    camera = args.cam + ':' if args.cam[-1] != ':' else args.cam
    model = PV(f'{camera}Model_RBV', connection_timeout=5).get()
    if not model:
        raise Exception(f'Could not connect to {camera}Model_RBV.')
    # Make sure you're capturing if the bin is != 1
    # First check the source of the stats plugin
    stats_input_port = PV(f'{camera}Stats2:NDArrayPort', connection_timeout=5).get()
    port = camera if 'CAM' in stats_input_port else f'{camera}{stats_input_port}:'
    bin_x = PV(f'{port}BinX_RBV', connection_timeout=5).get()
    bin_y = PV(f'{port}BinX_RBV', connection_timeout=5).get()
    # Initialize lists and connect to centroid PVs
    total = 5000
    if args.size:
        total = args.size
    x_samples = []
    y_samples = []

    centroid_x_pv, centroid_y_pv = connect_centroids(camera)

    # Collect data
    centroid_x_pv.add_callback(partial(build_data, x_samples))
    centroid_y_pv.add_callback(partial(build_data, y_samples))

    while min(len(x_samples), len(y_samples)) < total:
        if not args.quiet:
            print_progress_bar(min(len(x_samples), len(y_samples)) + 1,
                               total=total,
                               prefix='Collecting data...', fill="\u2588")
        time.sleep(0.1)

    # Remove callback after collection
    centroid_x_pv.remove_callback(1)
    centroid_y_pv.remove_callback(1)

    # Convert focal length to micron
    focal_length = 10.0*1E4
    if args.focal_length:
        focal_length = args.focal_length*1E4

    # Trim to same array lengths if necessary
    if len(x_samples) != len(y_samples):
        _length = min(len(x_samples), len(y_samples))
        x_samples = x_samples[:_length]
        y_samples = y_samples[:_length]

    # Convert from pixels to real dimensions using vendor's data and account for binning
    pixel_size = PIXEL_DICT[model]
    x_samples_um = np.asarray(x_samples)*pixel_size*bin_x
    y_samples_um = np.asarray(y_samples)*pixel_size*bin_y

    # Now let's do some fun math
    x_mean = np.mean(x_samples_um)
    y_mean = np.mean(y_samples_um)
    x_centered = x_samples_um - x_mean
    y_centered = y_samples_um - y_mean

    x_std_dev = np.std(x_samples_um, ddof=1)
    y_std_dev = np.std(y_samples_um, ddof=1)

    positional_stability_x = 4*x_std_dev
    positional_stability_y = 4*y_std_dev
    pos_stabilities = [positional_stability_x, positional_stability_y]

    # Now let's look at angular displacements
    if not args.near_field:
        theta_x = np.arctan(x_centered/focal_length)*1E6
        theta_y = np.arctan(y_centered/focal_length)*1E6

        theta_x_avg = np.mean(theta_x)
        theta_y_avg = np.mean(theta_y)

        theta_x_std = np.std(theta_x, ddof=1)
        theta_y_std = np.std(theta_y, ddof=1)

        theta_means = [theta_x_avg, theta_y_avg]
        theta_stds = [theta_x_std, theta_y_std]

    if not args.quiet:
        print('\nPositional stability \u0394 :\n\t'
              + '('
              + ', '.join([f'{_s:2.3e}'
                          for _s in pos_stabilities]
                          )
              + ') \u03bcm')

    if not args.near_field and not args.quiet:
        # Print (Θ_x ± σ_x, Θ_y ± σ_y)
        print('Angular pointing:\n\t'
              + '('
              + ', '.join([f'{_m:2.3e} \u00b1 {_std:2.3e}'
                          for _m, _std in zip(theta_means, theta_stds)]
                          )
              + ') \u03bcrad')
    # #-----------------------------------------------------------------------------------------# #
    # Plotting outputs
    # #-----------------------------------------------------------------------------------------# #
    # Positional displacement subplot
    num_plots = 3
    if args.near_field:
        num_plots = 2
    fig, axs = plt.subplots(num_plots,
                            height_ratios=(num_plots-1)*[1]+[0.5])
    axs[0].scatter(x_centered, y_centered)
    axs[0].axhline(y=0, color='black', linestyle='--')
    axs[0].axvline(x=0, color='black', linestyle='--')
    axs[0].set_xlabel('X displacement (\u03bcm)')
    axs[0].set_ylabel('Y displacement (\u03bcm)')
    axs[0].set_box_aspect(1)
    # Stat data for table printing
    col_labels = ['X', 'Y']
    row_labels = ['\u0394 (\u03bcm)']
    table_data = [pos_stabilities]
    # Angular displacement subplot
    if not args.near_field:
        axs[1].hist(theta_x, bins='fd',
                    fc=(0, 0, 1, 0.5),
                    edgecolor='black',
                    label='X')
        axs[1].hist(theta_y, bins='fd',
                    fc=(1, 0.25, 0.25, 0.5),
                    edgecolor='black',
                    label='Y')
        axs[1].legend(loc='upper right')
        axs[1].set_xlabel("Pointing (\u03bcrad)")
        axs[1].set_ylabel("Counts")
        row_labels = row_labels + ['\u03b8_avg (\u03bcrad)', '\u03b8 std_dev (\u03bcrad)']
        table_data = table_data + [theta_means, theta_stds]
    # Now add the table
    table_data = [[f'{_s:2.3e}' for _s in _ls] for _ls in table_data]
    axs[-1].table(cellText=table_data,
                  cellLoc='center',
                  loc='center',
                  rowLabels=row_labels,
                  colLabels=col_labels
                  )
    axs[-1].axis('Off')
    plt.suptitle(f'{camera}')
    plt.subplots_adjust(hspace=0.4)
    fig.set_figheight(10)
    fig.set_figwidth(10)
    plt.tight_layout()
    plt.gca().set_aspect('equal')
    if not args.quiet:
        plt.show()

    # Format the data for saving

    camera_header = (f"{camera.replace(':', '_').lower()}_imaging_distance_{focal_length*1E-4}"
                     + '\nx_centered (\u03bcm),y_centered (\u03bcm)')
    data = np.concatenate((x_centered, y_centered))
    data = np.resize(data, (2, total))

    timestamp = time.strftime('D%Y_%m_%d_T%H_%M_%S')

    _dir = os.getcwd()
    # Use the user-specified directory and create if it does not exist
    if args.dir:
        _dir = args.dir
        if not os.path.exists(_dir):
            os.makedirs(_dir)

    # Set a default file name and use the user-specified one if it supplied
    file_dest = f"{_dir}/data_{camera.replace(':', '_').lower()}{timestamp}"
    if args.filename:
        file_dest = f"{_dir}/{args.filename}"

    np.savetxt(f"{file_dest}.csv", np.transpose(data), delimiter=',', header=camera_header)
    fig.savefig(f"{file_dest}.png")

    sys.exit(0)


if __name__ == '__main__':
    main()
