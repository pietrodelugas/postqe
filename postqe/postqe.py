#!/usr/bin/env python3
#encoding: UTF-8

import time, sys
import numpy as np
from readutils import read_line, read_n_real_numbers,\
read_charge_file_iotk, read_pp_out_file, write_charge, create_header
from compute_vs import compute_v_bare, compute_v_h, compute_v_xc
from celldm import calcola_celldm


def get_from_xml(fname):
    """
    Get some useful values from xml file
    """

    import xsdtypes
    xd = xsdtypes.XmlDocument("../../qexsd/qespresso/scheme/qes.xsd")
    print ("Reading xml file: ",fname)
    xd.read(fname)
    d = xd.to_dict()
    
    dout = d["{http://www.quantum-espresso.org/ns/qes/qes-1.0}espresso"]["output"]
    ecutwfc = (dout["basis_set"]["ecutwfc"])
    ecutrho = (dout["basis_set"]["ecutrho"])
    alat = (dout["atomic_structure"]["alat"])
    a1 = np.array(dout["atomic_structure"]["cell"]["a1"])
    a2 = np.array(dout["atomic_structure"]["cell"]["a2"])
    a3 = np.array(dout["atomic_structure"]["cell"]["a3"])   
    ibrav = (dout["atomic_structure"]["bravais_index"])
    b1 = np.array(dout["basis_set"]["reciprocal_lattice"]["b1"])
    b2 = np.array(dout["basis_set"]["reciprocal_lattice"]["b2"])
    b3 = np.array(dout["basis_set"]["reciprocal_lattice"]["b3"])
    functional = np.array(dout["dft"]["functional"])
    a_p = (dout["atomic_structure"]["atomic_positions"]["atom"])
    a_s = (dout["atomic_species"]["species"])
    nat = (dout["atomic_structure"]["nat"])
    ntyp = (dout["atomic_species"]["ntyp"])
    
    # for subsequent loops it is important to have always lists for atomic_positions
    # and atomic_species. If this is not, convert
    if (type(a_s)==type([])):
        atomic_species = a_s
    else:
        atomic_species = [a_s,]
        
       
    if (type(a_p)==type([])):
        atomic_positions = a_p
    else:
        atomic_positions = [a_p,]
    
    a = np.array([a1,a2,a3])
    b = np.array([b1,b2,b3])
    
    return ecutwfc, ecutrho, ibrav, alat, a, b, functional, atomic_positions, atomic_species, nat, ntyp



def get_input_parameters():
    """
    Get postprocessing input parameters using argparse.
    """
    import argparse 
    
    parser = argparse.ArgumentParser(description='QE post processing')
    
    parser.add_argument('-plot_num', type=int, nargs='?', default=2, choices=range(0, 21),
    help="""selects what to save in filplot:\n
    0  = electron (pseudo-)charge density\n
    1  = total potential V_bare + V_H + V_xc\n
    2  = local ionic potential V_bare\n
    3  = local density of states at e_fermi (number of states per volume, in bohr^3,\
         per energy unit, in Ry)\n\
    4  = local density of electronic entropy\n\
    5  = STM images\n\
        Tersoff and Hamann, PRB 31, 805 (1985)\n\
    6  = spin polarization (rho(up)-rho(down))\n
    
    7  = contribution of a selected wavefunction to the
        (pseudo-)charge density. For norm-conserving PPs,
        |psi|^2 (psi=selected wavefunction). Noncollinear case:
        contribution of the given state to the charge or
        to the magnetization along the direction indicated
        by spin_component (0 = charge, 1 = x, 2 = y, 3 = z )

    8  = electron localization function (ELF)

    9  = charge density minus superposition of atomic densities

    10 = integrated local density of states (ILDOS)
        from emin to emax (emin, emax in eV)
        if emax is not specified, emax=E_fermi

    11 = the V_bare + V_H potential

    12 = the sawtooth electric field potential (if present)

    13 = the noncollinear magnetization.

    17 = all-electron valence charge density
        can be performed for PAW calculations only
        requires a very dense real-space grid!

    18 = The exchange and correlation magnetic field in
        the noncollinear case

    19 = Reduced density gradient
        (J. Chem. Theory Comput. 7, 625 (2011))
        Set the isosurface between 0.3 and 0.6 to plot the
        non-covalent interactions (see also plot_num = 20)

    20 = Product of the electron density (charge) and the second
        eigenvalue of the electron-density Hessian matrix;
        used to colorize the RDG plot (plot_num = 19)

    21 = all-electron charge density (valence+core).
        For PAW calculations only; requires a very dense
        real-space grid.
    """

        )
    default_prefix = "SiO2"
    default_prefix = "SrTiO3"
    parser.add_argument('-prefix', type=str, nargs='?', default=default_prefix,
                    help='prefix of files saved by program pw.x')
    default_outdir = "../tests/"+default_prefix
    parser.add_argument('-outdir', type=str, nargs='?', default=default_outdir,
                    help='directory containing the input data, i.e. the same as in pw.x')
    parser.add_argument('-filplot', type=str, nargs='?', default="filplot",
                    help='file \"filplot\" contains the quantity selected by plot_num\
                        (can be saved for further processing)')
    args = parser.parse_args()
    
    return args


if __name__ == "__main__":
    
    start_time = time.time()
    
    # get the input parameters
    pars = get_input_parameters()
    
    print (pars)
    
    # get some needed values from the xml output
    #print (pars.outdir+pars.prefix+".xml")
    ecutwfc, ecutrho, ibrav, alat, a, b, functional, atomic_positions, atomic_species,\
    nat, ntyp = get_from_xml(pars.outdir+"/"+pars.prefix+".xml")    
    celldms = calcola_celldm(alat,a[0],a[1],a[2],ibrav)
    
    charge_file = pars.outdir+"/charge-density.dat"
    charge = read_charge_file_iotk(charge_file)
    nr = charge.shape
    header = create_header(pars.prefix,nr,ibrav,celldms,nat,ntyp,atomic_species,atomic_positions)
    
    v_bare = read_pp_out_file("SiO2_quarzo_plotnum2.dat", 15, nr[0],nr[1],nr[2])
    v_bare_v_h = read_pp_out_file("SiO2_quarzo_plotnum11.dat", 15, nr[0],nr[1],nr[2])
    v_h = v_bare_v_h - v_bare
    write_charge("SiO2_vh",v_h,header)
    v_h2 =  compute_v_h(charge,ecutrho,alat,b)
    write_charge("SiO2_vhmio",v_h2,header)  
        
    #v_bare = read_pp_out_file("SrTiO3_plotnum2.dat", 12, nr[0],nr[1],nr[2])
    #v_bare_v_h = read_pp_out_file("SrTiO3_plotnum11.dat", 12, nr[0],nr[1],nr[2])
    #v_h = v_bare_v_h - v_bare
    #write_charge("SrTiO3_vh",v_h,header)
    #v_h2 =  compute_v_h(charge,ecutrho,alat,b)
    #write_charge("SrTiO3_vhmio",v_h2,header)  
    exit()
    
    if (pars.plot_num==0):   # Read the charge and write it in filpl       
        write_charge(pars.filplot,charge,header)
        
    elif (pars.plot_num==1):
        v_bare = compute_v_bare(ecutrho, alat, a[0], a[1], a[2], nr, atomic_positions, atomic_species)      
        v_h =  compute_v_h(charge,ecutrho,alat,b)
        charge_core = np.zeros(charge.shape)    # only for now, later in input
        v_xc = compute_v_xc(charge,charge_core,str(functional))
        v_tot = v_bare + v_h + v_xc
        write_charge(pars.filplot,v_tot,header)     
            
    elif (pars.plot_num==2):
        v_bare = compute_v_bare(ecutrho, alat, a[0], a[1], a[2], nr, atomic_positions, atomic_species)          
        write_charge(pars.filplot,v_bare,header)   
    
    elif (pars.plot_num==11):
        v_bare = compute_v_bare(ecutrho, alat, a[0], a[1], a[2], nr, atomic_positions, atomic_species)    
        write_charge("pippo1",v_bare,header)
        v_h =  compute_v_h(charge,ecutrho,alat,b)
        write_charge("pippo2",v_h,header)
        v_tot = v_bare + v_h
        write_charge(pars.filplot,v_tot,header)        
        
    else:
        print ("Not implemented yet")

  
    end_time = time.time()
    elapsed_time = end_time - start_time
    print ("Finished. Elapsed time: "+str(elapsed_time)+" s.")