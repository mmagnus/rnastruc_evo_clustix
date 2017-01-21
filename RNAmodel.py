#!/usr/bin/env python

import os
import Bio.PDB.PDBParser
import Bio.PDB.Superimposer
from Bio.PDB.PDBIO import Select
from Bio.PDB import PDBIO, Superimposer

class RNAmodel:
    """RNAModel"""
    def __init__(self, fpath, residues, save, output_dir):
        # parser 1-5 -> 1 2 3 4 5
        self.struc = Bio.PDB.PDBParser().get_structure('', fpath)
        self.residues = residues #self.__parser_residues(residues)
        self.__get_atoms()
        self.fpath = fpath
        self.fn = os.path.basename(fpath)
        #self.atoms = []
        if save:
            self.save(output_dir) # @save


    def __parser_residues(self, residues):
        """Get string and parse it
        '1 4 5 10-15' -> [1, 4, 5, 10, 11, 12, 13, 14, 15]"""
        rs = []
        for r in residues.split():
            l = parse_num_list(r)
            for i in l:
                if i in rs:
                    raise Exception('You have this resi already in your list! See', residues)
            rs.extend(l)
        return rs

    def __get_atoms(self):
        self.atoms=[]
        for res in self.struc.get_residues():
            if res.id[1] in self.residues:
                self.atoms.append(res["C3'"])
                #print res.id
                #ref_atoms.extend(, ref_res['P'])
            #ref_atoms.append(ref_res.get_list())
        if len(self.atoms) <= 0:
            raise Exception('problem: none atoms were selected!')
        return self.atoms
    
    def __str__(self):
        return self.fn #+ ' # beads' + str(len(self.residues))

    def __repr__(self):
        return self.fn #+ ' # beads' + str(len(self.residues))

    def get_report(self):
        """Str a short report about rna model""" 
        t = ' '.join(['File: ', self.fn, ' # of atoms:', str(len(self.atoms)), '\n'])
        for r,a in zip(self.residues, self.atoms ):
            t += ' '.join(['resi: ', str(r) ,' atom: ', str(a) , '\n' ])
        return t

    def get_rmsd_to(self, other_rnamodel, output=''):
        """Calc rmsd P-atom based rmsd to other rna model"""
        sup = Bio.PDB.Superimposer()
        sup.set_atoms(self.atoms, other_rnamodel.atoms)
        rms = round(sup.rms, 3)
        if output:
            io = Bio.PDB.PDBIO()
            sup.apply(self.struc.get_atoms())
            io.set_structure( self.struc )
            io.save("aligned.pdb")

            io = Bio.PDB.PDBIO()
            sup.apply(other_rnamodel.struc.get_atoms())
            io.set_structure( other_rnamodel.struc )
            io.save("aligned2.pdb")
            
        return rms

    def save(self, output_dir, verbose=True):
        """Save structures and motifs """
        folder_to_save =  output_dir + os.sep # ugly hack 'rp14/'
        try:
            os.makedirs(folder_to_save)
        except OSError:
            pass

        try:
            os.mkdir(folder_to_save + 'structures')
        except OSError:
            pass

        try:
            os.mkdir(folder_to_save + 'motifs')
        except OSError:
            pass

        RESI = self.residues
        if not self.struc:
            raise Exception('self.struct was not defined! Can not save a pdb!')
        class BpSelect(Select):
            def accept_residue(self, residue):
                if residue.get_id()[1] in RESI:
                    return 1
                else:
                    return 0

        io = PDBIO()
        io.set_structure(self.struc)
        fn = folder_to_save + 'structures' + os.sep + self.fn #+ '.pdb'
        io.save(fn)
        if verbose:
            print '    saved to struc: %s ' % fn

        io = PDBIO()
        io.set_structure(self.struc)
        fn = folder_to_save +  'motifs/' + os.sep + self.fn #+ self.fn.replace('.pdb', '_motif.pdb')# #+ '.pdb'
        io.save(fn, BpSelect())
        if verbose:
            print '    saved to motifs: %s ' % fn
