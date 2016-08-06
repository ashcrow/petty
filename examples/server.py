import helloworld_pb2

from petty.server import Petty


class Greeter(helloworld_pb2.GreeterServicer):

    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)


def main():
    s = Petty(logger_conf_file='conf/logging.yaml')
    s.add_servicer(helloworld_pb2, Greeter())
    s.run_forever()


if __name__ == '__main__':
    main()
