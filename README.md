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
List of subjects you want to include, separated with space
>### pipelines_name
Pipeline names used for denoising from package
### costomize your own denoise stratege
>### use_custom_pipeline
check this one if you want to custom the denoise pipeline here. And then set the denoiseing parameters from below.
>### motion 
add motion or not
>### motion-temp_deriv
add motion temp_deriv or not
>### motion-quad_terms
add motion quad_terms or not
>### wm
add white matter or not
>### wm-temp_deriv
add white matter temp_deriv or not
>### wm-quad_terms
add white matter quad_terms or not
>### csf
add csf or not
>### csf-temp_deriv
add csf temp_deriv or not
>### csf-quad_terms
add csf quad_terms or not
>### gs
add global signal or not 
>### gs-temp_deriv
add global signal temp_deriv or not 
>### gs-quad_terms
add global signal quad_terms or not
>### acompcor
add acompcor or not
>### aroma
add aroma or not
>### spikes
add spikes or not; if yes you can choice either use
>#### fd_th
framewise_displacement threshold, numeric which scans have fd greater thant it will be identified as outliers
<br />
or 
>#### dvars_th
std_dvars threshold, numeric which scans have std_dvars greater thant it will be identified as outliers.

"gear-dry-run": {
    "default": true,
    "description": "Do everything except actually executing the command line",
    "type": "boolean"
},


  
