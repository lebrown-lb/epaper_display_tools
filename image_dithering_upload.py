import numpy as np
from PIL import Image
import sys
import socket
import time


TIMEOUT_SEC = 5   


def connect_to_esp32(data_to_send, ip, port):
    l = len(data_to_send)
    if l > 960_000:
        print("DATA IS TO LARGE FOR EPAPER DISPLAY")
        return

    print(f"Connecting to ESP32-S3 at {ip}:{port}...")

    # Create a standard TCP/IP socket
    # AF_INET = IPv4, SOCK_STREAM = TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Set a timeout so the script doesn't freeze if the ESP32 is offline
        client_socket.settimeout(TIMEOUT_SEC)

        try:
            # Establish connection
            client_socket.connect((ip, port))
            print("Connected successfully!")

            # Send data (strings must be encoded to bytes over network sockets)
            print(f"Sending: '{l}' bytes")
            pkt_size = 1200
            pkts = [data_to_send[i: i + pkt_size] for i in range(0, len(data_to_send), pkt_size)]
            data_ofst = 0
            pkt_cnt = 0
            pbx = 0
            pbs = int(len(pkts) / 40)
            for pkt in pkts:
                pkt_len = len(pkt)
                tmp = b"DAT:" + pkt_len.to_bytes(2, byteorder='big') + data_ofst.to_bytes(4,byteorder='big') + pkt
                client_socket.sendall(tmp)
                data_ofst += pkt_len
                if pkt_cnt % pbs == 0:
                    pb = "*" * pbx
                    print("\r[", f"{pb:<40}","]",sep='', end='')
                    pbx += 1
                pkt_cnt += 1
                time.sleep(0.01)

            client_socket.close()

        except socket.timeout:
            print(f"Error: Connection timed out after {TIMEOUT_SEC} seconds.")
        except ConnectionRefusedError:
            print("Error: Connection refused. Is the server running on the ESP32?")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            print("Socket closed.\n")

def get_closest_color(pixel: np.ndarray, palette: np.ndarray) -> np.ndarray:
    """Finds the closest palette color to a pixel using Euclidean distance."""
    # Calculate the straight-line distance to all palette colors across R, G, B channels
    distances = np.sum((palette - pixel) ** 2, axis=1)
    closest_index = np.argmin(distances)
    return palette[closest_index]

def pixel_to_palette_num(pixel):
    if pixel == [0,0,0]:
        return 0
    elif pixel == [255,255,255]:
        return 1
    elif pixel == [255,255,0]:
        return 2
    elif pixel == [255,0,0]:
        return 3
    elif pixel == [0,0,255]:
        return 5
    elif pixel == [0,255,0]:
        return 6

def custom_palette_dither(image_path: str, output_path: str):
    """Applies Floyd-Steinberg error diffusion dithering using a custom color palette."""
    # 1. Define the custom palette as normalized RGB float array
    palette = np.array(
        [
            [0, 0, 0],  # Black
            [255, 255, 255],  # White
            [0, 255, 0],  # Green
            [255, 0, 0],  # Red
            [255, 255, 0],  # Yellow
            [0, 0, 255],  # Blue
        ],
        dtype=np.float32,
    )

    # 2. Open image, convert to RGB, and load into a float32 NumPy array
    img = Image.open(image_path).convert("RGB")
    img = img.resize((1600,1200), Image.Resampling.LANCZOS)
    img = img.transpose(Image.ROTATE_90)
    pixels = np.array(img, dtype=np.float32)
    height, width, channels = pixels.shape
    s = int(height * width / 2)

    ba = bytearray(s)
    pixel_cnt = 0
    write_cnt = 0
    pbs = height * width / 40
    pbx = 0
    print("Dithering IMAGE")
    # 3. Iterate through every pixel in the image matrix
    for y in range(height):
        for x in range(width):
            old_pixel = pixels[y, x].copy()

            # Find the closest matching color from our palette
            new_pixel = get_closest_color(old_pixel, palette)
            pixels[y, x] = new_pixel
            pixel_cnt += 1

            # Calculate the quantization error difference for all 3 color channels
            error = old_pixel - new_pixel

            # 4. Distribute the error to neighboring pixels (Error Diffusion)
            if x + 1 < width:
                pixels[y, x + 1] += error * 7 / 16
            if y + 1 < height:
                if x - 1 >= 0:
                    pixels[y + 1, x - 1] += error * 3 / 16
                pixels[y + 1, x] += error * 5 / 16
                if x + 1 < width:
                    pixels[y + 1, x + 1] += error * 1 / 16

            if pixel_cnt % 2 == 0:
                if not x:
                    p0 = pixels[y-1,width -1]
                else:
                    p0 = pixels[y,x-1]

                b = (pixel_to_palette_num(list(p0)) << 4) | pixel_to_palette_num(list(new_pixel))
                ba[write_cnt] = b
                write_cnt += 1
            if pixel_cnt % pbs == 0:
                pb = "*" * pbx
                print("\r[", f"{pb:<40}","]",sep='', end='')
                pbx += 1


    # 5. Clip values safely to the 0-255 spectrum, convert to uint8, and save
    dithered_img = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8))
    dithered_img = dithered_img.transpose(Image.ROTATE_270)
    dithered_img.save(output_path)
    print(f"\nSuccessfully saved custom palette dithered image to {output_path}")
    return ba


# --- Example Usage ---
# Install dependencies via: pip install Pillow numpy
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: {} <input> <output>".format(sys.argv[0]))
        print("USAGE: {} <input> <output> <ip> <port>".format(sys.argv[0]))
    else:
        data = custom_palette_dither(sys.argv[1],sys.argv[2])
        if len(sys.argv) == 5:
            connect_to_esp32(data,sys.argv[3],int(sys.argv[4]))
