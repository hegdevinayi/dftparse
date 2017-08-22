from dft_parser.pwscf.stdout_parser import PwscfStdOutputParser


def test_simple():
    """Test that parsing simple one-line rules works"""
    parser = PwscfStdOutputParser()
    lines = """
        bravais-lattice index     =            0
        lattice parameter (alat)  =       7.1517  a.u.
        unit-cell volume          =     919.5821 (a.u.)^3
    """.split("\n")
    results = list(parser.parse(lines))
    flattened = {}
    for r in results:
        flattened.update(r)
    assert flattened["lattice parameter"] == 7.1517
    assert flattened["bravais-lattice index"] == 0
    assert flattened["unit-cell volume"] == 919.5821
    assert flattened["unit-cell volume units"] == "(a.u.)^3"


def test_energy_contributions():
    """Test that rules which are generated by a function work"""
    lines = """
        !    total energy              =    -439.62704582 Ry
             Harris-Foulkes estimate   =    -439.62704606 Ry
             estimated scf accuracy    <       0.00000033 Ry
        
             The total energy is the sum of the following terms:
        
             one-electron contribution =     -13.58082604 Ry
             hartree contribution      =      68.24717960 Ry
             xc contribution           =    -123.45729278 Ry
             ewald contribution        =    -370.83610660 Ry
             smearing contrib. (-TS)   =       0.00000000 Ry
        
             convergence has been achieved in   8 iterations
    """.split("\n")
    parser = PwscfStdOutputParser()
    results = list(parser.parse(lines))
    flattened = {}
    for r in results:
        flattened.update(r)
    assert flattened["total energy"] == -439.62704582
    assert flattened["total energy units"] == "Ry"
    assert flattened["one-electron energy contribution"] == -13.58082604
    assert flattened["one-electron energy contribution units"] == "Ry"


def test_parse_stress():
    """Test that parses multiple lines into a list output"""
    lines = """
                total   stress  (Ry/bohr**3)                   (kbar)     P=  -77.72
        -0.00055293   0.00000000   0.00000000        -81.34      0.00      0.00
         0.00000000  -0.00055293   0.00000000          0.00    -81.34      0.00
         0.00000000   0.00000000  -0.00047917          0.00      0.00    -70.49
      """.split("\n")
    parser = PwscfStdOutputParser()
    results = list(parser.parse(lines))
    flattened = {}
    for r in results:
        flattened.update(r)
    assert flattened["pressure"] == -77.72
    assert flattened["pressure units"] == "kbar"
    assert len(flattened["stress"]) == 3
    assert flattened["stress"][1][1] == -81.34
    assert flattened["stress units"] == "kbar"


def test_parse_force():
    """Test that force parsing works"""
    lines = """
        Forces acting on atoms (Ry/au):
      
        atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
        atom    2 type  2   force =     0.00000000    0.00000000    0.00000054
        The non-local contrib.  to forces
        atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
        atom    2 type  2   force =     0.00000000    0.00000000   -0.00000016
        The ionic contribution  to forces
        atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
        atom    2 type  2   force =     0.00000000    0.00000000    0.00000000
        The local contribution  to forces
        atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
        atom    2 type  2   force =     0.00000000    0.00000000    0.00000187
        The core correction contribution to forces
        atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
        atom    2 type  2   force =     0.00000000    0.00000000    0.00000000
        The Hubbard contrib.    to forces
        atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
        atom    2 type  2   force =     0.00000000    0.00000000    0.00000000
        The SCF correction term to forces
        atom    1 type  1   force =     0.00000000    0.00000000    0.00000000
        atom    2 type  2   force =     0.00000000    0.00000000   -0.00000117
      
        Total force =     0.011752     Total SCF correction =     0.000072
    """.split("\n") 
    parser = PwscfStdOutputParser()
    results = list(parser.parse(lines))
    flattened = {}
    for r in results:
        flattened.update(r)
    assert flattened["force units"] == "(Ry/au)"
    assert flattened["total force"] == 0.011752
    assert flattened["total SCF correction"] == 0.000072
    assert flattened["forces"][1][2] == 0.00000054 
    assert flattened["non-local contribution to forces"][1][2] == -0.00000016
    assert flattened["Atomic species index for forces"][1] == 2


def test_parse_force_short():
    """Test that force parsing without the contributions works"""
    lines = """
        Forces acting on atoms (Ry/au):

        atom    1 type  1   force =    -0.00147138    0.00084950    0.00000000
        atom    2 type  1   force =     0.00137999   -0.00079673    0.00000000
        atom    3 type  1   force =     0.00147138   -0.00084950    0.00000000
        atom    4 type  1   force =    -0.00137999    0.00079673    0.00000000

        Total force =     0.003294     Total SCF correction =     0.000014
    """.split("\n")
    parser = PwscfStdOutputParser()
    results = list(parser.parse(lines))
    flattened = {}
    for r in results:
        flattened.update(r)
    assert flattened["force units"] == "(Ry/au)"
    assert flattened["total force"] == 0.003294
    assert flattened["total SCF correction"] == 0.000014
    assert flattened["forces"][3][0] == -0.00137999
    assert flattened["Atomic species index for forces"][3] == 1
