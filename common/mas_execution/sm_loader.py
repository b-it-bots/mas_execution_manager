from __future__ import print_function
import oyaml as yaml

from mas_execution.sm_params import StateParams, StateMachineParams, SMFileKeys

class SMLoader(object):
    '''An interface for loading state machine configuration files

    Author -- Alex Mitrevski
    Email -- aleksandar.mitrevski@h-brs.de

    '''
    @staticmethod
    def load_sm(sm_file, parent_sm_file=''):
        '''Returns an 'mas_execution_manager.sm_params.StateMachineParams'
        object containing state machine description parameters

        Keyword arguments:
        sm_file -- path to a state machine file in yaml format
        parent_sm_file -- path to a parent state machine file in yaml format

        '''
        sm_params = StateMachineParams()

        # we load the state machine file
        sm_data = SMLoader.__load_sm_file(sm_file)

        # if we have a parent state machine, we first load its parameters
        # and then update them based on the child config
        parent_sm_data = None
        if parent_sm_file:
            parent_sm_data = SMLoader.__load_sm_file(parent_sm_file)
            sm_params = SMLoader.__load_parent_config(parent_sm_data)

        # we replace the state machine ID if it's redefined in the child config
        if SMFileKeys.ID in sm_data:
            sm_params.id = sm_data[SMFileKeys.ID]

        # we add any new states that are defined in the child config
        # to the list of state machine states
        if SMFileKeys.STATES in sm_data:
            states = list(set(sm_params.states).union(set(sm_data[SMFileKeys.STATES])))
            sm_params.states = states

        # we add any new outcomes that are defined in the child config
        # to the list of state machine outcomes
        if SMFileKeys.OUTCOMES in sm_data:
            outcomes = list(set(sm_params.outcomes).union(set(sm_data[SMFileKeys.OUTCOMES])))
            sm_params.outcomes = outcomes

        # we add any new states that are defined in the child config
        # to the list of state machine states; we also remove states
        # defined in the parent state machine config if the child config
        # specifies that they should be removed; states that are redefined
        # in the child config are replaced by the child definition
        for state_description in sm_data[SMFileKeys.STATE_DESCRIPTIONS]:
            state_data = state_description[SMFileKeys.STATE]
            state_name = state_data[SMFileKeys.STATE_NAME]
            if state_name not in sm_params.states:
                error = '[sm_loader] State {0} not declared in the state list'.format(state_name)
                raise AssertionError(error)

            if SMFileKeys.REMOVE_STATE in state_data:
                sm_params.states.remove(state_name)
                if state_name in sm_params.state_params:
                    sm_params.state_params.pop(state_name, None)
            else:
                state_params = None
                if state_name in sm_params.state_params:
                    state_params = sm_params.state_params[state_name]
                else:
                    state_params = StateParams()

                state_params.name = state_name

                if SMFileKeys.STATE_MODULE_NAME in state_data:
                    state_params.state_module_name = state_data[SMFileKeys.STATE_MODULE_NAME]
                else:
                    print('[sm_loader, WARNING] State module name not defined for state {0}; reusing parent module name'.format(state_params.name))
                    if not state_params.state_module_name:
                        error = 'state_module_name cannot be empty (it is empty for state {0})'.format(state_name)
                        raise AssertionError(error)

                if SMFileKeys.STATE_CLASS_NAME in state_data:
                    state_params.state_class_name = state_data[SMFileKeys.STATE_CLASS_NAME]
                else:
                    print('[sm_loader, WARNING] State class name not defined for state {0}; reusing parent class name'.format(state_params.name))
                    if not state_params.state_class_name:
                        error = 'state_class_name cannot be empty (it is empty for state {0})'.format(state_name)
                        raise AssertionError(error)

                if SMFileKeys.TRANSITIONS in state_data:
                    for transition in state_data[SMFileKeys.TRANSITIONS]:
                        transition_data = transition[SMFileKeys.TRANSITION]
                        transition_name = transition_data[SMFileKeys.TRANSITION_NAME]
                        resulting_state = transition_data[SMFileKeys.RESULT_STATE]
                        if resulting_state not in sm_params.states and \
                           resulting_state not in sm_params.outcomes:
                            error = 'Invalid transition {0} for state {1}\n'.format(state_name,
                                                                                    transition_name)
                            error += '-> {0} not declared in the state or outcome list'.format(resulting_state)
                            raise AssertionError(error)

                        state_params.transitions[transition_name] = resulting_state
                else:
                    print('[sm_loader, WARNING] Transitions not defined for state {0}; reusing parent state machine transitions (if any)'.format(state_params.name))

                if SMFileKeys.ARGS in state_data:
                    for arg in state_data[SMFileKeys.ARGS]:
                        arg_data = arg[SMFileKeys.ARG]
                        try:
                            state_params.args[arg_data[SMFileKeys.ARG_NAME]] = \
                            arg_data[SMFileKeys.ARG_VALUE]
                        except TypeError as exc:
                            print('[sm_loader, ERROR] Error loading argument {0}'.format(arg_data))
                            print('[sm_loader, ERROR] {0}', str(exc))
                else:
                    print('[sm_loader, INFO] No arguments passed for state {0}; reusing parent state parameters (if any)'.format(state_params.name))

                for arg_name, arg_value in sm_params.global_params.items():
                    state_params.args[arg_name] = arg_value

                # we add the state machine ID and the state name as additional state arguments
                state_params.args['sm_id'] = sm_params.id
                state_params.args['state_name'] = state_params.name

                sm_params.state_params[state_params.name] = state_params

        # we add any new arguments that are defined in the child config
        # to the list of global state machine arguments
        if SMFileKeys.ARGS in sm_data:
            for arg in sm_data[SMFileKeys.ARGS]:
                arg_data = arg[SMFileKeys.ARG]
                try:
                    sm_params.global_params[arg_data[SMFileKeys.ARG_NAME]] = \
                    arg_data[SMFileKeys.ARG_VALUE]
                except TypeError as exc:
                    print('[sm_loader, ERROR] Error loading argument {0}'.format(arg_data))
                    print('[sm_loader, ERROR] {0}', str(exc))

        return sm_params

    @staticmethod
    def __load_sm_file(sm_file):
        '''Loads the file whose path is specified by 'sm_file'

        Keyword arguments:
        sm_file -- path to a state machine file in yaml format

        '''
        sm_data = None
        try:
            with open(sm_file, 'r') as file_handle:
                sm_data = yaml.safe_load(file_handle)
        except Exception as exc:
            print('[sm_loader, ERROR] {0}'.format(str(exc)))
            raise
        return sm_data

    @staticmethod
    def __load_parent_config(parent_sm_data):
        '''Returns an 'mas_execution_manager.sm_params.StateMachineParams'
        object containing description parameters for a generic state machine description

        Keyword arguments:
        parent_sm_data -- an 'mas_execution_manager.sm_params.StateMachineParams' object

        '''
        sm_params = StateMachineParams()
        sm_params.id = parent_sm_data[SMFileKeys.ID]
        sm_params.states = parent_sm_data[SMFileKeys.STATES]
        sm_params.outcomes = parent_sm_data[SMFileKeys.OUTCOMES]
        if SMFileKeys.ARGS in parent_sm_data:
            for arg in parent_sm_data[SMFileKeys.ARGS]:
                arg_data = arg[SMFileKeys.ARG]
                try:
                    sm_params.global_params[arg_data[SMFileKeys.ARG_NAME]] = \
                    arg_data[SMFileKeys.ARG_VALUE]
                except TypeError as exc:
                    print('[sm_loader, ERROR] Error loading argument {0}'.format(arg_data))
                    print('[sm_loader, ERROR] {0}', str(exc))

        for state_description in parent_sm_data[SMFileKeys.STATE_DESCRIPTIONS]:
            state_data = state_description[SMFileKeys.STATE]
            state_params = StateParams()
            state_name = state_data[SMFileKeys.STATE_NAME]
            if state_name not in sm_params.states:
                error = '[sm_loader] State {0} not declared in the state list'.format(state_name)
                raise AssertionError(error)

            state_params.name = state_name
            state_params.state_module_name = state_data[SMFileKeys.STATE_MODULE_NAME]
            state_params.state_class_name = state_data[SMFileKeys.STATE_CLASS_NAME]

            for transition in state_data[SMFileKeys.TRANSITIONS]:
                transition_data = transition[SMFileKeys.TRANSITION]
                transition_name = transition_data[SMFileKeys.TRANSITION_NAME]
                resulting_state = transition_data[SMFileKeys.RESULT_STATE]
                if resulting_state not in sm_params.states and \
                   resulting_state not in sm_params.outcomes:
                    error = 'Invalid transition {0} for state {1}\n'.format(state_name,
                                                                            transition_name)
                    error += '-> {0} not declared in the state or outcome list'.format(resulting_state)
                    raise AssertionError(error)

                state_params.transitions[transition_name] = resulting_state

            if SMFileKeys.ARGS in state_data:
                for arg in state_data[SMFileKeys.ARGS]:
                    arg_data = arg[SMFileKeys.ARG]
                    try:
                        state_params.args[arg_data[SMFileKeys.ARG_NAME]] = \
                        arg_data[SMFileKeys.ARG_VALUE]
                    except TypeError as exc:
                        print('[sm_loader, ERROR] Error loading argument {0}'.format(arg_data))
                        print('[sm_loader, ERROR] {0}', str(exc))

            for arg_name, arg_value in sm_params.global_params.items():
                arg_data = arg[SMFileKeys.ARG]
                state_params.args[arg_name] = arg_value

            sm_params.state_params[state_params.name] = state_params
        return sm_params

    @staticmethod
    def __print_sm_configuration(sm_params):
        '''Prints the state machine description parameters specified by 'sm_params'

        Keyword arguments:
        sm_params -- an 'mas_execution_manager.sm_params.StateMachineParams' object

        '''
        print('State machine ID: %s' % (sm_params.id))
        print('States: %s' % (sm_params.states))
        print()
        for _, state in sm_params.state_params.items():
            print('    State: %s' % (state.name))
            print('    State module name: %s' % (state.state_module_name))
            print('    State class name: %s' % (state.state_class_name))
            print('    Transitions:')
            for transition, resulting_state in state.transitions.items():
                print('        Transition name: %s' % (transition))
                print('        Resulting state: %s' % (resulting_state))
                print()
            if state.args:
                print('    Arguments:')
                for arg, value in state.args.items():
                    print('        Name: %s' % (arg))
                    print('        Value: %s' % (value))
                    print()
