=======================================================
Error
=======================================================
Error: >>> [13:41.05] ERROR: MultishotRead_lighting_MASTER_ATMOS_A: [value root.IMG_ROOT][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.MultishotRead_lighting_MASTER_ATMOS_A.shot_version]/MASTER_ATMOS_A/MASTER_ATMOS_A.%04d.exr: Read error: No such file or directory
   at Deadline.Plugins.PluginWrapper.RenderTasks(Task task, String& outMessage, AbortLevel& abortLevel)

=======================================================
Type
=======================================================
RenderPluginException

=======================================================
Stack Trace
=======================================================
   at Deadline.Plugins.SandboxedPlugin.d(DeadlineMessage bgz, CancellationToken bha)
   at Deadline.Plugins.SandboxedPlugin.RenderTask(Task task, CancellationToken cancellationToken)
   at Deadline.Slaves.SlaveRenderThread.c(TaskLogWriter akd, CancellationToken ake)

=======================================================
Log
=======================================================
2025-11-19 13:40:51:  0: Loading Job's Plugin timeout is Disabled
2025-11-19 13:40:51:  0: SandboxedPlugin: Render Job As User disabled, running as current user 'rocky'
2025-11-19 13:40:53:  0: Executing plugin command of type 'Initialize Plugin'
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: debug logging enabled
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: m_pluginParamFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dc8dd4c1fd3ab7085ff76/Nuke.param'
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: m_pluginScriptFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dc8dd4c1fd3ab7085ff76/Nuke.py'
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: m_pluginPreLoadFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dc8dd4c1fd3ab7085ff76/PluginPreLoad.py'
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: m_jobPreLoadFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dc8dd4c1fd3ab7085ff76/JobPreLoad.py'
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: Checking for Plugin Pre-Load
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: Loading Plugin...
2025-11-19 13:40:53:  0: INFO: Executing plugin script '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dc8dd4c1fd3ab7085ff76/Nuke.py'
2025-11-19 13:40:53:  0: INFO: Plugin execution sandbox using Python version 3
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: getting job user
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: setting job filenames
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: Obtaining Deadline plugin object
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: Setting internal variables and delegates
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: Preparing Environment Variables
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: Obtaining network settings
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: Initializing Deadline plugin
2025-11-19 13:40:53:  0: DEBUG: This is an advanced plugin job.
2025-11-19 13:40:53:  0: INFO: About: Nuke Plugin for Deadline
2025-11-19 13:40:53:  0: INFO: The job's environment will be merged with the current environment before rendering
2025-11-19 13:40:53:  0: DEBUG: InitializePlugin: returning
2025-11-19 13:40:53:  0: Done executing plugin command of type 'Initialize Plugin'
2025-11-19 13:40:53:  0: Start Job timeout is disabled.
2025-11-19 13:40:53:  0: Task timeout is disabled.
2025-11-19 13:40:53:  0: Loaded job: Ep03_sq0060_SH0180_comp_v004.nk (691dc8dd4c1fd3ab7085ff76)
2025-11-19 13:40:53:  0: Executing plugin command of type 'Start Job'
2025-11-19 13:40:53:  0: DEBUG: StartJob: called
2025-11-19 13:40:53:  0: DEBUG: StartJob: Checking for Job Pre-Load
2025-11-19 13:40:53:  0: DEBUG: S3BackedCache Client is not installed.
2025-11-19 13:40:53:  0: DEBUG: GlobalAssetTransferPreLoadJob: called
2025-11-19 13:40:53:  0: INFO: Executing global asset transfer preload script '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/plugins/691dc8dd4c1fd3ab7085ff76/GlobalAssetTransferPreLoad.py'
2025-11-19 13:40:53:  0: INFO: Looking for legacy (pre-10.0.26) AWS Portal File Transfer...
2025-11-19 13:40:53:  0: INFO: Looking for legacy (pre-10.0.26) File Transfer controller in /opt/Thinkbox/S3BackedCache/bin/task.py...
2025-11-19 13:40:53:  0: INFO: Could not find legacy (pre-10.0.26) AWS Portal File Transfer.
2025-11-19 13:40:53:  0: INFO: Legacy (pre-10.0.26) AWS Portal File Transfer is not installed on the system.
2025-11-19 13:40:53:  0: DEBUG: GlobalAssetTransferPreLoadJob: returning
2025-11-19 13:40:53:  0: DEBUG: StartJob: Starting Job...
2025-11-19 13:40:53:  0: INFO: Scrubbing the LD and DYLD LIBRARY paths
2025-11-19 13:40:53:  0: INFO: Prepping OFX cache
2025-11-19 13:40:53:  0: INFO: Checking Nuke temp path: /var/tmp/nuke-u1000
2025-11-19 13:40:53:  0: INFO: Path already exists
2025-11-19 13:40:53:  0: INFO: OFX cache prepped
2025-11-19 13:40:53:  0: INFO: Starting monitored managed process Nuke
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped "V:/SWA/all/scene/Ep03/sq0060/SH0180/comp/version/Ep03_sq0060_SH0180_comp_v004.nk" with "/mnt/igloo_swa_v/SWA/all/scene/Ep03/sq0060/SH0180/comp/version/Ep03_sq0060_SH0180_comp_v004.nk"
2025-11-19 13:40:53:  0: INFO: Enable Path Mapping: True
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " name V:/SWA/all/scene/Ep03/sq0060/SH0180/comp/version/Ep03_sq0060_SH0180_comp_v004.nk
2025-11-19 13:40:53:  0: " with " name /mnt/igloo_swa_v/SWA/all/scene/Ep03/sq0060/SH0180/comp/version/Ep03_sq0060_SH0180_comp_v004.nk
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " project_directory V:/SWA/all/scene/Ep00/sq0010/SH0060/comp/version
2025-11-19 13:40:53:  0: " with " project_directory /mnt/igloo_swa_v/SWA/all/scene/Ep00/sq0010/SH0060/comp/version
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " customOCIOConfigPath T:/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio
2025-11-19 13:40:53:  0: " with " customOCIOConfigPath /mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " multishot_custom "\{\n  \"PROJ_ROOT\": \"V:/\",\n  \"IMG_ROOT\": \"W:/\",\n  \"element\": \"beauty\",\n  \"frame\": \"####\",\n  \"ext\": \"exr\"\n\}"
2025-11-19 13:40:53:  0: " with " multishot_custom "\{\n  \"PROJ_ROOT\": \"/mnt/igloo_swa_v/\",\n  \"IMG_ROOT\": \"W:/\",\n  \"element\": \"beauty\",\n  \"frame\": \"####\",\n  \"ext\": \"exr\"\n\}"
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " PROJ_ROOT V:/
2025-11-19 13:40:53:  0: " with " PROJ_ROOT /mnt/igloo_swa_v/
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " IMG_ROOT W:/
2025-11-19 13:40:53:  0: " with " IMG_ROOT /mnt/igloo_swa_w/
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " addUserKnob {26 snow__retarget_from l "Retargeted From" T V:/SWA/all/scene/Ep00/sq0010/SH0020/comp/version/Ep00_sq0010_SH0020_comp_comp_v002.nk}
2025-11-19 13:40:53:  0: " with " addUserKnob {26 snow__retarget_from l "Retargeted From" T /mnt/igloo_swa_v/SWA/all/scene/Ep00/sq0010/SH0020/comp/version/Ep00_sq0010_SH0020_comp_comp_v002.nk}
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_grass.png
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_grass.png
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_Buildings.png
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_Buildings.png
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/all/scene/Ep02/sq0010/SH0010/anim/publish/v001/Ep02_sq0010_SH0010__SWA_Ep02_SH0010_camera.abc
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/all/scene/Ep02/sq0010/SH0010/anim/publish/v001/Ep02_sq0010_SH0010__SWA_Ep02_SH0010_camera.abc
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/all/asset/Setdress/exterior/PGExtGroundHill/hero/PGExtGroundHill_geo.abc
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/all/asset/Setdress/exterior/PGExtGroundHill/hero/PGExtGroundHill_geo.abc
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/all/asset/Setdress/exterior/PGExtGround/hero/PGExtGround_geo.abc
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/all/asset/Setdress/exterior/PGExtGround/hero/PGExtGround_geo.abc
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_clouds.png
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_clouds.png
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_Buildings.png
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_Buildings.png
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_clouds.png
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_clouds.png
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_sky.png
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/_fromClient/00_FromDevelopment/02_Designs/Ep02/ENV/Mattpaint/SW001_EV_02_Park_MattePainting_Final_sky.png
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_01_V1.jpg
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_01_V1.jpg
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_02_V1.jpg
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_02_V1.jpg
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: CheckPathMapping: Swapped " file V:/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_03_V1.jpg
2025-11-19 13:40:53:  0: " with " file /mnt/igloo_swa_v/SWA/_EpMaterial/Ep03/Colorscript/SW103_ColorScript_03_V1.jpg
2025-11-19 13:40:53:  0: "
2025-11-19 13:40:53:  0: INFO: Stdout Redirection Enabled: True
2025-11-19 13:40:53:  0: INFO: Asynchronous Stdout Enabled: False
2025-11-19 13:40:53:  0: INFO: Stdout Handling Enabled: True
2025-11-19 13:40:53:  0: INFO: Popup Handling Enabled: True
2025-11-19 13:40:53:  0: INFO: QT Popup Handling Enabled: False
2025-11-19 13:40:53:  0: INFO: WindowsForms10.Window.8.app.* Popup Handling Enabled: False
2025-11-19 13:40:53:  0: INFO: Using Process Tree: True
2025-11-19 13:40:53:  0: INFO: Hiding DOS Window: True
2025-11-19 13:40:53:  0: INFO: Creating New Console: False
2025-11-19 13:40:53:  0: INFO: Running as user: rocky
2025-11-19 13:40:53:  0: INFO: Executable: "/home/rocky/Nuke16.0v6/Nuke16.0"
2025-11-19 13:40:53:  0: INFO: Setting Process Environment Variable EDDY_DEVICE_LIST to 
2025-11-19 13:40:53:  0: INFO: Argument: -V 2 -t "/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/jobsData/691dc8dd4c1fd3ab7085ff76/thread0_tempGf70Q0/Ep03_sq0060_SH0180_comp_v004.nk"
2025-11-19 13:40:53:  0: INFO: Full Command: "/home/rocky/Nuke16.0v6/Nuke16.0" -V 2 -t "/var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/jobsData/691dc8dd4c1fd3ab7085ff76/thread0_tempGf70Q0/Ep03_sq0060_SH0180_comp_v004.nk"
2025-11-19 13:40:53:  0: INFO: Startup Directory: "/home/rocky/Nuke16.0v6"
2025-11-19 13:40:53:  0: INFO: Process Priority: BelowNormal
2025-11-19 13:40:53:  0: INFO: Process Affinity: default
2025-11-19 13:40:53:  0: INFO: Process is now running
2025-11-19 13:40:53:  0: DEBUG: StartJob: returning
2025-11-19 13:40:53:  0: Done executing plugin command of type 'Start Job'
2025-11-19 13:40:53:  0: Plugin rendering frame(s): 1032
2025-11-19 13:40:54:  0: Executing plugin command of type 'Render Task'
2025-11-19 13:40:54:  0: DEBUG: RenderTasks: called
2025-11-19 13:40:54:  0: DEBUG: RenderTasks: rendering frames 1032 to 1032
2025-11-19 13:40:54:  0: INFO: Rendering all enabled write nodes
2025-11-19 13:40:54:  0: STDOUT: Nuke 16.0v6, 64 bit, built Sep 11 2025.
2025-11-19 13:40:54:  0: STDOUT: Copyright (c) 2025 The Foundry Visionmongers Ltd.  All Rights Reserved.
2025-11-19 13:40:55:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:40:56:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:40:57:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:40:57:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:40:58:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:40:58:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:40:59:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:00:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:00:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:01:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:01:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:02:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:03:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:03:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:04:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:04:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/_pathsetup.py
2025-11-19 13:41:04:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/init.tcl
2025-11-19 13:41:04:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/init.py
2025-11-19 13:41:04:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/setenv.tcl
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/formats.tcl
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/caravr/init.py
2025-11-19 13:41:05:  0: STDOUT: Loading /mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot/init.py
2025-11-19 13:41:05:  0: STDOUT: Multishot: Batch mode detected - initializing variables only...
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/getenv.tcl
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/OCIOColorSpace.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/exrReader.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Reformat.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Shuffle2.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Remove.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Copy.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Premult.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Saturation.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Grade.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Merge2.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Multiply.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Crop.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/pngReader.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Transform.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Camera3.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/abcSceneReader.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ReadGeo2.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/abcReader.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Scene.tcl
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/MergeGeo.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Constant.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Cylinder.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Sphere.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ColorCorrect.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ScanlineRender.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/OCIODisplay.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/exrWriter.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Invert.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Radial.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Denoise2.so
2025-11-19 13:41:05:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/EXPTool.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/BlinkScript.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/CopyBBox.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Ramp.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ColorLookup.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Clamp.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Colorspace.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Dilate.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ColorMatrix.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Add.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/AdjBBox.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/NodeWrapper.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/EdgeBlur.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Axis2.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/FilterErode.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Gamma.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/IDistort.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Keymix.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Dissolve.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ZDefocus2.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Glint.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/LightWrap.gizmo
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Keyer.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/CCorrect.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/HueCorrect.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ContactSheet.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Mirror2.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/LayerContactSheet.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/pngWriter.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Cryptomatte.so
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/jpgReader.tcl
2025-11-19 13:41:05:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/jpegReader.so
2025-11-19 13:41:05:  0: STDOUT: [13:41:05 UTC] Read nuke script: /var/lib/Thinkbox/Deadline10/workers/ip-10-100-136-98/jobsData/691dc8dd4c1fd3ab7085ff76/thread0_tempGf70Q0/Ep03_sq0060_SH0180_comp_v004.nk
2025-11-19 13:41:05:  0: STDOUT: ================================================================================
2025-11-19 13:41:05:  0: STDOUT: MULTISHOT DEBUG: Printing ALL root knobs
2025-11-19 13:41:05:  0: STDOUT: ================================================================================
2025-11-19 13:41:05:  0: STDOUT: Total knobs on root: 61
2025-11-19 13:41:05:  0: STDOUT: Multishot JSON knobs:
2025-11-19 13:41:05:  0: STDOUT:   multishot_context = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   multishot_custom = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   multishot_variables = MISSING!
2025-11-19 13:41:05:  0: STDOUT: Individual variable knobs:
2025-11-19 13:41:05:  0: STDOUT:   ep = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   seq = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   shot = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   project = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   PROJ_ROOT = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   IMG_ROOT = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   first_frame = '1.0'
2025-11-19 13:41:05:  0: STDOUT:   last_frame = '100.0'
2025-11-19 13:41:05:  0: STDOUT: ================================================================================
2025-11-19 13:41:05:  0: STDOUT: Multishot: Manually creating individual knobs from JSON...
2025-11-19 13:41:05:  0: STDOUT: Multishot: Variables initialized in batch mode
2025-11-19 13:41:05:  0: STDOUT: ================================================================================
2025-11-19 13:41:05:  0: STDOUT: ================================================================================
2025-11-19 13:41:05:  0: STDOUT: MULTISHOT DEBUG: Printing ALL root knobs
2025-11-19 13:41:05:  0: STDOUT: ================================================================================
2025-11-19 13:41:05:  0: STDOUT: Total knobs on root: 61
2025-11-19 13:41:05:  0: STDOUT: Multishot JSON knobs:
2025-11-19 13:41:05:  0: STDOUT:   multishot_context = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   multishot_custom = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   multishot_variables = MISSING!
2025-11-19 13:41:05:  0: STDOUT: Individual variable knobs:
2025-11-19 13:41:05:  0: STDOUT:   ep = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   seq = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   shot = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   project = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   PROJ_ROOT = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   IMG_ROOT = MISSING!
2025-11-19 13:41:05:  0: STDOUT:   first_frame = '1.0'
2025-11-19 13:41:05:  0: STDOUT:   last_frame = '100.0'
2025-11-19 13:41:05:  0: STDOUT: ================================================================================
2025-11-19 13:41:05:  0: STDOUT: Multishot: Manually creating individual knobs from JSON...
2025-11-19 13:41:05:  0: STDOUT: Multishot: Variables initialized in batch mode
2025-11-19 13:41:05:  0: STDOUT: ================================================================================
2025-11-19 13:41:05:  0: STDOUT: >>> [13:41.05] ERROR: MultishotRead_lighting_MASTER_ATMOS_A: [value root.IMG_ROOT][value root.project]/all/scene/[value root.ep]/[value root.seq]/[value root.shot]/lighting/publish/[value parent.MultishotRead_lighting_MASTER_ATMOS_A.shot_version]/MASTER_ATMOS_A/MASTER_ATMOS_A.%04d.exr: Read error: No such file or directory
2025-11-19 13:41:05:  0: Done executing plugin command of type 'Render Task'

=======================================================
Details
=======================================================
Date: 11/19/2025 13:41:09
Frames: 1032
Elapsed Time: 00:00:00:18
Job Submit Date: 11/19/2025 13:40:45
Job User: katha.nab
Average RAM Usage: 1460762752 (5%)
Peak RAM Usage: 1545003008 (5%)
Average CPU Usage: 4%
Peak CPU Usage: 10%
Used CPU Clocks (x10^6 cycles): 33311
Total CPU Clocks (x10^6 cycles): 832762

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
Memory Usage: 1.4 GB / 30.4 GB (4%)
Free Disk Space: 116.391 GB 
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
