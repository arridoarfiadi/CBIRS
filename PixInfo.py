# PixInfo.py
# Program to start evaluating an image in python

# Program Name: Content-Based Image Retrieval system
# Modified by: Arrido Arfiadi
# Last Modified: 1/31/18 2:04:15 PM

from PIL import Image, ImageTk
import glob, os, math
import csv
import numpy


# Pixel Info class.
class PixInfo:

    # Constructor.
    def __init__(self, master):

        self.master = master
        self.imageList = []
        self.photoList = []
        self.xmax = 0
        self.ymax = 0
        self.colorCode = []
        self.intenCode = []
        self.combinationCode = []
        self.invertedMatrix=[]
        self.averageColumns = []
        self.stDeviation = []
        self.matrixNormalized=[]


        # Add each image (for evaluation) into a list,
        # and a Photo from the image (for the GUI) in a list.
        for infile in glob.glob('images/*.jpg'):

            file, ext = os.path.splitext(infile)
            im = Image.open(infile)


            # Resize the image for thumbnails.
            imSize = im.size
            x = int(imSize[0]/2)
            y = int(imSize[1]/2)
            imResize = im.resize((x, y), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(imResize)


            # Find the max height and width of the set of pics.
            if x > self.xmax:
              self.xmax = x
            if y > self.ymax:
              self.ymax = y


            # Add the images to the lists.
            self.imageList.append(im)
            self.photoList.append(photo)

        # gets the values from previous calculation
        if os.path.isfile('savedColorCode.csv') and os.path.isfile('savedIntenCode.csv') and os.path.isfile('savedCombinedCode.csv') and os.path.isfile('savedNormalizedMatrix.csv'):
            # reads the values
            with open('savedNormalizedMatrix.csv','r') as csv_file:
                csv_reader = csv.reader(csv_file)
                with open('savedCombinedCode.csv','r') as csv_file3:
                    csv_reader3 = csv.reader(csv_file3)
                    with open('savedColorCode.csv','r') as csv_file1:
                        csv_reader1 = csv.reader(csv_file1)
                        with open('savedIntenCode.csv','r') as csv_file2:
                            csv_reader2 = csv.reader(csv_file2)
                            with open('savedStandardDeviation.csv','r') as csv_file5:
                                csv_reader5 = csv.reader(csv_file5)
                                with open('savedAverage.csv','r') as csv_file6:
                                    csv_reader6 = csv.reader(csv_file6)
                                    # Put the values in
                                    for line3 in csv_reader3:
                                        self.combinationCode.append(line3)
                                    for line2 in csv_reader2:
                                        self.intenCode.append(line2)

                                    for line1 in csv_reader1:
                                        self.colorCode.append(line1)
                                    for line in csv_reader:
                                        self.matrixNormalized.append(line)
                                    for line5 in csv_reader5:
                                        self.stDeviation.append(line5)
                                    for line6 in csv_reader6:
                                        self.averageColumns.append(line5)


        # calculates new values
        else:
            self.calculateValues(self.imageList)
            self.findNormalizedMatrix()

    # Name: firstTwoBits
    # Function: returns the first two bits for
    # color code method
    def firstTwoBits(self,value):
        binaryCode = bin(value)[2:].zfill(8)
        return  binaryCode[:2]

    # Name: encode
    # Function: Bin function returns an array of bins for each
    # image, both Intensity and Color-Code methods.
    def encode(self, pixlist):

        # 2D array initilazation for bins, initialized
        # to zero.
        CcBins = [0]*64
        InBins = [0]*25

        self.firstTwoBits(pixlist[0][0])
        # Loops through all pixels in the image (98,304 pixels)
        for pixelVal in pixlist:
            # Calculates Intensity Method using the formula provided
            intensity = 0.299*pixelVal[0] + 0.587*pixelVal[1] + 0.114*pixelVal[2]
            # Find which bins it belongs to
            assignBins = int(intensity/10)
            if assignBins >= 25:
                assignBins = 24
            # Put it in the bin
            InBins[assignBins] +=1


            # Assign R,G,B values
            r = pixelVal[0]
            g = pixelVal[1]
            b = pixelVal[2]
            # Get first two values of r,g,b and combine together and change binary to decimal
            colorMethod = int(str(self.firstTwoBits(r) + self.firstTwoBits(g)  + self.firstTwoBits(b)),2)

            if colorMethod >= 64:
                colorMethod = 63
            # Put it in the bins
            CcBins[colorMethod] += 1


        # Prints out to the console the results
        print("Intensity Value")
        print(InBins)
        print("Color Code Value")
        print(CcBins)
        print('\n')
        # Return the list of the number of pixels in the bins for ColorCode and Intensity
        return CcBins, InBins

    # Name: calculateValues
    # Function: calculates the values
    def calculateValues(self,imageList):
        # Make two files one for Color Code one for Intensity Values
        with open('savedCombinedCode.csv','w') as new_file3:
            csv_writer3 = csv.writer(new_file3, delimiter=',', lineterminator = '\n')
            with open('savedColorCode.csv','w') as new_file:
                csv_writer1 = csv.writer(new_file, delimiter=',', lineterminator = '\n')
                with open('savedIntenCode.csv','w') as new_file2:
                    csv_writer2 = csv.writer(new_file2, delimiter=',', lineterminator = '\n')
                    for im in self.imageList[:]:
                        combine =[]
                        # Get Pixel values
                        pixList = list(im.getdata())
                        # Ge the number of pixels in each bins for ColorCode and Intensity
                        CcBins, InBins = self.encode(pixList)
                        # Add it to the list for all 100 image
                        self.colorCode.append(CcBins)
                        self.intenCode.append(InBins)


                        # Write the values in the file for faster access next time
                        csv_writer1.writerow(CcBins)
                        csv_writer2.writerow(InBins)

                        #Find the combination of the two with
                        combine = self.findCombinedDivided(InBins,CcBins)
                        self.combinationCode.append(combine)
                        csv_writer3.writerow(combine)
                    #get Inverted Combination for easy calculation
                    self.findInvertedMatrix()

    #Name: findCombinedDivided
    #Function: Find the combined matrix of Intensity and Color Code
    def findCombinedDivided(self,InBins,CcBins):
        totalPix=0
        inten = []*25
        cc=[]*64
        #Get total Pixel
        for i in InBins:
            totalPix = int(i) + totalPix
        #Get Intensity Values normalized
        for i in range (len(InBins)):
            x= float(InBins[i])/totalPix
            inten.append(x)
        #Get ColorCode Normalized
        for i in range (len(CcBins)):
            y= float(CcBins[i])/totalPix
            cc.append(y)
        #Add Both
        temp= inten+cc
        return temp
    #Name: findInvertedMatrix
    #Function: Get the invertedMatrix for easier calculation
    def findInvertedMatrix(self):
        #Make temp bin
        w,h=100,89
        self.newBin = [[1 for x in range(w)] for y in range(h)]
        m=0

        #Write it for faster reading
        with open('savedInvertedMatrix.csv','w') as new_file:
            csv_writer = csv.writer(new_file, delimiter=',', lineterminator = '\n')
            #Inverts the combinationMatrix
            for i in self.combinationCode:
                for j in range(len(i)):
                    self.newBin[j][m]=i[j]
                m+=1
            for i in self.newBin:
                self.invertedMatrix.append(i)
                csv_writer.writerow(i)
    #Name: findNormalizedMatrix
    #Function: Find the Normalized matrix using the formula (Xi-Averagei/StdDevi)
    def findNormalizedMatrix(self):
        w,h=89,100
        self.normalizedMatrix = [[1 for x in range(w)] for y in range(h)]

        m=0
        #Write for faster reading
        with open('savedAverage.csv','w') as new_file6:
            csv_writer6 = csv.writer(new_file6, delimiter=',', lineterminator = '\n')
            #Getting Average
            for i in self.invertedMatrix:
                total =0
                for j in i:
                    total += float(j)

                average = float(total/len(i))

                self.averageColumns.append(average)
            csv_writer6.writerow(self.averageColumns)
        #Write for faster reading
        with open('savedStandardDeviation.csv','w') as new_file5:
            csv_writer5 = csv.writer(new_file5, delimiter=',', lineterminator = '\n')
            #Getting StandardDeviation
            for i in self.invertedMatrix:
                temp = i
                temp = list(map(float,temp))
                stddev = numpy.std(temp)
                self.stDeviation.append(stddev)

            csv_writer5.writerow(self.stDeviation);
        #Write for faster reading
        with open('savedNormalizedMatrix.csv','w') as new_file4:
            csv_writer4 = csv.writer(new_file4, delimiter=',', lineterminator = '\n')
            #Getting normalized values
            for i in self.combinationCode:
                for j in range(len(i)):

                    if (self.stDeviation[j] == 0):
                        answer=0
                    else:
                        #Using the formula
                        answer = (float(i[j]) - self.averageColumns[j])/self.stDeviation[j]
                    self.normalizedMatrix[m][j] = answer
                m+=1
            #Add them to the list
            for i in self.normalizedMatrix:
                csv_writer4.writerow(i)
                self.matrixNormalized.append(i)

    # Accessor functions:
    def get_imageList(self):
        return self.imageList

    def get_photoList(self):
        return self.photoList

    def get_xmax(self):
        return self.xmax

    def get_ymax(self):
        return self.ymax

    def get_colorCode(self):
        return self.colorCode

    def get_intenCode(self):
        return self.intenCode
    def get_combinationCode(self):
        return self.combinationCode
    def get_standardDeviation(self):
        return self.stDeviation
    def get_averageColumn(self):
        return self.averageColumns
    def get_NormalizedMatrix(self):
        return self.matrixNormalized
