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
                    "StopIdx"   :   1,
                    "MimoEna"   :   0,
                    "Frms"      :   1
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
Rp = Proc.RangeProfile(Data)
myAngles = angle(Rp[:,0], deg=True)

Data2 = Brd.BrdGetData()
Rp2 = Proc.RangeProfile(Data2)
myAngles2 = angle(Rp2[:,0], deg=True)

Data3 = Brd.BrdGetData()
Rp3 = Proc.RangeProfile(Data3)
myAngles3 = angle(Rp3[:,0], deg=True)

Data4 = Brd.BrdGetData()
Rp4 = Proc.RangeProfile(Data4)
myAngles4 = angle(Rp4[:,0], deg=True)

Difference = myAngles - myAngles2
#--------------------------------------------------------------------------
# Matplotlib Plots
#--------------------------------------------------------------------------
plt.style.use("ggplot")
fig, ax = plt.subplots(2, 2, figsize=(11, 8.5))
for axlist in ax:
    for axis in axlist:
        axis.set_xlabel("Range")
        
ax[0, 0].plot(Range, abs(Rp[:, 0]))
ax[0, 0].set_title("Amplitude Measurement 1")
ax[0, 0].set_ylabel("Power (W)")

ax[0, 1].plot(Range, abs(Rp2[:, 0]))
ax[0, 1].set_title("Amplitude Measurement 2")
ax[0, 1].set_ylabel("Power (W)")

ax[1, 0].plot(Range, myAngles)
ax[1, 0].set_title("Phase Measurement 1")
ax[1, 0].set_ylabel("Phase (Deg)")
ax[1, 0].set_ylim(-200, 200)

ax[1, 1].plot(Range, myAngles2)
ax[1, 1].set_title("Phase Measurement 2")
ax[1, 1].set_ylabel("Phase (Deg)")
ax[1, 1].set_ylim(-200, 200)

#ax[2, 1].plot(Range, Difference)
#ax[2, 1].set_title("Phase Difference 2")
#ax[2, 1].set_ylabel("Phase (Deg)")

fig.tight_layout()
fig.show()
#fig.savefig("SingleChirpCoherency.png")

Output = vstack((Rp[:, 0], Rp2[:, 0]))
#savetxt("SingleMeasurement.csv", Output, delimiter=",")