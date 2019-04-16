from __future__ import print_function
import json
print ('Loading Lambda function')


def lambda_handler(event, context):
    print ('value = %s' % event.get('key1'))
    print ('value = %s' % event.get('key2'))
    print ('value = %s' % event.get('key3'))
    print (context)
    return event.get('key1')


if __name__ == '__main__':
    class Event:
        def get(self, key):
            e = {
                'key1': 'value1',
                'key2': 'value2',
                'key3': 'value3'
            }
            return e[key]
    context = 'myContext'
    event = Event()

    print(lambda_handler(event, context))