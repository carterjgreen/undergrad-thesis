# AN24_02 -- FMCW Basics

import      Class.Adf24Tx2Rx4 as Adf24Tx2Rx4
import      Class.RadarProc as RadarProc
from        numpy import *
import      time as time

from        pyqtgraph.Qt import QtGui, QtCore
import      pyqtgraph as pg

# (1) Connect to Radarbook
# (2) Enable Supply
# (3) Configure RX
# (4) Configure TX
# (5) Start Measurements
# (6) Configure calculation of range profile

DispRp      =   0

App         =   QtGui.QApplication([])

Win         =   pg.GraphicsWindow(title="Time signals")
Win.setBackground((255, 255, 255))
Win.resize(1000,600)

Plot1       =   Win.addPlot(title="Tx1-Rx1", col=0, row=0)
Plot1.showGrid(x=True, y=True)

Plot2       =   Win.addPlot(title="Tx1-Rx2", col=1, row=0)
Plot2.showGrid(x=True, y=True)

Plot3       =   Win.addPlot(title="Tx1-Rx3", col=2, row=0)
Plot3.showGrid(x=True, y=True)

Plot4       =   Win.addPlot(title="Tx1-Rx4", col=3, row=0)
Plot4.showGrid(x=True, y=True)

Plot5       =   Win.addPlot(title="Tx2-Rx1", col=0, row=1)
Plot5.showGrid(x=True, y=True)

Plot6       =   Win.addPlot(title="Tx2-Rx2", col=1, row=1)
Plot6.showGrid(x=True, y=True)

Plot7       =   Win.addPlot(title="Tx2-Rx3", col=2, row=1)
Plot7.showGrid(x=True, y=True)

Plot8       =   Win.addPlot(title="Tx2-Rx4", col=3, row=1)
Plot8.showGrid(x=True, y=True)

Pen1        =   pg.mkPen(color=(0, 0, 255), width=1)
Pen2        =   pg.mkPen(color=(0, 255, 0), width=1)
Pen3        =   pg.mkPen(color=(255, 0, 0), width=1)
Pen4        =   pg.mkPen(color=(255, 0, 255), width=1)

#--------------------------------------------------------------------------
# Setup Connection
#--------------------------------------------------------------------------
Brd         =   Adf24Tx2Rx4.Adf24Tx2Rx4()

Brd.BrdRst()

#--------------------------------------------------------------------------
# Software Version
#--------------------------------------------------------------------------
Brd.BrdDispSwVers()

#--------------------------------------------------------------------------
# Configure Receiver
#--------------------------------------------------------------------------
Brd.RfRxEna()
TxPwr       =   100
NrFrms      =   1000
#--------------------------------------------------------------------------
# Configure Transmitter (Antenna 0 - 3, Pwr 0 - 31)
#--------------------------------------------------------------------------
Brd.RfTxEna(1, TxPwr)

#--------------------------------------------------------------------------
# Configure Up-Chirp
#--------------------------------------------------------------------------
dCfg        =   {
                    "fs"        :   1.0e6,
                    "fStrt"     :   24.0e9,
                    "fStop"     :   24.25e9,
                    "TRampUp"   :   260/1.0e6,
                    "Tp"        :   300/1.0e6,
                    "N"         :   256,
                    "StrtIdx"   :   0,
                    "StopIdx"   :   2,
                    "MimoEna"   :   1
                }


Brd.RfMeas('Adi', dCfg);

kf              =   (dCfg['fStop'] - dCfg['fStrt'])/dCfg["TRampUp"]
fs              =   Brd.RfGet('fs')
FuSca           =   Brd.Get('FuSca')

print("kf:", kf)
print("fs:", fs)

dRpCfg          =   {
                        "RemoveMean"    :   1, 
                        "FFT"           :   2**9,
                        "FuSca"         :   FuSca,
                        "fs"            :   fs,
                        "kf"            :   kf,
                        "RMin"          :   1,
                        "RMax"          :   50,
                        "dB"            :   1,
                        "Ext"           :   1
                    }       

Proc            =   RadarProc.RadarProc()
Proc.CfgRangeProfile(dRpCfg)


fStrt           =   Brd.Adf_Pll.fStrt
fStop           =   Brd.Adf_Pll.fStop
TRampUp         =   Brd.Adf_Pll.TRampUp
n               =   arange(int(dCfg['N']))
N               =   int(dCfg['N'])
Range           =   Proc.GetRangeProfile('Range')


DataTx1         =   zeros((256*dCfg["StopIdx"]*4, int(NrFrms)))
for Cycles in range(0, int(NrFrms)):
    Data        =   Brd.BrdGetData()
    Data1       =   Data[0:N,:]
    Data2       =   Data[N:,:]
    Rp1         =   Proc.RangeProfile(Data1)
    Rp2         =   Proc.RangeProfile(Data2)

    Plot1.clear()
    Plot2.clear()
    Plot3.clear()
    Plot4.clear()
    Plot5.clear()
    Plot6.clear()
    Plot7.clear()
    Plot8.clear()

    if DispRp > 0:
        Plot1.plot(Range,Rp1[:,0], pen=Pen1)   
        Plot2.plot(Range,Rp1[:,0], pen=Pen2)
        Plot3.plot(Range,Rp1[:,0], pen=Pen3)
        Plot4.plot(Range,Rp1[:,0], pen=Pen4)   
        Plot5.plot(Range,Rp2[:,0], pen=Pen1)   
        Plot6.plot(Range,Rp2[:,0], pen=Pen2)
        Plot7.plot(Range,Rp2[:,0], pen=Pen3)
        Plot8.plot(Range,Rp2[:,0], pen=Pen4)                
    else:
        Plot1.plot(n[1:],Data1[1:,0], pen=Pen1)
        Plot2.plot(n[1:],Data1[1:,1], pen=Pen2)
        Plot3.plot(n[1:],Data1[1:,2], pen=Pen3)
        Plot4.plot(n[1:],Data1[1:,3], pen=Pen4)
        Plot5.plot(n[1:],Data2[1:,0], pen=Pen1)
        Plot6.plot(n[1:],Data2[1:,1], pen=Pen2)
        Plot7.plot(n[1:],Data2[1:,2], pen=Pen3)
        Plot8.plot(n[1:],Data2[1:,3], pen=Pen4)        
    pg.QtGui.QApplication.processEvents()



del Brd
