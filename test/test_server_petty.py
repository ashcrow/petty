# Copyright 2016, Steve Milner
# Distributed under the Modified BSD License.
# See LICENSE for the full license text.
"""
Tests for the Petty server class.
"""

import unittest

import mock
import yaml

import helloworld_pb2

from petty.server import Petty


class Greeter(helloworld_pb2.GreeterServicer):

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)



class TestPetty(unittest.TestCase):

    def test_initialization(self):
        """
        Ensure initialization of Petty does the right things.
        """
        '''
        with mock.patch('grpc.server') as _grpc_server:
            server = Petty()
            self.assertFalse(server.running)
            self.assertEquals('petty', server.logger.name)
            _grpc_server.assert_called_once()
        '''
        pass

    def test__init_logger_no_config(self):
        """
        Ensure the server logger is created properly without a config.
        """
        with mock.patch('grpc.server'):
            server = Petty()
            self.assertEquals('petty', server.logger.name)
            self.assertFalse(server.logger.propagate)

    def test__init_logger_no_yaml(self):
        """
        Ensure the server logger is created properly without a config.
        """
        with mock.patch('grpc.server'), \
                mock.patch('yaml.safe_load') as _yaml_safe_load:
            _yaml_safe_load.side_effect = ImportError
            server = Petty()
            self.assertEquals('petty', server.logger.name)
            self.assertFalse(server.logger.propagate)

    def test__init_logger_with_config(self):
        """
        Ensure the server logger is created properly with a valid config.
        """
        with open('../conf/logging.yaml', 'r') as f:
            dict_config_yaml = yaml.safe_load(f)

        with mock.patch('grpc.server'), \
                mock.patch('yaml.safe_load') as _yaml_safe_load:

            _yaml_safe_load.return_value = dict_config_yaml
            server = Petty(logger_conf_file='../conf/logging.yaml')
            self.assertEquals('petty', server.logger.name)
            self.assertFalse(server.logger.propagate)
            _yaml_safe_load.assert_called_once()

    def test__init_logger_with_invalid_config(self):
        """
        Ensure the server logger is created properly with an invalid config.
        """
        with mock.patch('grpc.server'), \
                mock.patch('yaml.safe_load') as _yaml_safe_load:

            _yaml_safe_load.return_value = '!!--//s'
            server = Petty(logger_conf_file='../conf/logging.yaml')
            self.assertEquals('petty', server.logger.name)
            self.assertFalse(server.logger.propagate)
            _yaml_safe_load.assert_called_once()

    def test__init_logger_with_missing_config(self):
        """
        Ensure the server logger is created properly with a missing config.
        """
        with mock.patch('grpc.server'), \
                mock.patch('yaml.safe_load') as _yaml_safe_load:
            server = Petty(logger_conf_file='./doesnotexist')
            self.assertEquals('petty', server.logger.name)
            self.assertFalse(server.logger.propagate)
            _yaml_safe_load.assert_not_called()

    def test_add_servicer_with_valid_instance(self):
        """
        Ensure servicers are added to the server properly.
        """
        with mock.patch('test.helloworld_pb2') as _hw:
            server = Petty()
            server.add_servicer(_hw, Greeter())
            _hw.add_GreeterServicer_to_server.assert_called_once()

    def test_add_servicer_with_invalid_instance(self):
        """
        Ensure servicers are added to the server properly.
        """
        with mock.patch('test.helloworld_pb2') as _hw:
            server = Petty()
            server.add_servicer(_hw, dict())
            _hw.add_GreeterServicer_to_server.assert_not_called()

    def test_start_with_defaults(self):
        """
        Ensure start infact does start the server with defaults without looping.
        """
        with mock.patch('grpc.server') as _grpc_server:
            server = Petty()
            server.start()
            _grpc_server().add_insecure_port.assert_called_once_with(
                '127.0.0.1:8080')

    def test_start_with_addresses_and_ports(self):
        """
        Ensure start does start the server with input addresses/ports.
        """
        with mock.patch('grpc.server') as _grpc_server:
            for kwargs in (
                {'host': '127.0.0.2', 'port': 8000},
                {'port': 8000},
                {'host': '127.0.0.2'},
            ):
                _grpc_server().add_insecure_port.reset_mock()
                expected_host = kwargs.get('host', '127.0.0.1')
                expected_port = kwargs.get('port', 8080)
                server = Petty()
                server.start(**kwargs)
                _grpc_server().add_insecure_port.assert_called_once_with(
                    '{}:{}'.format(expected_host, expected_port))

    def test_stop_when_running(self):
        """
        Ensure stop does stop the server when it is running.
        """
        with mock.patch('grpc.server') as _grpc_server:
            server = Petty()
            server.start()
            server.stop()
            _grpc_server().stop.assert_called_once()

    def test_stop_when_not_running(self):
        """
        Ensure stop skips running stop when the server is not running.
        """
        with mock.patch('grpc.server') as _grpc_server:
            server = Petty()
            server.stop()
            _grpc_server().stop.assert_not_called()

    def test_run_forever_without_start(self):
        """
        Ensure run executes start if the server has not already been started.
        """
        with mock.patch('grpc.server') as _grpc_server, \
                mock.patch('time.sleep') as _sleep:
            # Raise so that we don't loop forever
            _sleep.side_effect = KeyboardInterrupt
            server = Petty()
            server.run_forever()
            _grpc_server().start.assert_called_once()
            _sleep.assert_called_once()

    def test_run_forever_skips_start_if_already_running(self):
        """
        Ensure run executes start if the server has not already been started.
        """
        with mock.patch('grpc.server') as _grpc_server, \
                mock.patch('time.sleep') as _sleep:
            # Raise so that we don't loop forever
            _sleep.side_effect = KeyboardInterrupt
            server = Petty()
            server.start()
            self.assertEquals(1, _grpc_server().start.call_count)
            server.run_forever()
            # We should still have only called start once
            self.assertEquals(1, _grpc_server().start.call_count)
            _sleep.assert_called_once()
