# This script makes a photomosiac out of an image using the images contained within the CollageImages folder
# The script is designed and tested to work with PNGs, but it seems to do fine with JPGs. Using other file formats may crash the script

from PIL import Image
import glob
import math
import random


def getColorAverage(imageObject):
    # Crushes the input image into a single pixel and returns the color value of that pixel.
    return imageObject.resize((1, 1)).getcolors()[0][1]


def squareCrop(imageObject):  # Crops the image towards the center into a square
    imx, imy = imageObject.size
    if imx > imy:  # True if the width of the image is larger than it's hight
        # Makes a square box that is as large as the image's hight since hight is the limiting factor
        # PIL's crop is anchored to the top left so we need to also offset the square box so that it crops the middle of the image instead of the left side of the image.
        offset = (imx // 2) - (imy // 2)
        box = (0 + offset, 0, imy + offset, imy)
    elif imy > imx:  # True if the hight of the image is larger than it's width
        # Same deal as above, but this time the square box is made of the width and offset is used to move the square down to the center of the image
        offset = (imy // 2) - (imx // 2)
        box = (0, 0 + offset, imx, imx + offset)
    else:  # The image's x and y resolution are the same, meaning the image is already square
        box = (0, 0, imx, imy)
    return imageObject.crop(box)


# Returns a list of tuples that has a square cropped version of every image in the CollageImages folder and the square cropped image's average color
def processCollageImages(squareSize, scale):
    processedCollageImages = []
    for imageFile in sorted(glob.iglob("CollageImages/*")):
        imageObject = Image.open(imageFile)
        # We save the image's filename here because it doesn't work after we have processed the image for some reason
        imageFilename = imageObject.filename
        imageObject = squareCrop(imageObject)
        color = getColorAverage(imageObject)

        # Rescales the image according to the squareSize and scale the user wants it to be in
        imageObject = imageObject.resize(
            (squareSize * scale, squareSize * scale), Image.NEAREST)
        processedCollageImages.append((imageObject, color))
        print(f"Proccessed {imageFilename}")
    return processedCollageImages


def main():
    while True:
        # Get the name of the input image and try to open it
        while True:
            try:
                inputImageName = input(
                    "What is the complete file name of the input image with it's file extension?\n(NOTE: The image should be located in the same folder as this python file, not in the CollageImages folder.)\n")
                imageObject = Image.open(inputImageName)
                break
            except:
                print(
                    "An error has occured when trying to open the file as an image. Please try again.")

        # Get squareSize
        while True:
            try:
                # Controls how large the image gets sectioned into
                squareSize = int(input(
                    "How large (in pixels) should each small image making up the larger image be?\n"))
                break
            except:
                print("Invalid input. Try again.")

        # Get scale
        while True:
            try:
                # Essentially controls how much the output image should increase in resolution to allow the user to see more details of the smaller images making up the bigger one
                scale = int(input("Should the image be scaled up by a factor to allow for more details in the smaller images? (Whole Numbers Only)\nIf you put a scale of 1, the output image will have the same resolution as the input image.\nIf you put a scale of 2, the output image will be double the resolution of the input image. The increased resolution allows the smaller images to have more detail in case you like to zoom into the output image and be able to tell what exactly the smaller images are.\n"))
                break
            except:
                print("Invalid input. Try again.")

        # Get the desired name of the output image
        outputImageName = input(
            "What should the name of the output image be including file extension?\n")

        # Check with the user if they got everything right
        if input(f"\nAre these settings correct?\nSquare Size: {squareSize}px\nScale: {scale}x\nInput Image: {inputImageName}\nOutput Image: {outputImageName}\n(Press Enter to continue. Enter anything else to try again.)\n") == "":
            break

    print(
        f"Processing CollageImages...\n(NOTE: None of the pictures involved will be changed / destroyed. The only picture edited and saved is '{outputImageName}'.")
    processedCollageImages = processCollageImages(squareSize, scale)
    print(
        f"Finished processing CollageImages folder.\nCreating {outputImageName}...   (This may take some time).")

    # Gets the input image's x and y resolution and puts it into two variables
    imx, imy = imageObject.size

    # Calculates the amout of squares of squareSize that can fit in the image's x and y axis
    # If a square cannot fit, the pixels are discared essentially making the new image have a resolution that is a multiple of squareSize
    xsquares = imx // squareSize
    ysquares = imy // squareSize
    newim = Image.new("RGB", (xsquares * squareSize *
                      scale, ysquares * squareSize * scale))

    # Lazy to comment what everything does
    # Essentially it creates loops to go row by row across the input image and crops out squares based on user input.
    # It takes the square's average color and tries to find the collage image with the closest average color
    # Once it finds the closest image, it resizes and pastes the collage image onto a new image in the same place as where we were taking that square and moves on to that next square.
    for yindex in range(ysquares):
        yoffset = yindex * squareSize
        for xindex in range(xsquares):
            xoffset = xindex * squareSize

            region = (xoffset, yoffset, squareSize +
                      xoffset, squareSize + yoffset)
            cropim = imageObject.resize((1, 1), box=region)

            croprgb = getColorAverage(cropim)

            distance = -1
            # Shuffles the images in case there are multiple images that have the same average
            random.shuffle(processedCollageImages)
            for pic in processedCollageImages:
                picrgb = pic[1]
                newdistance = math.sqrt(  # Color distance calculation. Basically calculates the distance between two points in 3d space.
                    (picrgb[0] - croprgb[0])**2 + (picrgb[1] - croprgb[1])**2 + (picrgb[2] - croprgb[2])**2)
                if distance == 0:  # If the distance to a color is 0, the average RGB of the two images are the same so we stop looking for a better image to use
                    break
                elif distance == -1 or newdistance < distance:
                    distance = newdistance
                    closestimage = pic[0]

            newim.paste(closestimage, (xoffset * scale, yoffset * scale))

    newim.save(outputImageName)
    print(f"Finished creating {outputImageName}!")


if __name__ == "__main__":
    main()
