#!/usr/bin/env python3
"""Run the gear: set up for and call command-line command."""
import json
import logging
import os
import re
import shutil
import sys
from pathlib import Path
import json

import flywheel_gear_toolkit
from flywheel_gear_toolkit.interfaces.command_line import (
    build_command_list,
    exec_command,
)
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive, zip_output
from utils.fly.environment import get_and_log_environment
from utils.bids.download_run_level import download_bids_for_runlevel, walklevel
from utils.bids.run_level import get_analysis_run_level_and_hierarchy
from utils.singularity import run_in_tmp_dir

log = logging.getLogger(__name__)
GEAR = "RestingfMRI_Denoising"
REPO = "xiaoqianxiao"
CONTAINER = Path(REPO).joinpath(GEAR)
BIDS_APP = "RestingfMRI_Denoise"
# What level to run at (positional_argument #3)
ANALYSIS_LEVEL = "project"

def generate_command(gtk_context, config, work_dir, output_analysis_id_dir, errors):
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
        str(work_dir),
    ]

    # get parameters to pass to the command by skipping gear config parameters
    # (which start with "gear-") and singularity commands.
    skip_pattern = re.compile("gear-|lsf-|singularity-")
    command_parameters = {}
    ##
    pipelines_file_path = gtk_context.get_input_path("pipelines")
    if pipelines_file_path is not None:
        paths = list(Path("input/pipelines").glob("*"))
        command_parameters['pipelines'] = paths[0]
    log_to_file = False
    config_keys = config.keys()
    if 'use_custom_pipline' in config_keys:
        use_custom_pipline = config['use_custom_pipline']
        pipeline_json_dict = {}
        if use_custom_pipline is not None:
            pipeline_json_dict['name'] = config['name']
            pipeline_json_dict['description'] = config['description']
            for k in ["wm", "csf", "gs", "motion"]:
                key_temp_deriv = k + '-temp_deriv'
                key_quad_terms = k + '-quad_terms'
                if config[k] == "fasle":
                    pipeline_json_dict["confounds"][k] = "False"
                else:
                    pipeline_json_dict["confounds"][k]["temp_deriv"] = config[key_temp_deriv]
                    pipeline_json_dict["confounds"][k]["quad_terms"] = config[key_quad_terms]
            pipeline_json_dict["confounds"]["acompcor"] = config["acompcor"]
            pipeline_json_dict["aroma"] = config["aroma"]
            if config["spikes"] == "false":
                pipeline_json_dict["spikes"] = "False"
            else:
                pipeline_json_dict["fd_th"] = config["fd_th"]
                pipeline_json_dict["dvars_th"] = config["dvars_th"]
            json_object = json.dumps(pipeline_json_dict, indent = 4)      
            command_parameters['pipelines'] = json_object
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
    environ = get_and_log_environment()
    
    # Get output directory and put it into log
    output_dir = gtk_context.output_dir
    log.info("output_dir is %s", output_dir)
    # Get output directory and put it into log
    work_dir = gtk_context.work_dir
    log.info("work_dir is %s", work_dir)
    
    gear_name = gtk_context.manifest["name"]
    # run-time configuration options from the gear's context.json
    config = gtk_context.config
    
    import json
    data = {}
    data['name'] = config.get("name")
    data['description'] = config.get("description")
    
    json_data = json.dumps(data)

    # Given the destination container, figure out if running at the project,
    # subject, or session level.
    destination_id = gtk_context.destination["id"]
    print(destination_id)
    hierarchy = get_analysis_run_level_and_hierarchy(gtk_context.client, destination_id)
    print(hierarchy)

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
        gtk_context, config, work_dir, output_analysis_id_dir, errors
    )

    # Download fmriprep results as the input of the gear
    fmriprep_dir = os.path.join(work_dir, "derivatives/fmriprep")
    zipFile_dir = os.path.join(fmriprep_dir, 'zip_files')
    isExist = os.path.exists(zipFile_dir)
    if not isExist:
       os.makedirs(zipFile_dir)
    
    unzipFile_dir = os.path.join(fmriprep_dir, 'unzipped_files') 
    isExist = os.path.exists(unzipFile_dir)
    if not isExist:
       os.makedirs(unzipFile_dir)
    if len(errors) == 0:
        download_bids_for_runlevel(
            gtk_context.client,
            destination_id,
            gtk_context,
            hierarchy,
            work_dir
        )
        # un-zip fmriprep output and re-orgernize.
        import zipfile
        import re
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
                        shutil.move(os.path.join(root,filename), os.path.join(fmriprep_dir,re.split('/',root)[-1],filename))
        if os.path.isfile(os.path.join(root,'dataset_description.json')):
            shutil.move(os.path.join(root,'dataset_description.json'), fmriprep_dir)
    else:
        log.info("Did not download fmriprep because of previous errors")
        print(errors)
        
    num_tries = 0
    if len(errors) > 0:
        num_tries == 2  # don't try to run
    while num_tries < 2:
        try:
            num_tries += 1
            if num_tries > 1:
                log.info("Trying a second time")          
                # this is all about it    
                exec_command(
                            command,
                            environ=environ,
                            shell=True
                        )
                break
        except RuntimeError as exc:
            if num_tries == 2:
                return_code = 1
            errors.append(exc)
            log.critical(exc)
            log.exception("Unable to execute command.")

            os.system("echo ")
            os.system("echo Disk Information on Failure")
            os.system("df -h")
             
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
        
     if len(errors) > 0:
        msg = "Previous errors:\n"
        for err in errors:
            if str(type(err)).split("'")[1] == "str":
                # show string
                msg += "  Error msg: " + str(err) + "\n"
            else:  # show type (of error) and error message
                err_type = str(type(err)).split("'")[1]
                msg += f"  {err_type}: {str(err)}\n"
        log.info(msg)

    if num_tries == 1:
        log.info("Happily, RestingfMRI_Denoise worked on the first try.")
    else:
        msg = (
            "first try but it did on the second"
            if return_code == 0
            else "first or second try"
        )
        log.info("Sadly, RestingfMRI_Denoise did not work on the %s.", msg)

    log.info("%s Gear is done.  Returning %s", CONTAINER, return_code)
    return return_code

if __name__ == "__main__":
    with flywheel_gear_toolkit.GearToolkitContext() as gtk_context:
        return_code = main(gtk_context)
    sys.exit(return_code)
