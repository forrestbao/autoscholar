import lib.get_highlighted_text
           
import sys,os


if __name__ == "__main__":
    db=str(sys.argv[1])
    output=str(sys.argv[2])
    print("db:",db)
    print("output:",output)
    lib.get_highlighted_text.main(db,output)

