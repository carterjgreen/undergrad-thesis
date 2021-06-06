# Authors Royce Burningham & Carter Green

import      Class.Adf24Tx2Rx4 as Adf24Tx2Rx4
import      Class.RadarProc as RadarProc
from        numpy import *
import      matplotlib.pyplot as plt

# (1) Connect to Radarbook
# (2) Enable Supply
# (3) Configure RX
# (4) Configure TX
# (5) Configure calculation of range profile
# (6) Start Measurements
# (7) Plot Measurements

#--------------------------------------------------------------------------
# Setup Connection
#--------------------------------------------------------------------------
Brd         =   Adf24Tx2Rx4.Adf24Tx2Rx4()

Brd.BrdRst()

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
                    "fStop"     :   24.3e9,
                    "TRampUp"   :   260/1.0e6,
                    "Tp"        :   300/1.0e6,
                    "N"         :   256,
                    "StrtIdx"   :   0,
                    "StopIdx"   :   128,
                    "MimoEna"   :   0,
                    "Frms"      :   128
                }

Brd.RfMeas('Adi', dCfg);

kf              =   (dCfg['fStop'] - dCfg['fStrt'])/dCfg["TRampUp"]
fs              =   Brd.RfGet('fs')
FuSca           =   Brd.Get('FuSca')

dRpCfg          =   {
                        "RemoveMean"    :   1, 
                        "FFT"           :   2**9,
                        "FuSca"         :   FuSca,
                        "fs"            :   fs,
                        "kf"            :   kf,
                        "RMin"          :   1,
                        "RMax"          :   10,
                        "dB"            :   0,
                        "Abs"           :   0,
                        "Ext"           :   1,
                        "NrFrms"        :   128
                    }

Proc            =   RadarProc.RadarProc()
#Proc.RangeProfile_Abs           =   0
#Proc.RangeProfile_dB            =   0
#Proc.RangeProfile_RMax          =   10
#Proc.RangeProfile_Ext           =   1

Range           =   Proc.GetRangeProfile('Range')
Proc.CfgRangeProfile(dRpCfg)

fStrt           =   Brd.Adf_Pll.fStrt
fStop           =   Brd.Adf_Pll.fStop
TRampUp         =   Brd.Adf_Pll.TRampUp
n               =   arange(int(dCfg['N']))
Range           =   Proc.GetRangeProfile('Range')

Data = Brd.BrdGetData()
savetxt("128ChirpADC.csv", Data, delimiter=",")
