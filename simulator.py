'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys
import copy
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
     #store the (switching time, proccess_id) pair
    schedule = []
    pending_list = []
    _process_list = copy.deepcopy(process_list)
    current_time = 0
    waiting_time = 0
    while len(pending_list)!=0 or len(_process_list) != 0:
        if len(pending_list) == 0: # fetch new process from process_list
            new_process = _process_list.pop(0)
            pending_list.append(new_process)
            current_time = new_process.arrive_time
        else:
            processing_task = pending_list.pop(0)
            schedule.append((current_time,processing_task.id))
            waiting_time += current_time - processing_task.arrive_time
            if processing_task.burst_time >= time_quantum: # if remaining completion time is longer than quantum
                current_time += time_quantum
            else: # if remainnig completion time is shorter than quantum
                current_time += processing_task.burst_time
            while len(_process_list) != 0 : # if there was incoming process in this period
                if current_time >= _process_list[0].arrive_time:
                    pending_list.append(_process_list.pop(0))
                else:
                    break
            if processing_task.burst_time > time_quantum: # if remainnig completion time is longer than quantum, append back to pending_list
                pending_list.append(Process(processing_task.id, current_time, processing_task.burst_time-time_quantum))
                
    return schedule, waiting_time/float(len(process_list))

def SRTF_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    #pending_list example: [((process.id, process.arrive_time, process.remaining_time), process.last_termination_time)]
    pending_list = [] 
    _process_list = copy.deepcopy(process_list)
    current_time = 0
    waiting_time = 0
    while len(pending_list)!=0 or len(_process_list) != 0:
        if len(pending_list) == 0: # fetch new process from process_list
            new_process = _process_list.pop(0)
            pending_list.append((new_process, new_process.arrive_time))
            current_time = new_process.arrive_time
        else:
            processing_task, last_termination_time = pending_list.pop(0)
            waiting_time += current_time - last_termination_time
            # append to schedule if there is a process switch
            if len(schedule) == 0:
                schedule.append((current_time,processing_task.id))
            elif schedule[-1][1] != processing_task.id:
                schedule.append((current_time,processing_task.id))
            # if next task come before current task completes
            if len(_process_list) != 0 and processing_task.burst_time + current_time > _process_list[0].arrive_time:
                _processing_remaining_time = processing_task.burst_time-(_process_list[0].arrive_time-current_time)
                # compute next current_time, i.e. current task termination time
                current_time =  _process_list[0].arrive_time
                pending_list.append((_process_list.pop(0), current_time))
                pending_list.append((Process(processing_task.id, processing_task.arrive_time, _processing_remaining_time), current_time))
                #sort pending_list according to remaining time and arrival time
                pending_list = sorted(pending_list, key=lambda x: x[0].burst_time * 1e10 + x[0].arrive_time)
                
            else: # finish current task and compute next current_time
                current_time += processing_task.burst_time
    return schedule, waiting_time/float(len(process_list))

def SJF_scheduling(process_list, alpha):
    #store the (switching time, proccess_id) pair
    schedule = []
    pending_list = [] 
    _process_list = copy.deepcopy(process_list)
    estimated_time = dict((process.id, 5) for process in process_list)
    current_time = 0
    waiting_time = 0
    while len(pending_list)!=0 or len(_process_list) != 0:
        if len(pending_list) == 0: # fetch new process from process_list
            new_process = _process_list.pop(0)
            pending_list.append(new_process)
            current_time = new_process.arrive_time
        else:
            processing_task = pending_list.pop(0)
            schedule.append((current_time,processing_task.id))
            waiting_time += current_time - processing_task.arrive_time
            current_time += processing_task.burst_time
            # updated estimated_time by burst_time
            estimated_time[processing_task.id] = alpha * processing_task.burst_time + (1 - alpha) * estimated_time[processing_task.id]
            while len(_process_list) != 0: # if there was incoming process in this period
                if(_process_list[0].arrive_time <= current_time):
                    pending_list.append(_process_list.pop(0))
                else:
                    break
            # sort pending_list according to estimated time
            pending_list = sorted(pending_list, key=lambda x: estimated_time[x.id])
            
    return schedule, waiting_time/float(len(process_list))

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))

def plotImage(x, y):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.grid()
    ax.set(xlabel='alpha', ylabel='average_waiting_time')
    fig.savefig("test.png")
    plt.show()   
    
def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    for i in range(10):
        RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = i+1)
        print("RR_avg_waiting_time for quantum " + str(i+1) + " is %.2f"%(RR_avg_waiting_time))

    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 10)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    y = []
    for i in np.arange(0.1, 1.1, 0.1):
        SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = i)
        y.append(SJF_avg_waiting_time)
        print("RR_avg_waiting_time for quantum %.1f"%(i) + " is %.2f"%(SJF_avg_waiting_time))
    plotImage(np.arange(0.1, 1.1, 0.1), y)
    
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])

 