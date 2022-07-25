from PIL import Image

img= Image.open('/home/mathieuhoude/source/SmartJourneyWeek9/frames/afed0773-770f-40c1-8ee8-64db8c147507.jpg')  
# img = img.crop((1735, 26, 1892, 81))
img = img.crop((1138.0, 16.0 - 10, 1202.0, 85.0 + 10))
img.save('./sample_cropped.jpg')