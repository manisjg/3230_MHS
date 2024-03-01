import os
import tkinter as tk
from tkinter.filedialog import askopenfilename
tk.Tk().withdraw()
# TODO for MVP  - Display configuration
#               - Implement LRU
#               - Implement Optimal(offline) greedy algorithm
#               - ^^ IDK what this is ^^


class Trace:
    """
    The purpose of this class is to be a placeholder for memory
    references so that we can read the .dat file and fill out one
    instance object per line in the file. A list of these objects
    can then be fed into each algorithm in order to it to complete
    each instance (determine PT result and Phys page #)
    """
    def __init__(self, type_rw, v_add, v_pg_num, pg_off, pt_res, phys_pg_num):
        """
        initializes values for new Trace objects.
        :param type_rw:
        :param v_add:
        :param v_pg_num:
        :param pg_off:
        :param pt_res:
        :param phys_pg_num:
        """
        self.type_rw = type_rw  # AccessType, read or write
        self.v_add = v_add  # Virtual Address
        self.v_pg_num = v_pg_num  # Virtual Page Number
        self.pg_off = pg_off  # Page Offset
        self.pt_res = pt_res  # Page table result, hit or miss
        self.phys_pg_num = phys_pg_num  # Physical page number

    def __str__(self):
        """
        this method allows us to print(trace_instance) in order
        to output the information in a relatively pretty format
        matching the statistics header based on the length of the
        virtual address.
        :return:
        """
        # currently doesn't output very cleanly (still correctish just ugly)
        # ("------\t--------\t------\t----\t----\t----")
        if len(self.v_add) > 6:
            return f"    {self.type_rw}\t{self.v_add}\t     {self.v_pg_num}\t  {self.pg_off}\t{self.pt_res}\t   {self.phys_pg_num}"
        elif len(self.v_add) > 3:
            return f"    {self.type_rw}\t00{self.v_add}\t     {self.v_pg_num}\t  00{self.pg_off}\t{self.pt_res}\t   {self.phys_pg_num}"
        else:
            return f"     {self.type_rw}\t00000{self.v_add}\t     {self.v_pg_num}\t  {self.pg_off}\t{self.pt_res}\t   {self.phys_pg_num}"


# I don't think this needs to be just for FIFO, we should probably
# refactor it to be called "Statistics" and reuse for other algos
class Statistics:
    """
    The purpose of this class is to be a placeholder for the stats
    associated with each .dat file as it is run through each
    algorithm. This helps with decent looking output.
    """
    def __init__(self, hits, misses, hit_ratio, reads, writes, access_ratio, total_refs):
        """
        initializes values for new Statistics object t
        :param hits:
        :param misses:
        :param hit_ratio:
        :param reads:
        :param writes:
        :param access_ratio:
        :param total_refs:
        """
        self.hits = hits
        self.misses = misses
        self.hit_ratio = hit_ratio
        self.reads = reads
        self.writes = writes
        self.access_ratio = access_ratio
        self.total_refs = total_refs

    def __str__(self):
        """
        allows us to print(Statistics_instance) with some
        relatively pretty output formatting
        :return:
        """
        out = f"Simulation Statistics\n" \
              f"Page table hits: {self.hits}\n" \
              f"Page Table Misses: {self.misses}\n" \
              f"Page table hit Ratio: {self.hit_ratio}\n\n" \
              f"Total # of Reads: {self.reads}\n" \
              f"Total # of Writes: {self.writes}\n" \
              f"Read / Write Ratio: {self.access_ratio}\n" \
              f"Total # of references: {self.total_refs}"
        return out


def read_dat():
    """
    This function reads the .dat file line by line, and adds info
    into a new instance of the Trace class above. Each instance is
    created with the access type, the virtual address, the virtual
    page #, and the page offset. These will not be updated again.
    The page table result and the physical page number, however, are
    initialized to "empty" (somewhat arbitrarily) to be updated
    later by the memory management algorithms.

    There's several different ways to open the .dat files. I think
    if your .dat file are in the same folder, then askopenfilename
    should work to allow user to choose files from the explorer.

    otherwise, the open with an absolute path should work after you
    replace the path.

    :return:
    """
    # Replace open statement with next 2 lines in order to open file explorer for user to choose file
    filepath = askopenfilename(initialdir=os.getcwd())
    dat = open(filepath, 'r')
    # dat = open("C:/Users/JGMan/PycharmProjects/3230MHS/trace.dat", 'r')
    head = dat
    # Uncomment next line for large files like  real_tr.dat
    # head = [next(dat) for _ in range(10000)]
    dats = []
    # creating Trace instances before adding each to list.
    for i in head:
        type_rw = i[:1].strip()  # AccessType, read or write
        v_add = i[2:].strip()  # Virtual Address
        v_pg_num = i[2:3]  # Virtual Page Number
        pg_off = i[3:].strip()  # Page Offset
        pt_res = "empty"  # Page table result, hit or miss
        phys_pg_num = "empty"  # Physical page number
        d = Trace(type_rw, v_add, v_pg_num, pg_off, pt_res, phys_pg_num)
        dats.append(d)
    # print(dats[1])
    return dats


def fifo(traces_list):
    """
    accepts a list of traces after read__dat(),
    runs each memory reference through a dictionary with the FIFO
    algorithm. During the algorithm, it tracks stats in a Statistics
    object, as well as updating the trace instance as it finds the
    values of page table result and physical page number.

    Returns the list of updated traces and the statistics object:
    This is read later like: outputList, outputStats = fifo(traces)
    :param traces_list:
    :return:
    """
    # the page table is a dictionary with 4 physical page numbers
    # (the keys of the dict) and the values (virtual page numbers)
    # for each key are initialized to -1 for empty
    # I probably didn't do this very dynamically; might make it
    # relatively difficult to work with later if we work on the
    # exceeds to make this configurable, whoops sorry.
    pageTable = dict([(0, -1), (1, -1), (2, -1), (3, -1)])
    # empty list to store traces after ran through fifo
    FIFOtraces = []
    # creates empty statistic object to be incremented during run
    stats = Statistics(0, 0, 0, 0, 0, 0, 0)
    # Idk if this is smart, but firstOUT is a list I used as a queue
    # to track which physical page number needs dumped first.
    firstOUT = []
    # next in is a counter to track which page number is written to.
    nextIn = 0
    # loop through list of traces
    for t in range(len(traces_list)):
        instr = traces_list.pop(0)
        # count access types.
        if instr.type_rw == "R":
            stats.reads += 1
        if instr.type_rw == "W":
            stats.writes += 1
        # loops through dict assigning misses vs hits
        for phys, virt in pageTable.items():
            if virt != instr.v_pg_num:
                instr.pt_res = "Miss"
            else:
                instr.pt_res = " Hit"
                instr.phys_pg_num = phys
                stats.hits += 1
                break
        # do nothing on hit, but add to page table if miss

        # if page table not yet full
        if instr.pt_res == "Miss" and pageTable[3] == -1:
            pageTable.update(({nextIn: instr.v_pg_num}))
            instr.phys_pg_num = nextIn
            firstOUT.append(nextIn)
            nextIn += 1
            stats.misses += 1
        # if page table full and must boot someone
        elif instr.pt_res == "Miss" and pageTable[3] != -1:
            physIn = firstOUT.pop(0)
            pageTable.update(({physIn: instr.v_pg_num}))
            instr.phys_pg_num = physIn
            firstOUT.append(nextIn)
            nextIn += 1
            stats.misses += 1
        # keeps counter within page table bounds
        if nextIn == 4:
            nextIn = 0
        FIFOtraces.append(instr)
    # update last stats
    stats.hit_ratio = stats.hits / stats.misses
    stats.access_ratio = stats.reads / stats.writes
    stats.total_refs = stats.reads + stats.writes
    return FIFOtraces, stats


# reads file into list of Trace objects
traces = read_dat()
# Gets list of updated Traces and Statistics objects from FIFO
outputList, outputStats = fifo(traces)
# outputs header based on virtual address size for pretty formatting
# before outputting each Trace object in list and then the stats
if len(outputList[1].v_add) > 3:
    header = "Access\tVirtual \tVirt. \t  Page   \tPT  \tPhys\n"\
           + "  Type\tAddress \tPage #\t  Offset \tRes.\tPg #\n"\
           + "------\t--------\t------\t  -------\t----\t----\n"
else:
    header = "Access\tVirtual \tVirt. \tPage\tPT  \tPhys\n" \
             + "  Type\tAddress \tPage #\tOff.\tRes.\tPg #\n" \
             + "------\t--------\t------\t----\t----\t----\n"
print(header)

for x in outputList:
    print(x)
print(outputStats)


