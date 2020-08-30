from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from models import Station, Line, LineName, GasMeter, Measurement, MeasurementParameter, \
    Driver, Controller, ControllerLineDetail, DriverLineDetail

DB_PATH = f'/home/elangaar/.config/libreoffice/4/user/Scripts/python/stuff.db'
DB_STRING = f'sqlite:///{DB_PATH}'

engine = create_engine(DB_STRING)
Session = sessionmaker(bind=engine)
session = Session()

# Auxiliary functions

def clean_data_range(sheet, start_cell, end_cell, *args):
    c_range = sheet.getCellRangeByName(f'{start_cell}:{end_cell}')
    c_range.clearContents(4)
    c_range.clearContents(2)
    c_range.clearContents(1)
    return

def get_libre_date(d):
    temp = datetime(1899, 12, 30)    # 30st Dec, not 31th
    delta = d - temp
    return float(delta.days) + (float(delta.seconds) / 86400)

def get_m_coeff(m, *args):
    s_temp = 293
    s_press = 1013
    press = m.mp.pressure
    temp = m.mp.temperature
    return (press*s_temp)/(temp*s_press)

def get_rt_value(m, *args):
    return get_m_coeff(m)*m.g_value

def get_err(m, *args):
    rt_value = get_rt_value(m)
    return ((m.c_value-rt_value)/rt_value)*100

def get_lines(*args):
    lines = [(l.id_line, str(l)) for l in session.query(Line).all()]
    return lines

# Macro functions

def update_data(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    clean_data_range(doc.Sheets['pomocniczy'], 'A20', 'Z20')
    stations = session.query(Station).all()
    for i, s in enumerate(stations):
        doc.Sheets['pomocniczy'][f'A{i+2}'].setString(s.id_station)
        doc.Sheets['pomocniczy'][f'B{i+2}'].setString(s.name)
    line_names = session.query(LineName).all()
    for i, ln in enumerate(line_names):
        doc.Sheets['pomocniczy'][f'C{i+2}'].setValue(ln.id_ln)
        doc.Sheets['pomocniczy'][f'D{i+2}'].setString(ln.name)
    gas_meters = session.query(GasMeter).all()
    for i, gm in enumerate(gas_meters):
        doc.Sheets['pomocniczy'][f'E{i+2}'].setValue(gm.id_gm)
        doc.Sheets['pomocniczy'][f'F{i+2}'].setString(gm.serial_number)
    lines = get_lines()
    for i, l in enumerate(lines):
        doc.Sheets['pomocniczy'][f'I{i+2}'].setString(l[1])
        doc.Sheets['pomocniczy'][f'J{i+2}'].setValue(l[0])
    drivers = session.query(Driver).all()
    for i, d in enumerate(drivers):
        doc.Sheets['pomocniczy'][f'L{i+2}'].setString(d.serial_number)
        doc.Sheets['pomocniczy'][f'M{i+2}'].setValue(d.id_driver)
    controllers = session.query(Controller).all()
    for i, c in enumerate(controllers):
        doc.Sheets['pomocniczy'][f'P{i+2}'].setString(c.serial_number)
        doc.Sheets['pomocniczy'][f'Q{i+2}'].setValue(c.id_controller)
    return

def save_measurement_data(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    sheet = doc.Sheets['Pomiar']

    temp = sheet.getCellRangeByName('D9').getValue()
    press = sheet.getCellRangeByName('C10').getValue()
    mp = MeasurementParameter(temperature=temp, pressure=press)

    line_id = doc.Sheets['pomocniczy']['K2'].getValue()
    line = session.query(Line).filter_by(id_line=line_id).one()
    gm_serial_number = sheet.getCellRangeByName('C6').getString()
    gm = session.query(GasMeter).filter_by(serial_number=gm_serial_number).first()

    dt = datetime.now()
    gv = sheet.getCellRangeByName('C11').getValue()
    cv = sheet.getCellRangeByName('C12').getValue()
    g_b_value = sheet.getCellRangeByName('C21').getValue()
    g_e_value = sheet.getCellRangeByName('C22').getValue()
    c_b_value = sheet.getCellRangeByName('C24').getValue()
    c_e_value = sheet.getCellRangeByName('C25').getValue()
    mtime = sheet.getCellRangeByName('C27').getValue()
    comments = sheet.getCellRangeByName('C35').getString()

    meas = Measurement(m_datetime=dt, g_value=gv, c_value=cv, line=line, gm=gm, mp=mp, \
                       g_b_value=g_b_value, g_e_value=g_e_value, c_b_value=c_b_value, \
                       c_e_value=c_e_value, m_time=timedelta(minutes=mtime), comments=comments)
    session.add(meas)
    session.commit()
    return

def get_error_line_chart(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    clean_data_range(doc.Sheets['pomocniczy'], 'G2', 'H40')
    l_id = doc.Sheets['Wykresy']['B10'].getValue()
    measurements = session.query(Measurement).filter_by(line_id=l_id).all()
    for i, m in enumerate(measurements):
        doc.Sheets['pomocniczy'][f'G{i+2}'].setValue(get_libre_date(m.m_datetime))
        doc.Sheets['pomocniczy'][f'H{i+2}'].setValue(get_err(m))
    return

def get_error_driver_chart(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    clean_data_range(doc.Sheets['pomocniczy'], 'N2', 'O40')
    d_id = doc.Sheets['Wykresy']['I10'].getValue()
    measurements = session.query(Measurement).\
        join(Measurement.line).\
        join(Line.driver).\
        join(DriverLineDetail.driver).\
        filter(Driver.id_driver==d_id).all()
    for i, m in enumerate(measurements):
        doc.Sheets['pomocniczy'][f'N{i+2}'].setValue(get_libre_date(m.m_datetime))
        doc.Sheets['pomocniczy'][f'O{i+2}'].setValue(get_err(m))
    return

def get_error_controller_chart(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    clean_data_range(doc.Sheets['pomocniczy'], 'R2', 'S40')
    c_id = doc.Sheets['Wykresy']['P10'].getValue()
    measurements = session.query(Measurement).\
        join(Measurement.line).\
        join(Line.controller).\
        join(ControllerLineDetail.controller).\
        filter(Controller.id_controller==c_id).all()
    for i, m in enumerate(measurements):
        doc.Sheets['pomocniczy'][f'R{i+2}'].setValue(get_libre_date(m.m_datetime))
        doc.Sheets['pomocniczy'][f'S{i+2}'].setValue(get_err(m))
    return
