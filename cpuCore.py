import time
from termcolor import colored
import globals


class CPUCore:
    def __init__(self, name):
        self.name = name
        self.idle_time = 0
        self.state = 'idle'
        self.running_task = None

    def set_running_task(self, task):
        globals.cpu_core_mutex.acquire(blocking=False)
        self.running_task = task
        globals.cpu_core_mutex.release()

    def set_state(self, state):
        globals.cpu_core_mutex.acquire(blocking=False)
        self.state = state
        globals.cpu_core_mutex.release()

    def get_state(self):
        globals.cpu_core_mutex.acquire(blocking=False)
        state = self.state
        globals.cpu_core_mutex.release()
        return state

    def process_task(self, task, resources, cpu_cores, time_quantum=None, time_slice=None, queue=None, state='ready', origin_queue=None, origin_state='queue 0'):

        task.set_state('running')
        task.allocate_resources(resources)

        # indicates the selected scheduler
        # algorithm is non-preemptive
        if time_quantum == None:
            for _ in range(task.duration):
                time.sleep(1)
                # print_system_status(cpu_cores, resources)
                task.increment_cpu_time()
                self.idle_time += 1
                globals.increment_system_total_time()

            task.set_state('done')
            task.free_resources(resources)

        else:
            remain_time = task.duration - task.cpu_time
            for _ in range(min(remain_time, time_slice)):
                time.sleep(1)
                # print_system_status(cpu_cores, resources)
                task.increment_cpu_time()
                task.queue_time += 1
                self.idle_time += 1
                globals.increment_system_total_time()

            task.free_resources(resources)
            if task.cpu_time == task.duration:
                task.set_state('done')

            else:
                if task.queue_time == time_quantum:
                    task.queue_time = 0
                    task.set_state(state)
                    task.set_isAssigned(False)
                    with globals.task_mutex:
                        queue.append(task)
                else:
                    task.set_state(origin_state)
                    task.set_isAssigned(False)
                    with globals.task_mutex:
                        origin_queue.append(task)

        print()
        globals.task_mutex.acquire(blocking=False)
        globals.resource_mutex.acquire(blocking=False)
        print(colored('Task ' + task.name + ' current cputime: ', 'yellow')+ str(task.cpu_time) \
            + '\n' + colored('Task ' + task.name + ' current state: ' , 'yellow')+ task.state)
        globals.task_mutex.release()
        globals.resource_mutex.release()
        self.set_state('idle')
        self.set_running_task(None)