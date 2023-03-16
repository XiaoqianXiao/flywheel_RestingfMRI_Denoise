# flywheel_RestingfMRI_Denoise
The scrips for building the gear were mostly modified from [fmriprep flywheel gear](https://github.com/flywheel-apps/bids-fmriprep).
## Setup:
The RestingfMRI_Denoise using fMRIprep outputs as input. Before running RestingfMRI_Denoise, you must run fmripep first.
## Running:
To run the gear, select a project, subject or session.
Note it can run for 12 to 48 or more hours.
## Inputs:
>### pipelines: 
Name of pipelines used for denoising, can be both paths of json files with pipeline or file with name of pipelines from package.
<br />-An example of json file with pipeline is [here](https://github.com/XiaoXiaoqian/flywheel_RestingfMRI_Denoise/blob/main/docs/pipeline-ICA-AROMA_2Phys_1GS_spikes-FD5.json).
<br />-You can find a list of pipelines already set in the package [here](https://github.com/XiaoXiaoqian/flywheel_RestingfMRI_Denoise/blob/main/docs/pipelines).
>### api-key:
This will allow the gear to use the flywheel SDK using your api key, giving the gear all the same access permissions that your account has.
Please refer the [flywheel document](https://flywheel-io.gitlab.io/product/backend/sdk/branches/master/python/getting_started.html#api-key) for more info about the api-key.
<br />
## Config:
Two thing you can help to set in the Config session: 1)set some parameters for the tool, and 2)costomize your own denoise stratege. Please see more details below:
### set parameters for the tool
>### subjects
List of subjects you want to include, separated with spaces
>### pipelines_name
Pipeline names used for denoising from package
### costomize your own denoise stratege
>### use_custom_pipeline
check this one if you want to custom the denoise pipeline here. And then set the denoiseing parameters from below.
>### motion 
add motion or not
>### motion-temp_deriv
add motion temp_deriv or not
>###
>###
>### 
>### 
>###
>###
>###
>### 
>### 
>###
>###
>###
>### 
>### 
>###
>###
>###
"gear-dry-run": {
    "default": true,
    "description": "Do everything except actually executing the command line",
    "type": "boolean"
},


        "motion": {
            "default": false,
            "description": "add motion or not",
            "type": "boolean"
        },
        "motion-temp_deriv": {
            "default": false,
            "description": "add motion temp_deriv or not",
            "type": "boolean"
        },
        "motion-quad_terms": {
            "default": false,
            "description": "add motion quad_terms or not",
            "type": "boolean"
        },
        "wm": {
            "default": false,
            "description": "add white matter or not",
            "type": "boolean"
        },
        "wm-temp_deriv": {
            "default": false,
            "description": "add white matter temp_deriv or not",
            "type": "boolean"
        },
        "wm-quad_terms": {
            "default": false,
            "description": "add white matter quad_terms or not",
            "type": "boolean"
        },
        "csf": {
            "default": false,
            "description": "add csf or not",
            "type": "boolean"
        },
        "csf-temp_deriv": {
            "default": false,
            "description": "add csf temp_deriv or not",
            "type": "boolean"
        },
        "csf-quad_terms": {
            "default": false,
            "description": "add csf quad_terms or not",
            "type": "boolean"
        },
        "gs": {
            "default": false,
            "description": "add global signal or not",
            "type": "boolean"
        },
        "gs-temp_deriv": {
            "default": false,
            "description": "add global signal temp_deriv or not",
            "type": "boolean"
        },
        "gs-quad_terms": {
            "default": false,
            "description": "add global signal quad_terms or not",
            "type": "boolean"
        },
        "acompcor": {
            "default": false,
            "description": "add acompcor or not",
            "type": "boolean"
        },
        "aroma": {
            "default": false,
            "description": "add aroma or not",
            "type": "boolean"
        },
        "spikes": {
            "default": false,
            "description": "add spikes or not",
            "type": "boolean"
        },
        "fd_th": {
            "default": 0.5,
            "description": "framewise_displacement threshold, numeric which scans have fd greater thant it will be identified as outliers.",
            "type": "number"
        },
        "dvars_th": {
            "default": 3,
            "description": "std_dvars threshold, numeric which scans have std_dvars greater thant it will be identified as outliers.",
            "type": "number"
        }
