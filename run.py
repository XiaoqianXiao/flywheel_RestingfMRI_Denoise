#!/usr/bin/env python3
"""Run the gear: set up for and call command-line command."""
import json
import logging
import os
import re
import shutil
import sys
from pathlib import Path

import flywheel_gear_toolkit
from flywheel_gear_toolkit.interfaces.command_line import (
    build_command_list,
    exec_command,
)
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive, zip_output

from utils.bids.download_run_level import download_bids_for_runlevel
from utils.bids.run_level import get_analysis_run_level_and_hierarchy

log = logging.getLogger(__name__)
GEAR = "RestingfMRI_Denoising"
REPO = "xiaoqianxiao"
CONTAINER = Path(REPO).joinpath(GEAR)
BIDS_APP = "RestingfMRI_Denoising"
# What level to run at (positional_argument #3)
ANALYSIS_LEVEL = "project"

def generate_command(gtk_context, config, work_dir, output_analysis_id_dir, errors, warnings):
    """Build the main command line command to run.
    Args:
        config (GearToolkitContext.config): run-time options from config.json
        work_dir (path): scratch directory where non-saved files can be put
        output_analysis_id_dir (path): directory where output will be saved
        errors (list of str): error messages
        warnings (list of str): warning messages
    Returns:
        cmd (list of str): command to execute
    """
    # start with the command itself:
    # 3 positional args: bids path, output dir, ANALYSIS_LEVEL
    # This should be done here in case there are nargs='*' arguments
    # These follow the BIDS Apps definition (https://github.com/BIDS-Apps)
    cmd = [
        BIDS_APP,
        os.path.join(work_dir, "bids"),
    ]

    # get parameters to pass to the command by skipping gear config parameters
    # (which start with "gear-") and singularity commands.
    skip_pattern = re.compile("gear-|lsf-|singularity-")
    command_parameters = {}
    ##
    pipelines_file_path = gtk_context.get_input_path("pipelines")
    if pipelines_file_path:
        paths = list(Path("input/pipelines").glob("*"))
        command_parameters['pipelines'] = paths[0]
    log_to_file = False
    for key, val in config.items():
        # these arguments are passed directly to the command as is
        if key == "bids_app_args":
            bids_app_args = val.split(" ")
            for baa in bids_app_args:
                cmd.append(baa)
        elif not skip_pattern.match(key):
            command_parameters[key] = val

    # Validate the command parameter dictionary - make sure everything is
    # ready to run so errors will appear before launching the actual gear
    # code.  Add descriptions of problems to errors & warnings lists.
    # print("command_parameters:", json.dumps(command_parameters, indent=4))
    cmd = build_command_list(cmd, command_parameters)
    for ii, cc in enumerate(cmd):
        if cc.startswith("--verbose"):
            # handle a 'count' argparse argument where manifest gives
            # enumerated possibilities like v, vv, or vvv
            # e.g. replace "--verbose=vvv' with '-vvv'
            cmd[ii] = "-" + cc.split("=")[1]
        elif " " in cc:  # then is is a space-separated list so take out "="
            # this allows argparse "nargs" to work properly
            cmd[ii] = cc.replace("=", " ")

    log.info("command is: %s", str(cmd))
    return cmd

def main(gtk_context):
    # Get current working directory
    FWV0 = Path.cwd()
    # Put current working directory into log
    log.info("Running gear in %s", FWV0)
    gtk_context.log_config()

    # Errors and warnings will always be logged when they are detected.
    # Keep a list of errors and warning to print all in one place at end of log
    # Any errors will prevent the command from running and will cause exit(1)
    errors = []
    warnings = []

    # Get output directory and put it into log
    output_dir = gtk_context.output_dir
    log.info("output_dir is %s", output_dir)
    # Get output directory and put it into log
    work_dir = gtk_context.work_dir
    log.info("work_dir is %s", work_dir)
    
    gear_name = gtk_context.manifest["name"]
    # run-time configuration options from the gear's context.json
    config = gtk_context.config
    dry_run = config.get("gear-dry-run")

    # Given the destination container, figure out if running at the project,
    # subject, or session level.
    destination_id = gtk_context.destination["id"]
    hierarchy = get_analysis_run_level_and_hierarchy(gtk_context.client, destination_id)

    # Output will be put into a directory named as the destination id.
    # This allows the raw output to be deleted so that a zipped archive
    # can be returned.
    output_analysis_id_dir = output_dir / destination_id
    log.info("Creating output directory %s", output_analysis_id_dir)
    if Path(output_analysis_id_dir).exists():
        log.info(
            "Not actually creating output directory %s because it exists.  This must be a test",
            output_analysis_id_dir,
        )
    else:
        Path(output_analysis_id_dir).mkdir()
            
    command = generate_command(
        config, work_dir, output_analysis_id_dir, errors, warnings
    )

    # Download fmriprep results as the input of the gear
    if len(errors) == 0:
        download_bids_for_runlevel(
            gtk_context,
            hierarchy,
            output_dir
        )
        # un-zip fmriprep output and re-orgernize.
        import os, zipfile
        import re
        fmripep_dir = os.path.join(work_dir, "bids")
        zipFile_dir = os.path.join(fmripep_dir, 'zip_files')
        unzipFile_dir = os.path.join(fmripep_dir, 'unzipped_files')  
        extension = ".zip"
        for item in os.listdir(zipFile_dir): # loop through items in dir
            if item.endswith(extension): # check for ".zip" extension
                file_name = os.path.abspath(item) # get full path of files
                zip_ref = zipfile.ZipFile(file_name) # create zipfile object
                zip_ref.extractall(unzipFile_dir) # extract file to dir
                zip_ref.close() # close file
                os.remove(file_name) # delete zipped file
        for root, dirs, files in walklevel(unzipFile_dir, level=3):
            if ('fmriprep' in root.split('/') and 'sub' in re.split('/|-',root)):
                for filename in os.listdir(root):
                    if 'ses' in filename.split('-'):
                        shutil.move(os.path.join(root,filename), os.path.join(fmripep_dir,re.split('/',root)[-1],filename))
        shutil.move(os.path.join(root,'dataset_description.json'), fmripep_dir)
    else:
        log.info("Did not download fmriprep because of previous errors")
        print(errors)
    # this is all about it    
    exec_command(
                command
            )
    # zip entire output/<analysis_id> folder into <gear_name>_<analysis.id>.zip
    zip_file_name = gear_name + f"_{destination_id}.zip"
    zip_output(
        str(output_dir),
        destination_id,
        zip_file_name,
        dry_run=False,
        exclude_files=None,
    )
    # clean up: remove output that was zipped
    if Path(output_analysis_id_dir).exists():
        if not config.get("gear-keep-output"):

            log.debug('removing output directory "%s"', str(output_analysis_id_dir))
            shutil.rmtree(output_analysis_id_dir)

        else:
            log.info('NOT removing output directory "%s"', str(output_analysis_id_dir))

    else:
        log.info("Output directory does not exist so it cannot be removed")
    return return_code

if __name__ == "__main__":
    # make sure /flywheel/v0 is writable, use a scratch directory if not
    with flywheel_gear_toolkit.GearToolkitContext() as gtk_context:
        scratch_dir = run_in_tmp_dir(gtk_context.config["gear-writable-dir"])
    # Has to be instantiated twice here, since parent directories might have
    # changed
    with flywheel_gear_toolkit.GearToolkitContext() as gtk_context:
        return_code = main(gtk_context)
    # clean up (might be necessary when running in a shared computing environment)
    if scratch_dir:
        log.debug("Removing scratch directory")
        for thing in scratch_dir.glob("*"):
            if thing.is_symlink():
                thing.unlink()  # don't remove anything links point to
                log.debug("unlinked %s", thing.name)
        shutil.rmtree(scratch_dir)
        log.debug("Removed %s", scratch_dir)
    sys.exit(return_code)
