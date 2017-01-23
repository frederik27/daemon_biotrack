from cx_Freeze import setup, Executable

executables = [
    Executable('ManagerDaemons.py')
]

setup(name='ManagerDaemons',
      version='1.0.5',
      description='ManagerDaemons',
      executables=executables
      )
