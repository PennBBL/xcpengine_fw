#!/usr/bin/env python
import json
import flywheel
import os
import shutil
import logging
from fw_heudiconv.cli import curate, export, tabulate
from fw_heudiconv.backend_funcs.query import print_directory_tree


# logging stuff
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fw-heudiconv-gear')
logger.info("=======: fw-heudiconv starting up :=======")

# start up inputs
invocation = json.loads(open('config.json').read())
config = invocation['config']
inputs = invocation['inputs']
destination = invocation['destination']

fw = flywheel.Flywheel(inputs['api_key']['key'])
user = fw.get_current_user()

# start up logic:
heuristic = None #inputs['heuristic']['location']['path']
analysis_container = fw.get(destination['id'])
project_container = fw.get(analysis_container.parents['project'])
project_label = project_container.label
dry_run = False #config['dry_run']
action = "Export" #config['action']
use_all_sessions = config['use_all_sessions']

# is there a separate t1/t2?
if 't1w_anatomy' in inputs:
    logger.info("Prepping seperate T1w image...")
    t1_acq = fw.get(inputs['t1w_anatomy']['hierarchy']['id'])
else:
    t1_acq = None

if 't2w_anatomy' in inputs:
    logger.info("Prepping separate T2w image...")
    t2_acq = fw.get(inputs['t2w_anatomy']['hierarchy']['id'])
else:
    t2_acq = None

# whole project, single session?
do_whole_project = False #config['do_whole_project']

if not do_whole_project:

    if not use_all_sessions:

        # find session object origin
        session_container = fw.get(analysis_container.parent['id'])
        sessions = [session_container.label]
        # find subject object origin
        subject_container = fw.get(session_container.parents['subject'])
        subjects = [subject_container.label]

    else:

        session_container = fw.get(analysis_container.parent['id'])
        sessions = None
        subject_container = fw.get(session_container.parents['subject'])
        subjects = [subject_container.label]

else:
    sessions = None
    subjects = None

# logging stuff
logger.info("Running fw-heudiconv with the following settings:")
logger.info("Project: {}".format(project_label))
logger.info("Subject(s): {}".format(subjects))
logger.info("Session(s): {}".format(sessions))
#logger.info("Heuristic found at: {}".format(heuristic))
logger.info("Action: {}".format(action))
logger.info("Dry run: {}".format(dry_run))

# action
if action == "Curate":
    print("fMRIPREP isn't designed for BIDS Curation!")
    #curate.convert_to_bids(fw, project_label, heuristic, subjects, sessions, dry_run=dry_run)

elif action == "Export":

    downloads = export.gather_bids(fw, project_label, subjects, sessions)
    export.download_bids(fw, downloads, "/flywheel/v0/output", dry_run=dry_run)

    if t1_acq:
        logger.info("Adding additional T1w folder...")

        nifti = [f for f in t1_acq.files if '.nii' in f.name].pop()
        path = nifti.info['BIDS']['Path']
        path = "/flywheel/v0/output/bids_dataset/" + path
        fname = nifti.info['BIDS']['Filename']
        sidecar = nifti.info

        if not os.path.exists(path):
            os.makedirs(path)

        if os.path.isfile("/".join([path, fname])):
            logger.info("Overwriting current T1w image...")
            os.remove("/".join([path, fname]))
        t1_acq.download_file(nifti.name, "/".join([path, fname]))

        sidecar_name = fname.replace('.nii.gz', '.json')
        if os.path.isfile(path + sidecar_name):
            os.remove(path + sidecar_name)
        export.download_sidecar(sidecar, "/".join([path, sidecar_name]))

    if t2_acq:
        logger.info("Adding additional T2w folder...")

        nifti = [f for f in t2_acq.files if '.nii' in f.name].pop()
        path = nifti.info['BIDS']['Path']
        path = "/flywheel/v0/output/bids_dataset/" + path
        fname = nifti.info['BIDS']['Filename']
        sidecar = nifti.info

        if not os.path.exists(path):
            os.makedirs(path)

        if os.path.isfile("/".join([path, fname])):
            logger.info("Overwriting current T2w image...")
            os.remove("/".join([path, fname]))
        t2_acq.download_file(nifti.name, "/".join([path, fname]))

        sidecar_name = fname.replace('.nii.gz', '.json')
        if os.path.isfile(path + sidecar_name):
            os.remove(path + sidecar_name)
        export.download_sidecar(sidecar, "/".join([path, sidecar_name]))

    if t1_acq or t2_acq:
        logger.info("Final directory tree with additional anatomical files:")
        print_directory_tree("/flywheel/v0/output/bids_dataset")

    if not dry_run:
        pass
        # tidy up
        # output_dir = "/flywheel/v0/output"
        # os.system("zip -r {}_BIDSexport.zip output/*".format(destination['id']))
        # os.system("mv *.zip output")
        # to_remove = os.listdir(output_dir)
        # to_remove = ["{}/{}".format(output_dir, x) for x in to_remove if ".zip" not in x]
        # for x in to_remove:
        #     if os.path.isfile(x):
        #         os.remove(x)
        #     else:
        #         shutil.rmtree(x)

elif action == "Tabulate":
    print("fMRIPREP isn't designed for BIDS Tabulation!")
    #tabulate.tabulate_bids(fw, project_label, "/flywheel/v0/output", subjects, sessions, dry_run=dry_run)

else:

    raise Exception('Action not specified correctly!')
