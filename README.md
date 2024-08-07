# 5001CEM Software Engineering - BookShop
This project belongs to Helena Torrinha for the 5001CEM module. 
This code aims to simulate a book shop where the customers can see the available books and buy them 
and administrators can change their quantity and add new ones.

From the GitHub repository download the zip with the files and unzip it to the destination folder. 
In the terminal do sudo apt update Do cd into the directory where the project is and do sudo apt-get install python3-venv 
Then do python3 -m venv venv 
Then activate the venv virtual environment by doing . venv/bin/activate 
You should get something like this but with a different box name: https://micro-corner-5000.codio-box.uk 
Then do pip install Flask And do pip install Flask-SQLALchemy 
And finally do pip install flask-cors 
And the project is setup so now, every time you want to run the project you just need to 
cd into the directory where the project is, 
do . venv/bin/activate (if you just setup the project, you don’t need to do these two steps), 
export the file you want to run (in this case main.py) by doing export FLASK_APP=main.py 
and then run it with flask run --host=0.0.0.0

To see the website running check your project box info and change the URL to port 5000 (e.g. https://micro-corner-5000.codio-box.uk)
