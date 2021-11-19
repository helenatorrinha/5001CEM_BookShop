import os
from werkzeug.utils import secure_filename

def upload_file(picture, uploadfolder):
    # check if the post request has the file part
    #https://stackoverflow.com/questions/44926465/upload-image-in-flask
    if 'picture' not in picture:
        return False
    file = picture['picture']
    filename = secure_filename(file.filename)
    path = os.path.join(uploadfolder, filename)
    file.save(path)
    return filename

def remove_picture(uploadfolder, picture): #function to delete a book picture from the db through the path
    #https://stackoverflow.com/questions/26647248/how-to-delete-files-from-the-server-with-flask
    print(uploadfolder)
    print(picture)
    os.remove(os.path.join(picture, uploadfolder))


    