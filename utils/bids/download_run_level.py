import os
def download_bids_for_runlevel(
    client,
    destination_id,
    gtk_context,
    hierarchy,
    work_dir):
    """Copy fmriprep processed output to working container.
    Args:
        hierarchy: the dictionary of the run level info
    """
    group_label = 'nolanw'
    project_label = hierarchy['project_label']
    subject = hierarchy['subject_label']
    session = hierarchy['session_label']
    acquisition = hierarchy['acquisition_label']
    run_level = hierarchy["run_level"]
    project_finder = 'group=' + group_label + ',label=' + project_label
    project = client.projects.find_one(project_finder)
    #run_level is in ["project", "subject", "session", "acquisition"]
    file_of_interest = 'fmriprep'
    fmriprep_dir = os.path.join(work_dir, "derivatives/fmriprep")
    zipFile_dir = os.path.join(work_dir, 'zip_files')
    config = gtk_context.config
    subjects_IDs = config['subjects']
    if subjects_IDs != "Not choose":
        subjects_of_interest = re.split(' ', subjects_IDs)
        
    #    command_parameters['subjects'] = subjects_IDs  
    if run_level == 'project':
        sessions = project.sessions()
        for s in sessions:
            sub_name = s.subject.label
            s_id = re.split('-', sub_name)[1]
            prep_list = []
            createdTime_list = []
            analyses = s.reload()['analyses']
            session_name = s.label
            subjects_of_interest = re.split(' ', subjects_IDs)
            if (subjects_IDs == "Not choose") or (s_id in subjects_of_interest):
                for a in analyses:
                    if a.gear_info:
                        if (file_of_interest in a.gear_info.name and a.files):
                            analysisID =  a._id
                            prep_list.append(a._id)
                            createdTime_list.append(a.created.strftime("%Y-%m-%d"))
                if len(prep_list) > 1:
                    latest_index = createdTime_list.index(max(createdTime_list))
                    analysisID = prep_list[latest_index]
                if prep_list:
                    print('start download sub-' + sub_name + '_session-' + session_name)
                    analysis = client.get(analysisID)
                    for f in analysis.files:
                        if file_of_interest in f.name:
                            output_file_name = os.path.join(zipFile_dir,f.name)
                            if not os.path.exists(output_file_name):
                                   f.download(output_file_name)
                                   
    else:
        destination = client.get(destination_id)
        container = client.get(destination.parents[run_level])
        s = container
        analyses = s.reload()['analyses']
        prep_list = []
        createdTime_list = []
        for a in analyses:
            if a.gear_info:
                if (file_of_interest in a.gear_info.name and a.files):
                    analysisID =  a._id
                    prep_list.append(a._id)
                    createdTime_list.append(a.created.strftime("%Y-%m-%d"))
            if len(prep_list) > 1:
                latest_index = createdTime_list.index(max(createdTime_list))
                analysisID = prep_list[latest_index]
            if prep_list:
                analysis = client.get(analysisID)
                for f in analysis.files:
                    if file_of_interest in f.name:
                        output_file_name = os.path.join(zipFile_dir,f.name)
                        if not os.path.exists(output_file_name):
                               f.download(output_file_name)
                            
def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]
