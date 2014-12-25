import logging

from worker.executors import executor

log = logging.getLogger(__name__)

@executor.bind("python")
class PythonExecutor(executor.Executor):

    def execute(self, task):
        """
        Run python script file
        """
        variables = {"runner": self, "stat": lambda *args, **kwargs: self.report(*args, scenario=task.scenario_id, **kwargs)}
        local_vars = {"runner": self, "output": {}}
        try:
            execfile(self.script_file, variables, local_vars)
        except:
            log.exception("Failed to execute scenario")
        return local_vars
