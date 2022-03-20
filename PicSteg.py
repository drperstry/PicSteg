# This code is originally from https://betterprogramming.pub/image-steganography-using-python-2250896e48b9
# Edited by drperstry to be working in encoding and decoding for multiple pictures.

# more references
    # https://www.geeksforgeeks.org/program-decimal-binary-conversion/
    # https://www.geeksforgeeks.org/working-images-python/
    # https://dev.to/erikwhiting88/let-s-hide-a-secret-message-in-an-image-with-python-and-opencv-1jf5
    # A code along with the dependencies can be found here: https://github.com/goelashwin36/image-steganography

# Python program implementing Image Steganography
# added the function of multiple pictures.
# this code doens't support JPG pictures
# Possible improvements
# need to consider limiting the amount of data can be hidden in this file as this doens't work for every picture!!

# PIL module is used to extract pixels of image and modify it
from PIL import Image
import argparse
import textwrap


# Convert encoding data into 8-bit binary
# form using ASCII value of characters
def genData(data):

        # list of binary codes
        # of given data
        newd = []

        for i in data:
            newd.append(format(ord(i), '08b'))
        return newd

# Pixels are modified according to the
# 8-bit binary data and finally returned
def modPix(pix, data):

    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)
    #this for loop is not simple
    for i in range(lendata):

        # Extracting 3 pixels at a time
        pix = [value for value in imdata.__next__()[:3] +
                                imdata.__next__()[:3] +
                                imdata.__next__()[:3]]

        # Pixel value should be made
        # odd for 1 and even for 0
        for j in range(0, 8):
            if (datalist[i][j] == '0' and pix[j]% 2 != 0):
                pix[j] -= 1

            elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                if(pix[j] != 0):
                    pix[j] -= 1
                else:
                    pix[j] += 1
                # pix[j] -= 1

        # Eighth pixel of every set tells
        # whether to stop ot read further.
        # 0 means keep reading; 1 means thec
        # message is over.
        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                if(pix[-1] != 0):
                    pix[-1] -= 1
                else:
                    pix[-1] += 1

        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]

def divideString(string, n):
    str_size = len(string)
    # Calculate the size of parts to find the division points
    part_size = int(str_size/n)
    k = 1
    str1=""
    strlist=[]
    for i in string:
        str1=str1+i    
        if k % part_size == 0:
            strlist.append(str1)
            str1=""
        k += 1
    if(len(str1)!=0):
        strlist[-1]+=(str1)
    return strlist

def encode_enc(newimgs, data):
    #newimgs should be a list of images, data should be a list of chunk of data 
    # divided to be same as number of images
    #making multiple values of w in the same way
    #divide data
    w=[]
    for img in newimgs:
        w.append(img.size[0])
    
    dataList=divideString(data, len(newimgs))
    #dataList, w
    #2 outer for loops for each data and for each img,
    for i, img in enumerate(newimgs):
        (x, y) = (0, 0)
        #pixel for ordering the imgs
        # pix = [value for value in img.__next__()[:3]]
        pix=(i,0,0)
        img.putpixel((x, y), pix)
        (x, y) = (1, 0)

        for pixel in modPix(img.getdata(), dataList[i]):
            # Putting modified pixels in the new image
            img.putpixel((x, y), pixel)
            if (x == w[i] - 1):
                x = 0
                y += 1
            else:
                x += 1

# Encode data into image
def encode(ImagesIn, file, ImagesOut):
    #enter multiple images name
    string1=""
    imgs=[]
    for image in ImagesIn:
        imgs.append(Image.open(image, 'r'))

    if (not open(file)):
        raise ValueError('Secret file does not exist')
    
    with open(file, "r") as f:
        data=f.read()
    #copy all images like next line, a list  enter it in the encode_enc method
    newimgs =[]
    for img in imgs:
        newimgs.append(img.copy())
    
    #inputting the list of newimgs and data
    encode_enc(newimgs, data)

    #save an img for each new img exist
    for i, newimg in enumerate(newimgs):
        new_img_name=ImagesOut
        name=new_img_name.split(".")
    
        name=name[0]+str(i)+"."+name[-1]
        new_img_name=name
        newimg.save(new_img_name, str(new_img_name.split(".")[1].upper()))

# Decode the data in the image
def decode(SecretImages, file):

    imgs=[]
    for img in SecretImages:
        imgs.append(Image.open(img, 'r'))
    
    data = ''
    #for each img in the list do iter
    imgsdata=[]
    for img in imgs:
        imgsdata.append(iter(img.getdata()))
    
    #ordering the imgs based on first color on the first pixel
    imgsdataOrdered=[]
    for data in imgsdata:
        pixel= data.__next__()[:3]
        imgsdataOrdered.append([data, pixel[0]])

    imgsdata=[]
    for ordering in range(len(imgsdataOrdered)):
        for ls in imgsdataOrdered:
            for index, x in enumerate(ls):
                if(index==1):
                    if(x==ordering):
                        imgsdata.append(ls[0])

    for imgdata in imgsdata:
        data=''
        #this to skip first pixel which was used for ordering
        while(True):
            pixels = [value for value in imgdata.__next__()[:3] +
                                    imgdata.__next__()[:3] +
                                    imgdata.__next__()[:3]]
            # string of binary data
            binstr = ''

            for i in pixels[:8]:
                if (i % 2 == 0):
                    binstr += '0'
                else:
                    binstr += '1'

            data += chr(int(binstr, 2))
            if (pixels[-1] % 2 != 0):
                with open(file, "a") as f:
                    f.write(data)
                    break
    return "Done Check the new file to see hidden data"
# Main Function
def main():
    desc=textwrap.dedent('''Pic Steganography:

            usage: 
                1: PicSteg.py Hide [-h] --images IMAGES [IMAGES ...] --secret SECRET --NewImage NEWIMAGE
                2: PicSteg.py Unhide [-h] --SecretImages SECRETIMAGES [SECRETIMAGES ...] --NewFile NEWFILE''')
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
    subparser=parser.add_subparsers(dest='Command')
    Hide=subparser.add_parser('Hide')
    Unhide=subparser.add_parser('Unhide')


    Hide.add_argument("--images", '-I', nargs="+",type=str, help="--images img1.png, img2.png, ...", required=True)
    Hide.add_argument('--secret', "-S", type=str, help='--secret file_name', required=True)
    Hide.add_argument('--NewImage', "-NI", type=str, help='--NewImage file_name', required=True)

    Unhide.add_argument("--SecretImages","-SI" , nargs="+", type=str, help="--SecretImages img1.png, img2.png, ...", required=True)
    Unhide.add_argument('--NewFile', "-NF", type=str, help='--NewFile file_name', required=True)


    args = parser.parse_args()
    if args.Command == None:
        print("choose command Hide or Unhide")
    elif args.Command == 'Hide':
        encode(args.images, args.secret, args.NewImage)

    elif args.Command == 'Unhide':
        decode(args.SecretImages, args.NewFile)

# Driver Code
if __name__ == '__main__' :
    # Calling main function
    main()
