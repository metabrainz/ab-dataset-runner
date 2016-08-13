from __future__ import print_function

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
import config

import gaia_wrapper
import artistfilter
import gaia2.fastyaml as yaml
import utils.path
import tempfile
import logging
import shutil
#import time
import json
import os
import ast
import fileutils

SLEEP_DURATION = 30  # number of seconds to wait between runs
HISTORY_STORAGE_DIR = os.path.join(config.FILE_STORAGE_DIR, "history")


def main():
    logging.info("Starting dataset evaluator...")
    job = fileutils.get_job_details()
    if job:
        logging.info("Processing job %s..." % job["id"])
        evaluate_dataset(job)


def evaluate_dataset(eval_job):

    eval_location = os.path.join(os.path.abspath(config.DATASET_DIR), eval_job["id"])
    utils.path.create_path(eval_location)
    temp_dir = tempfile.mkdtemp()
    try:
        snapshot = {}
        snapshot['data'] = fileutils.create_snapshot(eval_job['dataset'])
        train, test = artistfilter.filter(snapshot, eval_job["options"])
        logging.info("Generating filelist.yaml and copying low-level data for evaluation...")
        filelist_path = os.path.join(eval_location, "filelist.yaml")
        filelist = dump_lowlevel_data(train.keys(), temp_dir)

        with open(filelist_path, "w") as f:
            yaml.dump(filelist, f)

        logging.info("Generating groundtruth.yaml...")
        groundtruth_path = os.path.join(eval_location, "groundtruth.yaml")
        with open(groundtruth_path, "w") as f:
            yaml.dump(create_groundtruth_dict(snapshot["data"]["name"], train), f)

        logging.info("Training model...")
        results = gaia_wrapper.train_model(
            project_dir=eval_location,
            groundtruth_file=groundtruth_path,
            filelist_file=filelist_path,
        )
        logging.info("Saving results...")
#        save_history_file(results["history_path"], eval_job["id"])
        logging.info("Evaluation job %s has been completed." % eval_job["id"])

    except:
        pass
    # TODO(roman): Also need to catch exceptions from Gaia.
#    except db.exceptions.DatabaseException as e:
#        logging.info("Evaluation job %s has failed!" % eval_job["id"])
#        db.dataset_eval.set_job_status(
#            job_id=eval_job["id"],
#            status=db.dataset_eval.STATUS_FAILED,
#            status_msg=str(e),
#        )
#        logging.info(e)

    finally:
        # Clean up the source files used to generate this model.
        # We can recreate them from the database if we need them
        # at a later stage.
        shutil.rmtree(temp_dir)


def create_groundtruth_dict(name, datadict):
    groundtruth = {
        "type": "unknown",  # TODO: See if that needs to be modified.
        "version": 1.0,
        "className": fileutils._slugify(unicode(name)),
        "groundTruth": {},
    }
    for r, cls in datadict.items():
        if isinstance(r, unicode):
            r = r.encode("UTF-8")
        groundtruth["groundTruth"][r] = cls.encode('UTF-8')
    return groundtruth


def create_groundtruth(dataset):
    groundtruth = {
        "type": "unknown",  # TODO: See if that needs to be modified.
        "version": 1.0,
        "className": db.dataset._slugify(unicode(dataset["name"])),
        "groundTruth": {},
    }
    for cls in dataset["classes"]:
        for recording_mbid in cls["recordings"]:
            groundtruth["groundTruth"][recording_mbid] = cls["name"].encode("UTF-8")
    return groundtruth


def dump_lowlevel_data(recordings, location):
    """Dumps low-level data for all recordings into specified location.

    Args:
        recordings: List of MBIDs of recordings.
        location: Path to directory where low-level data will be saved.

    Returns:
        Filelist.
    """
    utils.path.create_path(location)
    filelist = {}
    for recording in recordings:
        print(recording)
        filelist[recording] = os.path.join(location, "%s.yaml" % recording)
        print(filelist[recording])
        with open(filelist[recording], "w") as f:
            f.write(lowlevel_data_to_yaml(fileutils.load_low_level(recording)))
    return filelist


def lowlevel_data_to_yaml(data):
    """Prepares dictionary with low-level data about recording for processing
    and converts it into YAML string.
    """
    # Removing descriptors, that will otherwise break gaia_fusion due to
    # incompatibility of layouts (see Gaia implementation for more details).
    if "tags" in data["metadata"]:
        del data["metadata"]["tags"]
    if "sample_rate" in data["metadata"]["audio_properties"]:
        del data["metadata"]["audio_properties"]["sample_rate"]
    if 'lossless' in data['metadata']['audio_properties']:
        del data['metadata']['audio_properties']['lossless']

    return yaml.dump(data)


def extract_recordings(dataset):
    """Extracts set of recordings used in a dataset."""
    recordings = set()
    for cls in dataset["classes"]:
        for recording_mbid in cls["recordings"]:
            recordings.add(recording_mbid)
    return recordings


def save_history_file(history_file_path, job_id):
    directory = os.path.join(HISTORY_STORAGE_DIR, job_id[0:1], job_id[0:2])
    utils.path.create_path(directory)
    destination = os.path.join(directory, "%s.history" % job_id)
    shutil.copyfile(history_file_path, destination)
    return destination


if __name__ == "__main__":
    main()
