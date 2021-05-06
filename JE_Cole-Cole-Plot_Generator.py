from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import pandas as pd
import os
import sys

temperatur_interval_in_kelvin = 1.5
error_temp_interval_in_percent = 0.1

print("Insert dat-filepath, out-filepath, molecular weight [g/mol] and mass [mg] seperated by comma as follows:\n")
print("C:\...\...\example.dat,C:\...\...,1000,20\n")

def get_inputs():
    '''This function tells the user to input a dat-filepath, a molecular weight and a mass.

    Returns a tuple: (dat-filepath, out-filepath, molecular_weight, mass)
    '''

    while True:
        userinput = input("Your Input:")
        print("------------------------------------------------------------------------------\n")

        ####in case a dumb user don't know difference between Space and Tab...
        ###userinput = userinput.replace("\t", " ")

        userinput_split_list = userinput.split(",")

        #####in case there are more than one Spaces between the inputs....
        ###userinput_split_list = list(filter(None, userinput_split_list))
        #print(userinput_split_list)
        print(userinput_split_list)
        #checks if file exists, if molecular mass and mass are > 0. If everything is fine, assign the list items to variables and break the while loop. If something is wrong -> Go to beginn of while loop (Ccontinue)
        if len(userinput_split_list) == 4:
            if Path(userinput_split_list[0]).is_file() == False:
                print("1Error! Invalid file path! Please input a proper dat-filepath, a molecular weight and the used mass!\n")
                continue

            if Path(userinput_split_list[1]).is_file() == False:
                print("2Error! Invalid file path! Please input a proper dat-filepath, a molecular weight and the used mass!\n")
                continue


            try:
                mol_weight = float(userinput_split_list[2])
                if mol_weight <= 0:
                    print("3Error! Molecular weight cannot be negative or zero!\n")
                    continue
            except ValueError:
                print("4Error! Invalid molecular mass! Please input a proper dat-filepath, a molecular weight and the used mass!\n")
                continue

            try:
                mass = float(userinput_split_list[3])
                if mass <= 0:
                    print("5Error! Mass cannot be negative or zero!\n")
                    continue
            except ValueError:
                print("6Error! Invalid mass! Please input a proper dat-filepath, a molecular weight and the used mass!\n")
                continue
            
            return_tuple = (userinput_split_list[0], userinput_split_list[1], mol_weight, mass)
            return return_tuple
        else:
            print("7Error! Please input only a dat-filepath, a molecular weight and the used mass!\n")
        
def create_dataframe_from_datfile(dat_filepath):
    ''' This function creates a pandas dataframe from the user choosen dat-file.
        It converts the columns "m' (emu)", "m" (emu)", and "Drive Amplitude (Oe)" to float64. The remaining clolumns stay as object.

        Returns a pandas dataframe
    
    '''

    raw_data = open(dat_filepath, "r", encoding="UTF-8")
    raw_data_lines_list = raw_data.readlines()
    raw_data.close()

    for i in range(0,len(raw_data_lines_list),1):
        if raw_data_lines_list[i].find("[Data]") != -1:
            #creating headers for forw
            raw_data_lines_list[i+1] = raw_data_lines_list[i+1].replace("\n", "")
            headers_list = raw_data_lines_list[i+1].split(",")

            #creating a Dataframe with the first data line
            raw_data_lines_list[i+2] = raw_data_lines_list[i+2].replace("\n", "")
            index0_df_list = raw_data_lines_list[i+2].split(",")
            dataframe = pd.DataFrame([index0_df_list], columns=headers_list)

            #appending the rest of the data to the dataframe
            for i in range(i+3,len(raw_data_lines_list),1):
                raw_data_lines_list[i] = raw_data_lines_list[i].replace("\n", "")
                dataframe.loc[len(dataframe)] = raw_data_lines_list[i].split(",")

    #drops the two empty rows at the end of the dataframe
    try:
        dataframe.drop([""], axis=1, inplace = True)
    except:
        pass

    #converts the important columns to float64; everything else can stay as object (=string), cause it won't be needed
    dataframe = dataframe.astype({"Field (Oe)": "float64"})
    dataframe = dataframe.astype({"Temperature (K)": "float64"})
    dataframe = dataframe.astype({"m' (emu)": "float64"})
    dataframe = dataframe.astype({"""m" (emu)""": "float64"})
    dataframe = dataframe.astype({"Drive Amplitude (Oe)": "float64"})
    dataframe = dataframe.astype({"Wave Frequency (Hz)": "float64"})
    #print(dataframe.dtypes)

    return dataframe

def create_fit_arrays_from_outfile(out_filepath):
    #out_filepath = r"C:\Users\Julian\Desktop\Andi.out"
    out_file = open(out_filepath, "r", encoding="UTF-8")
    read_outfile_list = out_file.readlines()
    out_file.close()

    temp_fit_list = []
    xM_prime_fit_list = []
    xM_doubleprime_fit_list = []
    cut_fit_list = []
    counter_fit_cut = 0
    for line in read_outfile_list:
        if line.find("T =") != -1:
            line = line.replace("T", "").replace("=", "").replace("\n", "").replace(" ", "")
            line = float(line)
            temp_fit_list.append(line)
            cut_fit_list.append(counter_fit_cut)
        elif line.find("Wave_freq") != -1:
            pass
        else:
            line = line.replace("\n", "").replace("\t", " ")
            line_split_list = line.split(" ")
            line_split_list = list(filter(None, line_split_list))
            xM_prime_fit_list.append(float(line_split_list[1]))
            xM_doubleprime_fit_list.append(float(line_split_list[2]))
            counter_fit_cut = counter_fit_cut+1
    cut_fit_list.append(counter_fit_cut)

    temp_fit_arr = np.array(temp_fit_list)
    amount_temps_fit = len(temp_fit_arr)
    xM_prime_fit_arr = np.array(xM_prime_fit_list)
    xM_doubleprime_fit_arr = np.array(xM_doubleprime_fit_list)

   
    #print(xM_prime_fit_arr[-10:])
    #print("---------------------------")
    #print(xM_doubleprime_fit_arr[-10:])
    #print("---------------------------")
    print("cut_fit_list:", cut_fit_list)
    print("temp_fit_arr:", temp_fit_arr)
    print("amount_temps_fit:", amount_temps_fit)
    
    return temp_fit_arr, cut_fit_list, xM_prime_fit_arr, xM_doubleprime_fit_arr

def create_xM_prime_doubleprime(dataframe):
    ''' This function creates xM_prime and xM_doubleprime as 1d-numpy arrays
        
        Returns xM_prime_arr, xM_doubleprime_array    
    '''
    df = dataframe
    m_prime_arr = df["m' (emu)"].to_numpy()
    m_doubleprime_arr = df["""m" (emu)"""].to_numpy()
    drive_amplitude_arr = df["Drive Amplitude (Oe)"].to_numpy()
    xV_prime_arr = np.divide(m_prime_arr, drive_amplitude_arr)
    xV_doubleprime_arr = np.divide(m_doubleprime_arr, drive_amplitude_arr)
    xM_prime_arr = np.array([((item*mol_weight)/(0.001*mass)) for item in xV_prime_arr])
    xM_doubleprime_arr = np.array([((item*mol_weight)/(0.001*mass)) for item in xV_doubleprime_arr])

    return xM_prime_arr, xM_doubleprime_arr

def create_cut_list_by_temp(temp_arr, temperatur_interval_in_kelvin, error_temp_interval_in_percent):        
    ''' 1) This function creates a new list cut_data with the indices to cut the data in respect to the given temperatures. 

        2) This function calculates the amount of temperatures

        Construction: Iterate through the temp_array. If a the absolute difference between two consecutive temps is SMALLER then
        (temperatur_interval_in_kelvin-(temperatur_interval_in_kelvin*error_temp_interval_in_percent) --> save the cut index 

        returns a tuple (cut_data (list), amount_temps (int))
    '''
    cut_data = []
    index = 0
    amount_temps = 1
    reference_temp = temp_arr[0]
    for temp in temp_arr:
        #print(temp)
        #print(abs(temp-reference_temp))
        if abs(temp - reference_temp) >= (temperatur_interval_in_kelvin - (temperatur_interval_in_kelvin*error_temp_interval_in_percent)):
            reference_temp = temp
            cut_data.append(index)
            amount_temps = amount_temps + 1
        index = index + 1
    cut_data.append(index)
    return_tuple = (cut_data, amount_temps)
    return return_tuple

def plot_cole_cole_exp(xM_prime_arr, xM_doubleprime_arr, temp_arr, cut_data_list, color_diversity, cmap_name):
    X = xM_prime_arr
    Y = xM_doubleprime_arr
    temp_min = np.amin(temp_arr)
    temp_max = np.amax(temp_arr)
    cmap = cm.get_cmap(cmap_name, color_diversity)

    plt.scatter(X, Y, c = temp_arr, cmap=cmap)

    start_plot = 0
    temp_counter = 0
    for cut in cut_data_list:
        #print(temp_arr[start_plot])
        plt.plot(X[start_plot:cut], Y[start_plot:cut], linewidth = 2, color = cmap(float(abs(temp_arr[start_plot]-temp_min)/(temp_max-temp_min))))
        start_plot = cut
        temp_counter = temp_counter + 1

    #defining labels
    plt.xlabel("xM'")
    plt.ylabel("xM''")

    #defining colorbar
    plt.colorbar()#orientation="horizontal", pad=0.2)
    plt.show()

def plot_cole_cole_exp_fit(xM_prime_arr, xM_doubleprime_arr, temp_arr, xM_prime_fit_arr, xM_doubleprime_fit_arr, temp_fit_arr, cut_fit_list,  color_diversity, cmap_name):
    X_exp = xM_prime_arr
    Y_exp = xM_doubleprime_arr
    X_fit = xM_prime_fit_arr
    Y_fit = xM_doubleprime_fit_arr
    temp_min = np.amin(temp_arr)
    temp_max = np.amax(temp_arr)
    cmap = cm.get_cmap(cmap_name, color_diversity)

    plt.scatter(X_exp, Y_exp, c = temp_arr, cmap=cmap)

    cut_fit_list.pop(0)
    start_plot = 0
    temp_counter = 0
    for cut in cut_fit_list:
        plt.plot(X_fit[start_plot:cut], Y_fit[start_plot:cut], linewidth = 2, color = cmap(float(abs(temp_fit_arr[temp_counter]-temp_min)/(temp_max-temp_min))))
        start_plot = cut
        temp_counter = temp_counter + 1

    #defining labels
    plt.xlabel("xM'")
    plt.ylabel("xM''")

    #defining colorbar
    plt.colorbar()#orientation="horizontal", pad=0.2)
    plt.show()

if __name__ == "__main__": 
    #gets and stores user input
    inputs_tuple = get_inputs()
    dat_filepath = inputs_tuple[0]
    out_filepath = inputs_tuple[1]
    mol_weight = inputs_tuple[2]
    mass = inputs_tuple[3]

    #creates Dataframe from dat file
    df = create_dataframe_from_datfile(dat_filepath)

    #converts magnetization to suszeptibility. Gives you 5 arrays to work with: xM_prime, xM_doubleprime, Field(Oe), Temp(K), Frequenzy(Hz)
    xM_prime_arr, xM_doubleprime_arr = create_xM_prime_doubleprime(df)
    field_arr = df["Field (Oe)"].to_numpy()
    temp_arr = df["Temperature (K)"].to_numpy()
    frequ_arr = df["Wave Frequency (Hz)"].to_numpy()    
    #important for the Colorbar! Otherwise its scale won't start and end at the end
    temp_arr = np.round(temp_arr, 1)
    print("temp_arr:", temp_arr)
    

    #gets amount of temperetures and a list with starting indices of new temperatures values
    sort_data_tuple = create_cut_list_by_temp(temp_arr, temperatur_interval_in_kelvin, error_temp_interval_in_percent)
    cut_data_list = sort_data_tuple[0]
    amount_temps = sort_data_tuple[1]
    print("cut_data_list:", cut_data_list)
    print("amount_temps:", amount_temps)

    #Plot the data using xM_prime, xM_doubleprime, cut_data_list, amount_temps, colordiversity for the cmap and the name of the cmap:
    plot_cole_cole_exp(xM_prime_arr, xM_doubleprime_arr, temp_arr, cut_data_list, 256, "coolwarm")

    #creates fit arrays from out file
    temp_fit_arr, cut_fit_list, xM_prime_fit_arr, xM_doubleprime_fit_arr = create_fit_arrays_from_outfile(out_filepath)
    amount_temps_fit = len( temp_fit_arr)

    if amount_temps != amount_temps_fit:
        print("Error! Amount of temperatures in data does not match the amount of temperatures")
        sys.exit()

    #Plot exp data and fit:
    plot_cole_cole_exp_fit(xM_prime_arr, xM_doubleprime_arr, temp_arr, xM_prime_fit_arr, xM_doubleprime_fit_arr, temp_fit_arr, cut_fit_list,  256, "coolwarm")

    print(xM_prime_fit_arr[0]/xM_prime_arr[0])

