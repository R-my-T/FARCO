# FARCO - An attendance system using facial recognition

Farco which stands for **FA**cial **R**e**CO**gnition is a web application that runs on any computer with a webcam and helps organisations manage the attendance of their employees/students/workers etc in an easier and more efficient way! Register your organisation and let FARCO take care of all the hard work for you.<br/><br/>
![farco1](https://user-images.githubusercontent.com/88109466/170859242-3ccc6f0b-5363-46e4-a5f8-2863cd5f3c15.png)

## Requirements
conda 4.10.3<br/>
Python 3.6.13 :: Anaconda, Inc.<br/>
cmake version 3.22.1<br/>
dlib version: 19.22.0<br/>
numpy version: 1.19.5<br/>
OpenCV version: 4.5.5<br/>
face-recognition version: 1.3.0<br/>
passlib version: 1.7.4<br/>
Flask-Session version: 0.4.0<br/>
pandas version: 1.1.5<br/>

## What does this repository contain?

1. **CSV_Input_files** : A folder where farco saves the csv files and reads from it. It also deletes the csv file after reading.
2. **Face_Imgs** : A folder where all the input images given by the user will be stored.
3. **flask_session** : A folder required by flask sessions to run and manage the app's sessions.
4. **Sample_Inputs** : A folder which you can utilise to check out the functionalities of FARCO. It contains the images and the csv file that you can upload to Farco and also has test images that you can test the attendance system with stored in the folder 'Test_Imgs'.
5. **static** : A folder which contains the stylesheets and the stock images that are used in the website.
6. **templates** : A folder which contains all the html pages that flask renders.
7. **attendance.db** : The database where all the user informations are stored.
8. **Main.py** : A python file which contains the server code.
9. **virtualenv** : An anaconda python virtual environment which has all the dependencies and libraries installed.

## How to run FARCO in your system?

1. Create a folder and clone this repository.
2. Open Anaconda Prompt (anaconda3) by searching for the same in the search bar and type
```bash1
conda info
```
3. Note down the first path from the list of the virtual environment paths shown under the heading 'envs directories'. It should look something like this:
```bash1
envs directories : C:\Users\T__Ra\anaconda3\envs
```
4. Copy the virtualenv folder given in this repository and navigate to the above found file path and paste it there.
5. In the anaconda prompt type
```bash1
conda activate virtualenv
```
6. The virtualenv should be running now. You can check if its running or not by looking at the starting of the line where (base) would have turned into (virtualenv).<br/> 
![conda activate](https://user-images.githubusercontent.com/88109466/170859448-1e34c0ca-16f0-4ae3-ab33-9499477347ba.png)<br/>

7. Now that you have ensured that the provided virtaulenv is running navigate to the folder where this repository is stored and type:
```bash1
python Main.py
```
8. The python program will execute and provide you with the url for the local host which you would have to copy and paste in a web browser to see Farco up and running!<br/> 
![output](https://user-images.githubusercontent.com/88109466/170859486-1d7461d3-32a7-4b7a-b15f-d0bffc71d45c.png)<br/>

_Note: Kindly use **only anaconda prompt to activate this virtual environtment** to avoid any unexpected errors. If there are any errors such as a package missing etc., use pip install package-name to fix it. If you wish to use a different virtual environment kindly make sure all the above mentioned requirements are installed in it._
## Tech stack used
<p align="left">
<img height="32" width="32" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/python/python.png">
<img height="32" width="32" src="https://i.ibb.co/bzZKwJ8/sqlite.png"> <img height="32" width="32" src="https://instructobit.com/static/posts/111/ECHUS82IWZWS55YQOLWQD8PM1NKIM5WQLPNAXF1VF3P5526CDQ.jpg" > <img height="32" width="32" src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/OpenCV_Logo_with_text_svg_version.svg/1200px-OpenCV_Logo_with_text_svg_version.svg.png" > <img height="32" width="32" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/javascript/javascript.png" > <img height="32" width="32" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/html/html.png" > <img height="32" width="32" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/bootstrap/bootstrap.png" > <img height="32" width="32" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/css/css.png" >
</p>
## Features
-  Extremely flexible and versatile platform that can be used by any type of organisation.
- Adding information and registering is very simple and does not require user to manually enter each and every field.
- Lets the user choose how long the attendance system should capture attendance for.
- Lets employees or students view their attendance record without having to create an account.
