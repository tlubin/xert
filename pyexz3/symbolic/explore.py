# Copyright: see copyright.txt

from collections import deque
import logging
import os

from .z3_wrap import Z3Wrapper
from .path_to_constraint import PathToConstraint
from .invocation import FunctionInvocation
from .symbolic_types import symbolic_type, SymbolicType

log = logging.getLogger("se.conc")

class ExplorationEngine:
    def __init__(self, funcinv):
        self.invocation = funcinv
        # the input to the function
        self.symbolic_inputs = {}  # string -> SymbolicType
        # initialize
        for n in funcinv.getNames():
            self.symbolic_inputs[n] = funcinv.createArgumentValue(n)

        self.constraints_to_solve = deque([])
        self.num_processed_constraints = 0

        self.path = PathToConstraint(lambda c : self.addConstraint(c))
        # link up SymbolicObject to PathToConstraint in order to intercept control-flow
        symbolic_type.SymbolicObject.SI = self.path

        self.solver = Z3Wrapper()

        # outputs
        self.generated_inputs = []
        self.C = []
        self.execution_return_values = []

    def addConstraint(self, constraint):
        self.constraints_to_solve.append(constraint)
        # make sure to remember the input that led to this constraint
        constraint.inputs = self._getInputs()
        #self.C.append((self._getInputs(), constraint))

    def explore(self, max_iterations=0):
        self._oneExecution()

        iterations = 1
        if max_iterations != 0 and iterations >= max_iterations:
            log.debug("Maximum number of iterations reached, terminating")
            return self.execution_return_values

        while not self._isExplorationComplete():
            selected = self.constraints_to_solve.popleft()
            if selected.processed:
                continue
            self._setInputs(selected.inputs)

            print("Selected constraint %s" % selected)
            print("Selected input %s" % selected.inputs)
            asserts, query = selected.getAssertsAndQuery()
            print("asserts %s" % asserts)
            print("query %s" % query)
            model = self.solver.findCounterexample(asserts, query)

            if model == None:
                continue
            else:
                self.C.append(selected.inputs)
                self.C.append(selected)
                vardict = {}
                for name in model.keys():
                    print('Counterexample name: %s' % name),
                    print('Counterexample val: %s' % model[name])
                    self._updateSymbolicParameter(name,model[name])
                    vardict[name] = model[name]
            self._oneExecution(selected)
            print('\n')

            iterations += 1
            self.num_processed_constraints += 1

            if max_iterations != 0 and iterations >= max_iterations:
                log.info("Maximum number of iterations reached, terminating")
                break

        return self.generated_inputs, self.execution_return_values, self.C

    # private

    def _updateSymbolicParameter(self, name, val):
        self.symbolic_inputs[name] = self.invocation.createArgumentValue(name,val)

    def _getInputs(self):
        return self.symbolic_inputs.copy()

    def _setInputs(self,d):
        self.symbolic_inputs = d

    def _isExplorationComplete(self):
        num_constr = len(self.constraints_to_solve)
        if num_constr == 0:
            log.info("Exploration complete")
            return True
        else:
            print("%d constraints yet to solve (total: %d, already solved: %d)" % (num_constr, self.num_processed_constraints + num_constr, self.num_processed_constraints))
            print('\n')
            return False

    def _getConcrValue(self,v):
        if isinstance(v,SymbolicType):
            return v.getConcrValue()
        else:
            return v

    def _recordInputs(self):
        args = self.symbolic_inputs
        inputs = [ (k,self._getConcrValue(args[k])) for k in args ]
        self.generated_inputs.append(inputs)
        #print(inputs)

    def _oneExecution(self,expected_path=None):
        self._recordInputs()
        self.path.reset(expected_path)
        ret = self.invocation.callFunction(self.symbolic_inputs)
        #print(ret)
        self.execution_return_values.append(ret)

