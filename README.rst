Commmande
===

Requirements
~~~~~~~~~~~~

**PyQT4**
    ``sudo aptitude install python-qt4``

**ReportLab 2.4**
    ``pip install reportlab==2.4``

**gettext**
    ``sudo aptitude install gettext``

**xlwt**
    ``pip install xlwt==0.7.3``

Windows
~~~~~~~

You need a working windows environment to build Commmande windows packageL
    nsis-2.46-setup.exe

    pywin32-210.win32-py3.4.exe

    py2exe-0.6.9.win32-py3.4.exe

    PyQt-Py2.7-x86-gpl-4.8.3-1.exe

    python-2.7.6.msi (add C:\Python27 to PATH)

    reboot

    xlwt-0.7.2.win32.exe

    reportlab-2.5.win32-py2.7.exe

    setuptools-0.6c11.win32-py2.7.exe

Once setup, create windows executable:
    cd path\orders\order
    example: cd C:\Documents and Settings\Administrateur\Bureau\orders\order
    ``copy ..\resources\microsoftdll\*.dll .``

    ``copy ..\resources\microsoftdll\*.man* .``

    ``python.exe setup-win.py py2exe``

Once windows binary is complete, create installer with:

    ``"C:\Program Files\NSIS\makensis.exe" installer.nsi``

New methode
    py -3.4 -m py2exe.build_exe main_mb.py
    py -3.4 setup-win.py py2exe --includes sip