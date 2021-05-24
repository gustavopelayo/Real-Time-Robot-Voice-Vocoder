import time
import numpy
import pyaudio
from robot import rob_voice

chunk = 1024

# 16 bits per sample
sample_format = pyaudio.paInt16

channels = 1
# Record at 44400 samples per second
smpl_rt = 44400

record_seconds = 5

# Create an interface to PortAudio
audio = pyaudio.PyAudio()

stream = audio.open(format=sample_format,
                    channels=channels,
                    rate=smpl_rt,
                    input=True,
                    frames_per_buffer=chunk)

stream_output = audio.open(format=sample_format,
                           channels=channels,
                           rate=smpl_rt,
                           output=True,
                           frames_per_buffer=chunk)

# for measuring
frame_count = 0
start_time = time.time()
avg_delay_robot = 0
avg_delay_loop = 0
avg_delay_read = 0
avg_delay_write = 0

for i in range(0, int(smpl_rt / chunk * record_seconds)):
    time_start_loop = time.time()
    data = stream.read(chunk)
    avg_delay_read = float(avg_delay_read + (time.time() - time_start_loop))
    npdata = numpy.frombuffer(data, dtype=numpy.int16)
    time_start_robot = time.time()
    result = rob_voice(smpl_rt, npdata)
    result = result.astype(numpy.int16).tostring()
    avg_delay_robot = float(avg_delay_robot + (time.time() - time_start_robot))
    time_start_write = time.time()
    stream_output.write(result)
    avg_delay_write = float(avg_delay_write + (time.time() - time_start_write))
    frame_count = frame_count+1
    avg_delay_loop = float(avg_delay_loop + (time.time() - time_start_loop))

# Stop and close the stream
stream.stop_stream()
stream.close()

# Terminate - PortAudio interface
audio.terminate()

frame_rate = frame_count / (time.time() - start_time)

print('STREAM STOPPED')
print('--------------------FRAME RATE-------------------')
print("Time Passed: = %.4f" % (time.time() - start_time))
print("Frame Count: = %d" % frame_count)
print('Average Frame Rate = {:.0f} FPS'.format(frame_rate))
print('-----------------DELAY STATISTICS----------------')
print("Average Delay of Main Loop = %.4f ms" % ((avg_delay_loop*1000)/frame_count))
print('')
print('Elements Inside Loop:')
print("   Average delay of Vocoder Algorithm = %.4f ms" % ((avg_delay_robot*1000)/frame_count))
print("   Average delay of Read Function = %.4f ms" % ((avg_delay_read*1000)/frame_count))
print("   Average delay of Write Function = %.4f ms" % ((avg_delay_write*1000)/frame_count))
print('-------------------------------------------------')
