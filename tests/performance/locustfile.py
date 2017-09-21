'''
Locust file for loading tests purposes.
'''
from locust import HttpLocust, TaskSet, task


class WebsiteTasks(TaskSet):
    '''
    Set of tasks.
    '''

    # August 9, 2017 06:56:12 pm
    timestamp = 1502304972

    @task(1)
    def post_logs(self):
        '''
        Post some logs.
        '''
        self.timestamp += 1

        self.client.post(
            '/api/1/service/1/logs',
            json={
                'logs': [
                    {
                        'message': 'a log message',
                        'level': 'a low level',
                        'category': 'a category',
                        'date': str(self.timestamp),
                    }
                ]
            }
        )

    @task(1)
    def get_logs(self):
        '''
        Get some logs.
        '''
        self.client.get(
            '/api/1/service/1/logs/2017-08-09-06-50-00/2017-08-09-10-00-00'
        )


class WebsiteUser(HttpLocust):
    '''
    User simulation.
    '''
    task_set = WebsiteTasks
    min_wait = 500
    max_wait = 1000
