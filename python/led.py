import platform
import numpy as np
import config
import socket


_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

pixels = np.tile(1, (3, config.N_PIXELS))
"""Pixel values for the LED strip""" 

def update():
    """Sends UDP packets to ESP8266 to update LED strip values

    The ESP8266 will receive and decode the packets to determine what values
    to display on the LED strip. The communication protocol supports LED strips
    with a maximum of 256 LEDs.

    The packet encoding scheme is:
        |i|r|g|b|
    where
        i (0 to 255): Index of LED to change (zero-based)
        r (0 to 255): Red value of LED
        g (0 to 255): Green value of LED
        b (0 to 255): Blue value of LED
    """
    global pixels
    # Truncate values and cast to integer
    pixels = np.clip(pixels, 0, 255).astype(int)
    p = np.copy(pixels)
    MAX_PIXELS_PER_PACKET = 126
    # Pixel indices
    idx = []
    for i in range(config.N_PIXELS):
        idx.append(i)
    n_packets = len(idx) // MAX_PIXELS_PER_PACKET + 1
    idx = np.array_split(idx, n_packets)
    for packet_indices in idx:
        m = []
        for i in packet_indices:
            m.append(i)  # Index of pixel to change
            m.append(p[0][i])  # Pixel red value
            m.append(p[1][i])  # Pixel green value
            m.append(p[2][i])  # Pixel blue value
        m = bytes(m)
        _sock.sendto(m, (config.UDP_IP, config.UDP_PORT))


# Execute this file to run a LED strand test
# If everything is working, you should see a red, green, and blue pixel scroll across the LED strip continously
if __name__ == '__main__':
    import time
    # Turn all pixels off
    pixels *= 0
    pixels[0, 0] = 255  # Set 1st pixel red
    pixels[1, 1] = 255  # Set 2nd pixel green
    pixels[2, 2] = 255  # Set 3rd pixel blue
    print('Starting LED strand test')
    while True:
        pixels = np.roll(pixels, 1, axis=1)
        update()
        time.sleep(.1)
