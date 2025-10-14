"""
Compression with LZ77
"""

from src.classes import Buffer

def get_longest_match(
        lookahead_buff: Buffer,
        search_buff: Buffer
    ) -> tuple[tuple[int, int, str], str]:

    """
    A function that locates the longest match between the prefix of the lookahead buffer 
    and any position in the search buffer.

    Parameters:
        lookahead_buff (Buffer): 
            The buffer object assigned as the lookahead buffer.

        search_buff (Buffer): 
            The buffer object assigned as the search buffer.

    Returns:
        tuple:
        match_tupl (tuple[int, int, str]): It contains:
            offset (int): The position of the match in the search buffer, 0 if no match.
            - match length (int): The length of the longest match, 0 if no match.
            - mismatch character (str): The character that caused the mismatch.
                
        curr_longest (str): 
            The longest match found in the buffers, or an empty string 
            if no matches are found.
    """

    match_tupl = (0,0, lookahead_buff.elements[0])  # Returned if no matches
    curr_longest = ""                               # Current longest match

    # Iterate through the search buffer to find matches
    for pos, search_elem in enumerate(search_buff.elements, 0):

        # Find start sites by comparing with the 1st elem of the search buffer
        if lookahead_buff.elements[0] == search_elem:

            offset = len(search_buff.elements) - pos    # Save offset of match
            mtch = lookahead_buff.elements[0]           # Initialize match

            # Extend match until mismatch if found
            for i in range(1, len(lookahead_buff.elements)):
                
                # Match if position is within length of the search buff add elements match
                if pos + i < len(search_buff.elements) and lookahead_buff.elements[i] == search_buff.elements[pos + i]:
                    mtch += lookahead_buff.elements[i]

                # Mismatch: only save if the match is the current longest
                elif len(mtch) >= len(curr_longest):
                    curr_longest = mtch               # Match
                    new = lookahead_buff.elements[i]  # Mismatch element
                    match_tupl = (offset, len(mtch), new)   # Tuple
                break
                            
    return match_tupl, curr_longest

def seq_compress(
        text: str, 
        lwsize: int,
        swsize: int
    ) -> list[tuple[int,int,str]]:
    
    """
    Text compression with the LZ77 algorithm. The text is encoded as a list of tuples (offset, match length, next character).

    Parameters:
        text (str): The input string to be compressed.
        lwsize (int): size of the lookahead buffer.
        swsize (int): size of the search buffer.

    Returns:
        tupls_list (list[tuple[int,int,str]]): 
        list of compression tuples like (offset, match length, next character) for matches and (0, 0, next character) for mismatches.
    """

    # Initiate with window size lwsize, load with the 1st elements of the text
    start = list(text[:lwsize])
    lookahead_buff = Buffer(lwsize)
    lookahead_buff.load(start)

    # Initiate the search buffer, but don't add any content for now
    search_buff = Buffer(swsize)

    i = 0               # Position of window for reference
    tupls_list = []     # Save tuples here
    eof = False         # Flag to check for EOF

    # While lookahead buffer is not empty
    while (any(elem for elem in lookahead_buff.elements)):

        # Find the longest match and save tuple
        match_tupl, mtch = get_longest_match(lookahead_buff, search_buff)
        tupls_list.append(match_tupl)

        # If the offset is not 0, there is a match
        if match_tupl[0] != 0:

            # Add match and the next character to the search buffer
            add_search = list(mtch + match_tupl[2]) 

            i += len(mtch) + 1  # Move window
            
            # Handle EOF
            if i + lwsize < len(text):

                # 1) Not EOF, just add characters
                lookahead_buff.update(list(text[i: i+lwsize]))

            elif not eof:

                # 2) First time at EOF, switch the eof flag to True
                eof = True

                if i + lwsize == len(text):

                    # Case A) EOF is right at the end of the window
                    # Add all the remaining characters in the text
                    lookahead_buff.update(list(text[i:]))

                elif i + lwsize > len(text):
                    
                    # Case B) EOF happens before the end of the window
                    lookahead_buff.update(list(text[i:]))   # Add characters

                    # Calculate number of characters to delete
                    times_delete = len(mtch)+ i + lwsize - len(text) - 1
                    [lookahead_buff.update() for j in range(times_delete)]
            else:
                # 3) EOF reached in another iteration, just delete characters
                [lookahead_buff.update() for i in range(len(mtch) + 1)]
        else:
            # Offset is 0, no matches found
            # Add new character to search buff
            add_search = list(match_tupl[2])

            # Detect EOF
            if i + lwsize < len(text):
                add_lookahead = list(text[i + lwsize])
                lookahead_buff.update(add_lookahead)
            else:
                eof = True  # Switch eof flag to True
                lookahead_buff.update() # We only scroll 1 character in any case

            i += 1  # Move window
        
        # Add content to the search buffer
        if i == 1:
            # Load with the first element after first iteration
            search_buff.load([text[0]])
        else:
            search_buff.update(add_search) # Update from second iteration

    return tupls_list