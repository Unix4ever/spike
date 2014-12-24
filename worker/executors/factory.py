import logging

from worker.executors import *
from worker import executors
from worker.script_manager import ScriptManager

log = logging.getLogger(__name__)

class ExecutorFactory(object):

    def __init__(self):
        self.script_manager = ScriptManager()

    def create(self, task):
        """
        Create executor from the task
        """
        cls = executors.bindings.get(task.scenario_type, None)
        if not cls:
            log.error("Failed to create executor of type %s: no such type registered", task.scenario_type)
            return executors.ExecutorPrepareError("Failed to create executor of type %s" % task.scenario_type)

        executor = cls()
        script_file = self.get_script_file(task.scenario_id)
        if not script_file:
            raise executors.ExecutorPrepareError("Failed to get script file by id %s" % task.scenario_id)

        executor.prepare(script_file)
        return executor
    
    def get_script_file(self, script_id):
        return self.script_manager.get(script_id)

    def clean_cache(self):
        self.script_manager.clean()
