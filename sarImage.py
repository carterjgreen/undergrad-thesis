# Authors Royce Burningham & Carter Green

import Class.Adf24Tx2Rx4 as Adf24Tx2Rx4
import Class.RadarProc as RadarProc
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import test_stepper as step
import RPi.GPIO as GPIO
import sar
import datetime as datetime
import sys

STEP_DISTANCE = 3.4636e-3
c0 = 3e8

# Setup Connection
Brd = Adf24Tx2Rx4.Adf24Tx2Rx4()
Brd.BrdRst()

# Configure Receiver
Brd.RfRxEna()
TxPwr = 100

# Configure Transmitter (Antenna 0 - 3, Pwr 0 - 31)
Brd.RfTxEna(1, TxPwr)

# Configure Up-Chirp
dCfg = {
    "fs": 1.0e6,
    "fStrt": 23.9e9,
    "fStop": 24.3e9,
    "TRampUp": 260 / 1.0e6,
    "Tp": 300 / 1.0e6,
    "N": 256,
    "StrtIdx": 0,
    "StopIdx": 1,
    "MimoEna": 0,
    "Frms": 1,
}

Brd.RfMeas("Adi", dCfg)

kf = (dCfg["fStop"] - dCfg["fStrt"]) / dCfg["TRampUp"]
fs = Brd.RfGet("fs")
FuSca = Brd.Get("FuSca")

dRpCfg = {
    "RemoveMean": 1,
    "FFT": 2 ** 9,
    "FuSca": FuSca,
    "fs": fs,
    "kf": kf,
    "RMin": 0,
    "RMax": 4,
    "dB": 0,
    "Abs": 0,
    "Ext": 1,
    "NrFrms": 128,
}

# Configure Range Profile
Proc = RadarProc.RadarProc()
Proc.CfgRangeProfile(dRpCfg)

fStrt = Brd.Adf_Pll.fStrt
fStop = Brd.Adf_Pll.fStop
TRampUp = Brd.Adf_Pll.TRampUp
n = np.arange(int(dCfg["N"]))

Range = Proc.GetRangeProfile("Range")

# Configure SAR Features
if len(sys.argv) < 2:
    points = 166
    sum_size = 9
else:
    distance = float(sys.argv[1])
    points = int(distance / STEP_DISTANCE)
    if int(sys.argv[2]) % 2 == 0:
        sum_size = int(sys.argv[2]) + 1
    else:
        sum_size = int(sys.argv[2])

DataCube = np.zeros((dCfg["N"], points), dtype="int16")

# Collect Data
for i in range(0, points):
    Data = Brd.BrdGetData()
    DataCube[:, i] = np.flip(Data[:, 0])
    step.step(8)
    # print(i)

# Process Data
Out = sar.sar(DataCube, sum_size, window=False) / FuSca
Out2 = sar.focused_sar(DataCube, sum_size, kf, window=False) / FuSca

X, Y = np.meshgrid(np.arange(points - sum_size), Range)
lam = c0 / (dCfg["fStrt"] + dCfg["fStop"]) / 2
CR = X * lam * Y / (2 * STEP_DISTANCE * sum_size)

# Plot SAR Image
fig, ax1 = plt.subplots(1, 2, figsize=(8.5, 8.5))

beep = ax1[0].pcolormesh(
    X * lam / (2 * STEP_DISTANCE * sum_size),
    Y,
    np.abs(Out)[0 : len(Range), 0 : points - sum_size],
    cmap=cm.Greys,
)
fig.colorbar(beep, ax=ax1[1])
ax1[0].set_xlabel("Cross-Range (m)")
ax1[0].set_ylabel("Down-Range (m)")
ax1[0].set_title("Unfocused Sar")

ax1[1].pcolormesh(
    X * lam / (2 * STEP_DISTANCE * sum_size),
    Y,
    np.abs(Out2)[0 : len(Range), 0 : points - sum_size],
    cmap=cm.Greys,
)
ax1[1].set_xlabel("Cross-Range (m)")
ax1[1].set_ylabel("Down-Range (m)")
ax1[1].set_title("Focused Sar")

fig.suptitle("Distance: {} Array Size: {}".format(sys.argv[1], sys.argv[2]))
fig.tight_layout()

# Save Plot
fig_path = "/home/pi/Desktop/DemoRadSoftware/Software/Python/Figures/"
today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
plt.savefig(fig_path + today + ".png", dpi=300)

# Save Data
my_path = "/home/pi/Desktop/DemoRadSoftware/Software/Python/SavedData/"
np.save(my_path + today + ".npy", DataCube)

# Set GPIO ports to 0
GPIO.cleanup()

# Let user know image and data are saved
print(
    "\nDone! at "
    + today
    + "\n Distance: {} Array Size: {}".format(sys.argv[1], sys.argv[2])
)
