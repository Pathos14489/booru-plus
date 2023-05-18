from PIL import Image
import base64
import json

def read_chunk(data,idx):
    length = data[idx] << 24 | data[idx + 1] << 16 | data[idx + 2] << 8 | data[idx + 3]
    chunk_type = chr(data[idx + 4]) + chr(data[idx + 5]) + chr(data[idx + 6]) + chr(data[idx + 7])
    chunk_data = data[idx + 8:idx + 8 + length]
    crc = data[idx + 8 + length] << 24 | data[idx + 8 + length + 1] << 16 | data[idx + 8 + length + 2] << 8 | data[idx + 8 + length + 3]
    # if crc != zlib.crc32(chunk_data, zlib.crc32(chunk_type.encode("utf-8"))):
    #     raise Exception("CRC for \"" + chunk_type + "\" header is invalid, file is likely corrupted")
    return {
        "type": chunk_type,
        "data": chunk_data,
        "crc": crc
    }
def read_chunks(data):
    if data[0] != 0x89 or data[1] != 0x50 or data[2] != 0x4E or data[3] != 0x47 or data[4] != 0x0D or data[5] != 0x0A or data[6] != 0x1A or data[7] != 0x0A:
        raise Exception("Invalid PNG header")
    chunks = []
    idx = 8 # Skip signature
    while idx < len(data):
        chunk = read_chunk(data, idx)
        if len(chunks) == 0 and chunk["type"] != "IHDR":
            raise Exception("PNG missing IHDR header")
        chunks.append(chunk)
        idx += 4 + 4 + len(chunk["data"]) + 4 # Skip length, chunk type, chunk data, CRC
    if len(chunks) == 0:
        raise Exception("PNG ended prematurely, no chunks")
    if chunks[len(chunks) - 1]["type"] != "IEND":
        raise Exception("PNG ended prematurely, missing IEND header")
    return chunks

def extract_data_from_image(image_path):
    image_bytes = open(image_path, "rb").read()
    chunks = read_chunks(image_bytes)
    chunks = [chunk for chunk in chunks if chunk["type"] == "tEXt"]
    try:
        chunk = chunks[0]
        data = chunk["data"]
        # remove "chara" keyword from beginning of data
        if data[:5] == b"chara":
            data = data[5:]
        else:
            raise Exception("PNG missing chara keyword")
        # decode data from base64
        data = base64.b64decode(data)
        # decode data from utf-8
        data = data.decode("utf-8")
        return json.loads(data)
    except:
        return {}