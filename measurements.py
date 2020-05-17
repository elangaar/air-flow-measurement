import uno
from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from models import Station, Line, LineName, GasMeter, Measurement, MeasurementParameter

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
    return ((m.r_value-rt_value)/rt_value)*100

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
        doc.Sheets['pomocniczy'][f'F{i+2}'].setString(gm.name)
    lines = get_lines()
    for i, l in enumerate(lines):
        doc.Sheets['pomocniczy'][f'I{i+2}'].setString(l[1])
        doc.Sheets['pomocniczy'][f'J{i+2}'].setValue(l[0])
    return

def save_measurement_data(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    sheet = doc.Sheets['Pomiar']

    temp = sheet.getCellRangeByName('D9').getValue()
    press = sheet.getCellRangeByName('C10').getValue()
    mp = MeasurementParameter(temperature=temp, pressure=press)

    line_id = doc.Sheets['pomocniczy']['K2'].getValue()
    line = session.query(Line).filter_by(id_line=line_id).one()
    gm_name = sheet.getCellRangeByName('C6').getString()
    gm = session.query(GasMeter).filter_by(name=gm_name).first()

    dt = datetime.now()
    gv = sheet.getCellRangeByName('C11').getValue()
    rv = sheet.getCellRangeByName('C12').getValue()
    meas = Measurement(m_datetime=dt, g_value=gv, r_value=rv, line=line, gm=gm, mp=mp)
    session.add(meas)
    session.commit()
    return

