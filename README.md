# flywheel_RestingfMRI_Denoise
Modified from [fmriprep flywheel gear](https://github.com/flywheel-apps/bids-fmriprep).
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
