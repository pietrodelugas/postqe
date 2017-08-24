#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
import re
import numpy as np
import xmlschema

from ase.atoms import Atoms, Atom


def split_atomic_symbol(x):
    regex = r"([a-zA-Z]{1,2})([1-9]?\d?)"
    match = re.match(regex, x)
    if match:
        return match.groups()
    else:
        return False


def xml_to_dict(filename):
    """
    This function reads the xml output using the xmlschema package and returns a dictionary with the output section.
    :param filename:
    :return:
    """

    import xmlschema

    ##########################################################
    # TODO for whatever reason this is not working now
    # schemaLoc = xmlschema.fetch_schema(filename)
    # xs = xmlschema.XMLSchema(schemaLoc)
    #
    # temporary local solution
    xs = xmlschema.XMLSchema('/home/mauropalumbo/pythonprojects/postqe/postqe/schemas/qes.xsd')
    ##########################################################

    print("Reading xml file: ", filename)
    d = xs.to_dict(filename)
    return d["output"]


def read_espresso_xml(filename):

    dout = xml_to_dict(filename)
    a1 = np.array(dout["atomic_structure"]["cell"]["a1"])
    a2 = np.array(dout["atomic_structure"]["cell"]["a2"])
    a3 = np.array(dout["atomic_structure"]["cell"]["a3"])
    a_p = (dout["atomic_structure"]["atomic_positions"]["atom"])

    atoms = Atoms()

    # First define the unit cell from a1, a2, a3 and alat
    cell = np.zeros((3, 3))
    cell[0] = a1
    cell[1] = a2
    cell[2] = a3
    atoms.set_cell(cell)

    # Now the atoms in the unit cell
    for atomx in a_p:
        # TODO: extent to all possible cases the symbol splitting (for now, only numbering up to 9 work). Not a very common case...
        symbol = split_atomic_symbol(atomx['@name'])[0]
        print(atomx['@name'], symbol)
        x = float(atomx['$'][0])
        y = float(atomx['$'][1])
        z = float(atomx['$'][2])
        atoms.append(Atom(symbol, (x, y, z)))

    return atoms


if __name__ == "__main__":
    from ase.build import bulk
    from ase.visualize import view

    FeO = read_espresso_xml('feo_af.xml', schema='schemas/qes.xsd')
    print (FeO.get_atomic_numbers())
    print (FeO.get_cell(True))
    print (FeO.get_positions())
    print (FeO.get_scaled_positions())
    view(FeO)

    print (100*'#')

    Ni = bulk('Ni', 'fcc', a=6.65)
    print (Ni.get_atomic_numbers())
    print (Ni.get_cell(True))
    print (Ni.get_positions())
    view(Ni)

    Ni2 = read_espresso_xml('Ni.xml', schema='schemas/qes.xsd')
    print (Ni2.get_atomic_numbers())
    print (Ni2.get_cell(True))
    print (Ni2.get_positions())
    print (Ni2.get_volume())
    view(Ni2)