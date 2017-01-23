from cx_Freeze import setup, Executable

options = {
    'build_exe': {
        'includes': ['ServiceHandler']
    }
}

executables = [
    Executable('Config.py', base='Win32Service',
               targetName='cx_FreezeSampleService.exe')
]

setup(name='cx_FreezeSampleService',
      version='0.1',
      description='Sample cx_Freeze Windows serice',
      executables=executables,
      options=options
      )
