import pandas as pd
import numpy as np
import re


def extract_elements(tst, elements):
    t = [[tst.index(e[0]), e] for e in elements if e in tst]
    sorted_elements = sorted(t, key=lambda x: x[0])
    return [i[-1] for i in sorted_elements]

def weighted_average(values, weights):
    return np.dot(values, weights) / sum(weights)

def pol(tst, elements, Z, r):
    h = extract_elements(tst, elements)
    p = Z[h]**2/r[h]
    pwoCo = p.drop('Co').tolist()
    weights = list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", tst)[:-2]))
    return weighted_average(pwoCo, weights)

def total_charge(tst, elements, Z):
    h = extract_elements(tst, elements)
    Zz = Z[h]
    zwoCo = Zz.drop('Co').tolist()
    weights = list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", tst)[:-2]))
    return weighted_average(zwoCo, weights)

def electronegativity(tst, elements, x):
    h = extract_elements(tst, elements)
    xx = x[h]
    xwoCo = xx.drop('Co').tolist()
    weights = list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", tst)[:-2]))
    return weighted_average(xwoCo, weights)

def ra(tst, elements, r, c):
    h = extract_elements(tst, elements)
    a_site_elements = [e for e in h if c[e] == 8]
    weights = list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", tst)[:len(a_site_elements)]))
    return weighted_average(r[a_site_elements], weights)

def rb(tst, elements, r, c):
    h = extract_elements(tst, elements)
    b_site_elements = [e for e in h if c[e] == 6]
    a_site_elements = [e for e in h if c[e] == 8]
    weights = list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", tst)[len(a_site_elements):len(b_site_elements)+len(a_site_elements)]))
    return weighted_average(r[b_site_elements], weights)

def convert(filename, sheetname, exportfile, elements, Z, r, x, c):
    f = pd.read_excel(filename, sheet_name=sheetname)
    Name = f.iloc[:, 0].dropna()

    O = pd.DataFrame(columns=['Name', 'Temperature (deg C)', 'Oxygen Vacancy'])
    
    for idx, T in enumerate(f.columns[1:]):
        for q, k in enumerate(f[T]):
            O.loc[idx * len(f) + q] = [Name[q], T, k]

    name = O['Name']
    temperature = O['Temperature (deg C)']

    pdata = [pol(i, elements, Z, r) for i in name]
    zdata = [total_charge(i, elements, Z) for i in name]
    xxdata = [electronegativity(i, elements, x) for i in name]
    radata = [ra(i, elements, r, c) for i in name]
    rbdata = [rb(i, elements, r, c) for i in name]

    tolerancefactordata = [(a + 1.34) / (b + 1.34) / 2**0.5 for a, b in zip(radata, rbdata)]

    pd.DataFrame({
        'Samples': name,
        'Oxygen vacancy': O['Oxygen Vacancy'],
        'Polarization': pdata,
        'Charge': zdata,
        'Electronegativity': xxdata,
        'Radius A-site': radata,
        'Radius B-site': rbdata,
        'Tolerance factor': tolerancefactordata,
        'Temperature': temperature
    }).to_excel(exportfile)