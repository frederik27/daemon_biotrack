import configparser


def loadSettings(confname):
	config = configparser.ConfigParser()
	r = config.read(confname)
	if r == []:
		config['Database'] = {'host': '127.0.0.1',
							  'user': 'root',
							  'pwd': '123',
							  'db': 'biotrackonline'
		}

		config['SMTP'] = {'smtp_host': 'smtp.mail.ru',
						  'smtp_user': 'skywalker_87@mail.ru',
						  'smtp_pass': 'maxtrack',
						  'smtp_port': 25
		}

		config['TaskDaemon'] = {
			'param'
		}

	return config


def saveSettings(confname, config):
	with open(confname, 'w') as configfile:
		config.write(configfile)
