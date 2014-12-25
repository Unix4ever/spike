import logging

log = logging.getLogger(__name__)

class ProcessingError(Exception):
    pass

class SpikeTask(object):
    """
    Scenario task description
    """
    def __init__(self, message):
        self.valid = False
        if not self.validate(message):
            return

        self.id = message["id"]

        scenario = message["scenario"]
        self.scenario_id = scenario.get("id", None)
        self.scenario_type = scenario.get("type", None)
        
        self.valid = self.scenario_id is not None and self.scenario_type is not None

    def validate(self, message):
        """
        Validate that message has all required fields
        @param message: Dict from which to create this task
        """
        mandatory_fields = ["scenario", "id"]
        for field in mandatory_fields:
            if not message.get(field, None):
                log.error("Failed to process task %r, field %s", message, field)
                return False

        return True

class SpikeWorker(object):
    """
    Worker that can execute scenario
    """
    def __init__(self, executor_factory):
        self.executor_factory = executor_factory
        self.executors = {}

    def create_task(self, message):
        """
        Prepare executor for provided message
        """
        task = SpikeTask(message)
        if not task.valid:
            log.error("Failed to process task, task invalid")
            raise ProcessingError("Failed to process task, task invalid")

        executor = self.get_executor(task)
        if not executor:
            log.error("Failed to create executor for task %r", message)
            raise ProcessingError("Failed to process task, failed to create executor for task %r" % message)
        return task

    def process(self, task):
        """
        Process scenario
        """
        return self.get_executor(task).run(task)

    def get_executor(self, task):
        """
        Get executor for scenario
        @param task: task to process
        """
        id = (task.scenario_type, task.scenario_id)
        if id not in self.executors:
            self.executors[id] = self.executor_factory.create(task)

        return self.executors[id]

    def clean_cache(self):
        """
        Clean script cache
        """
        self.executor_factory.clean_cache()
