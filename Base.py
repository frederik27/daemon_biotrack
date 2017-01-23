import pymysql
import globals
from logs import LOG


class DB:
	"""
	Database connection class
	"""

	def __init__(self):
		self._cur = None
		self._con = None

	def connect(self):
		try:
			self._con = pymysql.connect(
				host=globals.DB_HOST,
				user=globals.DB_USER,
				passwd=globals.DB_PWD,
				db=globals.DB_NAME,
				cursorclass=pymysql.cursors.DictCursor)

			self._con.set_charset('utf8')
			self._cur = self._con.cursor()
			self._cur.execute("SET NAMES utf8")
			self._cur.execute("SET CHARACTER SET utf8")
			self._cur.execute("SET character_set_connection=utf8")


			return True
		except pymysql.Error as e:
			LOG.log('mysql:%s' % str(e))
			return False

	def exec_query(self, sql):
		try:
			self._cur.execute(sql)
			#self._con.commit()
			return self._cur.fetchall()
		except Exception as e:
			LOG.log('mysql error sql: %s, %s' % (str(e), sql))
			return []

	def exec(self, sql):
		try:
			self._cur.execute(sql)
			self._con.commit()
			return self._cur.rowcount
		except Exception as e:
			LOG.log('mysql error sql: %s, %s' % (str(e), sql))
			return 0


