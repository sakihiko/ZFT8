#!/usr/bin/env python3

# Copyright 2020 Akihiko Sasaki
#
# This software is released under the MIT License.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copyw
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import argparse
import serial
import struct
from collections import namedtuple
import csv
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--device", help="Serial device", required=True)
parser.add_argument("-f", "--file", help="Output file")
args = parser.parse_args()

ser = serial.Serial(
    port=args.device,\
    baudrate=115200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=2000
)

if args.file is not None:
    f = open(args.file, 'w')
else :
    f = sys.stdout

csv_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

FRAME_FORMAT = '>4s3BIIIIIBB2BIIIB3s'

FRAME_FIELD_NAME = [
    'Start',
    'Unknown1',
    'Unknown2',
    'Unknown3',
    'Voltage',
    'Current',
    'Power',
    'Acc_Wh',
    'Acc_Ah',
    'Unknown4',
    'Temp',
    'Unknown5',
    'Unknown6',
    'Current_Peak',
    'Power_Peak',
    'Voltage_Min',
    'Unknown7',
    'End'
]

# Fields for output
OUTPUT_FIELD_NAME = (
    'Count',
    'Date',
    'Voltage',
    'Current',
    'Power',
    'Acc_Wh',
    'Acc_Ah',
    'Temp',
    'Current_Peak',
    'Power_Peak',
    'Voltage_Min'
)

# Multiply factors for align digit or calibration
FACTOR = {
    'Voltage':1/1000,
    'Current':1/1000,
    'Power':1/1000,
    'Acc_Wh':1/1000,
    'Acc_Ah':1/1000,
    'Current_Peak':1/1000,
    'Power_Peak':1/1000,
    'Voltage_Min':1/1000
}

Frame = namedtuple('Frame', FRAME_FIELD_NAME)

# Write header
csv_writer.writerow(OUTPUT_FIELD_NAME)

frame_count = 0;

while True:
    # Get 1 frame and decode to dictionary
    line = ser.read(47)
    frame_count += 1
    frame = Frame._asdict(Frame._make(struct.unpack(FRAME_FORMAT, line)))

    # Add additional fields
    frame['Count'] = frame_count
    frame['Date'] = datetime.datetime.today()

    # Convert to string
    frame['Start'] = frame['Start'].decode('ascii')
    frame['End'] = frame['End'].decode('ascii')

    # Multiply factors to align digit or calibration
    for k in FACTOR:
        frame[k] = frame[k] * FACTOR[k] 

    # Write row
    csv_writer.writerow([frame[k] for k in OUTPUT_FIELD_NAME])
    f.flush()
