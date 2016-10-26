from enum import Enum

class InputAux:
    _defaultPrompt = ''
    _defaultFailureReturn = None

    def _defaultShaping (self, ipt):
        return ipt

    def _defaultValidation (self, shapedIpt):
        return True

    def __init__ (self, prompt = None, shaping = None,
            validation = None, failureReturn = None):
        self.prompt = self._defaultPrompt if prompt is None else prompt
        self.shaping = self._defaultShaping if shaping is None else shaping
        self.validation = self._defaultValidation if validation is None else validation
        self.failureReturn = self._defaultFailureReturn if failureReturn is None else failureReturn
        self.rowInput = None
        self.value = None

    def input (self):
        self.rowInput = input (self.prompt)
        ipt = self.shaping (self.rowInput)
        if self.validation (ipt):
            self.value = ipt
        else:
            self.value = self.failureReturn
        return self.value


class InputNothrow (InputAux):
    class _Nothing (Enum):
        nothing = 1

    def _shapingNothrow (self, rowInput):
        try:
            return self.shaping (rowInput)
        except:
            return self._Nothing.nothing

    def _validationNothrow (self, ipt):
        try:
            if self.validation (ipt):
                return True
            else:
                return False
        except:
            return False

    def input (self):
        self.rowInput = input (self.prompt)
        ipt = self._shapingNothrow (self.rowInput)
        if ipt == self._Nothing.nothing:
            self.value = self.failureReturn
        elif self._validationNothrow (ipt):
            self.value = ipt
        else:
            self.value = self.failureReturn
        return self.value


class InputLoop (InputNothrow):
    def _defaultInterval (self, rowIpt):
        pass

    def __init__ (self, prompt = None, shaping = None,
            validation = None, failureReturn = None, interval = None):
        super ().__init__ (prompt, shaping, validation, failureReturn)
        self.interval = self._defaultInterval if interval is None else interval

    def inputLoop (self):
        while True:
            self.rowInput = input (self.prompt)
            ipt = self._shapingNothrow (self.rowInput)
            if ipt != self._Nothing.nothing and self._validationNothrow (ipt):
                self.value = ipt
                return self.value
            self.interval (self.rowInput)

