import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
from sklearn.metrics import r2_score
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from os.path import join as pjoin

# define the curve-fit function, the tuning of number is a gaussian
def gaussian(x, *param):
    return param[0] * np.exp(-(x - param[1])**2 / (2 * param[2]**2))

out_path = '/nfs/s2/userhome/zhouming/workingdir/numerosity/out/images/numer' 
act_path = '/nfs/s2/userhome/zhouming/workingdir/numerosity/out/activation' 
num_path = '/nfs/s2/userhome/zhouming/workingdir/numerosity/out/numerosity_unit' 
# %% prepare columns
namelist = ['fc1_relu', 'fc2_relu']  # the 
for name in namelist:
    numlist = np.asarray([i for i in range(1, 33)])
    actname = 'act_' + name + '.npy'  # define the act file name
    act = np.load(pjoin(act_path, actname))  # load the act data of neure
    infoname = 'id80_' + name + '.npy'  # define the information file name
    info = np.load(pjoin(num_path, infoname))  # load the information data of neure
    info = pd.DataFrame(info)  # turns to a DataFrame
    # define the columns, nid: the neure id, pn: prefered number of neure, 
    # r2: the goodness of gaussian curve fit, A: the applitude of gaussian, 
    # M: the center of gaussian, S: the various of gaussian, 
    # sim: the similarity of the tuning curve in three datasets
    info.columns = ['nid', 'pn', 'r2', 'A', 'M', 'S', 'sim']
    # turn the id into the index
    loc = info.nid - 1
    # define the output file name prefix
    name = name + '80new'
    # flag the data of neure
    flag = 0
    # turn the data into a long list
    for index in loc:
        index = int(index)
        nid = info.nid[flag]
        
        col1 = act[:, index, 0, 0]
        col2 = np.repeat([1,2,3], np.shape(act)[0] / 3, axis=0)  # dataset
        col3 = np.tile(np.repeat(numlist, 600), 3)  # number
        col4 = np.repeat(info.pn[flag], np.shape(act)[0], axis=0)  # prefered number
        col5 = np.repeat(nid, np.shape(act)[0], axis=0)  # record the id of origin
        mat = np.zeros((np.shape(act)[0], 5))
        mat[:,0] = col1
        mat[:,1] = col2
        mat[:,2] = col3
        mat[:,3] = col4
        mat[:,4] = col5
        df = pd.DataFrame(mat)
        df.columns = ['act', 'dset', 'num', 'pn', 'id']
        if flag == 0:
            dfall = df
        else:
            dfall = pd.concat([dfall, df], ignore_index=True)
        flag += 1
    
    
    # %% plot tunning curve based on mean raw act 
    # open a figure
    plt.figure(figsize=(20, 15))
    # begin the plot
    for i in range(8):
        for j in range(4):
            PN = numlist[i * 4 + j]  # define the prefered number
            df = dfall[dfall['pn'] == PN].copy()  # choose out pictures that which prefered numbers equals the dots' numbers
            dfm = df.groupby(df['num']).mean()['act']  # means of group the numbers of the pictures
            dfstd = df.groupby(df['num']).std()['act']  # stds of group the numbers of the pictures
            dferr = dfstd / ((df.count() / 32)['act'] ** 0.5)  # the standard error of data
            ax = plt.subplot(8, 4, (i)*4+j+1)  # choose a subplot
            ax.set_xticks([])
            ax.set_title(f'PN = {PN}',fontsize=10)
            # plot out the row mean curve of three datasets
            if len(df) != 0:
                colorlist = ['red', 'blue', 'green']
                labellist = ['dset1', 'dset2', 'dset3']
                for k in range(3):
                    dfm1 = df[df['dset'] == k+1]
                    dfm1 = dfm1.groupby(df['num']).mean()['act']
                    dfm1n = (dfm1 - dfm1.min()) / (dfm1.max() - dfm1.min())
                    ax.plot(dfm1, color=colorlist[k], linewidth=0.7, label=labellist[k])
                if PN == 1:
                    ax.legend(fontsize=10)
                plt.errorbar(numlist, dfm, yerr=dferr, fmt='k', ecolor='black', elinewidth=2)
    picname = 'curve_ro_' + name + '.png'
    plt.savefig(pjoin(out_path, picname))
    plt.close('all')
    
    
    # %% plot tunning curve based on mean scaled act 
    plt.figure(figsize=(20, 15))
    for i in range(8):
        for j in range(4):
            PN = numlist[i * 4 + j]
            df = dfall[dfall['pn'] == PN].copy()
            dfm = df.groupby(df['num']).mean()['act']
            dfmn = (dfm - dfm.min()) / (dfm.max() - dfm.min())
    
            scale = dfm.max() - dfm.min()
            dfstd = df.groupby(df['num']).std()['act'] / scale
            dferr = dfstd / ((df.count() / 32)['act'] ** 0.5)
            ax = plt.subplot(8, 4, (i)*4+j+1)
            ax.set_xticks([])
            ax.set_title(f'PN = {PN}',fontsize=10)
            # plot out the normolize mean curve of three datasets
            if len(df) != 0:
                colorlist = ['red', 'blue', 'green']
                labellist = ['dset1', 'dset2', 'dset3']
                for k in range(3):
                    dfm1 = df[df['dset'] == k+1]
                    dfm1 = dfm1.groupby(df['num']).mean()['act']
                    dfm1n = (dfm1 - dfm1.min()) / (dfm1.max() - dfm1.min())
                    ax.plot(dfm1n, color=colorlist[k], linewidth=0.7, label=labellist[k])
                if PN == 1:
                    ax.legend(fontsize=10)
                plt.errorbar(numlist, dfmn, yerr=dferr, fmt='k', ecolor='black', elinewidth=2)
    picname = 'curve_no_' + name + '.png'
    plt.savefig(pjoin(out_path, picname))
    plt.close('all')
    
    
    # %% decribe the distribution of numerosity units
    plt.figure(figsize=(20, 15))
    bar = dfall.groupby(dfall['pn']).count()['act'] / (np.shape(act)[0])
    # bar = bar.drop(1)
    plt.xticks(bar.index)
    plt.bar(bar.index, bar, width = 0.9)
    plt.tick_params(labelsize=20)
    # tag the number of different prefered numbers' neure
    for a,b in zip(bar.index, bar):
        plt.text(a, b, '%.0f'%b, ha='center', va='bottom', fontsize=20)
    picname = 'describe_' + name + '.png'
    plt.savefig(pjoin(out_path, picname))
    plt.close('all')


    # %%
    # calculate different gaussian's sigmas of different scale
    # line: linear scale, log: log scale, 
    # pow2: power of 1/2 scale, pow3: power of 1/3 scale
    sigmaline = []
    sigmalog = []
    sigmapow2 = []
    sigmapow3 = []
    r2line = []
    r2log = []
    r2pow2 = []
    r2pow3 = []
    plt.figure(figsize=(20, 15))
    for i in range(8):
        for j in range(4):
            PN = numlist[i * 4 + j]
            df = dfall[dfall['pn'] == PN].copy()
            dfm = df.groupby(df['num']).mean()['act']
            dfmn = (dfm - dfm.min()) / (dfm.max() - dfm.min())
            
            ax = plt.subplot(8, 4, (i)*4+j+1)
            ax.set_xticks([])
            ax.set_title(f'PN = {PN}', fontsize=10)
            plt.ylim(-0.1, 1.2)
            # plot out the mean curve to compared with the fit curve
            ax.plot(dfmn)
            if len(dfm) != 0:
                # fit the gaussian curve in linear scale, plot out it, and record the parameter
                popt, pcov = curve_fit(gaussian, numlist, dfmn, p0=[5, 5, 5], bounds=([0, 0, 0], [np.inf, 33, np.inf]), maxfev=5000000)
                plt.plot(numlist, gaussian(numlist, *popt))
                sigmaline.append(popt[2])
                r2 = r2_score(dfmn, gaussian(numlist, *popt))
                r2line.append(r2)
                # in log scale
                popt, pcov = curve_fit(gaussian, np.log2(numlist), dfmn, p0=[5, 5, 5], bounds=([0, 0, 0], [np.inf, 33, np.inf]), maxfev=5000000)
                sigmalog.append(popt[2])
                r2 = r2_score(dfmn, gaussian(np.log2(numlist), *popt))
                r2log.append(r2)
                # in pow2 scale
                popt, pcov = curve_fit(gaussian, numlist**(1/2), dfmn, p0=[5, 5, 5], bounds=([0, 0, 0], [np.inf, 33, np.inf]), maxfev=5000000)
                sigmapow2.append(popt[2])
                r2 = r2_score(dfmn, gaussian(numlist**(1/2), *popt))
                r2pow2.append(r2)
                # in pow3 scale
                popt, pcov = curve_fit(gaussian, numlist**(1/3), dfmn, p0=[5, 5, 5], bounds=([0, 0, 0], [np.inf, 33, np.inf]), maxfev=5000000)
                sigmapow3.append(popt[2])
                r2 = r2_score(dfmn, gaussian(numlist**(1/3), *popt))
                r2pow3.append(r2)
    picname = 'gaussian_' + name + '.png'
    plt.savefig(pjoin(out_path, picname))
    plt.close('all')


    # %%
    
    plt.figure(figsize=(20, 15))
    ax = plt.subplot(111)
    plt.tick_params(labelsize=20)
    num = dfall.groupby(dfall['pn']).mean().index
    ax.set_xticks(num)
    # plot out the sigma dot in different scale
    plt.plot(num, np.asarray(np.abs(sigmaline)) / (2**0.5), label = 'line')
    plt.plot(num, np.asarray(np.abs(sigmalog)) / (2**0.5), label = 'log')
    plt.plot(num, np.asarray(np.abs(sigmapow2)) / (2**0.5), label = 'pow1/2')
    plt.plot(num, np.asarray(np.abs(sigmapow3)) / (2**0.5), label = 'pow1/3')
    plt.xlabel('PN', fontsize=30)
    plt.ylabel('sigma', fontsize=30)
    ax.legend(fontsize=30)
    picname = 'sigma_' + name + '.png'
    plt.savefig(pjoin(out_path, picname))
    plt.close('all')


    # %%
    length = len(num)
    plt.figure(figsize=(20, 15))
    mat = np.zeros((length * 4, 2))
    mat[:,0] = r2line + r2log + r2pow2 + r2pow3
    mat[:,1] = ['1'] * length + ['2'] * length + ['3'] * length + ['4'] * length
    dfr2 = pd.DataFrame(mat)
    dfr2.columns = ['r2', 'scale']
    formula = 'r2~C(scale)'
    res = anova_lm(ols(formula, dfr2).fit())
    print(res);

    r2 = dfr2.groupby(dfr2['scale']).mean()['r2']
    r2se = dfr2.groupby(dfr2['scale']).std()['r2'] / length**0.5
    # plot out goodnesses in different scale
    plt.ylim(0.8, 1)
    plt.tick_params(labelsize=30)
    plt.xlabel('Scale', fontsize=40)
    plt.ylabel('Goodness of fit (r2)', fontsize=40)
    plt.bar(['line', 'log', 'pow1/2', 'pow1/3'], r2, yerr=r2se, error_kw={'capsize' : 6, 'elinewidth' : 3, 'capthick' : 2})
    # and statistical test
    res1 = stats.ttest_rel(dfr2[dfr2['scale']==1]['r2'], dfr2[dfr2['scale']==2]['r2'])
    res2 = stats.ttest_rel(dfr2[dfr2['scale']==1]['r2'], dfr2[dfr2['scale']==3]['r2'])
    res3 = stats.ttest_rel(dfr2[dfr2['scale']==1]['r2'], dfr2[dfr2['scale']==4]['r2'])
    print('log', res1[1], 'pow1/2', res2[1], 'pow1/3', res3[1])
    picname = 'r2_' + name + '.png'
    plt.savefig(pjoin(out_path, picname))
    plt.close('all')
