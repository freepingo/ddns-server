from flask import Flask, render_template, request
from sqlalchemy import create_engine, Column, Integer, String, desc
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from json import dumps

application = Flask(__name__)
engine = create_engine("mysql+pymysql://pion:5.U)v5J7D:o`MEDB@localhost/noip?charset=utf8", convert_unicode=True, pool_recycle=1)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class Device(Base):
	__tablename__ = 'device'
	id = Column(Integer, primary_key=True)
	name = Column(String(64))
	ip = Column(String(15))
	date = Column(String(19))
	def __init__ (self, name, ip):
		self.name = name
		self.ip = ip
	def __repr__(self):
		return '<Device %r>' % (self.ip)

@application.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()

@application.route('/')
def hello_world():
	return render_template('index.html', you=request.environ.get('HTTP_CF_CONNECTING_IP', request.remote_addr))

@application.route('/set', methods=['post'])
def set():
	try:
		device = Device.query.filter(Device.name==request.json['name']).first()
		if device.ip == request.environ.get('HTTP_CF_CONNECTING_IP', request.remote_addr):
			return 'same'
		else:
			device.ip = request.environ.get('HTTP_CF_CONNECTING_IP', request.remote_addr)
			db_session.add(device)
			db_session.commit()
			return 'done'
	except:
		request.json['name']
		db_session.add(Device(name=request.json['name'], ip=request.environ.get('HTTP_CF_CONNECTING_IP', request.remote_addr)))
		db_session.commit()
	return 'done'

@application.route('/get/<device>')
def get(device):
	try:
		return Device.query.filter(Device.name==device).first().ip
	except:
		return 'failed'

@application.route('/list')
def list():
	return render_template('list.html', devices=Device.query.all(), you=request.environ.get('HTTP_CF_CONNECTING_IP', request.remote_addr))

if __name__ == '__main__':
	application.run()