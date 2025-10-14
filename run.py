import src.io as io

def main():

    # Parse arguments
    args = io.parse_arguments()
    
    if args.compress:    # Compression

        # Buffer sizes are needed for compression. 
        # Trigger error and exit if either is missing. 
        if not (args.lwsize and args.swsize):
            print("ERROR: compression needs --lwsize and --swsize")
            exit()

        io.seq_compress_file(
            input = args.input,
            output = args.output,
            lwsize = args.lwsize,
            swsize = args.swsize
        )

    elif args.decompress:    # Decompression
        
        # Decompression uses the swsize stored in the compressed file. 
        # --lwsize and --swsize options will not be used.
        if args.lwsize or args.swsize:
            print("WARNING: --lwsize and --swsize not needed for decompression. They will be ignored but the program will continue.")

        io.seq_decompress_file(
            input = args.input,
            output = args.output,
        )

if __name__ == "__main__":
    main()