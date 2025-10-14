"""
Decompression of file compressed with LZ77
"""

def seq_decompress(
        tuples_lst: list[tuple], 
        swsize: int
    ) -> str:

    """
    Restore original text from compression tuples.

    Parameters:
        tuples_lst (list[tuple[int,int,str]]): 
            A list of tuples representing the compressed data (offset, length_match, new).
        swsize (int): 
            size of the search buffer used during compression.

    Returns:
        str: original decompressed text.
    """

    string = ""

    for offset, length_match, new in tuples_lst:

        if offset == 0:
            string += new   # if offset is 0, character is new
        else:
            # If offset is not 0, there is a repetition
            start_rep = len(string) - offset    # Start index
            end_rep = start_rep + length_match  # End index

            # Add the repeated characters and the new character
            add_to_str = string[start_rep:end_rep] + new
            string += add_to_str
            
    return string