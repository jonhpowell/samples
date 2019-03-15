import os
import time
import queue
import multiprocessing
from multiprocessing import Process, Queue
import time

from core.utils.AutoAiLogger import AutoAiLogger

## to remove
import warnings
warnings.filterwarnings("ignore")


class AutoAiJobRunner(object):

    '''
    Job Runner to asynchronously run modeling jobs given a unique label that can be used to
    identify the job as it is running and to key the job's results once it completes.
    Jobs are submitted via add_job() and you can get overall status at any time using get_status().
    You can get a specific job's results using get_result(label) or all results via get_results().
    To start an entirely new set of unrelated jobs you will need to call reset_batch() or your
    results will get intermixed. You can call kill() to terminate jobs early.
    Note: we switched from threads to processes since it appears that some of the ML libraries such
        as scikit-learn or category-encoders are not thread-safe.
    Design: we use a producer-consumer, process-based execution model backed by TWO queues -- one to buffer
        work jobs another to buffer work results.
    '''

    def __init__(self):

        self.log = AutoAiLogger('AutoAiJobRunner')
        self.num_workers = os.cpu_count() - 1   # use fewer processes than CPU's to keep machine responsive
        self.log.info(f'Available cores={os.cpu_count()}, num_workers={self.num_workers} ')
        self.job_q = Queue()        # worker job Q (jobs are submitted, each pushes results on the results Q)
        self.res_q = Queue()        # worker results Q (receives job results from the worker, makes results available
        self.results = dict()       # final job results pulled from results Q
        self.workers = []           # list of worker processes
        self.jobs_submitted = 0     # must be successfully submitted
        self.jobs_completed = 0     # completed, both successful and not
        self.in_error = 0           # includes jobs that throw exceptions and those that have duplicate labels
        self.results_all = []       # TEST

        '''
        Utility function to convert a timestamp to a human-readable format.
        '''
        def time_to_str(time_in):
            return time.strftime("%H:%M:%S", time.gmtime(time_in))

        '''
        The method that is called to perform work in the process by continuing to pick up jobs from the job Q, execute
        them and push results into the results Q, recording job metrics. Jobs wait in the incoming job queue
        until a worker process frees up, at which time its execution is started.Note that multiple processes are 
        utilizing this same method simultaneously in their own process-space. 
        Note: exceptions thrown from a job are handled & logged here, so as to not crash the process & stop processing.
        '''

        def work(log, wrk_q_in, res_q_out):
            process_name = multiprocessing.current_process()
            while True:
                (label, func, args, kwargs) = wrk_q_in.get()
                if func is None:
                    log.debug(f'{process_name} worker found poison pill in Q--terminating')
                    break
                else:
                    log.info(f'{process_name} started job "{label}"')
                    start_time = time.time()
                    res = dict()
                    res['label'] = label
                    res['start_time'] = time_to_str(start_time)
                    try:
                        res['results'] = func(args, kwargs)
                    except Exception as exc:
                        exception_text = f'Exception: {exc}'
                        res['results'] = exception_text
                        log.error(f'exception in job "{label}": {exception_text}')
                    finally:
                        elapsed_time = time.time() - start_time
                        res['elapsed_time'] = time_to_str(elapsed_time)
                        log.info(f'{process_name} completed job "{label}" in {time_to_str(elapsed_time)} results={res}')
                        res_q_out.put(res)
            log.info(f'Exiting {process_name}')

        for _ in range(self.num_workers):
            worker = Process(target=work, args=(self.log, self.job_q, self.res_q))
            self.workers.append(worker)
            worker.start()
            self.log.debug(f'{worker.name} started')

    '''
    Add a job to be executed to the job process queue. Its label uniquely identifies it and allows it to be tracked 
    through the job run cycle.
    '''
    def add_job(self, label, func, *args, **kwargs):
        if label in self.results:
            self.in_error += 1
            self.log.error(f'Job "{label} already exists; ignoring!')
        else:
            self.jobs_submitted += 1
            self.results[label] = dict()  # register early to catch duplicate job race condition
            self.job_q.put((label, func, args, kwargs), block=False)
            self.log.info(f'Added job "{label}"')

    '''
    Graceful shutdown of thread pool. Lets currently executing jobs complete. Assuming don't want to 
    pull or see remaining / pending results.
    '''
    def shutdown(self):
        self.log.info(f'Shutdown initiated.')
        self.pull_results()         # make sure results are available, if wanted
        for _ in self.workers:
            self.job_q.put((None, None, None, None))     # poison-pill to halt each thread
        for worker in self.workers:
            worker.join()
        self.log.debug(f'All {len(self.workers)} processes joined')
        self.log.info(f'Shutdown complete')

    '''
    Immediate, disruptive shutdown of thread pool. May not allow currently executing processes to complete.
    '''
    def kill(self):
        self.log.info(f'Kill initiated!')
        for worker in self.workers:
            worker.terminate()
        self.log.info(f'Kill complete')

    '''
    When asked for results, pull them from the results Q, thus avoiding a separate results thread.
    '''
    def pull_results(self):
        while True:
            try:
                res = self.res_q.get_nowait()  # don't block waiting for processes to push any pending results
                self.results_all.append(res)
                label = res['label']
#                self.log.debug(f'Pulled results for job "{label}" from results Q')
                self.results[label]['label'] = label
                self.results[label]['results'] = res['results']
                self.results[label]['start_time'] = res['start_time']
                self.results[label]['elapsed_time'] = res['elapsed_time']
                self.jobs_completed += 1
                if str(res['results']).startswith('Exception'):
                    self.in_error += 1
            except queue.Empty:
#                self.log.debug(f'Result Q empty')
                break
            except Exception as exc:
                self.log.warning(f'Exception pulling results: {str(exc)}')
                break

    '''
    Get overall JobRunner status. Allows you to know when all submitted jobs are complete.
    Note: pulls all queued-up results into final results dict.
    '''
    def get_status(self):
        self.pull_results()
        return {"submitted": self.jobs_submitted, "completed": self.jobs_completed, "in_error": self.in_error}

    '''
    Get overall JobRunner status. Allows you to know when all submitted jobs are complete.
    '''
    def get_status_str(self, location):
        st = self.get_status()
        return f'JobRunner status ({location}): submitted={st["submitted"]}, completed={st["completed"]}, in_error={st["in_error"]}'

    '''
    Get results for a single job run.
    Note: pulls all queued-up results into final results dict.
    '''
    def get_result(self, label):
        self.pull_results()
        return self.results[label]

    '''
    Get results for all submitted jobs, whether or not they are complete.
    Note: pulls all queued-up results into final results dict.
    '''
    def get_results(self):
        self.pull_results()
#        return self.results  TODO TEST
        return self.results_all

    '''
    Reset the batch of jobs submitted and get ready for another.
    NOTE: results accumulate and total # of jobs accumulate until cleared.
    '''
    def reset_batch(self):
        self.jobs_submitted = 0
        self.in_error = 0
        self.results = dict()
        self.job_q = Queue()
        self.res_q = Queue()


if __name__ == '__main__':  # simple tests

    import time

    def sleep_square(args, kwargs):
        time.sleep(3)
        if args[0] % 4 == 0:
            raise ValueError('bad luck')
        return args[0] * args[0]

    def fib(args, kwargs):
        def call_fib(n):
            if n <= 2:
                return 1
            return call_fib(n-1) + call_fib(n-2)
        return call_fib(args[0])

    def error_func(args, kwargs):
        time.sleep(3)
        raise ValueError('Some wrong args')


    tpc = AutoAiJobRunner()     # auto-detects number of CPU's to use
    tpc.add_job("sleep_square-1", sleep_square, 1, None)
    tpc.add_job("fib-22", fib, 22, None)
    print(tpc.get_status_str("location1"))
    time.sleep(1)
    tpc.add_job("sleep_square-3", sleep_square, 3, None)
    tpc.add_job("sleep_square-4", sleep_square, 4, None)
    tpc.add_job("error_func-1", error_func, 2, None)
    print(tpc.get_status_str("location2"))

    #tpc.kill()

    time.sleep(1)
    tpc.add_job("fib-20", fib, 20, None)
    tpc.add_job("sleep_square-5", sleep_square, 5, None)
    print(tpc.get_status_str("location3"))
    tpc.add_job("sleep_square-9", sleep_square, 9, None)
    tpc.add_job("fib-7", fib, 7, None)
    print(tpc.get_status_str("location4"))
    time.sleep(1)
    tpc.add_job("sleep_square-3", sleep_square, 3, None)  # duplicate -- should ignore
    tpc.add_job("fib-35", fib, 35, None)
    print(tpc.get_status_str("location5"))

    tpc.shutdown()
    print(tpc.get_status_str("location6"))
    print(tpc.get_status())
    time.sleep(1)

    result = tpc.get_result("fib-7")
    print(f'"fib-7" results: {result}')
    results = tpc.get_results()
    print(f'All results: {results}')

    tpc.reset_batch()
    results_after_reset = tpc.get_results()
    print(tpc.get_status_str("AfterResetBatch"))
    print(f'All results after clearing: {results_after_reset}')


