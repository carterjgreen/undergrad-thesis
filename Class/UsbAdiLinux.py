"""@package usbADI
Implements a simple usb class, which uses pyusb to access libusb and access the DemoRad board
    @file    UsbAdiLinux.py
    @date    2017-07-18
    @brief   USB Python class for the DemoRad board
    @version 1.0.0
"""


import usb.core
import usb.util

import ctypes
import sys

import numpy as np
from struct import pack, unpack
from array import array


class usbADI():
    """Implements an interface to the libUSB1 driver under python3/linux

    Wraps the commands and functions
    """
    def __init__(self):
        self.PRODUCT_ID = 0x7823
        self.VENDOR_ID = 0x064b
        self.INTERFACE = 0

        self.UsbOpen = False
        self.usbDev = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID)
        if self.usbDev is None:
            self.UsbOpen = False
            raise ValueError('Device not found. Check if device is connected!')
        else:
            self.UsbOpen = True
            self.usbDev.set_configuration()
            self.usbCfg = self.usbDev.get_active_configuration()
            self.usbIntf = self.usbCfg[(0,0)]
            self.usbWrEp = usb.util.find_descriptor(
                self.usbIntf,
                # match the first OUT endpoint
                custom_match = \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_OUT)
            assert self.usbWrEp is not None
            self.usbRdEp = usb.util.find_descriptor(
                self.usbIntf,
                # match the first OUT endpoint
                custom_match = \
                lambda e: \
                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                    usb.util.ENDPOINT_IN)
            assert self.usbRdEp is not None


    def CmdBuild(self, Ack, CmdCod, Data):
        LenData = len(Data) + 1
        TxData = np.zeros(LenData, dtype='uint32')
        TxData[0] = (2**24)*Ack + (2**16)*LenData + CmdCod
        TxData[1:] = np.uint32(Data)
        return TxData

    def UsbWrCmd(self, Cmd):
        Payload = np.zeros(2048, dtype='uint8')
        PayloadIndex = 2
        for Val in Cmd:
            Payload[PayloadIndex + 3] = (Val >> 24) & 0xFF
            Payload[PayloadIndex + 2] = (Val >> 16) & 0xFF
            Payload[PayloadIndex + 1] = (Val >> 8) & 0xFF
            Payload[PayloadIndex] = (Val) & 0xFF
            PayloadIndex += 4
        PayloadIndex -= 2
        Payload[0] = PayloadIndex & 0xFF
        Payload[1] = (PayloadIndex >> 8) & 0xFF
        if self.UsbOpen:
            self.usbWrEp.write(Payload)
        else:
            print("ERROR: Device not Open")

    def UsbWriteADICmd(self, TxData):
        Payload = np.zeros(2048, dtype='uint8')
        PayloadIndex = 2
        for Val in TxData:
            Payload[PayloadIndex + 3] = (Val >> 24) & 0xFF
            Payload[PayloadIndex + 2] = (Val >> 16) & 0xFF
            Payload[PayloadIndex + 1] = (Val >> 8) & 0xFF
            Payload[PayloadIndex] = (Val) & 0xFF
            PayloadIndex += 4
        PayloadIndex -= 2
        Payload[0] = PayloadIndex & 0xFF
        Payload[1] = (PayloadIndex >> 8) & 0xFF

        if self.UsbOpen:
            self.usbWrEp.write(Payload)
        else:
            print("ERROR: Device not Open")

    def CmdSend(self, Ack, Cod, Data):
        Cmd = self.CmdBuild(Ack, Cod, Data)
        self.UsbWrCmd(Cmd)

    def CmdRecv(self):
        Result = (False, )
        RxData = self.usbRdEp.read(128)
        NrBytes = len(RxData)
        if NrBytes != 0:
            RxData32 = unpack('I' * int(NrBytes/4), RxData)
            Header = RxData32
            LenRxData = Header[0]//(2**16)
            RxBytesLen = NrBytes - 4
            if (RxBytesLen == ((LenRxData -1)*4)):
                Result = (True, RxData32[1:])
            else:
                Result = (False, )
                print("len(RxBytes) wrong: %d != %d" % (len(RxBytes)), (LenRxData -1)*4)
        else:
            print("Board not responding")
        return Result

    def UsbRead(self, RdLen):
        RxData = self.usbRdEp.read(int(RdLen))
        RetData   = bytes(RxData)
        return RetData

    def CloseGlobalHandles(self):
        # Dummy, not needed for Linux
        print("Close Handles")

    def ConnectToDevice(self, Val):
        # Dummy, not needed for Linux
        print("Connect Device")

    def GetDllVersion(self):
        # Dummy, not needed for Linux
        print("Get Dll Version")

