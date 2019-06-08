from abc import abstractmethod
from pyftsm.ftsm import FTSM, FTSMTransitions

class ActionSMBase(FTSM):
    def __init__(self, name, dependencies, max_recovery_attempts=1):
        super(ActionSMBase, self).__init__(name, dependencies, max_recovery_attempts)
        self.execution_requested = False
        self.preempted = False
        self.goal = None
        self.result = None

    def init(self):
        return FTSMTransitions.INITIALISED

    def configuring(self):
        return FTSMTransitions.DONE_CONFIGURING

    def ready(self):
        if self.execution_requested:
            self.result = None
            self.execution_requested = False
            return FTSMTransitions.RUN
        else:
            if self.result:
                self.result = None
            return FTSMTransitions.WAIT

    def running(self):
        return FTSMTransitions.DONE

    def recovering(self):
        return FTSMTransitions.DONE_RECOVERING

    @abstractmethod
    def set_result(self, success):
        pass
