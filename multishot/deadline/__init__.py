"""
Multishot Deadline Integration

Provides custom Deadline submission with automatic environment variable injection.
"""

from .submit import submit_to_deadline, submit_to_deadline_vanilla, get_environment_variables

__all__ = ['submit_to_deadline', 'submit_to_deadline_vanilla', 'get_environment_variables']

