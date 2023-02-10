import ezgmail,os
image_data=[]
for file in os.listdir("images2"):
    image_data.append(f'images2/{file}')

ezgmail.send('anikethvij464@gmail.com','test','testing whether an empty folder would work',attachments=image_data)
print("SENT")