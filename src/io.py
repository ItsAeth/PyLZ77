"""
Input / Output operations of the LZ77 compressor/decompressor program. Includes
command linea argument parsing, binary encoding/decoding and writing/reading
files.
"""

import argparse
from src.compress import seq_compress
from src.decompress import seq_decompress
import numpy as np

def parse_arguments() -> argparse.Namespace:

    """
    Parse the arguments received from command line.
    """

    parser = argparse.ArgumentParser(
        description = "LZ77 compressor/decompressor tool for command line."
        )
    
    # Input/output arguments
    parser.add_argument(
        "input",
        help = "Path to input file.", type = str
    )
    parser.add_argument(
        "output",
        help = "Path to output file.", type = str
    )

    # Next 2 are only required for compression, optional by default.
    parser.add_argument(
        "-l",
        "--lwsize",
        help = "Window size of the lookahead buffer for compression.",
        type = int,
        required = False
    )
    parser.add_argument(
        "-s",
        "--swsize",
        help = "Window size of the search buffer for compression.",
        type = int,
        required = False
    )

    # Compress/decompress options (mutually exclusive, 1 required)
    modes = parser.add_mutually_exclusive_group(required = True)
    modes.add_argument(
        "-c", 
        "--compress",
        help = "compress the input file",
        action = "store_true"
    )
    modes.add_argument(
        "-d",
        "--decompress",
        help = "decompress the input file",
        action = "store_true"
    )
    
    args = parser.parse_args()
    return args

def to_binary(tupl_lst, outfile, lwsize:int, swsize:int) -> None:
    """
    Encode the buffer sizes and the list of tuples as a series of bytes and 
    dump to a file. It also prints the minimum number of bytes to encode all
    the tuples. 

    Parameters:
        tupl_lst(list[tuple(int,int,str)]): 
            list of tuples to encode
        outfile(str):
            path of the output file to dump the bytes.
        lwsize (int): 
            size of the lookahead buffer.
        swsize (int): 
            size of the search buffer.

    Returns:
        None:
            This function dumps the results to a file and prints minimum number of bytes to encode all the tuples. 
    """

    # Bytes needed to represent swsize possible values of offset
    bytes_offset = int(np.ceil(np.log2(swsize) / 8))

    # The maximum length of the match is limited by the size of the smallest 
    # buffer. bytes needed to represent all possible values of match Length
    bytes_length =  int(np.ceil(np.log2(min(lwsize, swsize)) / 8))

    # Add 8 bits for the new character (1 byte) and calculate total bits
    total_bytes = int(bytes_offset + bytes_length + 1)

    print(f"Minimum compressed size of tuples: {total_bytes * len(tupl_lst)} bytes (assuming 1 char = 1 byte).")

    # Encode as bytes in little endian byteorder and dump to file
    with open(outfile, "wb") as f:
        
        # The first two bytes are the buffer sizes
        f.write(lwsize.to_bytes(byteorder = "little"))
        f.write(swsize.to_bytes(byteorder = "little"))

        # The next bytes are for the tuples
        for offset, len_match, new in tupl_lst:
            
            offset_byte = offset.to_bytes(bytes_offset, "little")
            len_byte = len_match.to_bytes(bytes_length, "little")
            new_byte = new.encode(encoding='utf-8')

            f.write(offset_byte)
            f.write(len_byte)
            f.write(new_byte)

    return None

def seq_compress_file(
        input: str, 
        output: str,
        lwsize: int,
        swsize:int
    ) -> None:

    """
    Compress the input file using the LZ77 algorithm to encode the text as 
    compression tuples. Write the compressed data to the output file in binary 
    format. 


    Parameters:
        input (str): path to the input file with text to compress. 
        output (str): path to the output file.
        lwsize (int): size of the lookahead buffer for compression.
        swsize (int): size of the search buffer for compression.

    Raises:
        FileNotFoundError: If the input file does not exist or cannot be opened.

    Returns:
        None: writes the result to the output file.
    """

    try:
        print(f"\nCOMPRESSING {input.upper()}\n")

        # Generate tuples
        with open(input, "r") as file:
            text = file.read()
            tuples_lst = seq_compress(text, lwsize = lwsize, swsize=swsize)

        # Encode as binary and write to outfile
        to_binary(tuples_lst, output, lwsize, swsize)

    except FileNotFoundError as e:
        print(f"{e}: input file can't be found or does not exist.")

    return None

def from_binary(input_path):

    """
    Reads the binary data from the input file to retrieve the `lwsize` and `swsize` parameters, and reconstruct the list of compression tuples.

    Parameters:
        input_path (str): path to the binary file with compressed data

    Returns:
        lwsize (int): 
            Lookahead buffer size used during compression.
            
        swsize (int): 
            The search buffer size used during compression.

        tupls_list (list[tuples[int,int,str]]): 
            list of compression tuples.where each tuple is in the form (offset,
            match length, new character).
    """

    with open(input_path, "rb") as f:
        
        # The first 2 bytes belong to the parameters
        lwsize =int.from_bytes(f.read(1), "little")
        swsize = int.from_bytes(f.read(1), "little")

        tupls_list = []
        
        # The rest of the bytes belong to the tuples
        bytes_read = f.read()

        # Iterate in in groups of 3 to restore the tuples
        for i in range(0, len(bytes_read), 3):

            offset = bytes_read[i]
            match_len = bytes_read[i + 1]
            new_char = chr(bytes_read[i + 2])

            # Agregar la tupla a la lista
            tupls_list.append((offset, match_len, new_char))
        
        return lwsize, swsize, tupls_list
    
def seq_decompress_file(
        input: str, 
        output: str
    ) -> None:

    """
    Decompresses the binary file and writes the decompressed text to the output file.

    Parameters:
        input (str): path to binary file with compression data.
        output (str): path to the output file to write decompressed text.

    Raises:
        FileNotFoundError: If the input file does not exist or cannot be opened.

    Returns:
        None: writes text to the output file.
    """

    try:
        
        # Decode from binary and decompress
        lwsize, swsize, tuples_lst = from_binary(input)
        text = seq_decompress(tuples_lst, swsize)

        # Write text to output
        with open(output, "w") as outfile:
            outfile.write(text)
    
    except FileNotFoundError as e:
        print(f"{e}: input file can't be found or does not exist.")

    return None
