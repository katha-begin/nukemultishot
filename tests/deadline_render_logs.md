=======================================================
Error
=======================================================
Error: [ 4:55.33] ERROR: Camera1: //SWA/all/scene/Ep01/sq0010/SH0010/anim/publish/v001/Ep01_sq0010_SH0010__SWA_Ep01_SH0010_camera.abc: No such file or directory
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
2025-11-20 04:55:18:  0: Loading Job's Plugin timeout is Disabled
2025-11-20 04:55:18:  0: SandboxedPlugin: Render Job As User disabled, running as current user 'rocky'
2025-11-20 04:55:20:  0: Executing plugin command of type 'Initialize Plugin'
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: debug logging enabled
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: m_pluginParamFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e9ee04c1fd3ab708600c8/Nuke.param'
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: m_pluginScriptFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e9ee04c1fd3ab708600c8/Nuke.py'
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: m_pluginPreLoadFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e9ee04c1fd3ab708600c8/PluginPreLoad.py'
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: m_jobPreLoadFilename = '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e9ee04c1fd3ab708600c8/JobPreLoad.py'
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: Checking for Plugin Pre-Load
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: Loading Plugin...
2025-11-20 04:55:20:  0: INFO: Executing plugin script '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e9ee04c1fd3ab708600c8/Nuke.py'
2025-11-20 04:55:20:  0: INFO: Plugin execution sandbox using Python version 3
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: getting job user
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: setting job filenames
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: Obtaining Deadline plugin object
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: Setting internal variables and delegates
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: Preparing Environment Variables
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: Obtaining network settings
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: Initializing Deadline plugin
2025-11-20 04:55:20:  0: DEBUG: This is an advanced plugin job.
2025-11-20 04:55:20:  0: INFO: About: Nuke Plugin for Deadline
2025-11-20 04:55:20:  0: INFO: The job's environment will be merged with the current environment before rendering
2025-11-20 04:55:20:  0: DEBUG: InitializePlugin: returning
2025-11-20 04:55:20:  0: Done executing plugin command of type 'Initialize Plugin'
2025-11-20 04:55:20:  0: Start Job timeout is disabled.
2025-11-20 04:55:20:  0: Task timeout is disabled.
2025-11-20 04:55:20:  0: Loaded job: Ep01_sq0010_SH0010_comp_v005.nk (691e9ee04c1fd3ab708600c8)
2025-11-20 04:55:20:  0: Executing plugin command of type 'Start Job'
2025-11-20 04:55:20:  0: DEBUG: StartJob: called
2025-11-20 04:55:20:  0: DEBUG: StartJob: Checking for Job Pre-Load
2025-11-20 04:55:20:  0: DEBUG: S3BackedCache Client is not installed.
2025-11-20 04:55:20:  0: DEBUG: GlobalAssetTransferPreLoadJob: called
2025-11-20 04:55:20:  0: INFO: Executing global asset transfer preload script '/var/lib/Thinkbox/Deadline10/workers/ip-10-100-133-212/plugins/691e9ee04c1fd3ab708600c8/GlobalAssetTransferPreLoad.py'
2025-11-20 04:55:20:  0: INFO: Looking for legacy (pre-10.0.26) AWS Portal File Transfer...
2025-11-20 04:55:20:  0: INFO: Looking for legacy (pre-10.0.26) File Transfer controller in /opt/Thinkbox/S3BackedCache/bin/task.py...
2025-11-20 04:55:20:  0: INFO: Could not find legacy (pre-10.0.26) AWS Portal File Transfer.
2025-11-20 04:55:20:  0: INFO: Legacy (pre-10.0.26) AWS Portal File Transfer is not installed on the system.
2025-11-20 04:55:20:  0: DEBUG: GlobalAssetTransferPreLoadJob: returning
2025-11-20 04:55:20:  0: DEBUG: StartJob: Starting Job...
2025-11-20 04:55:20:  0: INFO: Scrubbing the LD and DYLD LIBRARY paths
2025-11-20 04:55:20:  0: INFO: Prepping OFX cache
2025-11-20 04:55:20:  0: INFO: Checking Nuke temp path: /var/tmp/nuke-u1000
2025-11-20 04:55:20:  0: INFO: Path already exists
2025-11-20 04:55:20:  0: INFO: OFX cache prepped
2025-11-20 04:55:20:  0: INFO: Starting monitored managed process Nuke
2025-11-20 04:55:20:  0: CheckPathMapping: Swapped "V:/SWA/all/scene/Ep01/sq0010/SH0010/comp/version/Ep01_sq0010_SH0010_comp_v005.nk" with "/mnt/igloo_swa_v/SWA/all/scene/Ep01/sq0010/SH0010/comp/version/Ep01_sq0010_SH0010_comp_v005.nk"
2025-11-20 04:55:20:  0: INFO: Enable Path Mapping: False
2025-11-20 04:55:20:  0: INFO: Stdout Redirection Enabled: True
2025-11-20 04:55:20:  0: INFO: Asynchronous Stdout Enabled: False
2025-11-20 04:55:20:  0: INFO: Stdout Handling Enabled: True
2025-11-20 04:55:20:  0: INFO: Popup Handling Enabled: True
2025-11-20 04:55:20:  0: INFO: QT Popup Handling Enabled: False
2025-11-20 04:55:20:  0: INFO: WindowsForms10.Window.8.app.* Popup Handling Enabled: False
2025-11-20 04:55:20:  0: INFO: Using Process Tree: True
2025-11-20 04:55:20:  0: INFO: Hiding DOS Window: True
2025-11-20 04:55:20:  0: INFO: Creating New Console: False
2025-11-20 04:55:20:  0: INFO: Running as user: rocky
2025-11-20 04:55:20:  0: INFO: Executable: "/home/rocky/Nuke16.0v6/Nuke16.0"
2025-11-20 04:55:20:  0: INFO: Setting Process Environment Variable EDDY_DEVICE_LIST to 
2025-11-20 04:55:20:  0: INFO: Argument: -V 2 -t "/mnt/igloo_swa_v/SWA/all/scene/Ep01/sq0010/SH0010/comp/version/Ep01_sq0010_SH0010_comp_v005.nk"
2025-11-20 04:55:20:  0: INFO: Full Command: "/home/rocky/Nuke16.0v6/Nuke16.0" -V 2 -t "/mnt/igloo_swa_v/SWA/all/scene/Ep01/sq0010/SH0010/comp/version/Ep01_sq0010_SH0010_comp_v005.nk"
2025-11-20 04:55:20:  0: INFO: Startup Directory: "/home/rocky/Nuke16.0v6"
2025-11-20 04:55:20:  0: INFO: Process Priority: BelowNormal
2025-11-20 04:55:20:  0: INFO: Process Affinity: default
2025-11-20 04:55:20:  0: INFO: Process is now running
2025-11-20 04:55:20:  0: DEBUG: StartJob: returning
2025-11-20 04:55:20:  0: Done executing plugin command of type 'Start Job'
2025-11-20 04:55:20:  0: Plugin rendering frame(s): 1001-1010
2025-11-20 04:55:21:  0: Executing plugin command of type 'Render Task'
2025-11-20 04:55:21:  0: DEBUG: RenderTasks: called
2025-11-20 04:55:21:  0: DEBUG: RenderTasks: rendering frames 1001 to 1010
2025-11-20 04:55:21:  0: INFO: Rendering all enabled write nodes
2025-11-20 04:55:21:  0: STDOUT: Nuke 16.0v6, 64 bit, built Sep 11 2025.
2025-11-20 04:55:21:  0: STDOUT: Copyright (c) 2025 The Foundry Visionmongers Ltd.  All Rights Reserved.
2025-11-20 04:55:22:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:23:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:23:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:24:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:24:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:25:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:26:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:26:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:27:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:27:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:28:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:29:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:29:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:30:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:30:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:31:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:31:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/_pathsetup.py
2025-11-20 04:55:32:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:32:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/init.tcl
2025-11-20 04:55:32:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/init.py
2025-11-20 04:55:32:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/setenv.tcl
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/formats.tcl
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/caravr/init.py
2025-11-20 04:55:33:  0: STDOUT: Loading /mnt/ppr_dev_t/pipeline/development/nuke/nukemultishot/init.py
2025-11-20 04:55:33:  0: STDOUT: ================================================================================
2025-11-20 04:55:33:  0: STDOUT: MULTISHOT DEBUG: Checking OCIO environment variable
2025-11-20 04:55:33:  0: STDOUT: ================================================================================
2025-11-20 04:55:33:  0: STDOUT: OCIO environment variable: /mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio
2025-11-20 04:55:33:  0: STDOUT:   -> OCIO config file EXISTS: /mnt/ppr_dev_t/pipeline/ocio/aces_2.0/studio-config-v1.0.0_aces-v1.3_ocio-v2.0.ocio
2025-11-20 04:55:33:  0: STDOUT: ================================================================================
2025-11-20 04:55:33:  0: STDOUT: Multishot: Batch mode detected - initializing variables only...
2025-11-20 04:55:33:  0: STDOUT: ================================================================================
2025-11-20 04:55:33:  0: STDOUT: MULTISHOT DEBUG: Printing ALL root knobs
2025-11-20 04:55:33:  0: STDOUT: ================================================================================
2025-11-20 04:55:33:  0: STDOUT: Total knobs on root: 61
2025-11-20 04:55:33:  0: STDOUT: Multishot JSON knobs:
2025-11-20 04:55:33:  0: STDOUT:   multishot_context = MISSING!
2025-11-20 04:55:33:  0: STDOUT:   multishot_custom = MISSING!
2025-11-20 04:55:33:  0: STDOUT:   multishot_variables = MISSING!
2025-11-20 04:55:33:  0: STDOUT: Individual variable knobs:
2025-11-20 04:55:33:  0: STDOUT:   ep = MISSING!
2025-11-20 04:55:33:  0: STDOUT:   seq = MISSING!
2025-11-20 04:55:33:  0: STDOUT:   shot = MISSING!
2025-11-20 04:55:33:  0: STDOUT:   project = MISSING!
2025-11-20 04:55:33:  0: STDOUT:   PROJ_ROOT = MISSING!
2025-11-20 04:55:33:  0: STDOUT:   IMG_ROOT = MISSING!
2025-11-20 04:55:33:  0: STDOUT:   first_frame = '1.0'
2025-11-20 04:55:33:  0: STDOUT:   last_frame = '100.0'
2025-11-20 04:55:33:  0: STDOUT: ================================================================================
2025-11-20 04:55:33:  0: STDOUT: DEBUG: Checking Read node frame ranges...
2025-11-20 04:55:33:  0: STDOUT: ================================================================================
2025-11-20 04:55:33:  0: STDOUT: Multishot: Manually creating individual knobs from JSON...
2025-11-20 04:55:33:  0: STDOUT: DEBUG: Checking for JSON knobs...
2025-11-20 04:55:33:  0: STDOUT: DEBUG: 'multishot_context' in all_knobs: False
2025-11-20 04:55:33:  0: STDOUT: DEBUG: 'multishot_custom' in all_knobs: False
2025-11-20 04:55:33:  0: STDOUT: DEBUG: Created Multishot tab
2025-11-20 04:55:33:  0: STDOUT: DEBUG: multishot_context knob does NOT exist!
2025-11-20 04:55:33:  0: STDOUT: DEBUG: Knob PROJ_ROOT does NOT exist - trying to create from JSON...
2025-11-20 04:55:33:  0: STDOUT: DEBUG: Knob IMG_ROOT does NOT exist - trying to create from JSON...
2025-11-20 04:55:33:  0: STDOUT: Multishot: Variables initialized in batch mode
2025-11-20 04:55:33:  0: STDOUT: ================================================================================
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/getenv.tcl
2025-11-20 04:55:33:  0: DEBUG: PopupHandler.CheckForPopups: Getting popup handles
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/OCIOColorSpace.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/exrReader.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Shuffle2.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Premult.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Copy.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Reformat.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Remove.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Saturation.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Grade.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Merge2.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Multiply.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Crop.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/ContactSheet.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/movReader.so
2025-11-20 04:55:33:  0: STDOUT: [ 4:55.33] Warning: Could not find value "rec709" for "colorspace". It will be appended to the menu list.
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Constant.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Invert.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Radial.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Transform.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/BasicMaterial.so
2025-11-20 04:55:33:  0: STDOUT: Loading /home/rocky/Nuke16.0v6/plugins/Camera3.so
2025-11-20 04:55:33:  0: STDOUT: [ 4:55.33] ERROR: Camera1: //SWA/all/scene/Ep01/sq0010/SH0010/anim/publish/v001/Ep01_sq0010_SH0010__SWA_Ep01_SH0010_camera.abc: No such file or directory
2025-11-20 04:55:33:  0: Done executing plugin command of type 'Render Task'

=======================================================
Details
=======================================================
Date: 11/20/2025 04:55:42
Frames: 1001-1010
Elapsed Time: 00:00:00:24
Job Submit Date: 11/20/2025 04:53:51
Job User: katha.nab
Average RAM Usage: 1512735616 (5%)
Peak RAM Usage: 2454622208 (8%)
Average CPU Usage: 28%
Peak CPU Usage: 100%
Used CPU Clocks (x10^6 cycles): 57639
Total CPU Clocks (x10^6 cycles): 205852

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
CPU Usage: 17%
Memory Usage: 1.4 GB / 30.8 GB (4%)
Free Disk Space: 116.422 GB 
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
