=======================================================
Error
=======================================================
Error: >>> [ 1:38.22] ERROR: MultishotRead_lighting_MASTER_CHAR_A: /SWA/all/scene/Ep02/sq0010/SH0010/lighting/publish/v002/MASTER_CHAR_A/MASTER_CHAR_A.1001.exr: Read error: No such file or directory
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
2025-11-20 01:38:07:  0: Loading Job's Plugin timeout is Disabled
2025-11-20 01:38:07:  0: SandboxedPlugin: Render Job As User disabled, running as current user 'rocky'
2025-11-20 01:38:09:  0: Executing plugin command of type 'Initialize Plugin'
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: debug logging enabled
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: m_pluginParamFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e70fc4c1fd3ab70860076/Nuke.param'
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: m_pluginScriptFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e70fc4c1fd3ab70860076/Nuke.py'
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: m_pluginPreLoadFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e70fc4c1fd3ab70860076/PluginPreLoad.py'
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: m_jobPreLoadFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e70fc4c1fd3ab70860076/JobPreLoad.py'
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: Checking for Plugin Pre-Load
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: Loading Plugin...
2025-11-20 01:38:09:  0: INFO: Executing plugin script '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e70fc4c1fd3ab70860076/Nuke.py'
2025-11-20 01:38:09:  0: INFO: Plugin execution sandbox using Python version 3
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: getting job user
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: setting job filenames
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: Obtaining Deadline plugin object
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: Setting internal variables and delegates
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: Preparing Environment Variables
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: Obtaining network settings
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: Initializing Deadline plugin
2025-11-20 01:38:09:  0: DEBUG: This is an advanced plugin job.
2025-11-20 01:38:09:  0: INFO: About: Nuke Plugin for Deadline
2025-11-20 01:38:09:  0: INFO: The job's environment will be merged with the current environment before rendering
2025-11-20 01:38:09:  0: DEBUG: InitializePlugin: returning
2025-11-20 01:38:09:  0: Done executing plugin command of type 'Initialize Plugin'
2025-11-20 01:38:09:  0: Start Job timeout is disabled.
2025-11-20 01:38:09:  0: Task timeout is disabled.
2025-11-20 01:38:09:  0: Loaded job: test_variable.nk (691e70fc4c1fd3ab70860076)
2025-11-20 01:38:09:  0: Executing plugin command of type 'Start Job'
2025-11-20 01:38:09:  0: DEBUG: StartJob: called
2025-11-20 01:38:09:  0: DEBUG: StartJob: Checking for Job Pre-Load
2025-11-20 01:38:09:  0: DEBUG: S3BackedCache Client is not installed.
2025-11-20 01:38:09:  0: DEBUG: GlobalAssetTransferPreLoadJob: called
2025-11-20 01:38:09:  0: INFO: Executing global asset transfer preload script '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e70fc4c1fd3ab70860076/GlobalAssetTransferPreLoad.py'
2025-11-20 01:38:09:  0: INFO: Looking for legacy (pre-10.0.26) AWS Portal File Transfer...
2025-11-20 01:38:09:  0: INFO: Looking for legacy (pre-10.0.26) File Transfer controller in /opt/Thinkbox/S3BackedCache/bin/task.py...
2025-11-20 01:38:09:  0: INFO: Could not find legacy (pre-10.0.26) AWS Portal File Transfer.
2025-11-20 01:38:09:  0: INFO: Legacy (pre-10.0.26) AWS Portal File Transfer is not installed on the system.
2025-11-20 01:38:09:  0: DEBUG: GlobalAssetTransferPreLoadJob: returning
2025-11-20 01:38:09:  0: DEBUG: StartJob: Starting Job...
2025-11-20 01:38:09:  0: INFO: Scrubbing the LD and DYLD LIBRARY paths
2025-11-20 01:38:09:  0: INFO: Prepping OFX cache
2025-11-20 01:38:10:  0: INFO: Checking Nuke temp path: /var/tmp/nuke-u1000
2025-11-20 01:38:10:  0: INFO: Path already exists
2025-11-20 01:38:10:  0: INFO: OFX cache prepped
2025-11-20 01:38:10:  0: INFO: Starting monitored managed process Nuke
2025-11-20 01:38:10:  0: CheckPathMapping: Swapped "V:/SWA/all/scene/Ep00/sq0010/SH0020/comp/test_variable.nk" with "/mnt/igloo_swa_v/SWA/all/scene/Ep00/sq0010/SH0020/comp/test_variable.nk"
2025-11-20 01:38:10:  0: INFO: Enable Path Mapping: False
2025-11-20 01:38:10:  0: INFO: Stdout Redirection Enabled: True
2025-11-20 01:38:10:  0: INFO: Asynchronous Stdout Enabled: False
2025-11-20 01:38:10:  0: INFO: Stdout Handling Enabled: True
2025-11-20 01:38:10:  0: INFO: Popup Handling Enabled: True
2025-11-20 01:38:10:  0: INFO: QT Popup Handling Enabled: False
2025-11-20 01:38:10:  0: INFO: WindowsForms10.Window.8.app.* Popup Handling Enabled: False
2025-11-20 01:38:10:  0: INFO: Using Process Tree: True
2025-11-20 01:38:10:  0: INFO: Hiding DOS Window: True
2025-11-20 01:38:10:  0: INFO: Creating New Console: False
2025-11-20 01:38:10:  0: INFO: Running as user: rocky
2025-11-20 01:38:10:  0: INFO: Executable: "/home/rocky/Nuke16.0v6/Nuke16.0"
2025-11-20 01:38:10:  0: INFO: Setting Process Environment Variable EDDY_DEVICE_LIST to 
2025-11-20 01:38:10:  0: INFO: Argument: -V 2 -t "/mnt/igloo_swa_v/SWA/all/scene/Ep00/sq0010/SH0020/comp/test_variable.nk"
2025-11-20 01:38:10:  0: INFO: Full Command: "/home/rocky/Nuke16.0v6/Nuke16.0" -V 2 -t "/mnt/igloo_swa_v/SWA/all/scene/Ep00/sq0010/SH0020/comp/test_variable.nk"
2025-11-20 01:38:10:  0: INFO: Startup Directory: "/home/rocky/Nuke16.0v6"
2025-11-20 01:38:10:  0: INFO: Process Priority: BelowNormal
2025-11-20 01:38:10:  0: INFO: Process Affinity: default
2025-11-20 01:38:10:  0: INFO: Process is now running
2025-11-20 01:38:10:  0: DEBUG: StartJob: returning
2025-11-20 01:38:10:  0: Done executing plugin command of type 'Start Job'
2025-11-20 01:38:10:  0: Plugin rendering frame(s): 1001
2025-11-20 01:38:10:  0: Executing plugin command of type 'Render Task'
2025-11-20 01:38:10:  0: DEBUG: RenderTasks: called
2025-11-20 01:38:10:  0: DEBUG: RenderTasks: rendering frames 1001 to 1001
2025-11-20 01:38:10:  0: INFO: Rendering all enabled write nodes
2025-11-20 01:38:10:  0: STDOUT: Nuke 16.0v6, 64 bit, built Sep 11 2025.
2025-11-20 01:38:10:  0: STDOUT: Copyright (c) 2025 The Foundry Visionmongers Ltd.  All Rights Reserved.
2025-11-20 01:38:11:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:12:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:13:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:13:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:14:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:14:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:15:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:16:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:16:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:17:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:17:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:18:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:19:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:19:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:20:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:20:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/_pathsetup.py
2025-11-20 01:38:20:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:21:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/init.tcl
2025-11-20 01:38:21:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/init.py
2025-11-20 01:38:22:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:22:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/setenv.tcl
2025-11-20 01:38:22:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/formats.tcl
2025-11-20 01:38:22:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/caravr/init.py
2025-11-20 01:38:22:  0: STDOUT: Loading /mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot/init.py
2025-11-20 01:38:22:  0: STDOUT: Multishot: Batch mode detected - initializing variables only...
2025-11-20 01:38:22:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/getenv.tcl
2025-11-20 01:38:22:  0: STDOUT: [ 1:38.22] Warning: Error loading custom OCIO config. The previously loaded config, /home/rocky/Nuke16.0v6/plugins/OCIOConfigs/configs/nuke-default/config.ocio, will be used. 
2025-11-20 01:38:22:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/CheckerBoard2.so
2025-11-20 01:38:22:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/OCIOColorSpace.so
2025-11-20 01:38:22:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/exrReader.so
2025-11-20 01:38:22:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/OCIODisplay.so
2025-11-20 01:38:22:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 01:38:22:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/pngWriter.so
2025-11-20 01:38:22:  0: STDOUT: [01:38:22 UTC] Read nuke script: /mnt/igloo_swa_v/SWA/all/scene/Ep00/sq0010/SH0020/comp/test_variable.nk
2025-11-20 01:38:22:  0: STDOUT: ================================================================================
2025-11-20 01:38:22:  0: STDOUT: MULTISHOT DEBUG: Printing ALL root knobs
2025-11-20 01:38:22:  0: STDOUT: ================================================================================
2025-11-20 01:38:22:  0: STDOUT: Total knobs on root: 112
2025-11-20 01:38:22:  0: STDOUT: Multishot JSON knobs:
2025-11-20 01:38:22:  0: STDOUT:   multishot_context = {"project":"SWA","ep":"Ep02","seq":"sq0010","shot":"SH0010","version":"v001","variance":"main"}
2025-11-20 01:38:22:  0: STDOUT:   multishot_custom = {"PROJ_ROOT":"V:/","IMG_ROOT":"W:/","element":"beauty","frame":"####","ext":"exr"}
2025-11-20 01:38:22:  0: STDOUT:   multishot_variables = 
2025-11-20 01:38:22:  0: STDOUT: Individual variable knobs:
2025-11-20 01:38:22:  0: STDOUT:   ep = 'Ep02'
2025-11-20 01:38:22:  0: STDOUT:   seq = 'sq0010'
2025-11-20 01:38:22:  0: STDOUT:   shot = 'SH0010'
2025-11-20 01:38:22:  0: STDOUT:   project = 'SWA'
2025-11-20 01:38:22:  0: STDOUT:   PROJ_ROOT = 'V:/'
2025-11-20 01:38:22:  0: STDOUT:   IMG_ROOT = 'W:/'
2025-11-20 01:38:22:  0: STDOUT:   first_frame = '1001.0'
2025-11-20 01:38:22:  0: STDOUT:   last_frame = '1043.0'
2025-11-20 01:38:22:  0: STDOUT: ================================================================================
2025-11-20 01:38:22:  0: STDOUT: DEBUG: Checking Read node frame ranges...
2025-11-20 01:38:22:  0: STDOUT:   Read node: MultishotRead_lighting_MASTER_CHAR_A
2025-11-20 01:38:22:  0: STDOUT:     first value: 1001
2025-11-20 01:38:22:  0: STDOUT:     first expression: {"\[value root.first_frame]"}
2025-11-20 01:38:22:  0: STDOUT:     last value: 1043
2025-11-20 01:38:22:  0: STDOUT:     last expression: {"\[value root.last_frame]"}
2025-11-20 01:38:22:  0: STDOUT: ================================================================================
2025-11-20 01:38:22:  0: STDOUT: Multishot: Manually creating individual knobs from JSON...
2025-11-20 01:38:22:  0: STDOUT: DEBUG: Checking for JSON knobs...
2025-11-20 01:38:22:  0: STDOUT: DEBUG: 'multishot_context' in all_knobs: True
2025-11-20 01:38:22:  0: STDOUT: DEBUG: 'multishot_custom' in all_knobs: True
2025-11-20 01:38:22:  0: STDOUT: DEBUG: context_json value: '{"project":"SWA","ep":"Ep02","seq":"sq0010","shot":"SH0010","version":"v001","variance":"main"}'
2025-11-20 01:38:22:  0: STDOUT: DEBUG: Parsed context_vars: {'project': 'SWA', 'ep': 'Ep02', 'seq': 'sq0010', 'shot': 'SH0010', 'version': 'v001', 'variance': 'main'}
2025-11-20 01:38:22:  0: STDOUT:   Set project = SWA
2025-11-20 01:38:22:  0: STDOUT:   Set ep = Ep02
2025-11-20 01:38:22:  0: STDOUT:   Set seq = sq0010
2025-11-20 01:38:22:  0: STDOUT:   Set shot = SH0010
2025-11-20 01:38:22:  0: STDOUT:   Set version = v001
2025-11-20 01:38:22:  0: STDOUT:   Set variance = main
2025-11-20 01:38:22:  0: STDOUT: DEBUG: custom_json value: '{"PROJ_ROOT":"V:/","IMG_ROOT":"W:/","element":"beauty","frame":"####","ext":"exr"}'
2025-11-20 01:38:22:  0: STDOUT: DEBUG: Parsed custom_vars: {'PROJ_ROOT': 'V:/', 'IMG_ROOT': 'W:/', 'element': 'beauty', 'frame': '####', 'ext': 'exr'}
2025-11-20 01:38:22:  0: STDOUT:   Set PROJ_ROOT = V:/
2025-11-20 01:38:22:  0: STDOUT:   Set IMG_ROOT = W:/
2025-11-20 01:38:22:  0: STDOUT: Multishot: Variables initialized in batch mode
2025-11-20 01:38:22:  0: STDOUT: ================================================================================
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Starting...
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Linux detected, replacing Windows paths...
2025-11-20 01:38:22:  0: STDOUT:   Root 'PROJ_ROOT': V:/ -> /mnt/igloo_swa_v/
2025-11-20 01:38:22:  0: STDOUT:   Root 'IMG_ROOT': W:/ -> /mnt/igloo_swa_w/
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Replaced 2 Windows paths with Linux paths
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: context_json = '{"project":"SWA","ep":"Ep02","seq":"sq0010","shot":"SH0010","version":"v001","variance":"main"}'
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Parsed context_vars = {'project': 'SWA', 'ep': 'Ep02', 'seq': 'sq0010', 'shot': 'SH0010', 'version': 'v001', 'variance': 'main'}
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Set project = SWA
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Set ep = Ep02
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Set seq = sq0010
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Set shot = SH0010
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Set version = v001
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Set variance = main
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: custom_json = '{"PROJ_ROOT":"V:/","IMG_ROOT":"W:/","element":"beauty","frame":"####","ext":"exr"}'
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Parsed custom_vars = {'PROJ_ROOT': 'V:/', 'IMG_ROOT': 'W:/', 'element': 'beauty', 'frame': '####', 'ext': 'exr'}
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Set PROJ_ROOT = V:/
2025-11-20 01:38:22:  0: STDOUT: Multishot onScriptLoad: Set IMG_ROOT = W:/
2025-11-20 01:38:22:  0: STDOUT: Multishot: Variables initialized from onScriptLoad callback
2025-11-20 01:38:22:  0: STDOUT: ================================================================================
2025-11-20 01:38:22:  0: STDOUT: MULTISHOT DEBUG: Printing ALL root knobs
2025-11-20 01:38:22:  0: STDOUT: ================================================================================
2025-11-20 01:38:22:  0: STDOUT: Total knobs on root: 112
2025-11-20 01:38:22:  0: STDOUT: Multishot JSON knobs:
2025-11-20 01:38:22:  0: STDOUT:   multishot_context = {"project":"SWA","ep":"Ep02","seq":"sq0010","shot":"SH0010","version":"v001","variance":"main"}
2025-11-20 01:38:22:  0: STDOUT:   multishot_custom = {"PROJ_ROOT":"V:/","IMG_ROOT":"W:/","element":"beauty","frame":"####","ext":"exr"}
2025-11-20 01:38:22:  0: STDOUT:   multishot_variables = 
2025-11-20 01:38:22:  0: STDOUT: Individual variable knobs:
2025-11-20 01:38:22:  0: STDOUT:   ep = 'Ep02'
2025-11-20 01:38:22:  0: STDOUT:   seq = 'sq0010'
2025-11-20 01:38:22:  0: STDOUT:   shot = 'SH0010'
2025-11-20 01:38:22:  0: STDOUT:   project = 'SWA'
2025-11-20 01:38:22:  0: STDOUT:   PROJ_ROOT = 'V:/'
2025-11-20 01:38:22:  0: STDOUT:   IMG_ROOT = 'W:/'
2025-11-20 01:38:22:  0: STDOUT:   first_frame = '1001.0'
2025-11-20 01:38:22:  0: STDOUT:   last_frame = '1043.0'
2025-11-20 01:38:22:  0: STDOUT: ================================================================================
2025-11-20 01:38:22:  0: STDOUT: DEBUG: Checking Read node frame ranges...
2025-11-20 01:38:22:  0: STDOUT:   Read node: MultishotRead_lighting_MASTER_CHAR_A
2025-11-20 01:38:22:  0: STDOUT:     first value: 1001
2025-11-20 01:38:22:  0: STDOUT:     first expression: {"\[value root.first_frame]"}
2025-11-20 01:38:22:  0: STDOUT:     last value: 1043
2025-11-20 01:38:22:  0: STDOUT:     last expression: {"\[value root.last_frame]"}
2025-11-20 01:38:22:  0: STDOUT: ================================================================================
2025-11-20 01:38:22:  0: STDOUT: Multishot: Manually creating individual knobs from JSON...
2025-11-20 01:38:22:  0: STDOUT: DEBUG: Checking for JSON knobs...
2025-11-20 01:38:22:  0: STDOUT: DEBUG: 'multishot_context' in all_knobs: True
2025-11-20 01:38:22:  0: STDOUT: DEBUG: 'multishot_custom' in all_knobs: True
2025-11-20 01:38:22:  0: STDOUT: DEBUG: context_json value: '{"project":"SWA","ep":"Ep02","seq":"sq0010","shot":"SH0010","version":"v001","variance":"main"}'
2025-11-20 01:38:22:  0: STDOUT: DEBUG: Parsed context_vars: {'project': 'SWA', 'ep': 'Ep02', 'seq': 'sq0010', 'shot': 'SH0010', 'version': 'v001', 'variance': 'main'}
2025-11-20 01:38:22:  0: STDOUT:   Set project = SWA
2025-11-20 01:38:22:  0: STDOUT:   Set ep = Ep02
2025-11-20 01:38:22:  0: STDOUT:   Set seq = sq0010
2025-11-20 01:38:22:  0: STDOUT:   Set shot = SH0010
2025-11-20 01:38:22:  0: STDOUT:   Set version = v001
2025-11-20 01:38:22:  0: STDOUT:   Set variance = main
2025-11-20 01:38:22:  0: STDOUT: DEBUG: custom_json value: '{"PROJ_ROOT":"V:/","IMG_ROOT":"W:/","element":"beauty","frame":"####","ext":"exr"}'
2025-11-20 01:38:22:  0: STDOUT: DEBUG: Parsed custom_vars: {'PROJ_ROOT': 'V:/', 'IMG_ROOT': 'W:/', 'element': 'beauty', 'frame': '####', 'ext': 'exr'}
2025-11-20 01:38:22:  0: STDOUT:   Set PROJ_ROOT = V:/
2025-11-20 01:38:22:  0: STDOUT:   Set IMG_ROOT = W:/
2025-11-20 01:38:22:  0: STDOUT: Multishot: Variables initialized in batch mode
2025-11-20 01:38:22:  0: STDOUT: ================================================================================
2025-11-20 01:38:22:  0: STDOUT: >>> [ 1:38.22] ERROR: MultishotRead_lighting_MASTER_CHAR_A: /SWA/all/scene/Ep02/sq0010/SH0010/lighting/publish/v002/MASTER_CHAR_A/MASTER_CHAR_A.1001.exr: Read error: No such file or directory
2025-11-20 01:38:22:  0: Done executing plugin command of type 'Render Task'

=======================================================
Details
=======================================================
Date: 11/20/2025 01:38:27
Frames: 1001
Elapsed Time: 00:00:00:20
Job Submit Date: 11/20/2025 01:38:03
Job User: katha.nab
Average RAM Usage: 1297766016 (4%)
Peak RAM Usage: 1388220416 (5%)
Average CPU Usage: 22%
Peak CPU Usage: 51%
Used CPU Clocks (x10^6 cycles): 34082
Total CPU Clocks (x10^6 cycles): 154917

=======================================================
Worker Information
=======================================================
Worker Name: ip-10-100-133-212
Version: v10.4.2.2 Release (313c3e8f5)
Operating System: Linux
Machine User: rocky
IP Address: 10.100.133.212
MAC Address: 06:DE:05:27:E4:5F
CPU Architecture: x86_64
CPUs: 4
CPU Usage: 20%
Memory Usage: 1.3 GB / 30.8 GB (4%)
Free Disk Space: 116.438 GB 
Video Card: Amazon.com, Inc. Device 1111

=======================================================
AWS Information
=======================================================
Instance ID: i-01fabc94725fd8212
Instance Type: r5a.xlarge
Image ID: ami-0955e2e4cdc80a5e7
Region: ap-southeast-1
Architecture: x86_64
Availability Zone: ap-southeast-1a
