'''
Author: Wenbin FAN
First Release: Oct. 30, 2019
Modified: Dec. 12, 2019
Verision: 1.4

[Intro]
Plot
# (1) the overlap of each xi window,
# (2) the variance in each trajectory,
# (3) potential of mean force,
# (4) recrossing factor,
# (5) the evolution of normalized population of xi,
# (6) the force constant,
# (7) the evolution of the potential of mean force (PMF),
# (8) the evolution of free energy and corresponding reaction coordinates,
for a single task.

[Usage]
run `python <this file name>` then you will be ask to input a path containing a result for a single task.
Then you'll get all four figures above if your task ended normally.

Attention, please! The former figures will be deleted when the program started running.

[Contact]
Mail: fanwenbin@shu.edu.cn, langzihuigu@qq.com
WeChat: 178-6567-1650

Thanks for using this python program, with the respect to my supervisor Prof. Yongle!
Great thanks to Yang Hui.

[Bug Fixing]
V1.4:
1) plot 10 UI and PMF figure in evolution,
2) plot 3D version of UI and PMF
3) optimize the reading procedure
V1.3:
1) read information from input file,
2) add a plot for force constant.
3) add a plot for potential of mean force.
V1.2:
1) PMF: Plot range modified.
'''

import os
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

color = ['#00447c', '#ae0d16', '#47872c', '#800964']


# SHU Blue, Weichang Red, Willow Green, SHU Purple
# This color scheme can be easily obtained on the official website `vi.shu.edu.cn`.

def input_path():
    path = input('Please input the folder with `submitting script` and your input file: \n')
    return path


def clearFolder(path):
    if os.path.exists(path):
        for fileName in os.listdir(path):
            os.remove(os.path.join(path, fileName))
    else:
        os.makedirs(path)


def plot_parameters(title):
    print('[INFO] Plotting {}! '.format(title))
    plt.figure(figsize=(4, 3))
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["mathtext.fontset"] = "stix"  # The font closet to Times New Roman
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['ytick.right'] = True
    plt.rcParams['ytick.left'] = True
    plt.rcParams['xtick.top'] = True
    plt.minorticks_on()  # Turn on minor ticks

    file = '{}.png'.format(title)
    if os.path.exists(file):
        os.remove(file)


def plot_save(name):
    plt.tight_layout()
    plt.savefig(name + '.png', format='png', dpi=600)  # .svg is recommended!
    plt.clf()
    plt.close()


def my_gaussian(x, xav, xav2):
    y = (1.0 / (np.sqrt(2.0 * np.pi * xav2))) * np.exp(-(x - xav) ** 2 / (2.0 * xav2))
    return y


def plot_overlap():
    title = 'Overlap'
    plot_parameters(title)

    resolution = 2000
    extend = 0.03  # 3E-2

    xiMin = np.min(xi_list)
    xiMax = np.max(xi_list)
    length = len(xi_list)

    x_new = np.linspace(xiMin - extend, xiMax + extend, resolution)
    y_sum = np.zeros((resolution))  # Total density line

    maxPop = 0  # maximum of the summation of all population
    for i in range(length):
        # Gaussian smearing
        xav, xav2 = umbInfo[3:, NtrajEff - 1, i]
        if xav2 < 1E-10:  # xav2 is zero!
            plt.axvline(xi_list[i], ls='--', c='red', lw=0.2)
            print('[ERROR] Variance at `xi = {}` is ZERO! '.format(xi_list[i]))
        else:
            y_new = my_gaussian(x_new, xav, xav2)

            # Find biggest population
            if max(y_new) > maxPop:
                maxPop = max(y_new)

            y_sum += y_new  # sum all population
            if xav2 > 5.0E-5:
                print("[WARNING] May be too various in xi = {}! ".format(xi_list[i]))
                plt.plot(x_new, y_new, lw=1, c=color[1], alpha=0.8)
            else:
                plt.plot(x_new, y_new, lw=0.5, c=color[0], alpha=.3)

    # Plot summation and difference
    plt.plot(x_new, y_sum, lw=1, c=color[0], label=mylabel)  # label='Summation of all populations')  # SHU Blue

    # plt.xlabel('Reaction Coordinate / Å')
    plt.xlabel('Reaction Coordinate')
    plt.ylabel('Population')

    plt.xlim(xiMin - extend, xiMax + extend)
    # plt.ylim(0, maxPop*1.1)
    plt.ylim(0, max(y_sum) * 1.1)

    plt.yticks([])  # No ticks and labels in y axis

    plt.legend(loc="best")
    plot_save(title)


def plot_variance():
    if NtrajEff == 1:
        return

    title = 'Variance'
    plot_parameters(title)

    xiMin = np.min(xi_list)
    xiMax = np.max(xi_list)
    length = len(xi_list)

    for i in range(length):
        xivar = umbInfo[4, :, i]
        timeEvolution = umbInfo[2, :, i]

        timeStep = delta
        timeEvolution = [x * timeStep * 10E-4 for x in timeEvolution]  # 0.1 fs to 1 ns

        if xivar[-1] > 5E-5:
            print('       traj. at xi = {} may be too various! '.format(xi_list[i]))

        # xivarDelta = []
        # for i in range(len(xivar)-1):
        #     xivarDelta.append(np.abs(xivar[i+1] - xivar[i]))
        # x = range(len(xivar))
        # plt.yscale('log')

        # # Shifted
        # for i in range(len(xivar)):
        #     xivar[i] = xivar[i] - xivar[0]

        # color = (np.random.rand(), np.random.rand(), np.random.rand())
        plt.plot(timeEvolution, xivar, lw=0.2, c=color[0], alpha=0.5)

    plt.xlabel('$t$ (ns)')
    plt.ylabel('Variance')

    # Scientific notation for y axis
    # # plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    from matplotlib import ticker
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-1, 1))
    plt.gca().yaxis.set_major_formatter(formatter)

    plot_save(title)


def plot_pmf(path):
    title = 'PMF'
    plot_parameters(title)

    try:
        f = open(path + '/potential_of_mean_force.dat', 'r')
    except FileNotFoundError:
        print('[ERROR] {} file not found! '.format(title))
    else:
        fLines = f.readlines()
        f.close()

        xi = []
        pmf = []
        for i in fLines[12:-1]:
            xi.append(np.float(i.split()[0]))
            pmf.append(np.float(i.split()[1]))

        # Let W(xi=0) = 0!
        xiAbs = np.abs(xi)
        xiZeroIndex = list(xiAbs).index(min(np.abs(xi)))
        pmf = [(x - pmf[xiZeroIndex]) / 27.211 * 627.503 for x in pmf]  # shift and convert to kcal/mol

        plt.xlabel(r'Reaction Coordinate')
        plt.ylabel(r'$W(\xi)$ (kcal/mol)')

        # Choose the fit range of this plot
        plt.xlim(xi[0], xi[-1])
        yRange = max(pmf) - min(pmf)
        plt.ylim(min(pmf) - yRange * 0.1,
                 max(pmf) + yRange * 0.1)  # adds 0.1*yRange to the top and bottom

        plt.plot(xi, pmf, c=color[0], label=mylabel)

        # # plot a zoomed subfigure
        # xiMaxIndex = pmf.index(max(pmf)) # the position of maximum
        # extend = 80 # Extra points to plot
        # ximax = xi[xiMaxIndex - extend : xiMaxIndex + extend]
        # pmfmax = pmf[xiMaxIndex - extend : xiMaxIndex + extend]
        #
        # # # Find maximum of xi
        # f = itp(ximax, pmfmax, k=4)
        # cr_pts = f.derivative().roots()
        # cr_pts = np.append(cr_pts, (ximax[0], ximax[-1]))  # also check the endpoints of the interval
        # cr_vals = f(cr_pts)
        # #! min_index = np.argmin(cr_vals)
        # max_index = np.argmax(cr_vals)
        # pmfMax, xiMax = cr_vals[max_index], cr_pts[max_index]
        #
        # subfig = plt.axes([.3, .5, .5, .4])
        # subfig.plot(ximax, pmfmax, c=color[0])
        #
        # subfig.axvline(x=xiMax, c=color[0], lw=0.5, linestyle='--')
        # subfig.axhline(y=pmfMax, c=color[0], lw=0.5, linestyle='--')
        #
        # plt.setp(subfig, xlim=[min(ximax), max(ximax)])

        plt.legend(loc="best")
        plot_save(title)


def plot_rexFactor(path):
    title = 'Transmission_Coefficient'
    plot_parameters(title)

    # Find the file first!
    fileList = os.listdir(path)
    rexFileName = ''
    for file in fileList:
        if file[:18] == 'recrossing_factor_':
            rexFileName = file

    try:
        f = open(path + '/' + rexFileName, 'r')
    except FileNotFoundError:
        print('[ERROR] {} file not found! '.format(title))
    except PermissionError:
        print('[ERROR] {} file not found! '.format(title))
    else:
        fLines = f.readlines()
        f.close()
        time = []
        kappa = []
        for i in fLines[17:-1]:
            ele = i.split()
            time.append(np.float(ele[0]))
            kappa.append(np.float(ele[-1]))

        plt.xlabel('$t$ / fs')
        plt.ylabel('$\kappa(t)$')

        # plt.xscale('log')

        plt.xlim(time[0], time[-1])
        # # endRF = np.mean(kappa[-5:])
        # plt.axhline(y=kappa[-1], c=color[0], lw=0.5, linestyle='--')

        plt.plot(time, kappa, c=color[0], label=mylabel)

        plt.legend(loc="best")
        plot_save(title)


def plot_overlap_density(path):
    if NtrajEff == 1:
        return

    title = 'Overlap_Density'
    plot_parameters(title)

    resolution = 2000
    extend = 0.03  # 3E-2

    xiMin = np.min(xi_list)
    xiMax = np.max(xi_list)

    sizeV = NtrajEff  # np.shape(umbInfo)[1]
    sizeH = np.shape(umbInfo)[2]

    x_new = np.linspace(xiMin - extend, xiMax + extend, resolution)

    # Read time unit
    tempFile = open(path + "/umbrella_sampling_{0:.4f}.dat".format(xi_list[0]), 'r')
    lines = tempFile.readlines()
    timeSep = np.float(lines[9].split()[4]) / 1000.0  # to ns

    z = np.zeros((sizeV * resolution))
    y = np.linspace(xiMin - extend, xiMax + extend, resolution)

    # Gaussian summation
    for j in range(sizeV):  # xi
        y_sum = np.zeros((resolution))
        for i in range(sizeH):  # var
            y_new = my_gaussian(x_new, umbInfo[3, j, i], umbInfo[4, j, i])
            y_sum += y_new
            z[j * resolution:(j + 1) * (resolution)] = y_sum


    # plt.show()
    z = z.reshape(sizeV, resolution).transpose()
    z /= np.max(z)
    x = np.linspace(0, timeSep * sizeV, sizeV)
    plt.pcolormesh(x, y, z, cmap='Greens', vmax=1.0)  # pcolormesh # contourf # Greys_r

    plt.xlabel('time (ns)')
    plt.ylabel('Reaction Coordinate')

    plt.colorbar()
    # plt.title('The Evolution of Normalized Population')
    plot_save(title)

    # 3D UI
    X, Y = np.meshgrid(x, y)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, z, cmap='Greens', linewidth=0.2, edgecolors='black')
    ax.view_init(elev=20, azim=30)

    ax.set_xlabel(r'Time (ns)')
    ax.set_ylabel(r'Reaction Coordinate')
    ax.set_zlabel(r'Energy (kcal/mol)')

    plot_save('Overlap_Density_3D')

    clearFolder('UI')
    for cycle in range(NtrajEff):
        if (cycle + 1) % np.int(NtrajEff / 10) == 0 or cycle == 0 or cycle == NtrajEff - 1:
            resolution = 2000
            extend = 0.03  # 3E-2

            xiMin = np.min(xi_list)
            xiMax = np.max(xi_list)
            length = len(xi_list)

            x_new = np.linspace(xiMin - extend, xiMax + extend, resolution)
            y_sum = np.zeros((resolution))  # Total density line

            maxPop = 0  # maximum of the summation of all population

            timeCurrent = umbInfo[2, cycle, 0] * delta * 1E-3
            plot_parameters('UI at time {:.4f} ns'.format(timeCurrent))

            for i in range(length):
                # Gaussian smearing
                xav, xav2 = umbInfo[3:, cycle, i]
                y_new = my_gaussian(x_new, xav, xav2)

                if xav2 - 1E-8 < 0:
                    print(cycle, i, '<0', xav, xav2)

                # Find biggest population
                if max(y_new) > maxPop:
                    maxPop = max(y_new)

                y_sum += y_new  # sum all population
                if xav2 > 5.0E-5:
                    # print("[WARNING] May be too various in xi = {}! ".format(xi_list[i]))
                    plt.plot(x_new, y_new, lw=1, c=color[1], alpha=0.8)
                else:
                    plt.plot(x_new, y_new, lw=0.5, c=color[0], alpha=.3)

            # Plot summation and difference
            plt.plot(x_new, y_sum, lw=1, c=color[0], label='{:.4f} ns'.format(timeCurrent))
            # mylabel)  # label='Summation of all populations')  # SHU Blue

            # plt.xlabel('Reaction Coordinate / Å')
            plt.xlabel('Reaction Coordinate')
            plt.ylabel('Population')

            plt.xlim(xiMin - extend, xiMax + extend)
            # plt.ylim(0, maxPop*1.1)
            plt.ylim(0, max(y_sum) * 1.1)

            plt.yticks([])  # No ticks and labels in y axis

            plt.legend(loc="best")
            plot_save('UI/{:.4f}'.format(timeCurrent))



def plotKForce():
    plot_parameters('force constant')

    markerline, stemlines, baseline = \
        plt.stem(xi_list, kforce_list, use_line_collection=True,
                 basefmt=' ', markerfmt=' ', linefmt=color[0])
    plt.setp(stemlines, 'linewidth', 0.5)
    plt.scatter(xi_list, kforce_list, c=color[0], s=1, label=mylabel)

    plt.ylabel('Force Constant ($T$ K$^{-1}$ eV)')
    plt.xlabel('Reaction Coordinate')

    # plt.xlim(min(xi_list), max(xi_list))
    plt.ylim(0, max(kforce_list) * 1.1)

    plt.legend(loc="best")
    plot_save('kforce')


def plot_PMF_evolution():
    if NtrajEff == 1:
        return

    print('[INFO] Computing PMF evolution...')
    clearFolder('PMF')

    # Constants
    bins = 500
    beta = 4.35974417e-18 / (1.3806504e-23 * temp)
    totalCycle = NtrajEff  #np.shape(umbInfo)[1]  # the number of trajectories
    Nwindows = np.shape(umbInfo)[2]  # the number of windows

    # middle variables for calculations
    binList = np.linspace(min(xi_list), max(xi_list), bins, True)
    dA = np.zeros(bins)
    p = np.zeros(Nwindows)  # probability
    dA0 = np.zeros(Nwindows)

    # PMF data storage
    PMFdata = np.zeros((bins - 1, totalCycle))
    freeEnergy = np.zeros((3, totalCycle))  # time, xi, free energy

    for cycle in range(totalCycle):
        # for cycle in [-1]:
        print('       Computing PMF evolution {} of {}'.format(cycle + 1, totalCycle))
        N = umbInfo[2, cycle, :]
        for n, xi in enumerate(binList):
            for l in range(Nwindows):
                # av = window.av / window.count
                # av2 = window.av2 / window.count
                xi_mean = umbInfo[3, cycle, l]  # computed
                xi_var = umbInfo[4, cycle, l]  # computed
                xi_window = xi_list[l]  # fixed
                kforce = kforce_list[l] * temp  # fixed
                p[l] = 1.0 / np.sqrt(2 * np.pi * xi_var) * np.exp(-0.5 * (xi - xi_mean) ** 2 / xi_var)
                dA0[l] = (1.0 / beta) * (xi - xi_mean) / xi_var - kforce * (xi - xi_window)
                # plt.plot(p, label=l)
            dA[n] = np.sum(N * p * dA0) / np.sum(N * p)
            # plt.legend()
            # plt.show()

        # Now integrate numerically to get the potential of mean force
        potentialOfMeanForce = np.zeros((2, bins - 1))
        A = 0.0
        for n in range(bins - 1):
            dx = binList[n + 1] - binList[n]
            potentialOfMeanForce[0, n] = 0.5 * (binList[n] + binList[n + 1])
            A += 0.5 * dx * (dA[n] + dA[n + 1])
            potentialOfMeanForce[1, n] = A
        potentialOfMeanForce[1, :] -= np.min(potentialOfMeanForce[1, :])

        PMFcurrent = potentialOfMeanForce[1, :] * 627.503  # to kcal/mol

        # Let W(xi=0) = 0!
        xiAbs = np.abs(xi_list)
        xiZeroIndex = list(xiAbs).index(min(np.abs(xi_list)))
        PMFcurrent = [x - PMFcurrent[xiZeroIndex] for x in PMFcurrent]
        PMFdata[:, cycle] = PMFcurrent

        timeCurrent = umbInfo[2, cycle, 0] * delta * 1E-3

        # save 10 PMF figures
        if (cycle + 1) % np.int(totalCycle / 10) == 0 or cycle == 0 or cycle == totalCycle:
            plot_parameters('PMF at time {:.4f} ns'.format(timeCurrent))
            plt.plot(binList[:-1], PMFcurrent, c=color[0], label='{:.4f} ns'.format(timeCurrent))
            plt.xlabel(r'Reaction Coordinate')
            plt.ylabel(r'$W(\xi)$ (kcal/mol)')
            plt.legend()
            plot_save(r'PMF\{:.4f}'.format(timeCurrent))

        # calculate free energy
        pmfMaxValue = np.max(PMFcurrent)
        pmfMaxIndex = PMFcurrent.index(pmfMaxValue)
        freeEnergy[:, cycle] = timeCurrent, binList[pmfMaxIndex], pmfMaxValue


    # # write PMF datas
    # f = open('PMF_data.txt', 'w')
    # f.write('\t'.join(map(str, list(umbInfo[2,:,0]))) + '\n') # map(str, value_list)
    # for i in range(bins - 1):
    #     f.write('\t'.join(map(str, PMFdata[i,:])) + '\n')

    # write PMF datas
    f = open('PMF_data.txt', 'w')
    for j in range(totalCycle):
        for i in range(bins - 1):
            f.write(
                '{:.4f}\t{:.4f}\t{:.4f}\n'.format(umbInfo[2, j, 0] * delta * 1E-3, binList[i],
                                                  PMFdata[i, j]))  # time to ns
    f.close()

    # Plot PMF evolution
    plot_parameters('PMF evolution')

    a = pd.read_csv('PMF_data.txt', sep='\t', header=None)

    traj = list(a.iloc[:, 0])
    xibins = list(a.iloc[:, 1])
    pmfvalue = list(a.iloc[:, 2])

    pmfMin = np.min(pmfvalue)
    pmfMax = np.max(pmfvalue)
    level = np.arange(np.int(pmfMin) - 2, np.int(pmfMax) + 2, 1)

    plt.tricontourf(traj, xibins, pmfvalue, levels=level, cmap='Blues')
    plt.colorbar()
    plt.tricontour(traj, xibins, pmfvalue, linestyles='-', levels=level, colors='Black', linewidths=0.2)

    plt.xlabel(r'Time (ns)')
    plt.ylabel(r'Reaction Coordinate')
    plot_save('PMF_evolution')

    # 3D plot
    # print(len(traj), (totalCycle, bins - 1))
    X = np.reshape(traj, (totalCycle, bins - 1))
    Y = np.reshape(xibins, (totalCycle, bins - 1))
    Z = np.reshape(pmfvalue, (totalCycle, bins - 1))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, cmap='Blues', linewidth=0.2, edgecolors='black')
    ax.view_init(elev=20, azim=30)

    ax.set_xlabel(r'Time (ns)')
    ax.set_ylabel(r'Reaction Coordinate')
    ax.set_zlabel(r'Energy (kcal/mol)')

    plot_save('PMF_evolution_3D')

    # Plot free energy
    plot_parameters('free energy')

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    fig.set_figheight(3)
    fig.set_figwidth(4)
    ax1.set_xlim(0, np.max(freeEnergy[0, :]))

    ax1.plot(freeEnergy[0, :], freeEnergy[1, :], c=color[0])  # , label='Reaction Coordinate')
    ax2.plot(freeEnergy[0, :], freeEnergy[2, :], c=color[1], label='Free Energy')
    ax2.plot(freeEnergy[0, 0], freeEnergy[2, 0], c=color[0], label='Reaction Coordinate')  # fake figure for legend

    ax1.set_xlabel('Time (ns)')
    ax1.set_ylabel('Reaction Coordinate')  # , color=color[0])
    ax2.set_ylabel('Free Energy (kcal/mol)')  # , color=color[1])

    ax2.legend(loc='best')

    plot_save('PMF_free_energy')


def getBasicInfo(path):
    # get the name of submitting script
    subList = ['run.sh', 'highcpu', 'fat', 'gpu', 'pbs', 'run.txt']  # submitting script
    subName = ''
    subPath = ''
    for i, name in enumerate(subList):
        if os.path.exists(os.path.join(path, name)):
            subName = name
            subPath = os.path.join(path, name)
            break
    print('[INFO] Submitting arguments: ')

    # read temperature and the number of beads
    cmdLine = ''
    f = open(subPath, 'r')
    for line in f:
        if line[:6] == 'python':
            cmdLine = line.split()
    del cmdLine[:2]  # delete `python` and `...rpmdrate.py`

    # get the number of cores used
    cores = 0
    for i, cmd in enumerate(cmdLine):
        if cmd == '-p':
            cores = cmdLine[i + 1]
            print('       Cores:            {}'.format(np.int(cores)))
            del cmdLine[i:i + 2]
            break
    if cores == 0:
        print('       Cores:            single')

    # delete redirect output
    for i, cmd in enumerate(cmdLine):
        if cmd == '>' or cmd == '>>' or cmd == '#>':
            del cmdLine[i: i + 2]

    # get input file, temperature and the number of beads
    assert len(cmdLine) == 3, 'Your submitting script may be wrong! '
    global inputFile, temp, Nbeads  # There will be probably more pythonic way. Tell me plz if you know!
    inputFile = cmdLine[0]
    temp = np.int(cmdLine[1])
    Nbeads = np.int(cmdLine[2])

    print('       Temperature:      {} K'.format(temp))
    print('       Number of beads:  {}'.format(Nbeads))
    print('       Input file:       {}\n'.format(inputFile))

    return inputFile


def getUmbrellaInfo(path):
    print('[INFO] Getting umbrella data...')
    Nwindows = len(xi_list)
    print('       number of windows: {}'.format(Nwindows))

    # Count the total lines of xi and xvar
    NtrajList = np.zeros(Nwindows)
    for i in range(Nwindows):
        with open(path + "/umbrella_sampling_{0:.4f}.dat".format(xi_list[i]), 'r') as tempFile:
            for j, l in enumerate(tempFile):
                pass
        NtrajList[i] = j + 1 - 15  # 15 info lines # +1 means the number of lines

    global Ntraj, NtrajEff
    Ntraj = np.int(np.max(NtrajList))
    NtrajEff = np.int(np.min(NtrajList))  # Effective lines
    print('       Maximum of trajectories: {}'.format(Ntraj))
    print('       Minimum of trajectories: {}\n'.format(NtrajEff))

    global umbInfo
    umbInfo = np.zeros((5, Ntraj, Nwindows))  # `5` means five columns in the umbrella info files.

    # Read time unit
    tempFile = open(path + "/umbrella_sampling_{0:.4f}.dat".format(xi_list[0]), 'r')
    lines = tempFile.readlines()
    timeSep = np.float(lines[9].split()[4]) / 1000.0  # to ns
    tempFile.close()

    # Read in all data
    for i in range(Nwindows):
        fname = path + "/umbrella_sampling_{0:.4f}.dat".format(xi_list[i])
        f = open(fname, 'r').readlines()

        for j in range(Ntraj):
            try:
                line = f[15 + j].split()
                assert len(line) == 5
                umbInfo[:, j, i] = line
            except IndexError:
                umbInfo[:, j, i] = None

    return umbInfo


def getInput(folder):
    inputPath = os.path.join(folder, inputFile)

    # skip `import PES`
    f = open(inputPath, 'r')
    start = 0
    inputContent = ''
    for i, line in enumerate(f.readlines()):
        if line[:5] == 'label' or line[:5] == 'react':
            start = 1
        if start == 1:
            inputContent += line.replace('numpy', 'np')

    # execute the input.py and get force constant
    T = temp
    try:
        exec(inputContent)
    except (NameError, TypeError, SyntaxError):
        print('[ERROR] The input file {0!r} was invalid:'.format(inputPath))
        raise

    global path
    path = os.path.join(folder, str(temp), str(Nbeads))

    global mylabel
    if Nbeads == 1:
        mylabel = '{} K, {} bead'.format(temp, Nbeads)
    else:
        mylabel = '{} K, {} beads'.format(temp, Nbeads)

# Defination in RPMDrate:
def reactants(atoms, reactant1Atoms, reactant2Atoms, Rinf):
    pass


def transitionState(geometry, formingBonds, breakingBonds):
    pass


def equivalentTransitionState(formingBonds, breakingBonds):
    pass


def thermostat(type, **kwargs):
    pass


def generateUmbrellaConfigurations(dt, evolutionTime, xi_list, kforce):
    global delta
    delta = dt[0]
    assert np.float(delta) < 1

def conductUmbrellaSampling(dt, windows, saveTrajectories=False):
    global xi_list, kforce_list
    # print(windows)
    xi_list = np.zeros(len(windows))
    kforce_list = np.zeros(len(windows))
    for i in range(len(windows)):
        xi_list[i] = '{0:.4f}'.format(windows[i][0])
        kforce_list[i] = windows[i][1] / temp
    return xi_list, kforce_list


def computePotentialOfMeanForce(windows=None, xi_min=None, xi_max=None, bins=5000):
    pass


def computeRecrossingFactor(dt, equilibrationTime, childTrajectories, childSamplingTime, childrenPerSampling,
                            childEvolutionTime, xi_current=None, saveParentTrajectory=False,
                            saveChildTrajectories=False):
    pass


def computeRateCoefficient():
    pass


def Window(xi, kforce, trajectories, equilibrationTime, evolutionTime):
    return [np.float(xi), np.float(kforce)]


def main(folder=None):
    if folder == None:
        folder = input_path()

    # get info
    getBasicInfo(folder)
    getInput(folder)
    getUmbrellaInfo(path)

    # # plot
    # plotKForce()
    # plot_overlap()
    # plot_variance()
    # plot_pmf(path)
    # plot_rexFactor(path)
    # plot_overlap_density(path)
    plot_PMF_evolution()


main(r'D:\ohch4\400K')
