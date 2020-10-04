import os
import stat
import sys
import subprocess
import argparse
import numpy as np
import matplotlib.pyplot as plt

from os import path
from shutil import which
from sys import platform

##
# Check if the underlying OS is Linux
##
def is_linux():
    if platform == "linux" or platform == "linux2":
        return True
    else:
        return False
##
# Check if NB executable ("nb" on Linux and "nb.jar" on other OS)
#   exists - either in the current folder or findable in $PATH
##
def check_nb_existence():
    nb_exec_name = "nb"

    if not is_linux():
        nb_exec_name = "nb.jar"

    # NB is not in PATH
    nb_in_path = which(nb_exec_name) is not None
    nb_in_curdir = path.exists(nb_exec_name)

    # NB is not in the current folder
    return nb_in_path or nb_in_curdir

##
# Download NB executable binary and show downloading progress
##
def download_nb():
    if is_linux():
        cmdStr = "wget https://github.com/nosqlbench/nosqlbench/releases/download/nosqlbench-3.12.153/nb"
    else:
        cmdStr = "wget https://github.com/nosqlbench/nosqlbench/releases/download/nosqlbench-3.12.153/nb.jar"

    p = subprocess.Popen(
        [cmdStr],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    lncnt = 1
    prgrsCnt = 1

    while True:
        line = p.stdout.readline()
        if not line:
            break

        # Print a progress dot for every 50 lines processed
        if lncnt % 50 == 0:
            # Print max. 50 progress dots in each output line
            if prgrsCnt < 50:
                print(".", end='')
                prgrsCnt = prgrsCnt + 1
            else:
                print(".")
                prgrsCnt = 1

        lncnt = lncnt + 1

    print()
    print(">> NB is successfully downloaded.")

##
# Expect user input of Yes/No from the command line
##
def expect_cmd_input():
    input_str = input(">> Binding yaml file already exists in the current folder. Overwirte it?")

    while True:
        if input_str.lower() == "n" or input_str.lower() == "no":
            return False
        elif input_str.lower() == "y" or input_str.lower() == "yes":
            return True
        else:
            input_str = input("Please answer [Y|y]es or [N|n]o")

##
# Plot a graph based on the binding results
##
def plot_binding_graph(ax, data_x, data_y, func_name, show_detail):
    ax.plot(data_x, data_y)

    #min_val = data_y.astype(np.int).min()
    #max_val = data_y.astype(np.int).max()
    #yticks = np.arange(min_val, max_val + 1)
    #yrange = (yticks[0], yticks[-1])
    #ax.set_yticks(yticks)
    #ax.set_ylim(yrange)

    ax.set_xlabel('Cycle Number')
    ax.set_ylabel('Output')
    ax.set_title(func_name)

    if show_detail:
        print("   == Details for Function " + func_name + " ==")
        print("   Cycle Range:  [0 ~ " + str(len(data_x) - 1) + "]")
        print("   Binding Function Output:")
        print(data_y)
        print()

##
# Convert string literal to boolean
##
def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

##
# Main program logic
##
if __name__ == '__main__':
    print()

    ##
    # Process input parameters
    ##
    parser = argparse.ArgumentParser(prog='PlotBinding.py')
    parser.add_argument('--func', nargs='?', action='append', help='binding function')
    parser.add_argument('--subplot', nargs='?', default='false')
    parser.add_argument('--cycle_num', nargs='?', default='50')
    parser.add_argument('--show_detail', nargs='?', default='false')

    arg_ns, unknown = parser.parse_known_args()
    if arg_ns.func is None:
        print(">> Incorrect input parameters.")
        print("------------------------------")
        parser.print_help()
        sys.exit(10)

    bUseSubPlot = str2bool(arg_ns.subplot)
    bShowDetail = str2bool(arg_ns.show_detail)
    cycle_num = 100
    if arg_ns.cycle_num is not None:
        cycle_num = int(arg_ns.cycle_num)

    ##
    # Check if NB file is already available
    # Download it if needed
    ##
    if not check_nb_existence():
        print(">> Can't find NB binary file; downloading it.")
        print("---------------------------------------------")
        download_nb()

    ##
    # Check if the NB binding YAML file already exists in the current folder
    # Overwrite it if needed.
    ##
    bingYamlFileName = "bindingPlot.yaml"

    # bOverwrite = False
    # if path.exists(bingYamlFileName):
    #     bOverwrite = expect_cmd_input()

    bOverwrite = True
    func_names = []
    func_names_long = []
    if bOverwrite:
        bf = open(bingYamlFileName, "w+")
        bf.write("bindings:\n")

        for i in range(0, len(arg_ns.func)):
            func = arg_ns.func[i]
            nameonly = (func.split(('('))[0]).lower()

            func_names.append(nameonly)
            func_names_long.append(func)
            bf.write("  " + nameonly + ": " + func + "\n")

        bf.close()

    ##
    # At this point, we have a working binding YAML file that can run NB workload
    ##
    # Execute NB workload
    print(">> Execute NB workload simulation!")

    #curPath = os.getcwd() + "/"

    if is_linux():
        # Make sure NB has execution permission
        cur_nb_permission = stat.S_IMODE(os.lstat("nb").st_mode)
        os.chmod("nb", cur_nb_permission | stat.S_IXOTH)

        cmdStr = "./nb run driver=stdout workload=" + bingYamlFileName + \
                 " cycles=" + str(cycle_num) + " --show-stacktraces"
    else:
        cmdStr = "java -jar nb.jar run driver=stdout workload=" + bingYamlFileName + \
                 " cycles=" + str(cycle_num) + " --show-stacktraces"

    nb_proc = subprocess.Popen([cmdStr],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    bFirstLine = True
    logFileName = ""
    bExecError = False
    bindingResults = []
    while True:
        line = nb_proc.stdout.readline().decode('ascii')
        if not line:
            break

        # print the first output line that show the execution log file
        if bFirstLine:
            logFileName = line.split()[2]
            print("   == Execution Log: " + logFileName)
            bFirstLine = False

        bExecError = line.lower().find("error in scenario") != -1
        if bExecError:
            print("   == Error in NB execution. Please check log file for more details!")
            break

        if func_names[0] in line:
            keyValuePairs = line.split()
            line_values = []
            for i in range(0, len(keyValuePairs)):
                line_values.append(float(keyValuePairs[i].split('=')[1]))
            bindingResults.append(line_values)

    print()

    np_res_arr = np.array(bindingResults)
    cycles = np.arange(0, cycle_num)

    #x = np.linspace(0, cycle_num, cycle_num)

    if len(np_res_arr) > 0:
        func_num = len(np_res_arr[0])

        if bUseSubPlot == False:
            for plot_idx in range(0, func_num):
                fig, ax = plt.subplots()

                values = np.array(np_res_arr[:, plot_idx])
                # values_nocycle = np.subtract(values, cycles)
                plot_binding_graph(
                    ax,
                    cycles,
                    values,
                    func_names_long[plot_idx],
                    bShowDetail
                )
        else:
            plot_num = int(func_num / 4 + 1)

            for plot_idx in range(0, plot_num):
                fig, axs = plt.subplots(2, 2)
                plt.subplots_adjust(hspace=0.6, wspace=0.5)

                for subplot_idx in range(0, 4):
                    func_idx = plot_idx * 4 + subplot_idx
                    if func_idx >= func_num:
                        break

                    print (">> Plot binding function output for " + func_names_long[func_idx])
                    print()
                    values = np.array(np_res_arr[:, func_idx])
                    #values_nocycle = np.subtract(values, cycles)
                    plot_binding_graph(
                        axs[int(subplot_idx/2), (subplot_idx%2)],
                        cycles,
                        values,
                        func_names_long[func_idx],
                        bShowDetail
                    )
        plt.show()
