from argparse import ArgumentParser
from subprocess import getoutput
from time import time, sleep
import os.path
from hutch_python.cam_load import interpret_lines, build_cam
from sys import exit


def take_images(camera, num_images, path, filename):
    """
    Takes and saves images in hdf5 format.

    Uses the hdf51 plugin of camera to take num_images images and
    save them in an hdf5 file at the specified path with the
    as filename if it not empty; if it is empty, it will be saved
    {camera.name}-{timestamp}. Based on CamH5.collect from
    /reg/g/pcds/pyps/apps/hutch-python/rix/rix/cam_to_file.py.

    Parameters
    ----------
    camera: pcdsdevices.areadetector.detectors.PCDSAreaDetector
        The actual camera object containing the hdf51 plugin used to
        collect and save images. Created by build_cam in cam_load.
    num_images: int
        The number of images to take.
    path: string
        Path where the hdf5 file containing the images should be saved to.
    filename: string
        Name of hdf5 file images are saved in. Timestamp will be appended
        to ensure all captures have unique filenames.
    """
    # Creating callbacks to know when collecting/saving images is complete
    collecting = False
    writing = False
    # Getting start time for callbacks and appending to filename
    start_time = time()
    filename += "-" + str(int(start_time))

    def _collecting_cb(value, old_value, timestamp, **kwargs):
        """Get a callback for collecting changes"""
        nonlocal collecting
        if timestamp > start_time and old_value == 1:
            collecting = value

    def _writing_cb(value, old_value, timestamp, **kwargs):
        """Get a callback when writing changes"""
        nonlocal writing
        if timestamp > start_time and old_value == 1:
            writing = value

    # Start collecting and saving
    collect_uid = camera.hdf51.capture.subscribe(_collecting_cb)
    write_uid = camera.hdf51.write_file.subscribe(_writing_cb)

    # Setting up hdf51 plugin
    camera.hdf51.file_path.put(path)
    camera.hdf51.file_name.put(filename)
    camera.hdf51.file_template.put('%s%s.h5')
    camera.hdf51.num_capture.put(num_images)
    camera.hdf51.auto_save.put(True)
    camera.hdf51.file_write_mode.put('Capture')
    camera.hdf51.enable.put('Enabled')
    camera.hdf51.capture.put('Capture')
    collecting = True
    writing = True
    # Clean up subscribers when finished
    while collecting and camera.hdf51.num_captured.get() < num_images:
        sleep(0.1)
    camera.hdf51.capture.unsubscribe(collect_uid)
    while writing:
        sleep(0.1)
    camera.hdf51.write_file.unsubscribe(write_uid)
    # Cleaning up plugin
    camera.hdf51.enable.put('Disabled')
    camera.hdf51.file_path.put('')
    camera.hdf51.file_name.put('')
    camera.hdf51.file_template.put('')
    camera.hdf51.num_capture.put(0)
    print(f"Took {num_images} pictures with {camera.name}, "
          f"saved to {path}{filename}")


def load_camera(hutch, cam_name):
    """
    Creates camera object.

    Gets camera details based on name and hutch-specific
    camviewer config file and uses build_cam to create an
    individual camera object. Will exit if the config file
    or the camera cannot be found.

    Parameters
    ----------
    hutch: string
        Name of hutch the camera is in, needed to find and
        load the correct config file.
    cam_name: string
        Name of camera to load.

    Returns
    -------
    camera: pcdsdevices.areadetector.detectors.PCDSAreaDetector
        Camera object created by build_cam with hdf51 plugin
        member to take and save images.
    """
    # Get config for cam_name
    try:
        with open(f'/reg/g/pcds/pyps/config/{hutch}/camviewer.cfg', 'r') as f:
            lines = f.readlines()
    except Exception as e:
        exit('Could not open camera config file, '
             f'/reg/g/pcds/pyps/config/{hutch}/camviewer.cfg', e)
    cam_line = [line for line in lines if cam_name.upper() in line]
    if not cam_line:
        exit('Did not find camera in camera config file, '
             f'/reg/g/pcds/pyps/config/{hutch}/camviewer.cfg, '
             'check spelling of camera argument.')
    cam_info = interpret_lines(cam_line)
    camera = build_cam(*cam_info[0])
    return camera


def button_gui(cameras, num_images, path, filenames):
    """
    Takes pictures by clicking a button.

    Creates a pyqt window with a button that, when pressed, will take images
    according to the arguments passed. The button can be pressed an arbitrary
    number of time to take a series of images whenever desired using the
    specified args. A timestamp will be appended to the filename every press
    so that hdf5 files have unique names and do not overwrite each other. In
    the gui, num_images and the text of each button can be also be changed.
    The details of every capture will be printed to the terminal. A button will
    be green and unpressable while capturing.

    Parameters
    ----------
    camera: pcdsdevices.areadetector.detectors.PCDSAreaDetector
        The actual camera object containing the hdf51 plugin used to
        collect and save images. Created by build_cam in cam_load.
    num_images: int
        The number of images to take.
    path: string
        Path where the hdf5 file containing the images should be saved to.
    filename: string
        Name of hdf5 file images are saved in. A timestamp will be appended
        to ensure all captures have unique filenames.
    """
    from qtpy.QtWidgets import (QApplication, QWidget, QGridLayout,
                                QPushButton, QLineEdit, QLabel, QHBoxLayout,
                                QInputDialog)
    from qtpy.QtGui import QIntValidator
    from qtpy.QtCore import Qt
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Imager")
    window.setMinimumSize(210, len(cameras)*60 + 75)
    main_layout = QGridLayout()
    window.setLayout(main_layout)
    num_layout = QHBoxLayout()
    main_layout.addLayout(num_layout, 0, 0, 1, -1, Qt.AlignCenter)
    # Text box to change num_images
    num_label = QLabel()
    num_label.setFixedSize(80, 25)
    num_label.setText("Num. Images")
    num_layout.addWidget(num_label, Qt.AlignRight)
    num_setter = QLineEdit()
    num_setter.setText(str(num_images))
    num_setter.setValidator(QIntValidator())
    num_setter.setMaxLength(3)
    num_setter.setFixedSize(30, 25)

    def pressed(index):
        """Call take_images and reset button background color when finished"""
        take_images(cameras[index], num_images, path, filenames[index])
        buttons[index].clearFocus()

    def set_num(text):
        """Change number of images to take"""
        try:
            new_num = int(text)
        except ValueError:
            # '' or '-'
            return
        nonlocal num_images
        if new_num > 0:
            num_images = new_num
        else:
            print("Num. Images must be positive.")
    num_setter.textEdited.connect(set_num)
    num_layout.addWidget(num_setter, Qt.AlignLeft)

    def rename(index):
        text, ok = QInputDialog.getText(None, 'Rename Camera', 'New Name',
                                        text=buttons[index].text())
        if ok:
            buttons[index].setText(text)
    buttons = []
    # Add buttons to take images and change button text
    for index, (camera, filename) in enumerate(zip(cameras, filenames), 1):
        button = QPushButton(camera.name)
        button.setFixedSize(125, 50)
        button.clicked.connect(pressed, index)
        # Make button green when pressed
        button.setStyleSheet("QPushButton::focus"
                             "{"
                             "background-color : lightgreen;"
                             "}")
        buttons.append(button)
        main_layout.addWidget(button, index, 0, 1, -1, Qt.AlignCenter)
        renamer = QPushButton('...')
        renamer.setFixedSize(30, 30)
        renamer.clicked.connect(rename, index)
        main_layout.addWidget(renamer, index, 1)
    # Show save directory at bottom
    dir_label = QLabel()
    dir_label.setFixedHeight(25)
    dir_label.setText(f'Save dir: {path}')
    main_layout.addWidget(dir_label, index + 1, 0, 1, -1, Qt.AlignCenter)
    # Open gui
    window.show()
    app.exec_()


if __name__ == '__main__':
    # Arguments
    parser = ArgumentParser(usage='This script requires pcds_conda, '
                            'please source it before running.')
    parser.add_argument("-c", "--cam", help="name of camera(s)",
                        required=True, nargs='+')
    parser.add_argument("-H", "--hutch", required=False,
                        default=getoutput("get_info --gethutch"),
                        help="name of hutch for camera, "
                        "default is host hutch")
    parser.add_argument("-n", "--num_images", required=False, default=10,
                        help="number of images to take, default is 10",
                        type=int)
    parser.add_argument("-p", "--path", required=True, default='.',
                        help="path to save images in hdf5 file, "
                        "must be in /reg/d/iocData/ or /cds/data/iocData"
                        ", recommend using /reg/d/iocData/{IOC}/hdf5")
    parser.add_argument("-f", "--filename", required=False, default="",
                        help="prefix for name of hdf5 file to store "
                        "images in, camera name and timestamp will be "
                        "appended")
    parser.add_argument("-g", "--gui", action='store_true',
                        help="opens qt window where you take "
                        "images via button press, will append "
                        "timestamp to filename if given")
    args = parser.parse_args()
    # Checking args
    if not os.path.isdir(args.path):
        exit("path is not directory; must provide a valid path in"
             " /reg/d/iocData/ or /cds/data/iocData/.")
    if args.path[-1] != '/':
        args.path += '/'
    if args.num_images < 1:
        exit("num_images must be positive.")
    # Need hutch name to load cameras
    if args.hutch == 'unknown_hutch':
        exit("Host hutch unknown: must specify "
             "hutch with --hutch or be on a host"
             " with a known hutch")
    # Building cameras and appending camera name(s) to filename
    cameras = [load_camera(args.hutch, camera) for camera in args.cam]
    if args.filename:
        args.filename += "-"
    filenames = [args.filename + camera for camera in args.cam]
    if args.gui:
        button_gui(cameras=cameras, num_images=args.num_images, path=args.path,
                   filenames=filenames)
    else:
        for (camera, filename) in zip(cameras, filenames):
            take_images(camera=camera, num_images=args.num_images,
                        path=args.path, filename=args.filename)
