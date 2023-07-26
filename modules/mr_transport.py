# -*- coding: utf-8 -*-
"""

"""
def calc_transport(output_main_dir,custom_name,ichem_only,tchem_only,nroom,mrvol):

    '''
    import modules
    '''
    import pickle
    import numpy as np
    import csv


    output_data_before_transport={}
    for iroom in range(0, nroom):
        out_dir = ("%s/%s_%s" % (output_main_dir,'room{:02d}'.format(iroom+1),'c{:04d}'.format(ichem_only-1)))
        with open(("%s/%s" % (out_dir,'restart_data.pickle')),'rb') as handle:
            output_data_before_transport[iroom]=pickle.load(handle)

    #print(output_data_before_transport[1])

    # Comprises an array of AERs between rooms (m3/s)
    trans_params_csv = open("config_rooms/mr_tcon_transport_params.csv")
    trans_params = np.genfromtxt(trans_params_csv, delimiter=",")
    #print(trans_params)


#    output_data_after_transport={}
#    for iroom in range(0, nroom):
#        output_data_after_transport[iroom]=0.5*(output_data_before_transport[0]+output_data_before_transport[1])
#        output_folder = ("%s_%s_%s" % (custom_name,'c'+str(ichem_only-1),'r'+str(iroom+1)))
#        with open(("%s/%s" % (output_folder,'out_data.pickle')),'wb') as handle:
#            pickle.dump(output_data_after_transport[iroom],handle)


    output_data_after_transport={}
    for iroom_trans_orig in range(0, nroom):
        output_data_after_transport[iroom_trans_orig]=\
         output_data_before_transport[iroom_trans_orig]*(mrvol[iroom_trans_orig]*1.0E6)
        for iroom_trans_dest in range (0, nroom):
            if (iroom_trans_dest!=iroom_trans_orig) and (trans_params[iroom_trans_orig,iroom_trans_dest]!=0.0):
                output_data_after_transport[iroom_trans_orig]=(output_data_after_transport[iroom_trans_orig]
                 + ((trans_params[iroom_trans_orig,iroom_trans_dest]*tchem_only*1.0E6)
                 * (output_data_before_transport[iroom_trans_dest]
                 - output_data_before_transport[iroom_trans_orig])))
        output_data_after_transport[iroom_trans_orig] = \
            output_data_after_transport[iroom_trans_orig]/(mrvol[iroom_trans_orig]*1.0E6)
        out_dir = ("%s/%s_%s" % (output_main_dir,'room{:02d}'.format(iroom_trans_orig+1),'c{:04d}'.format(ichem_only-1)))
        with open(("%s/%s" % (out_dir,'restart_data.pickle')),'wb') as handle:
            pickle.dump(output_data_after_transport[iroom_trans_orig],handle)

    #print(output_data_after_transport[1])

    return None
