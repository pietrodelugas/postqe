#!/usr/bin/env python3
#encoding: UTF-8

"""
This is a simple example of plotting a 1D section of the different potentials.
"""
    
if __name__ == "__main__":

    from postqe import get_potential

    v_bare = get_potential(label="./Ni", schema='../../schemas/qes.xsd', pot_type='v_bare')
    v_bare.write('v_bare.dat')
    fig1 = v_bare.plot(x0=(0, 0, 0), e1=(1, 0, 0), nx=50)
    fig1.savefig("figure_v_bare.png")

    v_h = get_potential(label="./Ni", schema='../../schemas/qes.xsd', pot_type='v_h')
    v_h.write('v_h.dat')
    fig2 = v_h.plot(x0=(0, 0, 0), e1=(1, 0, 0), nx=50)
    fig2.savefig("figure_v_h.png")

    v_xc = get_potential(label="./Ni", schema='../../schemas/qes.xsd', pot_type='v_xc')
    v_xc.write('v_xc.dat')
    fig3 = v_xc.plot(x0=(0, 0, 0), e1=(1, 0, 0), nx=50)
    fig3.savefig("figure_v_xc.png")

    v_tot = get_potential(label="./Ni", schema='../../schemas/qes.xsd', pot_type='v_tot')
    v_tot.write('v_tot.dat')
    fig4 = v_tot.plot(x0=(0, 0, 0), e1=(1, 0, 0), nx=50)
    fig4.savefig("figure_v_tot.png")
