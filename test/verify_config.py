#!/usr/bin/env python
import unittest
from mas_execution.sm_loader import SMLoader

class TestConfigParser(unittest.TestCase):
    def test_correct_config(self):
        valid_config_path = 'config/valid_config.yaml'
        print('Verifying that {0} is processed as correct'.format(valid_config_path))
        try:
            SMLoader.load_sm(valid_config_path)
        except Exception as exc:
            error = '{0} not processed correctly; error: {1}'.format(valid_config_path,
                                                                     str(exc))
            self.fail(error)

    def test_config_with_undeclared_state(self):
        invalid_config_path = 'config/config_with_undeclared_state.yaml'
        print('Verifying that {0} is processed as incorrect'.format(invalid_config_path))
        with self.assertRaises(AssertionError):
            SMLoader.load_sm(invalid_config_path)

    def test_config_with_invalid_transition(self):
        invalid_config_path = 'config/config_with_invalid_transition.yaml'
        print('Verifying that {0} is processed as incorrect'.format(invalid_config_path))
        with self.assertRaises(AssertionError):
            SMLoader.load_sm(invalid_config_path)

    def test_child_config_state_removal(self):
        parent_config_path = 'config/valid_config.yaml'
        child_config_path = 'config/child_config_with_removed_state.yaml'
        print('''Verifying parent-child config relation: {0} -- {1}
                 The child removes a state from the parent config'''.format(parent_config_path,
                                                                            child_config_path))
        try:
            sm_params = SMLoader.load_sm(child_config_path, parent_config_path)
            assert len(sm_params.states) == len(sm_params.state_params.keys())
        except Exception as exc:
            error = '{0} -- {1} not processed correctly; error: {2}'.format(parent_config_path,
                                                                            child_config_path,
                                                                            str(exc))
            self.fail(error)

if __name__ == '__main__':
    unittest.main()
