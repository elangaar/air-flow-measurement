from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, \
    Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

engine = create_engine('sqlite:///stuff.db')

Base = declarative_base()


class Station(Base):
    __tablename__ = 'stations'
    id_station = Column(String(1), primary_key=True)
    name = Column(String(30), nullable=False, unique=True)

    lines = relationship('Line', back_populates='station')
    controllers = relationship('Controller', back_populates='station')
    drivers = relationship('Driver', back_populates='station')

    def __repr__(self):
        return f'<Station: {self.name}>'


class Driver(Base):
    __tablename__ = 'drivers'
    __table_args__ = (
            CheckConstraint('NOT(station_id IS NOT NULL AND line_id IS NOT NULL)'),
            )
    id_driver = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    version = Column(String(10))
    is_broken = Column(Boolean, default=False)
    is_working = Column(Boolean, default=False)
    station_id = Column(Integer, ForeignKey('stations.id_station'))
    line_id = Column(Integer, ForeignKey('lines.id_line'))

    station = relationship('Station', back_populates='drivers')
    line = relationship('Line', back_populates='driver')

    def __repr__(self):
        return f'<Driver: {self.name}, version: {self.version}>'


class ControllerType(Base):
    __tablename__ = 'controller_types'
    id_ct = Column(Integer, primary_key=True)
    c_type = Column(String(10), nullable=False, unique=True)

    ctypes = relationship('Controller', back_populates='ctype')

    def __repr__(self):
        return f'<Type: {self.c_type}>'


class Controller(Base):
    __tablename__ = 'controllers'
    __table_args__ = (
            CheckConstraint('NOT(station_id IS NOT NULL AND line_id IS NOT NULL)'),
            )
    id_controller = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    is_working = Column(Boolean, default=False)
    is_broken = Column(Boolean, default=False)
    id_ct = Column(Integer, ForeignKey('controller_types.id_ct'))
    station_id = Column(Integer, ForeignKey('stations.id_station'))
    line_id = Column(Integer, ForeignKey('lines.id_line'))

    ctype = relationship('ControllerType', back_populates='ctypes')
    station = relationship('Station', back_populates='controllers')
    line = relationship('Line', back_populates='controller')

    def __repr__(self):
        return f'<Controller: {self.name}, type: {self.c_type}>'


class Line(Base):
    __tablename__ = 'lines'
    id_line = Column(Integer, primary_key=True)
    line_name_id = Column(Integer, ForeignKey('line_names.id_ln'))
    station_id = Column(String(1), ForeignKey('stations.id_station'))

    measurements = relationship('Measurement', back_populates='line')
    ln = relationship('LineName', back_populates='lines')
    station = relationship('Station', back_populates='lines')
    controller = relationship('Controller', back_populates='line', uselist=False)
    driver = relationship('Driver', back_populates='line', uselist=False)

    def __repr__(self):
        return f'{self.station.name}, {self.ln.name}'


class LineName(Base):
    __tablename__ = 'line_names'
    id_ln = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)

    lines = relationship('Line', back_populates='ln')

    def __repr__(self):
        return f'<LineName: {self.name}>'


class Measurement(Base):
    __tablename__ = 'measurements'
    id_measurement = Column(Integer, primary_key=True)
    m_datetime = Column(DateTime, nullable=False)
    g_value = Column(Float, nullable=False)
    r_value = Column(Float, nullable=False)

    line_id = Column(Integer, ForeignKey('lines.id_line'))
    gm_id = Column(Integer, ForeignKey('gasmeters.id_gm'))
    mp_id = Column(Integer, ForeignKey('measurement_parameter.id_mp'))

    line = relationship('Line', back_populates='measurements')
    gm = relationship('GasMeter', back_populates='measurements')
    mp = relationship('MeasurementParameter', back_populates='measurements')

    def __repr__(self):
        return f'<{self.id_measurement}>'


class MeasurementParameter(Base):
    __tablename__ = 'measurement_parameter'
    id_mp = Column(Integer, primary_key=True)
    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)

    measurements = relationship('Measurement', back_populates='mp')

    def __repr__(self):
        return f'<Temnperature: {self.temperature}, pressure: {self.pressure}>'
    

class GasMeter(Base):
    __tablename__ = 'gasmeters'
    id_gm = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    g_type = Column(Integer, ForeignKey('gasmeters_type.id_gm_type'))

    gm_type = relationship('GasMeterType', back_populates='gm')
    measurements = relationship('Measurement', back_populates='gm')

    def __repr__(self):
        return f'<GasMeter: {self.name}>'


class GasMeterType(Base):
    __tablename__ = 'gasmeters_type'
    id_gm_type = Column(Integer, primary_key=True)
    gm_type = Column(String(30), nullable=False, unique=True)

    gm = relationship('GasMeter', back_populates='gm_type')

    def __repr__(self):
        return f'<GasMeter Type: {self.gm_type}>'


if __name__ == '__main__':
    Base.metadata.create_all(engine)
