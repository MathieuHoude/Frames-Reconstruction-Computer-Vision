from PIL import Image

img= Image.open('/home/mathieuhoude/source/MathieuHoude/SmartJourneyWeek9/frames/0465fe17-5ebc-459e-94a7-85e80f7e12b8.jpg')  
# img = img.crop((1735, 26, 1892, 81))
img = img.crop((1764.0, 15.0, 1925.0, 97.0))
img.save('./sample_cropped.jpg')