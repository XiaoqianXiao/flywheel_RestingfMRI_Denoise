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

log = logging.getLogger(__name__)

GEAR = "RestingfMRI_Denoise"
REPO = "xiaoqianxiao"
CONTAINER = Path(REPO).joinpath(GEAR)

BIDS_APP = "RestingfMRI_Denoise"

def generate_command(config, work_dir, output_analysis_id_dir, errors, warnings):
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
    cmd = [
        "/usr/bin/time",
        "-v",
        "--output=time_output.txt",
        BIDS_APP,
        os.path.join(work_dir, "bids"),
        str(output_analysis_id_dir),
        ANALYSIS_LEVEL
    ]

    # 3 positional args: bids path, output dir, 'participant'
    # This should be done here in case there are nargs='*' arguments
    # These follow the BIDS Apps definition (https://github.com/BIDS-Apps)

    # get parameters to pass to the command by skipping gear config parameters
    # (which start with "gear-") and singularity commands.
    skip_pattern = re.compile("gear-|lsf-|singularity-")

    command_parameters = {}
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

    FWV0 = Path.cwd()
    log.info("Running gear in %s", FWV0)

    gtk_context.log_config()

    # Errors and warnings will always be logged when they are detected.
    # Keep a list of errors and warning to print all in one place at end of log
    # Any errors will prevent the command from running and will cause exit(1)
    errors = []
    warnings = []

    output_dir = gtk_context.output_dir
    log.info("output_dir is %s", output_dir)
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

    # This is the label of the project, subject or session and is used
    # as part of the name of the output files.
    run_label = make_file_name_safe(hierarchy["run_label"])

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

    environ = get_and_log_environment()

    command = generate_command(
        config, work_dir, output_analysis_id_dir, errors, warnings
    )
    
    # zip entire output/<analysis_id> folder into
    #  <gear_name>_<project|subject|session label>_<analysis.id>.zip
    zip_file_name = gear_name + f"_{run_label}_{destination_id}.zip"
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
