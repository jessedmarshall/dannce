"""
Use this script to create required synchronization ('sync') files, which define the relationship
    between frames across different cameras over time.

Use this script if you know your camera frames are triggered and reliably synchronized.

If your cameras are not natively synchronized, but you can collect timestaps for each
    frame, MatchedFrames files should be generated by `preprocess_data.m`, together
    with a formatted `.mat` file listing the frameID for each camera and each timepoint.
    See `/dannce/utils/example_matchedframes.mat` file for how these timestamp data
    should be formatted.

Use of makeSyncFiles.py:
    python makeSyncFiles.py path_to_video_folder acquisition_frame_rate num_landmarks

path_to_video_folder: string, the path to your project main video folder, which
    contains separate subfolders for each camera. These subfolders contain the
    video files.
acquisition_frame_rate: int or float, the frame rate of your video acquisition
num_landmarks: number of landmarks you plan to label/track

Files will be written to a `sync` directory in the video folder parent directory
"""

import imageio
import numpy as np
import scipy.io as sio
import os
import sys

_VALID_EXT = ["mp4", "avi"]

vidpath = sys.argv[1]
fps = float(sys.argv[2])
num_landmarks = int(sys.argv[3])

outpath = os.path.dirname(vidpath.rstrip(os.sep))
outpath = os.path.join(outpath, "sync")

if not os.path.exists(outpath):
    os.makedirs(outpath)
    print("making new folder, {}".format(outpath))

print("Writing Sync files to {}...".format(outpath))

dirs = os.listdir(vidpath)
dirs = [d for d in dirs if os.path.isdir(os.path.join(vidpath, d))]

print("Found the following cameras: {}".format(dirs))

dirs = [os.path.join(vidpath, d) for d in dirs]


def get_vid_paths(dir_):
    vids = os.listdir(dir_)
    vids = [vd for vd in vids if vd.split(".")[-1] in _VALID_EXT]
    vids = [os.path.join(dir_, vd) for vd in vids]
    return vids


camnames = []
framecount = []
for d in dirs:
    cnt = 0
    vids = get_vid_paths(d)
    if len(vids) == 0:
        print("Traversing video subdirectory")
        d = os.path.join(d, os.listdir(d)[0])
        vids = get_vid_paths(d)

    for i in range(len(vids)):
        # Open each video file and count the number of frames
        thisvid = imageio.get_reader(vids[i])
        cnt += thisvid.count_frames()

    framecount.append(cnt)
    cname = os.path.basename(d.rstrip(os.sep))
    camnames.append(cname)

    print("Found {} frames for {}".format(cnt, cname))

if np.sum(framecount) // len(framecount) != framecount[0]:
    raise Exception("Your videos are not the same length")


if fps > 1000:
    raise Exception("Acquisition rates over 1000 Hz not currently supported")

fp = 1000.0 / fps  # frame period in ms
fp = fp.astype(int)

data_frame = np.arange(framecount[0])
data_sampleID = data_frame * fp + 1
data_2d = np.zeros((framecount[0], 2 * num_landmarks))
data_3d = np.zeros((framecount[0], 3 * num_landmarks))

checkf = os.listdir(outpath)
for cname in camnames:
    fname = cname + "_sync.mat"
    outfile = os.path.join(outpath, fname)
    if fname in checkf:
        ans = ""
        while ans != "y" and ans != "n":
            print(fname + " already exists. Overwrite (y/n)?")
            ans = input().lower()

        if ans == "n":
            print("Ok, skipping.")
            continue

    print("Writing " + outfile)
    sio.savemat(
        outfile,
        {
            "data_frame": data_frame[:, np.newaxis],
            "data_sampleID": data_sampleID[:, np.newaxis],
            "data_2d": data_2d,
            "data_3d": data_3d,
        },
    )

print("done!")
