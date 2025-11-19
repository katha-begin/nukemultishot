=======================================================
Error
=======================================================
The user 'katha.nab' does not exist

=======================================================
Type
=======================================================
Exception

=======================================================
Stack Trace
=======================================================
   at FranticX.Interop.libc.GetUserId(String username)
   at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive)
   at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe)
   at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser)
   at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser)
   at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser)
   at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh)
   at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc)
   at Deadline.Slaves.SlaveRenderThread.a()

=======================================================
Log
=======================================================
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Merge2.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Multiply.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Crop.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/pngReader.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Transform.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Camera3.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/abcSceneReader.so
2025-11-19 13:52:20:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ReadGeo2.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/abcReader.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Scene.tcl
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/MergeGeo.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Constant.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Cylinder.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Sphere.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ColorCorrect.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ScanlineRender.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/OCIODisplay.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/exrWriter.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Invert.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Radial.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Denoise2.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/EXPTool.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/BlinkScript.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/CopyBBox.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Ramp.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ColorLookup.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Clamp.so
2025-11-19 13:52:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Colorspace.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Dilate.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ColorMatrix.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Add.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/AdjBBox.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/NodeWrapper.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/EdgeBlur.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Axis2.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/FilterErode.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Gamma.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/IDistort.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Keymix.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Dissolve.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ZDefocus2.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Glint.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/LightWrap.gizmo
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Keyer.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/CCorrect.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/HueCorrect.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ContactSheet.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Mirror2.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/LayerContactSheet.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/pngWriter.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Cryptomatte.so
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/jpgReader.tcl
2025-11-19 13:52:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/jpegReader.so
2025-11-19 13:52:21:  0: STDOUT: [13:52:21 UTC] Read nuke script: /var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/jobsData/691dcb454c1fd3ab7085ff79/thread0_tempjNbrb0/Ep03_sq0060_SH0180_comp_v004.nk
2025-11-19 13:52:21:  0: STDOUT: ================================================================================
2025-11-19 13:52:21:  0: STDOUT: MULTISHOT DEBUG: Printing ALL root knobs
2025-11-19 13:52:21:  0: STDOUT: ================================================================================
2025-11-19 13:52:21:  0: STDOUT: Total knobs on root: 61
2025-11-19 13:52:21:  0: STDOUT: Multishot JSON knobs:
2025-11-19 13:52:21:  0: STDOUT:   multishot_context = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   multishot_custom = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   multishot_variables = MISSING!
2025-11-19 13:52:21:  0: STDOUT: Individual variable knobs:
2025-11-19 13:52:21:  0: STDOUT:   ep = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   seq = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   shot = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   project = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   PROJ_ROOT = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   IMG_ROOT = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   first_frame = '1.0'
2025-11-19 13:52:21:  0: STDOUT:   last_frame = '100.0'
2025-11-19 13:52:21:  0: STDOUT: ================================================================================
2025-11-19 13:52:21:  0: STDOUT: Multishot: Manually creating individual knobs from JSON...
2025-11-19 13:52:21:  0: STDOUT: Multishot: Variables initialized in batch mode
2025-11-19 13:52:21:  0: STDOUT: ================================================================================
2025-11-19 13:52:21:  0: STDOUT: ================================================================================
2025-11-19 13:52:21:  0: STDOUT: MULTISHOT DEBUG: Printing ALL root knobs
2025-11-19 13:52:21:  0: STDOUT: ================================================================================
2025-11-19 13:52:21:  0: STDOUT: Total knobs on root: 61
2025-11-19 13:52:21:  0: STDOUT: Multishot JSON knobs:
2025-11-19 13:52:21:  0: STDOUT:   multishot_context = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   multishot_custom = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   multishot_variables = MISSING!
2025-11-19 13:52:21:  0: STDOUT: Individual variable knobs:
2025-11-19 13:52:21:  0: STDOUT:   ep = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   seq = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   shot = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   project = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   PROJ_ROOT = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   IMG_ROOT = MISSING!
2025-11-19 13:52:21:  0: STDOUT:   first_frame = '1.0'
2025-11-19 13:52:21:  0: STDOUT:   last_frame = '100.0'
2025-11-19 13:52:21:  0: STDOUT: ================================================================================
2025-11-19 13:52:21:  0: STDOUT: Multishot: Manually creating individual knobs from JSON...
2025-11-19 13:52:21:  0: STDOUT: Multishot: Variables initialized in batch mode
2025-11-19 13:52:21:  0: STDOUT: ================================================================================
2025-11-19 13:52:21:  0: STDOUT: >>> [13:52.21] ERROR: MultishotRead_lighting_MASTER_ATMOS_A: [value root.IMG_ROOT][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.MultishotRead_lighting_MASTER_ATMOS_A.shot_version]/MASTER_ATMOS_A/MASTER_ATMOS_A.%04d.exr: Read error: No such file or directory
2025-11-19 13:52:21:  0: Done executing plugin command of type 'Render Task'
2025-11-19 13:52:21:  0: Executing plugin command of type 'End Job'
2025-11-19 13:52:21:  0: DEBUG: EndJob: called
2025-11-19 13:52:21:  0: INFO: Ending Nuke Job
2025-11-19 13:52:21:  0: DEBUG: EndJob: returning
2025-11-19 13:52:21:  0: Done executing plugin command of type 'End Job'
2025-11-19 13:52:24:  Scheduler Thread - Render Thread 0 threw a major error: 
2025-11-19 13:52:24:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 13:52:24:  Exception Details
2025-11-19 13:52:24:  RenderPluginException -- Error: >>> [13:52.21] ERROR: MultishotRead_lighting_MASTER_ATMOS_A: [value root.IMG_ROOT][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.MultishotRead_lighting_MASTER_ATMOS_A.shot_version]/MASTER_ATMOS_A/MASTER_ATMOS_A.%04d.exr: Read error: No such file or directory
2025-11-19 13:52:24:     at Deadline.Plugins.PluginWrapper.RenderTasks(Task task, String& outMessage, AbortLevel& abortLevel)
2025-11-19 13:52:24:  RenderPluginException.Cause: JobError (2)
2025-11-19 13:52:24:  RenderPluginException.Level: Major (1)
2025-11-19 13:52:24:  RenderPluginException.HasSlaveLog: True
2025-11-19 13:52:24:  RenderPluginException.SlaveLogFileName: /var/log/Thinkbox/Deadline10/deadlineslave_renderthread_0-ip-10-100-136-98-0000.log
2025-11-19 13:52:24:  Exception.TargetSite: Deadline.Slaves.Messaging.PluginResponseMemento d(Deadline.Net.DeadlineMessage, System.Threading.CancellationToken)
2025-11-19 13:52:24:  Exception.Data: ( )
2025-11-19 13:52:24:  Exception.Source: deadline
2025-11-19 13:52:24:  Exception.HResult: -2146233088
2025-11-19 13:52:24:    Exception.StackTrace: 
2025-11-19 13:52:24:     at Deadline.Plugins.SandboxedPlugin.d(DeadlineMessage bgz, CancellationToken bha
2025-11-19 13:52:24:     at Deadline.Plugins.SandboxedPlugin.RenderTask(Task task, CancellationToken cancellationToken
2025-11-19 13:52:24:     at Deadline.Slaves.SlaveRenderThread.c(TaskLogWriter akd, CancellationToken ake)
2025-11-19 13:52:24:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 13:52:26:  Skipping pending job scan because it is not required at this time
2025-11-19 13:52:26:  Skipping repository repair because it is not required at this time
2025-11-19 13:52:26:  Skipping house cleaning because it is not required at this time
2025-11-19 13:52:26:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 13:52:27:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 13:52:27:  0: SandboxedPlugin: Render Job As User disabled, running as current user 'rocky'
2025-11-19 13:52:28:  All job files are already synchronized
2025-11-19 13:52:28:  Plugin Nuke was already synchronized.
2025-11-19 13:52:28:  0: Executing plugin command of type 'Initialize Plugin'
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: debug logging enabled
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: m_pluginParamFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dcb454c1fd3ab7085ff79/Nuke.param'
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: m_pluginScriptFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dcb454c1fd3ab7085ff79/Nuke.py'
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: m_pluginPreLoadFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dcb454c1fd3ab7085ff79/PluginPreLoad.py'
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: m_jobPreLoadFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dcb454c1fd3ab7085ff79/JobPreLoad.py'
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: Checking for Plugin Pre-Load
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: Loading Plugin...
2025-11-19 13:52:28:  0: INFO: Executing plugin script '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dcb454c1fd3ab7085ff79/Nuke.py'
2025-11-19 13:52:28:  0: INFO: Plugin execution sandbox using Python version 3
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: getting job user
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: setting job filenames
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: Obtaining Deadline plugin object
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: Setting internal variables and delegates
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: Preparing Environment Variables
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: Obtaining network settings
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: Initializing Deadline plugin
2025-11-19 13:52:28:  0: DEBUG: This is an advanced plugin job.
2025-11-19 13:52:28:  0: INFO: About: Nuke Plugin for Deadline
2025-11-19 13:52:28:  0: INFO: The job's environment will be merged with the current environment before rendering
2025-11-19 13:52:28:  0: DEBUG: InitializePlugin: returning
2025-11-19 13:52:28:  0: Done executing plugin command of type 'Initialize Plugin'
2025-11-19 13:52:28:  0: Start Job timeout is disabled.
2025-11-19 13:52:28:  0: Task timeout is disabled.
2025-11-19 13:52:28:  0: Loaded job: Ep03_sq0060_SH0180_comp_v004.nk (691dcb454c1fd3ab7085ff79)
2025-11-19 13:52:28:  0: Executing plugin command of type 'Start Job'
2025-11-19 13:52:28:  0: DEBUG: StartJob: called
2025-11-19 13:52:28:  0: DEBUG: StartJob: Checking for Job Pre-Load
2025-11-19 13:52:28:  0: DEBUG: S3BackedCache Client is not installed.
2025-11-19 13:52:28:  0: DEBUG: GlobalAssetTransferPreLoadJob: called
2025-11-19 13:52:28:  0: INFO: Executing global asset transfer preload script '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dcb454c1fd3ab7085ff79/GlobalAssetTransferPreLoad.py'
2025-11-19 13:52:29:  0: INFO: Looking for legacy (pre-10.0.26) AWS Portal File Transfer...
2025-11-19 13:52:29:  0: INFO: Looking for legacy (pre-10.0.26) File Transfer controller in /opt/Thinkbox/S3BackedCache/bin/task.py...
2025-11-19 13:52:29:  0: INFO: Could not find legacy (pre-10.0.26) AWS Portal File Transfer.
2025-11-19 13:52:29:  0: INFO: Legacy (pre-10.0.26) AWS Portal File Transfer is not installed on the system.
2025-11-19 13:52:29:  0: DEBUG: GlobalAssetTransferPreLoadJob: returning
2025-11-19 13:52:29:  0: DEBUG: StartJob: Starting Job...
2025-11-19 13:52:29:  0: INFO: Scrubbing the LD and DYLD LIBRARY paths
2025-11-19 13:52:29:  0: INFO: Prepping OFX cache
2025-11-19 13:52:29:  0: INFO: Checking Nuke temp path: /var/tmp/nuke-u1000
2025-11-19 13:52:29:  0: INFO: Path already exists
2025-11-19 13:52:29:  0: INFO: OFX cache prepped
2025-11-19 13:52:29:  0: INFO: Starting monitored managed process Nuke
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped "V:/SWA/all/scene/Ep03/sq0060/SH0180/comp/version/Ep03_sq0060_SH0180_comp_v004.nk" with "/mnt/igloo_swa_v/SWA/all/scene/Ep03/sq0060/SH0180/comp/version/Ep03_sq0060_SH0180_comp_v004.nk"
2025-11-19 13:52:29:  0: INFO: Enable Path Mapping: True
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " name V:/SWA/all/scene/Ep03/sq0060/SH0180/comp/version/Ep03_sq0060_SH0180_comp_v004.nk
2025-11-19 13:52:29:  0: " with " name /mnt/igloo_swa_v/SWA/all/scene/Ep03/sq0060/SH0180/comp/version/Ep03_sq0060_SH0180_comp_v004.nk
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " project_directory V:/SWA/all/scene/Ep00/sq0010/SH0060/comp/version
2025-11-19 13:52:29:  0: " with " project_directory /mnt/igloo_swa_v/SWA/all/scene/Ep00/sq0010/SH0060/comp/version
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " customOCIOConfigPath T:/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio
2025-11-19 13:52:29:  0: " with " customOCIOConfigPath /mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " multishot_custom "\{\n  \"PROJ_ROOT\": \"V:/\",\n  \"IMG_ROOT\": \"W:/\",\n  \"element\": \"beauty\",\n  \"frame\": \"####\",\n  \"ext\": \"exr\"\n\}"
2025-11-19 13:52:29:  0: " with " multishot_custom "\{\n  \"PROJ_ROOT\": \"/mnt/igloo_swa_v/\",\n  \"IMG_ROOT\": \"W:/\",\n  \"element\": \"beauty\",\n  \"frame\": \"####\",\n  \"ext\": \"exr\"\n\}"
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " PROJ_ROOT V:/
2025-11-19 13:52:29:  0: " with " PROJ_ROOT /mnt/igloo_swa_v/
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " IMG_ROOT W:/
2025-11-19 13:52:29:  0: " with " IMG_ROOT /mnt/igloo_swa_w/
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " addUserKnob {26 snow__retarget_from l "Retargeted From" T V:/SWA/all/scene/Ep00/sq0010/SH0020/comp/version/Ep00_sq0010_SH0020_comp_comp_v002.nk}
2025-11-19 13:52:29:  0: " with " addUserKnob {26 snow__retarget_from l "Retargeted From" T /mnt/igloo_swa_v/SWA/all/scene/Ep00/sq0010/SH0020/comp/version/Ep00_sq0010_SH0020_comp_comp_v002.nk}
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_grass.png
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_grass.png
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_Buildings.png
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_Buildings.png
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/all/scene/Ep02/sq0010/SH0010/anim/publish/v001/Ep02_sq0010_SH0010__SWA_Ep02_SH0010_camera.abc
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/anim/publish/v001/Ep02_sq0010_SH0010__SWA_Ep02_SH0010_camera.abc
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/all/asset/Setdress/exterior/PGExtGroundHill/hero/PGExtGroundHill_geo.abc
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/all/asset/Setdress/exterior/PGExtGroundHill/hero/PGExtGroundHill_geo.abc
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/all/asset/Setdress/exterior/PGExtGround/hero/PGExtGround_geo.abc
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/all/asset/Setdress/exterior/PGExtGround/hero/PGExtGround_geo.abc
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_clouds.png
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_clouds.png
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_Buildings.png
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_Buildings.png
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_clouds.png
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_clouds.png
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_sky.png
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_sky.png
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_01_V1.jpg
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_01_V1.jpg
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_02_V1.jpg
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_02_V1.jpg
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: CheckPathMapping: Swapped " file V:/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_03_V1.jpg
2025-11-19 13:52:29:  0: " with " file /mnt/igloo_swa_v/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_03_V1.jpg
2025-11-19 13:52:29:  0: "
2025-11-19 13:52:29:  0: INFO: Stdout Redirection Enabled: True
2025-11-19 13:52:29:  0: INFO: Asynchronous Stdout Enabled: False
2025-11-19 13:52:29:  0: INFO: Stdout Handling Enabled: True
2025-11-19 13:52:29:  0: INFO: Popup Handling Enabled: True
2025-11-19 13:52:29:  0: INFO: QT Popup Handling Enabled: False
2025-11-19 13:52:29:  0: INFO: WindowsForms10.Window.8.app.* Popup Handling Enabled: False
2025-11-19 13:52:29:  0: INFO: Using Process Tree: True
2025-11-19 13:52:29:  0: INFO: Hiding DOS Window: True
2025-11-19 13:52:29:  0: INFO: Creating New Console: False
2025-11-19 13:52:29:  0: INFO: Running as user: rocky
2025-11-19 13:52:29:  0: INFO: Executable: "/home/rocky/Nuke16.0v6/Nuke16.0"
2025-11-19 13:52:29:  0: INFO: Setting Process Environment Variable EDDY_DEVICE_LIST to 
2025-11-19 13:52:29:  0: INFO: Argument: -V 2 -t "/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/jobsData/691dcb454c1fd3ab7085ff79/thread0_tempQAkje0/Ep03_sq0060_SH0180_comp_v004.nk"
2025-11-19 13:52:29:  0: INFO: Full Command: "/home/rocky/Nuke16.0v6/Nuke16.0" -V 2 -t "/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/jobsData/691dcb454c1fd3ab7085ff79/thread0_tempQAkje0/Ep03_sq0060_SH0180_comp_v004.nk"
2025-11-19 13:52:29:  0: INFO: Startup Directory: "/home/rocky/Nuke16.0v6"
2025-11-19 13:52:29:  0: INFO: Process Priority: BelowNormal
2025-11-19 13:52:29:  0: INFO: Process Affinity: default
2025-11-19 13:52:29:  0: INFO: Process is now running
2025-11-19 13:52:29:  0: DEBUG: StartJob: returning
2025-11-19 13:52:29:  0: Done executing plugin command of type 'Start Job'
2025-11-19 13:52:29:  0: Plugin rendering frame(s): 1032
2025-11-19 13:52:29:  0: Executing plugin command of type 'Render Task'
2025-11-19 13:52:29:  0: DEBUG: RenderTasks: called
2025-11-19 13:52:29:  0: DEBUG: RenderTasks: rendering frames 1032 to 1032
2025-11-19 13:52:29:  0: INFO: Rendering all enabled write nodes
2025-11-19 13:52:29:  0: STDOUT: Nuke 16.0v6, 64 bit, built Sep 11 2025.
2025-11-19 13:52:29:  0: STDOUT: Copyright (c) 2025 The Foundry Visionmongers Ltd.  All Rights Reserved.
2025-11-19 13:52:30:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:31:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:32:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:32:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:33:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:33:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:34:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:35:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:35:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:36:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:36:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:37:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:38:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:38:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:39:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:39:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/_pathsetup.py
2025-11-19 13:52:39:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:39:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/init.tcl
2025-11-19 13:52:39:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/init.py
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/setenv.tcl
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/formats.tcl
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/caravr/init.py
2025-11-19 13:52:40:  0: STDOUT: Loading /mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot/init.py
2025-11-19 13:52:40:  0: STDOUT: Multishot: Batch mode detected - initializing variables only...
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/getenv.tcl
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/OCIOColorSpace.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/exrReader.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Reformat.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Shuffle2.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Remove.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Copy.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Premult.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Saturation.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Grade.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Merge2.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Multiply.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Crop.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/pngReader.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Transform.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Camera3.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/abcSceneReader.so
2025-11-19 13:52:40:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ReadGeo2.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/abcReader.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Scene.tcl
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/MergeGeo.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Constant.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Cylinder.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Sphere.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ColorCorrect.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ScanlineRender.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/OCIODisplay.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/exrWriter.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Invert.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Radial.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Denoise2.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/EXPTool.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/BlinkScript.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/CopyBBox.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Ramp.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ColorLookup.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Clamp.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Colorspace.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Dilate.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ColorMatrix.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Add.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/AdjBBox.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/NodeWrapper.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/EdgeBlur.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Axis2.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/FilterErode.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Gamma.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/IDistort.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Keymix.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Dissolve.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ZDefocus2.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Glint.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/LightWrap.gizmo
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Keyer.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/CCorrect.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/HueCorrect.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ContactSheet.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Mirror2.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/LayerContactSheet.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/pngWriter.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Cryptomatte.so
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/jpgReader.tcl
2025-11-19 13:52:40:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/jpegReader.so
2025-11-19 13:52:40:  0: STDOUT: [13:52:40 UTC] Read nuke script: /var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/jobsData/691dcb454c1fd3ab7085ff79/thread0_tempQAkje0/Ep03_sq0060_SH0180_comp_v004.nk
2025-11-19 13:52:40:  0: STDOUT: ================================================================================
2025-11-19 13:52:40:  0: STDOUT: MULTISHOT DEBUG: Printing ALL root knobs
2025-11-19 13:52:40:  0: STDOUT: ================================================================================
2025-11-19 13:52:40:  0: STDOUT: Total knobs on root: 61
2025-11-19 13:52:40:  0: STDOUT: Multishot JSON knobs:
2025-11-19 13:52:40:  0: STDOUT:   multishot_context = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   multishot_custom = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   multishot_variables = MISSING!
2025-11-19 13:52:40:  0: STDOUT: Individual variable knobs:
2025-11-19 13:52:40:  0: STDOUT:   ep = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   seq = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   shot = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   project = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   PROJ_ROOT = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   IMG_ROOT = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   first_frame = '1.0'
2025-11-19 13:52:40:  0: STDOUT:   last_frame = '100.0'
2025-11-19 13:52:40:  0: STDOUT: ================================================================================
2025-11-19 13:52:40:  0: STDOUT: Multishot: Manually creating individual knobs from JSON...
2025-11-19 13:52:40:  0: STDOUT: Multishot: Variables initialized in batch mode
2025-11-19 13:52:40:  0: STDOUT: ================================================================================
2025-11-19 13:52:40:  0: STDOUT: ================================================================================
2025-11-19 13:52:40:  0: STDOUT: MULTISHOT DEBUG: Printing ALL root knobs
2025-11-19 13:52:40:  0: STDOUT: ================================================================================
2025-11-19 13:52:40:  0: STDOUT: Total knobs on root: 61
2025-11-19 13:52:40:  0: STDOUT: Multishot JSON knobs:
2025-11-19 13:52:40:  0: STDOUT:   multishot_context = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   multishot_custom = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   multishot_variables = MISSING!
2025-11-19 13:52:40:  0: STDOUT: Individual variable knobs:
2025-11-19 13:52:40:  0: STDOUT:   ep = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   seq = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   shot = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   project = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   PROJ_ROOT = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   IMG_ROOT = MISSING!
2025-11-19 13:52:40:  0: STDOUT:   first_frame = '1.0'
2025-11-19 13:52:40:  0: STDOUT:   last_frame = '100.0'
2025-11-19 13:52:40:  0: STDOUT: ================================================================================
2025-11-19 13:52:40:  0: STDOUT: Multishot: Manually creating individual knobs from JSON...
2025-11-19 13:52:40:  0: STDOUT: Multishot: Variables initialized in batch mode
2025-11-19 13:52:40:  0: STDOUT: ================================================================================
2025-11-19 13:52:40:  0: STDOUT: >>> [13:52.40] ERROR: MultishotRead_lighting_MASTER_ATMOS_A: [value root.IMG_ROOT][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.MultishotRead_lighting_MASTER_ATMOS_A.shot_version]/MASTER_ATMOS_A/MASTER_ATMOS_A.%04d.exr: Read error: No such file or directory
2025-11-19 13:52:40:  0: Done executing plugin command of type 'Render Task'
2025-11-19 13:52:40:  0: Executing plugin command of type 'End Job'
2025-11-19 13:52:40:  0: DEBUG: EndJob: called
2025-11-19 13:52:40:  0: INFO: Ending Nuke Job
2025-11-19 13:52:41:  0: DEBUG: EndJob: returning
2025-11-19 13:52:41:  0: Done executing plugin command of type 'End Job'
2025-11-19 13:52:44:  Scheduler Thread - Render Thread 0 threw a major error: 
2025-11-19 13:52:44:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 13:52:44:  Exception Details
2025-11-19 13:52:44:  RenderPluginException -- Error: >>> [13:52.40] ERROR: MultishotRead_lighting_MASTER_ATMOS_A: [value root.IMG_ROOT][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.MultishotRead_lighting_MASTER_ATMOS_A.shot_version]/MASTER_ATMOS_A/MASTER_ATMOS_A.%04d.exr: Read error: No such file or directory
2025-11-19 13:52:44:     at Deadline.Plugins.PluginWrapper.RenderTasks(Task task, String& outMessage, AbortLevel& abortLevel)
2025-11-19 13:52:44:  RenderPluginException.Cause: JobError (2)
2025-11-19 13:52:44:  RenderPluginException.Level: Major (1)
2025-11-19 13:52:44:  RenderPluginException.HasSlaveLog: True
2025-11-19 13:52:44:  RenderPluginException.SlaveLogFileName: /var/log/Thinkbox/Deadline10/deadlineslave_renderthread_0-ip-10-100-136-98-0000.log
2025-11-19 13:52:44:  Exception.TargetSite: Deadline.Slaves.Messaging.PluginResponseMemento d(Deadline.Net.DeadlineMessage, System.Threading.CancellationToken)
2025-11-19 13:52:44:  Exception.Data: ( )
2025-11-19 13:52:44:  Exception.Source: deadline
2025-11-19 13:52:44:  Exception.HResult: -2146233088
2025-11-19 13:52:44:    Exception.StackTrace: 
2025-11-19 13:52:44:     at Deadline.Plugins.SandboxedPlugin.d(DeadlineMessage bgz, CancellationToken bha
2025-11-19 13:52:44:     at Deadline.Plugins.SandboxedPlugin.RenderTask(Task task, CancellationToken cancellationToken
2025-11-19 13:52:44:     at Deadline.Slaves.SlaveRenderThread.c(TaskLogWriter akd, CancellationToken ake)
2025-11-19 13:52:44:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 13:52:46:  Skipping pending job scan because it is not required at this time
2025-11-19 13:52:47:  Skipping repository repair because it is not required at this time
2025-11-19 13:52:47:  Another house cleaning process is already in progress
2025-11-19 13:52:56:  Skipping pending job scan because it is not required at this time
2025-11-19 13:52:56:  Skipping repository repair because it is not required at this time
2025-11-19 13:52:56:  Skipping house cleaning because it is not required at this time
2025-11-19 13:53:02:  Another pending job scan process is already in progress
2025-11-19 13:53:02:  Skipping repository repair because it is not required at this time
2025-11-19 13:53:02:  Skipping house cleaning because it is not required at this time
2025-11-19 13:53:11:  Skipping pending job scan because it is not required at this time
2025-11-19 13:53:11:  Skipping repository repair because it is not required at this time
2025-11-19 13:53:11:  Skipping house cleaning because it is not required at this time
2025-11-19 13:53:17:  Skipping pending job scan because it is not required at this time
2025-11-19 13:53:17:  Skipping repository repair because it is not required at this time
2025-11-19 13:53:17:  Skipping house cleaning because it is not required at this time
2025-11-19 13:53:24:  Skipping pending job scan because it is not required at this time
2025-11-19 13:53:24:  Skipping repository repair because it is not required at this time
2025-11-19 13:53:24:  Skipping house cleaning because it is not required at this time
2025-11-19 13:53:31:  Skipping pending job scan because it is not required at this time
2025-11-19 13:53:31:  Skipping repository repair because it is not required at this time
2025-11-19 13:53:31:  Skipping house cleaning because it is not required at this time
2025-11-19 13:53:39:  Skipping pending job scan because it is not required at this time
2025-11-19 13:53:39:  Skipping repository repair because it is not required at this time
2025-11-19 13:53:39:  Skipping house cleaning because it is not required at this time
2025-11-19 13:53:46:  Skipping pending job scan because it is not required at this time
2025-11-19 13:53:46:  Skipping repository repair because it is not required at this time
2025-11-19 13:53:46:  Skipping house cleaning because it is not required at this time
2025-11-19 13:53:54:  Skipping pending job scan because it is not required at this time
2025-11-19 13:53:54:  Skipping repository repair because it is not required at this time
2025-11-19 13:53:54:  Another house cleaning process is already in progress
2025-11-19 13:54:01:  Skipping pending job scan because it is not required at this time
2025-11-19 13:54:01:  Another repository repair process is already in progress
2025-11-19 13:54:01:  Skipping house cleaning because it is not required at this time
2025-11-19 13:54:08:  Another pending job scan process is already in progress
2025-11-19 13:54:08:  Skipping repository repair because it is not required at this time
2025-11-19 13:54:08:  Skipping house cleaning because it is not required at this time
2025-11-19 13:54:14:  Skipping pending job scan because it is not required at this time
2025-11-19 13:54:14:  Skipping repository repair because it is not required at this time
2025-11-19 13:54:14:  Skipping house cleaning because it is not required at this time
2025-11-19 13:54:22:  Skipping pending job scan because it is not required at this time
2025-11-19 13:54:22:  Skipping repository repair because it is not required at this time
2025-11-19 13:54:22:  Skipping house cleaning because it is not required at this time
2025-11-19 13:54:29:  Skipping pending job scan because it is not required at this time
2025-11-19 13:54:29:  Skipping repository repair because it is not required at this time
2025-11-19 13:54:29:  Skipping house cleaning because it is not required at this time
2025-11-19 13:54:35:  Skipping pending job scan because it is not required at this time
2025-11-19 13:54:35:  Skipping repository repair because it is not required at this time
2025-11-19 13:54:35:  Skipping house cleaning because it is not required at this time
2025-11-19 13:54:43:  Skipping pending job scan because it is not required at this time
2025-11-19 13:54:43:  Skipping repository repair because it is not required at this time
2025-11-19 13:54:43:  Skipping house cleaning because it is not required at this time
2025-11-19 13:54:49:  Skipping pending job scan because it is not required at this time
2025-11-19 13:54:49:  Skipping repository repair because it is not required at this time
2025-11-19 13:54:49:  Skipping house cleaning because it is not required at this time
2025-11-19 13:54:55:  Skipping pending job scan because it is not required at this time
2025-11-19 13:54:55:  Skipping repository repair because it is not required at this time
2025-11-19 13:54:55:  Skipping house cleaning because it is not required at this time
2025-11-19 13:55:02:  Skipping pending job scan because it is not required at this time
2025-11-19 13:55:02:  Skipping repository repair because it is not required at this time
2025-11-19 13:55:02:  Skipping house cleaning because it is not required at this time
2025-11-19 13:55:08:  Skipping pending job scan because it is not required at this time
2025-11-19 13:55:08:  Skipping repository repair because it is not required at this time
2025-11-19 13:55:08:  Skipping house cleaning because it is not required at this time
2025-11-19 13:55:16:  Skipping pending job scan because it is not required at this time
2025-11-19 13:55:16:  Skipping repository repair because it is not required at this time
2025-11-19 13:55:16:  Skipping house cleaning because it is not required at this time
2025-11-19 13:55:25:  Skipping pending job scan because it is not required at this time
2025-11-19 13:55:25:  Skipping repository repair because it is not required at this time
2025-11-19 13:55:25:  Skipping house cleaning because it is not required at this time
2025-11-19 13:55:31:  Skipping pending job scan because it is not required at this time
2025-11-19 13:55:31:  Skipping repository repair because it is not required at this time
2025-11-19 13:55:31:  Skipping house cleaning because it is not required at this time
2025-11-19 13:55:39:  Skipping pending job scan because it is not required at this time
2025-11-19 13:55:39:  Skipping repository repair because it is not required at this time
2025-11-19 13:55:39:  Skipping house cleaning because it is not required at this time
2025-11-19 13:55:47:  Skipping pending job scan because it is not required at this time
2025-11-19 13:55:47:  Skipping repository repair because it is not required at this time
2025-11-19 13:55:47:  Skipping house cleaning because it is not required at this time
2025-11-19 13:55:54:  Skipping pending job scan because it is not required at this time
2025-11-19 13:55:54:  Skipping repository repair because it is not required at this time
2025-11-19 13:55:54:  Skipping house cleaning because it is not required at this time
2025-11-19 13:56:02:  Skipping pending job scan because it is not required at this time
2025-11-19 13:56:02:  Skipping repository repair because it is not required at this time
2025-11-19 13:56:02:  Skipping house cleaning because it is not required at this time
2025-11-19 13:56:09:  Skipping pending job scan because it is not required at this time
2025-11-19 13:56:09:  Another repository repair process is already in progress
2025-11-19 13:56:09:  Skipping house cleaning because it is not required at this time
2025-11-19 13:56:16:  Another pending job scan process is already in progress
2025-11-19 13:56:16:  Skipping repository repair because it is not required at this time
2025-11-19 13:56:16:  Skipping house cleaning because it is not required at this time
2025-11-19 13:56:25:  Skipping pending job scan because it is not required at this time
2025-11-19 13:56:25:  Skipping repository repair because it is not required at this time
2025-11-19 13:56:25:  Skipping house cleaning because it is not required at this time
2025-11-19 13:56:31:  Skipping pending job scan because it is not required at this time
2025-11-19 13:56:31:  Skipping repository repair because it is not required at this time
2025-11-19 13:56:31:  Skipping house cleaning because it is not required at this time
2025-11-19 13:56:37:  Skipping pending job scan because it is not required at this time
2025-11-19 13:56:37:  Skipping repository repair because it is not required at this time
2025-11-19 13:56:37:  Skipping house cleaning because it is not required at this time
2025-11-19 13:56:43:  Skipping pending job scan because it is not required at this time
2025-11-19 13:56:43:  Skipping repository repair because it is not required at this time
2025-11-19 13:56:43:  Skipping house cleaning because it is not required at this time
2025-11-19 13:56:50:  Skipping pending job scan because it is not required at this time
2025-11-19 13:56:50:  Skipping repository repair because it is not required at this time
2025-11-19 13:56:50:  Skipping house cleaning because it is not required at this time
2025-11-19 13:56:58:  Skipping pending job scan because it is not required at this time
2025-11-19 13:56:58:  Skipping repository repair because it is not required at this time
2025-11-19 13:56:58:  Skipping house cleaning because it is not required at this time
2025-11-19 13:57:05:  Skipping pending job scan because it is not required at this time
2025-11-19 13:57:05:  Skipping repository repair because it is not required at this time
2025-11-19 13:57:05:  Skipping house cleaning because it is not required at this time
2025-11-19 13:57:15:  Skipping pending job scan because it is not required at this time
2025-11-19 13:57:15:  Another repository repair process is already in progress
2025-11-19 13:57:15:  Skipping house cleaning because it is not required at this time
2025-11-19 13:57:18:  Unable to stream EC2 Deadline Worker status due to the following exception:
2025-11-19 13:57:18:  Unable to get IAM security credentials from EC2 Instance Metadata Service. (Amazon.Runtime.AmazonServiceException)
2025-11-19 13:57:18:     at Amazon.Runtime.DefaultInstanceProfileAWSCredentials.FetchCredentials()
2025-11-19 13:57:18:     at Amazon.Runtime.DefaultInstanceProfileAWSCredentials.GetCredentials()
2025-11-19 13:57:18:     at Amazon.Runtime.DefaultInstanceProfileAWSCredentials.GetCredentialsAsync()
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.CredentialsRetriever.InvokeAsync[T](IExecutionContext executionContext)
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.RetryHandler.InvokeAsync[T](IExecutionContext executionContext)
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.RetryHandler.InvokeAsync[T](IExecutionContext executionContext)
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.CallbackHandler.InvokeAsync[T](IExecutionContext executionContext)
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.CallbackHandler.InvokeAsync[T](IExecutionContext executionContext)
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.ErrorCallbackHandler.InvokeAsync[T](IExecutionContext executionContext)
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.MetricsHandler.InvokeAsync[T](IExecutionContext executionContext)
2025-11-19 13:57:18:     at Deadline.AWS.AWSUtils.k(AggregateException dnw, String dnx, String dny, String dnz, String[] doa)
2025-11-19 13:57:18:     at Deadline.AWS.AWSUtils.h[m](Task`1 dnh, String dni, String dnj, String dnk, String[] dnl)
2025-11-19 13:57:18:     at Deadline.AWS.Wrappers.SQSWrapper.a[m](Task`1 dsa, String dsb, String dsc, String dsd)
2025-11-19 13:57:18:     at Deadline.AWS.Wrappers.SQSWrapper.GetQueueUrl(String queueName)
2025-11-19 13:57:18:     at Deadline.Slaves.EC2ComputeNodeStatusPublisher.get_d()
2025-11-19 13:57:18:     at Deadline.Slaves.EC2ComputeNodeStatusPublisher.PushStatusUpdate(String statusReport, Boolean isTrackedByResourceTracker)
2025-11-19 13:57:18:  Exception Details
2025-11-19 13:57:18:  AmazonServiceException -- Unable to get IAM security credentials from EC2 Instance Metadata Service.
2025-11-19 13:57:18:  AmazonServiceException.ErrorType: Sender (0)
2025-11-19 13:57:18:  AmazonServiceException.StatusCode:  (0)
2025-11-19 13:57:18:  Exception.TargetSite: CredentialsRefreshState FetchCredentials()
2025-11-19 13:57:18:  Exception.Data: ( )
2025-11-19 13:57:18:  Exception.Source: AWSSDK.Core
2025-11-19 13:57:18:  Exception.HResult: -2146233088
2025-11-19 13:57:18:    Exception.StackTrace: 
2025-11-19 13:57:18:     at Amazon.Runtime.DefaultInstanceProfileAWSCredentials.FetchCredentials(
2025-11-19 13:57:18:     at Amazon.Runtime.DefaultInstanceProfileAWSCredentials.GetCredentials(
2025-11-19 13:57:18:     at Amazon.Runtime.DefaultInstanceProfileAWSCredentials.GetCredentialsAsync(
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.CredentialsRetriever.InvokeAsync[T](IExecutionContext executionContext
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.RetryHandler.InvokeAsync[T](IExecutionContext executionContext
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.RetryHandler.InvokeAsync[T](IExecutionContext executionContext
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.CallbackHandler.InvokeAsync[T](IExecutionContext executionContext
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.CallbackHandler.InvokeAsync[T](IExecutionContext executionContext
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.ErrorCallbackHandler.InvokeAsync[T](IExecutionContext executionContext
2025-11-19 13:57:18:     at Amazon.Runtime.Internal.MetricsHandler.InvokeAsync[T](IExecutionContext executionContext
2025-11-19 13:57:18:     at Deadline.AWS.AWSUtils.k(AggregateException dnw, String dnx, String dny, String dnz, String[] doa
2025-11-19 13:57:18:     at Deadline.AWS.AWSUtils.h[m](Task`1 dnh, String dni, String dnj, String dnk, String[] dnl
2025-11-19 13:57:18:     at Deadline.AWS.Wrappers.SQSWrapper.a[m](Task`1 dsa, String dsb, String dsc, String dsd
2025-11-19 13:57:18:     at Deadline.AWS.Wrappers.SQSWrapper.GetQueueUrl(String queueName
2025-11-19 13:57:18:     at Deadline.Slaves.EC2ComputeNodeStatusPublisher.get_d(
2025-11-19 13:57:18:     at Deadline.Slaves.EC2ComputeNodeStatusPublisher.PushStatusUpdate(String statusReport, Boolean isTrackedByResourceTracker)
2025-11-19 13:57:21:  Skipping pending job scan because it is not required at this time
2025-11-19 13:57:21:  Another repository repair process is already in progress
2025-11-19 13:57:21:  Skipping house cleaning because it is not required at this time
2025-11-19 13:57:29:  Skipping pending job scan because it is not required at this time
2025-11-19 13:57:29:  Skipping repository repair because it is not required at this time
2025-11-19 13:57:29:  Skipping house cleaning because it is not required at this time
2025-11-19 13:57:37:  Skipping pending job scan because it is not required at this time
2025-11-19 13:57:37:  Skipping repository repair because it is not required at this time
2025-11-19 13:57:37:  Skipping house cleaning because it is not required at this time
2025-11-19 13:57:43:  Skipping pending job scan because it is not required at this time
2025-11-19 13:57:43:  Skipping repository repair because it is not required at this time
2025-11-19 13:57:43:  Skipping house cleaning because it is not required at this time
2025-11-19 13:57:49:  Skipping pending job scan because it is not required at this time
2025-11-19 13:57:49:  Skipping repository repair because it is not required at this time
2025-11-19 13:57:49:  Skipping house cleaning because it is not required at this time
2025-11-19 13:57:50:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 13:57:50:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 13:57:51:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 13:57:51:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 13:57:51:  Exception Details
2025-11-19 13:57:51:  Exception -- The user 'katha.nab' does not exist
2025-11-19 13:57:51:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 13:57:51:  Exception.Data: ( )
2025-11-19 13:57:51:  Exception.Source: franticx
2025-11-19 13:57:51:  Exception.HResult: -2146233088
2025-11-19 13:57:51:    Exception.StackTrace: 
2025-11-19 13:57:51:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 13:57:51:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 13:57:51:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 13:57:51:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 13:57:51:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:57:51:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:57:51:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 13:57:51:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 13:57:51:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 13:57:51:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 13:57:53:  Skipping pending job scan because it is not required at this time
2025-11-19 13:57:53:  Skipping repository repair because it is not required at this time
2025-11-19 13:57:53:  Skipping house cleaning because it is not required at this time
2025-11-19 13:57:53:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 13:57:54:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 13:57:55:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 13:57:55:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 13:57:55:  Exception Details
2025-11-19 13:57:55:  Exception -- The user 'katha.nab' does not exist
2025-11-19 13:57:55:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 13:57:55:  Exception.Data: ( )
2025-11-19 13:57:55:  Exception.Source: franticx
2025-11-19 13:57:55:  Exception.HResult: -2146233088
2025-11-19 13:57:55:    Exception.StackTrace: 
2025-11-19 13:57:55:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 13:57:55:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 13:57:55:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 13:57:55:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 13:57:55:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:57:55:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:57:55:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 13:57:55:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 13:57:55:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 13:57:55:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 13:57:57:  Skipping pending job scan because it is not required at this time
2025-11-19 13:57:57:  Skipping repository repair because it is not required at this time
2025-11-19 13:57:57:  Skipping house cleaning because it is not required at this time
2025-11-19 13:57:57:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 13:57:58:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 13:57:59:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 13:57:59:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 13:57:59:  Exception Details
2025-11-19 13:57:59:  Exception -- The user 'katha.nab' does not exist
2025-11-19 13:57:59:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 13:57:59:  Exception.Data: ( )
2025-11-19 13:57:59:  Exception.Source: franticx
2025-11-19 13:57:59:  Exception.HResult: -2146233088
2025-11-19 13:57:59:    Exception.StackTrace: 
2025-11-19 13:57:59:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 13:57:59:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 13:57:59:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 13:57:59:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 13:57:59:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:57:59:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:57:59:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 13:57:59:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 13:57:59:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 13:57:59:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 13:58:01:  Skipping pending job scan because it is not required at this time
2025-11-19 13:58:01:  Skipping repository repair because it is not required at this time
2025-11-19 13:58:01:  Skipping house cleaning because it is not required at this time
2025-11-19 13:58:01:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 13:58:02:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 13:58:02:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 13:58:02:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 13:58:02:  Exception Details
2025-11-19 13:58:02:  Exception -- The user 'katha.nab' does not exist
2025-11-19 13:58:02:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 13:58:02:  Exception.Data: ( )
2025-11-19 13:58:02:  Exception.Source: franticx
2025-11-19 13:58:02:  Exception.HResult: -2146233088
2025-11-19 13:58:02:    Exception.StackTrace: 
2025-11-19 13:58:02:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 13:58:02:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 13:58:02:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 13:58:02:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 13:58:02:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:58:02:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:58:02:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 13:58:02:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 13:58:02:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 13:58:02:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 13:58:05:  Skipping pending job scan because it is not required at this time
2025-11-19 13:58:05:  Skipping repository repair because it is not required at this time
2025-11-19 13:58:05:  Skipping house cleaning because it is not required at this time
2025-11-19 13:58:05:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 13:58:05:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 13:58:06:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 13:58:06:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 13:58:06:  Exception Details
2025-11-19 13:58:06:  Exception -- The user 'katha.nab' does not exist
2025-11-19 13:58:06:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 13:58:06:  Exception.Data: ( )
2025-11-19 13:58:06:  Exception.Source: franticx
2025-11-19 13:58:06:  Exception.HResult: -2146233088
2025-11-19 13:58:06:    Exception.StackTrace: 
2025-11-19 13:58:06:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 13:58:06:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 13:58:06:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 13:58:06:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 13:58:06:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:58:06:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:58:06:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 13:58:06:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 13:58:06:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 13:58:06:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 13:58:09:  Skipping pending job scan because it is not required at this time
2025-11-19 13:58:09:  Skipping repository repair because it is not required at this time
2025-11-19 13:58:09:  Skipping house cleaning because it is not required at this time
2025-11-19 13:58:17:  Skipping pending job scan because it is not required at this time
2025-11-19 13:58:17:  Skipping repository repair because it is not required at this time
2025-11-19 13:58:17:  Another house cleaning process is already in progress
2025-11-19 13:58:26:  Skipping pending job scan because it is not required at this time
2025-11-19 13:58:26:  Another repository repair process is already in progress
2025-11-19 13:58:26:  Skipping house cleaning because it is not required at this time
2025-11-19 13:58:26:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 13:58:26:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 13:58:27:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 13:58:27:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 13:58:27:  Exception Details
2025-11-19 13:58:27:  Exception -- The user 'katha.nab' does not exist
2025-11-19 13:58:27:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 13:58:27:  Exception.Data: ( )
2025-11-19 13:58:27:  Exception.Source: franticx
2025-11-19 13:58:27:  Exception.HResult: -2146233088
2025-11-19 13:58:27:    Exception.StackTrace: 
2025-11-19 13:58:27:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 13:58:27:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 13:58:27:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 13:58:27:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 13:58:27:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:58:27:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 13:58:27:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 13:58:27:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 13:58:27:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 13:58:27:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 13:58:29:  Another pending job scan process is already in progress
2025-11-19 13:58:29:  Skipping repository repair because it is not required at this time
2025-11-19 13:58:29:  Skipping house cleaning because it is not required at this time
2025-11-19 13:58:36:  Skipping pending job scan because it is not required at this time
2025-11-19 13:58:36:  Skipping repository repair because it is not required at this time
2025-11-19 13:58:36:  Skipping house cleaning because it is not required at this time
2025-11-19 13:58:42:  Skipping pending job scan because it is not required at this time
2025-11-19 13:58:42:  Skipping repository repair because it is not required at this time
2025-11-19 13:58:42:  Skipping house cleaning because it is not required at this time
2025-11-19 13:58:49:  Skipping pending job scan because it is not required at this time
2025-11-19 13:58:49:  Skipping repository repair because it is not required at this time
2025-11-19 13:58:49:  Skipping house cleaning because it is not required at this time
2025-11-19 13:58:55:  Skipping pending job scan because it is not required at this time
2025-11-19 13:58:55:  Skipping repository repair because it is not required at this time
2025-11-19 13:58:55:  Skipping house cleaning because it is not required at this time
2025-11-19 13:59:01:  Skipping pending job scan because it is not required at this time
2025-11-19 13:59:01:  Skipping repository repair because it is not required at this time
2025-11-19 13:59:01:  Skipping house cleaning because it is not required at this time
2025-11-19 13:59:10:  Skipping pending job scan because it is not required at this time
2025-11-19 13:59:10:  Skipping repository repair because it is not required at this time
2025-11-19 13:59:10:  Skipping house cleaning because it is not required at this time
2025-11-19 13:59:16:  Skipping pending job scan because it is not required at this time
2025-11-19 13:59:16:  Skipping repository repair because it is not required at this time
2025-11-19 13:59:16:  Skipping house cleaning because it is not required at this time
2025-11-19 13:59:22:  Skipping pending job scan because it is not required at this time
2025-11-19 13:59:22:  Skipping repository repair because it is not required at this time
2025-11-19 13:59:22:  Another house cleaning process is already in progress
2025-11-19 13:59:30:  Skipping pending job scan because it is not required at this time
2025-11-19 13:59:30:  Another repository repair process is already in progress
2025-11-19 13:59:30:  Skipping house cleaning because it is not required at this time
2025-11-19 13:59:38:  Another pending job scan process is already in progress
2025-11-19 13:59:38:  Skipping repository repair because it is not required at this time
2025-11-19 13:59:38:  Skipping house cleaning because it is not required at this time
2025-11-19 13:59:46:  Skipping pending job scan because it is not required at this time
2025-11-19 13:59:46:  Skipping repository repair because it is not required at this time
2025-11-19 13:59:46:  Skipping house cleaning because it is not required at this time
2025-11-19 13:59:55:  Skipping pending job scan because it is not required at this time
2025-11-19 13:59:55:  Skipping repository repair because it is not required at this time
2025-11-19 13:59:55:  Skipping house cleaning because it is not required at this time
2025-11-19 14:00:01:  Skipping pending job scan because it is not required at this time
2025-11-19 14:00:01:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:01:  Skipping house cleaning because it is not required at this time
2025-11-19 14:00:07:  Skipping pending job scan because it is not required at this time
2025-11-19 14:00:07:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:07:  Skipping house cleaning because it is not required at this time
2025-11-19 14:00:13:  Skipping pending job scan because it is not required at this time
2025-11-19 14:00:13:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:13:  Skipping house cleaning because it is not required at this time
2025-11-19 14:00:13:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 14:00:14:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 14:00:14:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 14:00:14:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 14:00:14:  Exception Details
2025-11-19 14:00:14:  Exception -- The user 'katha.nab' does not exist
2025-11-19 14:00:14:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 14:00:14:  Exception.Data: ( )
2025-11-19 14:00:14:  Exception.Source: franticx
2025-11-19 14:00:14:  Exception.HResult: -2146233088
2025-11-19 14:00:14:    Exception.StackTrace: 
2025-11-19 14:00:14:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 14:00:14:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 14:00:14:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 14:00:14:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 14:00:14:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:00:14:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:00:14:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 14:00:14:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 14:00:14:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 14:00:14:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 14:00:17:  Skipping pending job scan because it is not required at this time
2025-11-19 14:00:17:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:17:  Skipping house cleaning because it is not required at this time
2025-11-19 14:00:17:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 14:00:17:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 14:00:18:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 14:00:18:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 14:00:18:  Exception Details
2025-11-19 14:00:18:  Exception -- The user 'katha.nab' does not exist
2025-11-19 14:00:18:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 14:00:18:  Exception.Data: ( )
2025-11-19 14:00:18:  Exception.Source: franticx
2025-11-19 14:00:18:  Exception.HResult: -2146233088
2025-11-19 14:00:18:    Exception.StackTrace: 
2025-11-19 14:00:18:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 14:00:18:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 14:00:18:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 14:00:18:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 14:00:18:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:00:18:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:00:18:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 14:00:18:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 14:00:18:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 14:00:18:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 14:00:20:  Skipping pending job scan because it is not required at this time
2025-11-19 14:00:20:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:20:  Skipping house cleaning because it is not required at this time
2025-11-19 14:00:21:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 14:00:21:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 14:00:22:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 14:00:22:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 14:00:22:  Exception Details
2025-11-19 14:00:22:  Exception -- The user 'katha.nab' does not exist
2025-11-19 14:00:22:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 14:00:22:  Exception.Data: ( )
2025-11-19 14:00:22:  Exception.Source: franticx
2025-11-19 14:00:22:  Exception.HResult: -2146233088
2025-11-19 14:00:22:    Exception.StackTrace: 
2025-11-19 14:00:22:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 14:00:22:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 14:00:22:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 14:00:22:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 14:00:22:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:00:22:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:00:22:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 14:00:22:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 14:00:22:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 14:00:22:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 14:00:24:  Skipping pending job scan because it is not required at this time
2025-11-19 14:00:24:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:24:  Skipping house cleaning because it is not required at this time
2025-11-19 14:00:24:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 14:00:25:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 14:00:26:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 14:00:26:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 14:00:26:  Exception Details
2025-11-19 14:00:26:  Exception -- The user 'katha.nab' does not exist
2025-11-19 14:00:26:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 14:00:26:  Exception.Data: ( )
2025-11-19 14:00:26:  Exception.Source: franticx
2025-11-19 14:00:26:  Exception.HResult: -2146233088
2025-11-19 14:00:26:    Exception.StackTrace: 
2025-11-19 14:00:26:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 14:00:26:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 14:00:26:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 14:00:26:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 14:00:26:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:00:26:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:00:26:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 14:00:26:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 14:00:26:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 14:00:26:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 14:00:28:  Skipping pending job scan because it is not required at this time
2025-11-19 14:00:28:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:28:  Skipping house cleaning because it is not required at this time
2025-11-19 14:00:28:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 14:00:29:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 14:00:31:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 14:00:31:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 14:00:31:  Exception Details
2025-11-19 14:00:31:  Exception -- The user 'katha.nab' does not exist
2025-11-19 14:00:31:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 14:00:31:  Exception.Data: ( )
2025-11-19 14:00:31:  Exception.Source: franticx
2025-11-19 14:00:31:  Exception.HResult: -2146233088
2025-11-19 14:00:31:    Exception.StackTrace: 
2025-11-19 14:00:31:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 14:00:31:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 14:00:31:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 14:00:31:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 14:00:31:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:00:31:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:00:31:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 14:00:31:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 14:00:31:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 14:00:31:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 14:00:34:  Skipping pending job scan because it is not required at this time
2025-11-19 14:00:34:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:34:  Another house cleaning process is already in progress
2025-11-19 14:00:40:  Another pending job scan process is already in progress
2025-11-19 14:00:40:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:40:  Skipping house cleaning because it is not required at this time
2025-11-19 14:00:46:  Skipping pending job scan because it is not required at this time
2025-11-19 14:00:46:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:46:  Skipping house cleaning because it is not required at this time
2025-11-19 14:00:54:  Skipping pending job scan because it is not required at this time
2025-11-19 14:00:54:  Skipping repository repair because it is not required at this time
2025-11-19 14:00:54:  Skipping house cleaning because it is not required at this time
2025-11-19 14:01:02:  Skipping pending job scan because it is not required at this time
2025-11-19 14:01:02:  Skipping repository repair because it is not required at this time
2025-11-19 14:01:02:  Skipping house cleaning because it is not required at this time
2025-11-19 14:01:10:  Skipping pending job scan because it is not required at this time
2025-11-19 14:01:10:  Skipping repository repair because it is not required at this time
2025-11-19 14:01:10:  Skipping house cleaning because it is not required at this time
2025-11-19 14:01:18:  Skipping pending job scan because it is not required at this time
2025-11-19 14:01:18:  Skipping repository repair because it is not required at this time
2025-11-19 14:01:18:  Skipping house cleaning because it is not required at this time
2025-11-19 14:01:26:  Skipping pending job scan because it is not required at this time
2025-11-19 14:01:26:  Skipping repository repair because it is not required at this time
2025-11-19 14:01:26:  Skipping house cleaning because it is not required at this time
2025-11-19 14:01:33:  Skipping pending job scan because it is not required at this time
2025-11-19 14:01:33:  Skipping repository repair because it is not required at this time
2025-11-19 14:01:33:  Skipping house cleaning because it is not required at this time
2025-11-19 14:01:33:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 14:01:34:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 14:01:35:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 14:01:35:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 14:01:35:  Exception Details
2025-11-19 14:01:35:  Exception -- The user 'katha.nab' does not exist
2025-11-19 14:01:35:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 14:01:35:  Exception.Data: ( )
2025-11-19 14:01:35:  Exception.Source: franticx
2025-11-19 14:01:35:  Exception.HResult: -2146233088
2025-11-19 14:01:35:    Exception.StackTrace: 
2025-11-19 14:01:35:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 14:01:35:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 14:01:35:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 14:01:35:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 14:01:35:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:01:35:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:01:35:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 14:01:35:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 14:01:35:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 14:01:35:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 14:01:37:  Skipping pending job scan because it is not required at this time
2025-11-19 14:01:37:  Skipping repository repair because it is not required at this time
2025-11-19 14:01:37:  Another house cleaning process is already in progress
2025-11-19 14:01:37:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 14:01:38:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 14:01:39:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 14:01:39:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 14:01:39:  Exception Details
2025-11-19 14:01:39:  Exception -- The user 'katha.nab' does not exist
2025-11-19 14:01:39:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 14:01:39:  Exception.Data: ( )
2025-11-19 14:01:39:  Exception.Source: franticx
2025-11-19 14:01:39:  Exception.HResult: -2146233088
2025-11-19 14:01:39:    Exception.StackTrace: 
2025-11-19 14:01:39:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 14:01:39:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 14:01:39:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 14:01:39:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 14:01:39:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:01:39:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:01:39:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 14:01:39:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 14:01:39:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 14:01:39:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 14:01:41:  Skipping pending job scan because it is not required at this time
2025-11-19 14:01:41:  Another repository repair process is already in progress
2025-11-19 14:01:41:  Skipping house cleaning because it is not required at this time
2025-11-19 14:01:41:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 14:01:42:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 14:01:43:  ERROR: Scheduler Thread - Render Thread 0 threw an unexpected error: 
2025-11-19 14:01:43:  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
2025-11-19 14:01:43:  Exception Details
2025-11-19 14:01:43:  Exception -- The user 'katha.nab' does not exist
2025-11-19 14:01:43:  Exception.TargetSite: UInt32 GetUserId(System.String)
2025-11-19 14:01:43:  Exception.Data: ( )
2025-11-19 14:01:43:  Exception.Source: franticx
2025-11-19 14:01:43:  Exception.HResult: -2146233088
2025-11-19 14:01:43:    Exception.StackTrace: 
2025-11-19 14:01:43:     at FranticX.Interop.libc.GetUserId(String username
2025-11-19 14:01:43:     at FranticX.IO.Directory2.SetUserAsOwner(String path, String username, Boolean recursive
2025-11-19 14:01:43:     at Deadline.IO.DeadlineClientPath.a(String bxc, UserInfo bxd, Boolean bxe
2025-11-19 14:01:43:     at Deadline.IO.DeadlineClientPath.CreateDirectoryWithMaxTwoUserAccess(String path, UserInfo additionalAllowedUser
2025-11-19 14:01:43:     at Deadline.IO.DeadlineClientPath.GetDeadlineClientSlaveJobPluginsFolder(String workerName, String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:01:43:     at Deadline.Slaves.SlaveSettings.GetSlavePluginPath(String jobId, Boolean createIfMissing, Boolean updatePermissions, UserInfo jobUser
2025-11-19 14:01:43:     at Deadline.Slaves.SlaveRenderThread.e(String akf, Job akg, CancellationToken akh
2025-11-19 14:01:43:     at Deadline.Slaves.SlaveRenderThread.b(TaskLogWriter akb, CancellationToken akc
2025-11-19 14:01:43:     at Deadline.Slaves.SlaveRenderThread.a()
2025-11-19 14:01:43:  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
2025-11-19 14:01:45:  Skipping pending job scan because it is not required at this time
2025-11-19 14:01:45:  Another repository repair process is already in progress
2025-11-19 14:01:45:  Skipping house cleaning because it is not required at this time
2025-11-19 14:01:45:  Scheduler Thread - Job's Limit Groups: 
2025-11-19 14:01:45:  0: Loading Job's Plugin timeout is Disabled


=======================================================
Details
=======================================================
Date: 11/19/2025 14:01:46
Frames: 1032
Elapsed Time: 00:00:00:01
Job Submit Date: 11/19/2025 14:01:32
Job User: katha.nab
Average RAM Usage: 1478286976 (5%)
Peak RAM Usage: 1569189888 (5%)
Average CPU Usage: 4%
Peak CPU Usage: 10%
Used CPU Clocks (x10^6 cycles): 33082
Total CPU Clocks (x10^6 cycles): 827026

=======================================================
Worker Information
=======================================================
Worker Name: ip-10-100-136-98
Version: v10.4.2.2 Release (313c3e8f5)
Operating System: Linux
Machine User: rocky
IP Address: 10.100.136.98
MAC Address: 06:0C:4E:5B:7D:85
CPU Architecture: x86_64
CPUs: 16
CPU Usage: 0%
Memory Usage: 1.3 GB / 30.4 GB (4%)
Free Disk Space: 116.389 GB 
Video Card: Amazon.com, Inc. Device 1111

=======================================================
AWS Information
=======================================================
Instance ID: i-088079d401c1b2c00
Instance Type: c5.4xlarge
Image ID: ami-0955e2e4cdc80a5e7
Region: ap-southeast-1
Architecture: x86_64
Availability Zone: ap-southeast-1a
