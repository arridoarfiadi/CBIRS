# ImageViewer.py
# Program to start evaluating an image in python
#
# Show the image with:
# os.startfile(imageList[n].filename)

# Program Name: Content-Based Image Retrieval system
# Modified by: Arrido Arfiadi
# Last Modified: 1/31/18 2:04:15 PM

from tkinter import *
import math, os
from PixInfo import PixInfo
import csv
import numpy


# Main app.
class ImageViewer(Frame):

    # Constructor.
    def __init__(self, master, pixInfo):

        Frame.__init__(self, master)
        self.master    = master
        self.pixInfo   = pixInfo
        # Get the color code and intensity code
        self.colorCode = pixInfo.get_colorCode()
        self.intenCode = pixInfo.get_intenCode()
        self.combinationCode = pixInfo.get_combinationCode()
        self.matrixNormalized = pixInfo.get_NormalizedMatrix()
        # Full-sized images.
        self.imageList = pixInfo.get_imageList()
        # Thumbnail sized images.
        self.photoList = pixInfo.get_photoList()
        # Image size for formatting.
        self.xmax = pixInfo.get_xmax()
        self.ymax = pixInfo.get_ymax()

        # Background Color for GUI
        self.background="#a1dbcd"


        # Start at page 0
        self.currentPage = 0

        # For changing the order of the images
        self.currentPhotoList = self.photoList
        self.currentImageList = self.imageList

        # Create Main frame.
        mainFrame = Frame(master,bg=self.background)
        mainFrame.pack()

        # Create header with two white bar
        whitebar1 = Label(mainFrame,bg="#FFFFFF")
        whitebar2 = Label(mainFrame,bg="#FFFFFF")
        header = Label(mainFrame,font=('Helvetica', 20), fg="#383a39", bg=self.background,
               text="Content Based Search")
        whitebar1.grid(row=0,columnspan = 3,sticky= W+E)
        header.grid(row=1,columnspan=3)
        whitebar2.grid(row=2,columnspan = 3,sticky= W+E)

        # Create Picture chooser frame.
        listFrame = Frame(mainFrame,bg=self.background)
        listFrame.grid(row=3, column=0, sticky=W)

        # Create Control frame.
        controlFrame = Frame(mainFrame,bg=self.background,)
        controlFrame.grid(row = 3, column = 2, sticky=W)

        # Create Preview frame.
        previewFrame = Frame(mainFrame,bg=self.background,
            width=self.xmax+45, height=self.ymax)
        previewFrame.pack_propagate(0)
        previewFrame.grid(row=3, column= 1,sticky=W)

        # Create Result frame
        result2 = Frame(mainFrame,bg=self.background)
        result2.grid(row=6,columnspan =3)
        self.canvas2 = Canvas(result2,highlightthickness=0)
        self.resultsScrollbar2 = Scrollbar(result2)
        self.resultLabel = Label(mainFrame,text = "Results: ",font=('Helvetica', 16),
                        fg="#383a39",pady=5,bg=self.background,)

        # Create Page Butoons
        self.pageNumber = Label(mainFrame,fg="#383a39",bg=self.background,
                    text="Page",font=('Helvetica',16))
        self.backButton = Button(mainFrame,text="Back",
                    padx = 10, width=5,bg="#FFFFFF",
                    command=lambda: self.backPage())
        self.nextButton = Button(mainFrame,text="Next",
                    padx = 10, width=5,bg="#FFFFFF",
                    command=lambda: self.nextPage())

        # Layout Picture Listbox.
        self.listScrollbar = Scrollbar(listFrame)
        self.listScrollbar.pack(side=RIGHT, fill=Y)
        self.list = Listbox(listFrame,
            yscrollcommand=self.listScrollbar.set,
            selectmode=BROWSE,
            highlightthickness=0,
            height=13)
        for i in range(len(self.imageList)):
            self.list.insert(i, self.imageList[i].filename)
        self.list.pack(side=LEFT, fill=BOTH)
        self.list.activate(1)
        self.list.bind('<<ListboxSelect>>', self.update_preview)
        self.listScrollbar.config(command=self.list.yview)

        # Layout Controls.
        button = Button(controlFrame, text="Inspect Pic",
             padx = 10, width=15,bg="#FFFFFF", pady=5,
            command=lambda: self.inspect_pic(
                self.list.get(ACTIVE)))
        button.grid(row=0, sticky=E)

        self.b1 = Button(controlFrame, text="Color-Code",
            padx = 10, width=15,bg="#FFFFFF",pady=5,
            command=lambda: self.find_distance('CC','new'))
        self.b1.grid(row=1, sticky=E)

        b2 = Button(controlFrame, text="Intensity",
            padx = 10, width=15,bg="#FFFFFF",pady=5,
            command=lambda: self.find_distance('inten','new'))
        b2.grid(row=2, sticky=E)


        # Recalculating the Intersity and Color Code if needed
        #b3 = Button(controlFrame, text="reCalculate",
        #    padx = 10, width=15,bg="#FFFFFF",pady=5,
        #    command=lambda: PixInfo.reCalculate(pixInfo))
        #b3.grid(row=0, sticky=E)

        b4 = Button(controlFrame, text="Intensity + Color-Code",
            padx = 10, width=15,bg="#FFFFFF",pady=5,
            command=lambda: self.find_distance('both','new'))
        b4.grid(row=3, sticky=E)

        b5 = Button(controlFrame, text="Submit Feedback",
            padx = 10, width=15,bg="#FFFFFF",pady=5,
            command=lambda: self.find_distance('both','true'))
        b5.grid(row=4, sticky=E)

        # Layout Preview.
        self.selectImg = Label(previewFrame,
            image=self.photoList[0])
        self.selectImg.grid()

        # Set up initial GUI
        self.checkList = dict()
        self.resetChecklist()
        self.find_distance('inten','new')
    # Name: resetChecklist
    # Function: resets the checklist to be untick again
    def resetChecklist(self):
        for img in self.imageList:
            self.checkList[img.filename] = IntVar()
            self.checkList[img.filename].set(0)
    # Name: totalPage
    # Function: Get the total number of page
    def totalPage(self):
        total = len(self.photoList) / 15
        if len(self.photoList) != 0:
            total +=1
        return total

    # Name: nextPage
    # Function: Go to the next page
    def nextPage(self):
        # If it is the last page, go to the first page
        if self.currentPage +2  >= self.totalPage():
            self.currentPage=0

        else:
            self.currentPage +=1
        # Get the six image for the page
        begin = self.currentPage * 15
        end = begin + 15
        newImageList = self.currentImageList[begin:end]
        newPhotoList = self.currentPhotoList[begin:end]
        # Update the result frame
        self.update_results((newImageList,newPhotoList),'false')

    # Name: backPage
    # Function: Go to the previous page
    def backPage(self):
        # If it is the first page, do nothing
        if self.currentPage == 0:
            pass

        else:
            self.currentPage -=1
        # Get the six image for the page
        begin = self.currentPage * 15
        end = begin + 15
        newImageList = self.currentImageList[begin:end]
        newPhotoList = self.currentPhotoList[begin:end]
        # Update the result frame
        self.update_results((newImageList,newPhotoList),'false')


    # Name: update_preview
    # Function: Update preview fram
    def update_preview(self, event):

        i = self.list.curselection()[0]
        self.selectImg.configure(
            image=self.photoList[int(i)])

    # Name: selectedImage
    # Function: get selected image name
    def selectedImage(self):
        i = self.list.get(ACTIVE)
        return i

    # Name: getSelectedPosition
    # Function: get selected image position
    def getSelectedPosition(self,selected):
        selectedPosition = 0
        for i in range (len(self.imageList)):
             if selected == self.imageList[i].filename:
                 selectedPosition = i
        return selectedPosition

    # Name: calculateAverageVal
    # Function: calculate the number of pixel in a bin over the total pixel
    def calculateAverageVal(self,value,total):
        averageValue = float(value/total)
        return averageValue
    # Name:zeroStandardDeviation
    # Function: Handles the weight when the standard deviation is 0
    def zeroStandardDeviation(self,mean,standardDeviation):
        smallest = 100.0
        #Gets the smallest value
        for i in standardDeviation:
            if i == 0:
                pass
            else:
                if i< smallest:
                    smallest = i
        #If mean is 0 weight is 0
        if mean == 0:
            weight=0
        else:
            weight = float(1/(0.5 * smallest))
        return weight
    # Name:getAllWeight
    # Function: gets the weight of the bins
    def getAllWeight(self,status,bins):
        tempWeight =[]
        relevant = []
        averageCol = []
        standardDeviation = []
        selected = self.selectedImage()
        selectedPostion = self.getSelectedPosition(selected)
        #relevant.append(bins[selectedPostion])

        #If its initial, no bias weight is applied
        if status == 'noBias':
            for i in range(len(bins[selectedPostion])):
                tempWeight.append(1/89)
            return tempWeight
        else:
            #Get checked values
            for key,value in self.checkList.items():
                if value.get() == 1:
                    selectedPos = self.getSelectedPosition(key)
                    relevant.append(bins[selectedPos])
            w,h=len(relevant),89
            newBin = [[1 for x in range(w)] for y in range(h)]
            m=0
            print(len(relevant))
            #Inverts to find std and average
            for i in relevant:
                for j in range(len(i)):
                    newBin[j][m]=i[j]
                m+=1
            #Find the average
            for i in newBin:
                total=0
                for j in i:
                    total += float(j)
                average = float(total/len(relevant))

                averageCol.append(average)
            #Finds the standardDeviation
            for i in newBin:
                temp = i
                temp = list(map(float,temp))
                stddev = numpy.std(temp)
                standardDeviation.append(stddev)
            #Gets the weight
            for i in range (len(standardDeviation)):
                #If standardDeviation is zero
                if standardDeviation[i] == 0.0:
                    mean = averageCol[i]

                    weight = self.zeroStandardDeviation(mean,standardDeviation)

                    tempWeight.append(weight)
                else:
                    #Formula
                    weight = float(1/standardDeviation[i])
                    tempWeight.append(weight)
            totalWeight=0
            #Get total weight
            for i in tempWeight:
                totalWeight = i + totalWeight
            #Normalized the weights
            for i in range(len(tempWeight)):

                tempWeight[i] = tempWeight[i]/totalWeight

            return tempWeight


    # Name: find_distance
    # Function: Find the Manhattan Distance of each image and
    # sorting from the smallest to the biggest to update the
    # result frame
    def find_distance(self, method, RF):

        #Initializer
        totalPix = 0
        totalDistance = []
        imagesAndDistance = {}
        photosAndDistance ={}
        self.newImageList= []
        self.newPhotoList = []
        self.result =[]
        selected = self.selectedImage()
        selectedPostion = self.getSelectedPosition(selected)
        # Get the bins according to the method chosen
        if method == 'inten':
            bins = self.intenCode
            self.method = "Intensity Value"
        elif method == 'CC':
            bins = self.colorCode
            self.method ="Color Code"


        #If Intensity + Color Code is chosen
        if method =='both':
            self.method = "Intensity + Color-Code"
            bins = self.matrixNormalized
            #If its a feedback or a new query
            if RF == 'true':
                weight=self.getAllWeight("normalized",bins)
            else:
                #Resets the checklist
                self.resetChecklist()
                #Apply no bias weight
                weight=self.getAllWeight("noBias",bins)
            # Iterate through all 100 images
            for i in range(len(bins)):
                total=0
                if selectedPostion == i:
                    totalDistance.append(0)
                else:
                    for j in range (len(bins[i])):
                        #Get the total distance
                        Vi = float(bins[selectedPostion][j])
                        Vj = float(bins[i][j])
                        #Apply formula
                        dif = weight[j] * (abs(Vi-Vj))
                        total = dif +total
                    totalDistance.append(total)
        else:
            #Resets the checklist
            self.resetChecklist()
            #Apply no bias weight
            weight=self.getAllWeight("noBias",bins)
            for i in bins[selectedPostion]:
                totalPix = int(i) + totalPix
            # Iterate through all 100 images
            for j in range (len(bins)):
                total=0
                # If the same image distance is 0
                if selectedPostion == j:
                    totalDistance.append(0)
                else:
                    # Iterate through all 25 or 64 bins
                    for i in range(len(bins[j])):
                        averageSelected = self.calculateAverageVal(float(bins[selectedPostion][i]),totalPix)
                        averageCompare = self.calculateAverageVal(float(bins[j][i]),totalPix)
                        dif = abs(averageSelected - averageCompare)
                        total = total + dif


                    # Add the distance to the list
                    totalDistance.append(total)

        # Make a dictionary with fileName as the key
        for i in range (len(totalDistance)):
            imagesAndDistance.update({self.imageList[i].filename: totalDistance[i]})
            photosAndDistance.update({self.photoList[i]:totalDistance[i]})
        # sorts the distances
        test =sorted(imagesAndDistance.values())
        # write the sorted order
        for r in test:
            for keys in imagesAndDistance.keys():
                if imagesAndDistance[keys] == r:
                    self.result.append(self.getSelectedPosition(keys))

        # Make new image and photo list
        for order in self.result:
            # If same picture, don't show on the page

            self.newImageList.append(self.imageList[order])
            self.newPhotoList.append(self.photoList[order])

        # Updates the pages with the new data
        self.currentImageList = self.newImageList
        self.currentPhotoList = self.newPhotoList
        self.update_results((self.newImageList,self.newPhotoList),'true')


    # Name: update_results
    # Function: Update the results window with the results from find_distance
    def update_results(self, sortedTup,new):
        #Resets the page number
        if new == 'true':
            self.currentPage = 0
        selected = self.selectedImage()
        selectedPostion = self.getSelectedPosition(selected)

        # Print out the buttons and other components
        self.pageNumber.configure(text = "Page number " + str(self.currentPage+1))
        i = self.selectedImage()
        self.resultLabel.configure(text= self.method +" Result for " + i)
        self.resultLabel.grid(row =4, sticky = W, columnspan =2)
        #self.resultsScrollbar2.pack(side=RIGHT, fill=Y)
        self.pageNumber.grid(row=5,column=0,sticky=W)
        self.backButton.grid(row=5,column=1,sticky=W)
        self.nextButton.grid(row=5,column=1)

        # Define page size
        cols = 5
        row = 3
        fullsize = (0, 0, (self.xmax*cols), (self.ymax*row))

        # Initialize the canvas with dimensions equal to the
        # number of results.
        self.canvas2.delete(ALL)
        self.canvas2.config(
            width=self.xmax*cols,
            height=self.ymax*row,
            scrollregion=fullsize)
        self.canvas2.pack()
        self.resultsScrollbar2.config(command=self.canvas2.yview)

        # Put the images and photos in a list for placing the images to the buttons
        photoRemain = []
        for i in range(len(sortedTup[0])):
            fname = sortedTup[0][i].filename
            img = sortedTup[1][i]
            photoRemain.append((fname,img))

        rowPos = 0
        # Place images on canvas
        while photoRemain:

            photoRow = photoRemain[:cols]
            photoRemain = photoRemain[cols:]
            colPos = 0
            for (filename, img) in photoRow:

                pictureFrame = Frame(self.canvas2,bg=self.background,border=0)
                pictureFrame.pack()
                link = Button(pictureFrame, image=img,border=0,width=self.xmax-20,bg=self.background)
                handler = lambda f=filename: self.inspect_pic(f)
                link.config(command=handler)
                link.pack(side=LEFT, expand=YES)
                #Adds the checklist
                chkBtn = Checkbutton(pictureFrame,variable=self.checkList[filename],
                    bg=self.background,onvalue=1,offvalue=1)
                chkBtn.pack(side=BOTTOM)
                self.canvas2.create_window(
                    colPos,
                    rowPos,
                    anchor=NW,
                    window=pictureFrame,
                    width=self.xmax,
                    height=self.ymax)
                colPos += self.xmax

            rowPos += self.ymax

    # Name: inspect_pic
    # Function: Open the picture with the default operating system image
    # viewer.
    def inspect_pic(self, filename):
        os.startfile(filename)


# Executable section.
if __name__ == '__main__':

    root = Tk()
    root.title('Image Analysis Tool')

    pixInfo = PixInfo(root)

    imageViewer = ImageViewer(root, pixInfo)

    root.mainloop()
