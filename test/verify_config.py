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
            print('{0} not processed correctly; error: {1}'.format(valid_config_path,
                                                                   str(exc)))

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

if __name__ == '__main__':
    unittest.main()
