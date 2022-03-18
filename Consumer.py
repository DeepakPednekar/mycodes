import pika
import os
from importlib import import_module
import signal
import threading
import time
import sys

# for trace ids
try:
    from . import extension
except ImportError:
    import extension

class AMQP(object):
    log = log
    _manual_requeue = False

    def __init__(self, queue=''):
        # to get common trace id
        extension.connection_trace_ids[os.getpid()] = extension.getuuid()
        print('consumer | ', extension.connection_trace_ids)

        params = pika.URLParameters(conf.AMQP_CREDENTIAL)
        self.queue = queue
        log.info('consumer started for %s | %s', self.queue, extension.connection_trace_ids)

        self.is_processing = False
        self.connection = pika.BlockingConnection(parameters=params)
        self.channel = self.connection.channel()
        self.register_signals()

    def register_signals(self):
        self.log.debug('registering signals')
        signal.signal(signal.SIGTERM, self.close_channel)
        signal.signal(signal.SIGINT, self.close_channel)

    def start(self):
        try:
            assert isinstance(self.channel, pika.adapters.blocking_connection.BlockingChannel)
            self.channel.basic_qos(prefetch_count=1)
            self.channel.queue_declare(queue=self.queue, durable=True)
            self.channel.basic_consume(on_message_callback=self.on_message_callback,
                                  queue=self.queue,
                                  auto_ack=False)

            self.log.info('started consuming')
            self.channel.start_consuming()
        except Exception as e:
            print('closed | ', e)
            import traceback
            traceback.print_exc()
            log.exception(e)

    def close_channel(self, first, second):
        if self.channel.is_open:
            self.log.info('consuming stopped..')
            self.channel.stop_consuming()
        print('interrupt happened.... closing')
        t = threading.Thread(target=self.graceful_termination)
        t.start()
        t.join()

    def graceful_termination(self):
        while self.is_processing:
            self.log.debug('msg still in process... sleeping for %s seconds', 2)
            time.sleep(2)

        if hasattr(self, 'cleanup'):
            if callable(self.cleanup):
                t = threading.Thread(target=self.cleanup)
                t.start()

                while t.is_alive():
                    self.log.info('[*] processing cleanup ....')
                    time.sleep(2)
                self.log.info('[*] cleanup done...')
        else:
            print('[*] no cleanup... exiting')
            self.log.info('[*] no cleanup... exiting')

        self.log.info('closing process')
        print('final closing')
        sys.exit(0)

    def on_message_callback(self, ch, method: pika.spec.Basic.Deliver, properties, body):
        # this is test callback
        print(body)
        assert isinstance(self.channel, pika.adapters.blocking_connection.BlockingChannel)
        print(type(method))
        print('processing msg .... ')
        print(threading.current_thread().name)

        t = threading.Thread(target=self.process_msg, args=(body,))
        t.start()
        while t.is_alive():
            print('in connection')
            self.channel._connection.sleep(1)
        #
        print('done i guess')
        self.channel.basic_ack(method.delivery_tag)

    def process_msg(self, msg):
        import time
        for each in range(60):
            print('-' * each)
            time.sleep(10)

# AMQP(queue='q_event_stream').start()

