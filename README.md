![Image](./common/dannce_logo.png)

DANNCE (3-Dimensional Aligned Neural Network for Computational Ethology) is a convolutional neural network (CNN) that extracts the 3D positions of user-defined anatomical keypoints from videos of behaving animals. The key innovations of DANNCE compared to existing approaches for 2D keypoint detection in animals (e.g. LEAP, DeepLabCut) are that (1) the network is fully 3D, so that it can learn more abstract 3D features about how cameras and keypoints relate to one another and (2) we pre-train DANNCE using a large dataset of rat motion capture and synchronized video, so that the network learns what rodents look like ahead of time. The network's ability to track keypoints transfers well to mice and other mammals, and works across different camera views, camera types, and illumination conditions. To use DANNCE, first you must collect video recordings of animals from at least two views using synchronized, calibrated cameras. Calibrating cameras is a straightforward procedure, with toolboxes available in Matlab and Python, and we include our calibration scripts below. After acquisition, one can use DANNCE to detect keypoints. The DANNCE algorithm is currently configured as a two-stage system. First, videos are processed to extract the overall position of the animal in each video frame. Then, these positions are used to create *unprojected* 3D image volumes for each view that contain the animal. These image volumes are used as input to the CNN to make keypoint predictions.

## Camera Calibration


## DANNCE Installation

The following combinations of operating systems, python, tensorflow, cuda, and cudnn distributions have been used for development.

|      OS      | python | tensorflow-gpu | cuda | cudnn |
|:------------:|:------:|:----------:|:----:|:-----:|
| Ubuntu 18.04 |  3.6.8 |   1.10.0   |  9.0 |  7.2  |
| Ubuntu 16.04 |  3.6.x |   1.10.x   |  9.0 |  7.x  |
|  Windows 10  |  3.6.8 |   1.10.0   |  9.0 |  7.6  |
|  Windows 10  |  3.6.8 |    1.4.x   |  8.0 |  6.0  |

We recommend installing `DANNCE` within a conda environment using `python 3.6.x`.

1. Install tensorflow by following the instructions [here](https://www.tensorflow.org/install/pip). This is often as simple as `pip install tensorflow==1.10.0` or `pip install tensorflow-gpu==1.10.0` for gpu support.

2. Install dependencies with the included setup script `python setup.py install`

3. Configure Matlab engine for python (often requires admin priviledges). Open Matlab, enter the command `matlabroot` in the command-line, and copy the resulting path. In Unix systems, enter the command `sudo $(which python) matlabroot/extern/engines/python/setup.py install` replacing `matlabroot` with the path you copied. In Windows, start a command prompt with admin priviledges and enter the command `python_path matlabroot/extern/engines/python/setup.py install`, replacing `python_path` with the path to your environment's python.

## Formatting The Data
During training and evaluation, DANNCE requires a set of videos across multiple views, a camera calibration parameters file, and a "matched frames" file that indexes the videos to ensure synchrony. DANNCE also supports data in the form of individual images and volumetric `.npy` files (used to accelerate training). For evaluation, the default data format is video.

**video directories**.
DANNCE requires a parent video directory with *n* sub-directories, one for each of *n* cameras. Within each subdirectory, videos must be named according the frame index of the first frame in the file. For example, for a three-camera system, the video directory must look like:

./videos/

+-- Camera1

|\_\_+--0.mp4

+-- Camera2

|\_\_+--0.mp4

+-- Camera3

|\_\_+--0.mp4

DANNCE can also accommodate an additional level of subdirectories if `vid_dir_flag` is set to `False` during configuration.

./videos/

+-- Camera1

|\_\_+--3503723726252562

|\_\_\_\_\_+--0.mp4

+-- Camera2

|\_\_+--3503723999451111

|\_\_\_\_\_+--0.mp4

+-- Camera3

|\_\_+--3503723711118999

|\_\_\_\_\_+--0.mp4

**camera calibration parameters**.
DANNCE requires a .mat file for each camera containing the camera's rotation matrix, translation vector, intrinsic matrix, radial distortion, and tangential distortion. To convert from Jesse's calibration format to the required format, use `utils/convert_calibration.m`.

A properly formatted calibration file has the following fields, `['R','t','K','RDistort','TDistort']`.

**matched frames file**.
To ensure that individual video frames are synchronized at each time point, DANNCE requires an array that associates each time point (in any unit) to an associated video frame in each camera. During dataset formatting, these indices are combined with any available training labels to form the core data representation. For making predictions with DANNCE, these training labels are ignored, although DANNCE still expects to find placeholder label arrays.
- *prediction mode, labeling mode*. Use `utils/preprocess_data.m` to convert Jesse's matched frame files into DANNCE format
- *training with hand-labeled data*. See **Hand-labeling** below.

## Predicting Keypoints With DANNCE

Making predictions with a trained DANNCE network requires 3 steps.

#### 1) Format the data (see above)
#### 2) Find the animal center of mass (COM) in each video frame
You can use your favorite method to find an estimate of the animal COM in each frame. We trained a U-Net to do it. To find the COM with our U-Net, run `predict_COMfinder.py`. This will generate a COM file that is used by DANNCE.

#### 3) Run the everything through DANNCE
Given formatted data and a COM file, DANNCE can now predict keypoints from your video streams.
To do this, run `predict_DANNCE.py`. See the python file for specific usage instructions. 

We have configured DANNCE to work best with a specific organization of data directories: 

./MyProject/

+-- videos

|\_\_+--Camera1

|\_\_\_\_\_+--0.mp4

|\_\_+--Camera2

|\_\_\_\_\_+--0.mp4

+-- data

|\_\_+--Camera1_MatchedFrames.mat

|\_\_+--Camera2_MatchedFrames.mat

+-- calibration

|\_\_+--Camera1_params.mat

|\_\_+--Camera2_params.mat

See ./demo/calibrd18_black6_mouseone_green/ for more details. 

The videos in the demo are too big to be uploaded, and can be found here:

calibrd18_black6_mouseone_green: https://www.dropbox.com/sh/q385p1689zdw8iz/AABPuxCyUBHffFZnGEmbOwQMa?dl=0
calibrd18_black6_mousetwo_green: https://www.dropbox.com/sh/1xvpe8e97x53ah6/AACaY3N7E-WzINoqY2ggFa6va?dl=0


## Training The COMfinder U-Net
DANNCE requires a reasonable estimate of the 3D position of the animal in each frame. We obtain this by triangulating the 2D COM of the animal in each frame. Our U-Net is brittle and typically requires some additional training data to get it working on new views, new environments, and new species. If working with hand-labeled data, your same data structures can be used to train the COMfinder network.

Given formatted data, a properly organized directory structure, and a config file (see demo folder), navigate to your project folder and run

`python $my_path_to_DANNCE/train_COMfinder.py ./config.yaml`, where `$my_path_to_DANNCE` is a path to the root DANNCE directory.

After training, run `python $my_path_to_DANNCE/predict_COMfinder.py ./config.yaml`. To generate center of mass predictions.

## Training DANNCE

Once the COM is found, the main DANNCE network can be trained by running:

`python $my_path_to_DANNCE/train_DANNCE.py ./config.yaml`

After training, run

`python $my_path_to_DANNCE/predict_DANNCE.py ./config.yaml` to make 3D predictions using the trained model.

Consult the demo folder for directory and config file formatting examples

## Hand-Labeling
Before starting, create an Amazon account and follow the instructions to set up the AWS CLI.


#### 1) Run ./dannce/labeling/prelabel.py

This requires a standard configuration file and project directory structure, see ./demo/calibrd18_black6_mouseone_green/ for details.

Example: Navigating to your project directory and running prelabel.py ./config.yaml 100 s3://myS3bucket/labeling1/ will create a labeling subdirectory, extract 100 random images from each of your videos, upload them to the indicated s3 bucket, and create a bash script that can be run to start the Amazon labeling job.

#### 2) Run create_job.sh

`prelabel.py` will create a bash script at ./myproject/labeling/imDir/create_job.sh. On Linux/UNIX, run this using `bash`.

#### 3) When labeling is completed, run ./dannce/labeling/postlabel.py

This uses the same config file as step #1. Navigate to your project directory and run `postlabel.py ./config.yaml`

`postlabel.py` will generate data files that immediately be used to train CMfindr or DANNCE!
