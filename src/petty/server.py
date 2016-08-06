# Copyright 2016, Steve Milner
# Distributed under the Modified BSD License.
# See LICENSE for the full license text.
"""
Server code.
"""

import logging
import logging.config
import time

from concurrent import futures

import grpc

#: One days worth of seconds. Used during run_forever to sleep.
_ONE_DAY_IN_SECONDS = 8640086400


class Petty(object):
    """
    The Petty server class.
    """

    #: Read-only accessor for the running attribute (__running)
    running = property(lambda s: s.__running)

    def __init__(self, generic_rpc_handlers=[],
                 max_workers=10, logger_conf_file=None):
        """
        Initializes a new Petty server.

        :param generic_rpc_handlers: Optional list of GenericRpcHandlers.
        :type generic_rpc_handlers: list
        :param max_workers: Optional number of workers to run. Default: 10.
        :type max_workers: int
        """
        self.logger_conf_file = logger_conf_file
        self._init_logger()
        self.__running = False
        self._server = grpc.server(
            generic_rpc_handlers=generic_rpc_handlers,
            thread_pool=futures.ThreadPoolExecutor(max_workers=max_workers))
        self.logger.debug(
            'gRPC server created: generic_rpc_handlers={}'
            'thread_pool=futures.ThreadPoolExecutor(max_workers={})'.format(
                generic_rpc_handlers, max_workers))

    def _init_logger(self):
        """
        Initializes a logger. If self.logger_conf_file is set it will be read.
        """
        self.logger = logging.getLogger('petty')
        if self.logger_conf_file:
            try:
                import yaml
                with open(self.logger_conf_file) as f:
                    logging.config.dictConfig(yaml.safe_load(f))
                self.logger.info('Loaded logging configuration from {}'.format(
                    self.logger_conf_file))
                # Return out since we successfully loaded the configuration
                return
            except ImportError as error:
                logging.warn('{}: Custom logger configuration '
                             'requires PyYAML'.format(error))
            except (ValueError, yaml.error.YAMLError) as error:
                logging.warn(
                    'Invalid YAML given for logging: {}'.format(error))
            except IOError as error:
                logging.warn('The logging config file provided '
                             'does not exist: {}'.format(error))

            logging.warn('Falling back to default logging config')
            self.logger_conf_file = None
            self._init_logger()
        else:
            self.logger.propagate = False
            self.logger.info('Using default logging configuration')
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            handler.formatter = logging.Formatter(
                '%(name)s - %(levelname)s - %(message)s')
            self.logger.handlers = [handler]

    def add_servicer(self, proto, servicer):
        """
        Adds a servicer to the server.

        :param proto: The imported protobuf module for the servicer.
        :type proto: module
        :param servicer: A grpc servicer instance.
        :type servicer: instance
        """
        servicer_cls_name = servicer.__class__.__name__
        adder_func_name = 'add_{}Servicer_to_server'.format(servicer_cls_name)
        servicer_adder = getattr(proto, adder_func_name)
        self.logger.debug('Executing {}({}, {})'.format(
            adder_func_name, servicer, self._server))
        servicer_adder(servicer, self._server)
        self.logger.info('Added {} to the server.'.format(servicer_cls_name))

    def start(self, host='127.0.0.1', port=8080, server_credentials=None):
        """
        Starts the server.

        :param host: The host to bind on. Default: 127.0.0.1.
        :type host: str
        :param port: The port to bind on. Default: 8080.
        :type port: int
        :param service_credentials: Optional credentials for secure bind.
        :type service_credentials: grpc.ServiceCredentials
        """
        bind_addr = '{}:{}'.format(host, port)
        if server_credentials:
            if not issubclass(server_credentials, grpc.ServerCredentials):
                raise TypeError('service_credentials must be a '
                                'subclass of grpc.ServerCredentials')
            self._server.add_secure_port(bind_addr, server_credentials)
            self.logger.info('Listening securely on {}'.format(bind_addr))
        else:
            self._server.add_insecure_port(bind_addr)
            self.logger.info('Listening insecurely on {}'.format(bind_addr))
        self.__running = True
        self._server.start()
        self.logger.debug('The server has started')

    def stop(self):
        """
        Stops a running server.
        """
        if not self.__running:
            self.logger.debug(
                'Ignoring stop request as the server is not running')
            return
        self.logger.info('Attempting to stop the server')
        self._server.stop(0)
        self.__running = False
        self.logger.info('The server is stopped')

    def run_forever(self):
        """
        Runs the server "forever".
        """
        if not self.__running:
            self.logger.debug('Starting the server before running forever')
            self.start()
        try:
            while True:
                self.logger.debug('Sleeping for one day')
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            self.logger.debug('Stopping the server due to KeyboardInterrupt')
            self._server.stop(0)
