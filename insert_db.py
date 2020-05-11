from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pythonpath.models import Station, Driver, Controller, ControllerType, Line, \
        LineName, Measurement, MeasurementParameter, GasMeter, GasMeterType 

engine = create_engine('sqlite:///stuff.db')
Session = sessionmaker(bind=engine)
session = Session()

# Drop existing data

session.query(Station).delete()
session.query(Driver).delete()
session.query(Controller).delete()
session.query(ControllerType).delete()
session.query(Line).delete()
session.query(LineName).delete()
session.query(Measurement).delete()
session.query(MeasurementParameter).delete()
session.query(GasMeter).delete()
session.query(GasMeterType).delete()


# Insert stations

station_j = Station(id_station='J', name='Jarczew')
station_l = Station(id_station='L', name='Łeba')
station_s = Station(id_station='S', name='Śnieżka')
station_t = Station(id_station='T', name='Test')

session.add_all([station_j, station_l, station_s])
session.commit()

# Insert LineName

ln_00 = LineName(name='Test')
ln_01 = LineName(name='NO2')
ln_02 = LineName(name='SO2')
ln_03 = LineName(name='NO3')
ln_04 = LineName(name='NH4')


session.add_all([ln_01, ln_02, ln_03, ln_04])
session.commit()

# Insert Line

l_00 = Line(line_name_id=0, station_id='T')
l_01 = Line(line_name_id=2, station_id='J')
l_02 = Line(line_name_id=3, station_id='J')
l_03 = Line(line_name_id=4, station_id='J')
l_04 = Line(line_name_id=5, station_id='J')
l_05 = Line(line_name_id=2, station_id='L')
l_06 = Line(line_name_id=3, station_id='L')
l_07 = Line(line_name_id=4, station_id='L')
l_08 = Line(line_name_id=5, station_id='L')
l_09 = Line(line_name_id=2, station_id='S')
l_10 = Line(line_name_id=3, station_id='S')
l_11 = Line(line_name_id=4, station_id='S')
l_12 = Line(line_name_id=5, station_id='S')

session.add_all([l_01, l_02, l_03, l_04, l_05, l_06, l_07, l_08, l_09, l_10, l_11, l_12])
session.commit()

# Insert Driver

d_01 = Driver(name='MPS10533', version='2.1.0')


session.add_all([d_01])
session.commit()

# Insert ControllerType

ct_01 = ControllerType(id_ct=1, c_type='1000 Air')
ct_02 = ControllerType(id_ct=5, c_type='5000 Air')

session.add_all([ct_01, ct_02])
session.commit()

# Insert Controller

c_01 = Controller(name='0904C3979.2fs', id_ct=5)

session.add_all([c_01])
session.commit()

# Insert GasMeterType

gmt_01 = GasMeterType(gm_type='test_type1')

session.add_all([gmt_01])
session.commit()

# Insert GasMeter

gm_01 = GasMeter(name='test_gas_meter_name1', g_type=1)

session.add_all([gm_01])
session.commit()

# Insert MeasurementParameter

mp_01 = MeasurementParameter(temperature=12, pressure=1010)

session.add_all([mp_01])
session.commit()

# Insert Measurement

m_01 = Measurement(m_datetime=datetime.now(), g_value=30.1, r_value=29.8, line_id=1, gm_id=1, mp_id=1)

session.add_all([m_01])
session.commit()



