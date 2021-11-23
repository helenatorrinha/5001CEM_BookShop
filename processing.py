import os
from werkzeug.utils import secure_filename

def upload_file(files, uploadfolder):     # check if the post request has the file part
    #code based on https://stackoverflow.com/questions/44926465/upload-image-in-flask
    if 'picture' not in files:        #if picture doesn't exist
        return False
    file = files['picture']       #gets the picture from the request files
    filename = secure_filename(file.filename)       
    path = os.path.join(uploadfolder, filename)     #creates the picture path
    file.save(path)     #saves the picture
    return filename

def remove_picture(uploadfolder, picture): #function to delete a book picture from the db through the path
    #code based on https://stackoverflow.com/questions/26647248/how-to-delete-files-from-the-server-with-flask
    os.remove(os.path.join(picture, uploadfolder))


    