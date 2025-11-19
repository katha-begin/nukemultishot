"""
Deadline Farm Submission for Multishot Workflow System.

Handles submission of farm scripts to Deadline with dependencies.
"""

import os
import sys
from typing import List, Dict, Optional

from ..utils.logging import get_logger


class DeadlineFarmSubmitter:
    """Handles Deadline submission for farm scripts."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
    def submit_write_nodes(
        self,
        farm_script_path: str,
        write_nodes: List[Dict],
        shot_data: Dict,
        frame_range: tuple
    ) -> List[str]:
        """
        Submit Write nodes as separate Deadline jobs with dependencies.
        
        Args:
            farm_script_path: Path to farm script
            write_nodes: List of Write node info dicts with 'node', 'name', 'order'
            shot_data: Shot context (project, ep, seq, shot)
            frame_range: (first_frame, last_frame)
            
        Returns:
            List of Deadline job IDs
        """
        try:
            import nuke
            
            self.logger.info(f"Submitting {len(write_nodes)} Write nodes to Deadline...")
            
            # Get Deadline command
            deadline_command = self._get_deadline_command()
            if not deadline_command:
                raise Exception("Deadline command not found")
            
            job_ids = []
            previous_job_ids = []  # Track previous jobs for dependencies
            
            for idx, write_info in enumerate(write_nodes):
                write_node = write_info['node']
                write_name = write_info['name']
                order = write_info['order']
                
                self.logger.info(f"Submitting job {idx + 1}/{len(write_nodes)}: {write_name}")
                
                # Create job info file
                job_info_path = self._create_job_info_file(
                    farm_script_path,
                    write_name,
                    shot_data,
                    frame_range,
                    order,
                    previous_job_ids
                )
                
                # Create plugin info file
                plugin_info_path = self._create_plugin_info_file(
                    farm_script_path,
                    write_name
                )
                
                # Submit to Deadline
                job_id = self._submit_to_deadline(
                    deadline_command,
                    job_info_path,
                    plugin_info_path
                )
                
                if job_id:
                    job_ids.append(job_id)
                    previous_job_ids.append(job_id)  # This job becomes a dependency for next jobs
                    self.logger.info(f"Submitted job: {job_id}")
                else:
                    self.logger.error(f"Failed to submit job for {write_name}")
            
            self.logger.info(f"Successfully submitted {len(job_ids)} jobs to Deadline")
            return job_ids
            
        except Exception as e:
            self.logger.error(f"Error submitting to Deadline: {e}")
            raise
            
    def _get_deadline_command(self) -> Optional[str]:
        """Get Deadline command path."""
        try:
            import platform
            
            deadline_path = os.environ.get('DEADLINE_PATH', '')
            if not deadline_path:
                self.logger.error("DEADLINE_PATH not set")
                return None
            
            if platform.system() == 'Windows':
                deadline_command = os.path.join(deadline_path, 'deadlinecommand.exe')
            else:
                deadline_command = os.path.join(deadline_path, 'deadlinecommand')
            
            if not os.path.exists(deadline_command):
                self.logger.error(f"Deadline command not found: {deadline_command}")
                return None
            
            return deadline_command
            
        except Exception as e:
            self.logger.error(f"Error getting Deadline command: {e}")
            return None

    def _create_job_info_file(
        self,
        farm_script_path: str,
        write_name: str,
        shot_data: Dict,
        frame_range: tuple,
        order: int,
        dependency_job_ids: List[str]
    ) -> str:
        """Create Deadline job info file."""
        try:
            import tempfile

            # Build job name
            script_name = os.path.splitext(os.path.basename(farm_script_path))[0]
            job_name = f"{script_name} - {write_name}"

            # Build batch name
            shot_key = f"{shot_data['project']}_{shot_data['ep']}_{shot_data['seq']}_{shot_data['shot']}"
            batch_name = shot_key

            # Get output directory from Write node
            output_dir = ""
            try:
                import nuke
                write_node = nuke.toNode(write_name)
                if write_node and write_node.knob('file'):
                    output_path = write_node['file'].value()
                    output_dir = os.path.dirname(output_path)
            except:
                pass

            # Create job info content
            first_frame, last_frame = frame_range
            job_info = [
                f"Name={job_name}",
                f"BatchName={batch_name}",
                f"Department=comp",
                f"Pool=nuke",
                f"Group=linux",
                f"Priority=50",
                f"Frames={first_frame}-{last_frame}",
                f"ChunkSize=10",
            ]

            # Add output directory if available
            if output_dir:
                job_info.append(f"OutputDirectory0={output_dir}")

            # Add dependencies
            if dependency_job_ids:
                job_info.append(f"JobDependencies={','.join(dependency_job_ids)}")

            # Write to temp file
            fd, job_info_path = tempfile.mkstemp(suffix='.job', text=True)
            with os.fdopen(fd, 'w') as f:
                f.write('\n'.join(job_info))

            self.logger.debug(f"Created job info file: {job_info_path}")
            return job_info_path

        except Exception as e:
            self.logger.error(f"Error creating job info file: {e}")
            raise

    def _create_plugin_info_file(self, farm_script_path: str, write_name: str) -> str:
        """Create Deadline plugin info file."""
        try:
            import tempfile
            import nuke

            # Get Nuke version
            nuke_version = f"{nuke.NUKE_VERSION_MAJOR}.{nuke.NUKE_VERSION_MINOR}"

            # Create plugin info content
            plugin_info = [
                f"SceneFile={farm_script_path}",
                f"Version={nuke_version}",
                f"WriteNode={write_name}",
                "UseGpu=True",
                "GpuOverride=0",
                "BatchMode=True",
                "BatchModeIsMovie=False",
                "ContinueOnError=False",
                "EnforceRenderOrder=False",
                "NukeX=True",
                "RenderMode=Use Scene Settings",
                "StackSize=0",
                "Threads=0",
                "UseNodeRange=False",
            ]

            # Write to temp file
            fd, plugin_info_path = tempfile.mkstemp(suffix='.plugin', text=True)
            with os.fdopen(fd, 'w') as f:
                f.write('\n'.join(plugin_info))

            self.logger.debug(f"Created plugin info file: {plugin_info_path}")
            return plugin_info_path

        except Exception as e:
            self.logger.error(f"Error creating plugin info file: {e}")
            raise

    def _submit_to_deadline(
        self,
        deadline_command: str,
        job_info_path: str,
        plugin_info_path: str
    ) -> Optional[str]:
        """Submit job to Deadline and return job ID."""
        try:
            import subprocess

            # Build command
            cmd = [
                deadline_command,
                job_info_path,
                plugin_info_path
            ]

            self.logger.debug(f"Executing: {' '.join(cmd)}")

            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse output for job ID
            if result.returncode == 0:
                output = result.stdout
                # Look for "JobID=" in output
                for line in output.split('\n'):
                    if line.startswith('JobID='):
                        job_id = line.split('=')[1].strip()
                        return job_id

                self.logger.warning("Job submitted but no JobID found in output")
                return None
            else:
                self.logger.error(f"Deadline submission failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            self.logger.error("Deadline submission timed out")
            return None
        except Exception as e:
            self.logger.error(f"Error submitting to Deadline: {e}")
            return None
        finally:
            # Cleanup temp files
            try:
                if os.path.exists(job_info_path):
                    os.remove(job_info_path)
                if os.path.exists(plugin_info_path):
                    os.remove(plugin_info_path)
            except:
                pass

