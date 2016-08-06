#!/usr/bin/env python
#

import argparse
import csv
import logging
from zipfile import ZipFile

import re


from webapp import db
from webapp.models import Turbine, TurbinePowerCurve


def load_file(axis, f):
    if axis == 'HAWTs':
        vertical_axis = False
    elif axis == 'VAWTs':
        vertical_axis = True
    else:
        raise Exception('Incorrect value instead of HAWTs or VAWTs: %s', axis)
    spamreader = csv.reader(f)
    row_counter = 0
    name = None
    diameter_int = None
    diameter_frac = None
    v_cutoff = None
    v_cutin = None
    power_curve = []
    description = None
    for row in spamreader:
        if row_counter == 0:
            name = row[0]
        elif row_counter == 1:
            diameter_int = int(row[0])
        elif row_counter == 2:
            diameter_frac = int(row[0])
        elif row_counter == 3:
            v_cutoff = float(row[0])
        elif row_counter == 4:
            v_cutin = float(row[0])
        else:
            try:
                power = float(row[0])
                wind_speed = row_counter - 5
                power_curve.append((wind_speed, power))
            except ValueError, e:
                description = row[0].decode('iso8859-1')

        row_counter += 1

    name = re.sub(r'\)\)$', ')', name)
    name = re.sub(r'\s\([^()]+\)$', '', name)
    print name

    rated_power = None
    mo = re.search(r'([0-9.,]+)([mMkK][wW])', name)
    if mo:
        power = mo.group(1)
        power = power.replace(',', '.')
        unit = mo.group(2).lower()
        if unit == 'kw':
            rated_power = 1e-3 * float(power)
        elif unit == 'mw':
            rated_power = float(power)
        else:
            raise Exception('Unexpected power measurement unit: %s', unit)
        print power

    diameter = diameter_int + diameter_frac / 10.0

    try:
        turbine = Turbine(name=name, vertical_axis=vertical_axis, rotor_diameter=diameter, v_cutin=v_cutin,
                          v_cutoff=v_cutoff, description=description, rated_power=rated_power)
        db.session.add(turbine)
        db.session.commit()
        for item in power_curve:
            point = TurbinePowerCurve(turbine_id=turbine.id, wind_speed=item[0], power=item[1])
            turbine.power_curve.append(point)
        db.session.commit()
    except Exception:
        db.session.rollback()


def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    if args.delete:
        turbines = db.session.query(Turbine).all()
        for turbine in turbines:
            db.session.delete(turbine)
        db.session.commit()

    with ZipFile(args.file) as myzip:
        for file_name in myzip.namelist():
            if not file_name.endswith('.pow'):
                continue
            parts = file_name.split('/')
            company = 'Unknown'
            if len(parts) == 4:
                (_, axis, power, name) = parts
            elif len(parts) == 5:
                (_, axis, power, company, name) = parts
            elif len(parts) == 6:
                (_, axis, power, company, _, name) = parts
            else:
                raise Exception('Unintelligible file %s', file_name)

            with myzip.open(file_name) as f:
                try:
                    load_file(axis, f)
                except Exception, e:
                    logging.error('Error while processing file %s: %r', name, e)


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Loads turbines database from http://www.wind-power-program.com to the application database.")
    parser.add_argument(
        "file",
        help="load FILE",
        metavar="FILE")
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")
    parser.add_argument(
        "-d",
        "--delete",
        help="delete all turbines in database before import",
        action="store_true")
    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    main(args, loglevel)
