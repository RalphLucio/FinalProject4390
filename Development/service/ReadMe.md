1. What if there is no database?!
    In `app.py` in lines 15-27, when the file is run it will create a new database called "image-database.db" based off the blueprints of `schema.sql`

2. There's multiple databases!
    Delete them both if its an issue.

3. Why does `create_app()` in `app.py` look like that?
    There was multiple problems being that some functions in `app.py` we're deprecated and thus caused issues
    Line 49-50 was originally run_before_first_request which is valid its just deprecated so this was the work around. Amongst other things.

4. What's in the database? I click it and it says "The file is not displayed in the text editor because it is either binary or uses an unsupported text encoding."
    Use DB browser -> https://sqlitebrowser.org/dl/
    When software open:
    1. Open database
    2. Find "image-database.db" in the project and select it
    3. Browse data
    4. Table: images

5. Which files are people allowed to upload
    `app.py` line 35

6. Give me the basic run down of `app.py`
    1. It opens the database, or creates one then opens it if there isnt one
    2. The end-user goes to website and uploads an image via `POST`
    3. The file upon recieving it, has its path (directory to that image specifically) written down
    4. We get the file that the path shows (the image) and hash it.
        Note: When we receive the file its temporarily stored in `Development\service\images\uploads`. One at a time.
    5. With the hash we see if it A. Already exists and B. Has a successful prediction already 
    6. We upload that file to the Google bucket using Google Cloud API
        Note: All you have to do is tell it where the file you want to upload is, and the name you want it to be when its there
    7. We store all the information we have so far in the database.
        Note: Thats, the name it originally was (NOT UNIQUE), the hash name its called in the bucket (UNIQUE), the URL that leads back to the image
        Note 2: The URL (EXAMPLE: https://storage.cloud.google.com/mediscan-images/2eb8b5bd51bc9bdd910d1d2f34a1932e.jpg) can only be seen through API requests. You NEED credentials. The ease of use is in the works.
    8. We send the image to tensorflow serving where it comes back with a prediction
        Note: The image is prepped, if need be, here. That means stuff like turning it into 224x224. `tfServe.py`
    9. We delete the file that was in `Development\service\images\uploads`
    10. We display the results

7. What is `meditensor-2178cd54ff6e.json`?
    Its a special API key for Google API permissions.

8. Why do we have `meditensor-2178cd54ff6e.json`?
    We have a Google Bucket (a database for SPECIFICALLY files, images in this case)
    That database is not public.
    It can only be accessed by people with permission.
    That JSON is the key that gives THIS program the permission to access that database.
    If you leak that key, people can screw with our database.
    Fun fact: GitHub will block you from uploading it.

9. So how do we share `meditensor-2178cd54ff6e.json`?
    Discord.
    If you don't have it just ask.

10. What does our database intend to hold?
    1. ID: An automatically assigned id
    2. Name: The original name of the uploaded file, [NOT UNIQUE]
    3. Hash: The hash name conveted from the file NOT THE NAME, [UNIQUE], uploading the same picture, despite having different names will generate the same hash, and thus crash the website
    4. URL: A url that leads back to the given image inside the database. So you can reference it later in HTML/JSX
    5. Predicted: A bool of whether this image has successfully predicted on TensorFlow. For later use if need be.
    6. Cancer_pred: A float the will hold the prediction it recieved back from TensorFlow

11. "I need more attributes than our table `images` has"
    1. Delete the current database
    2. Wipe the Google Bucket
    3. Adjust `schema.sql` to your needs
    4. run `app.py` and it'll automatically create the db from the blueprints of `schema.sql`

12. How do I see the Google Bucket and whats on it?
    You need permissions.
    Send me your email on discord saying something like 'I need access to the Google Bucket' and I'll get to it.
    Unless you just want to ask me whats in it. That's easy.

13. What images do I use for testing?
    `Development\service\images\Benign`
    or `Development\service\images\Malignant`
    Note: Unless you mean to I'd comment out the upload to Google bucket when testing unless you mean to
    and if you upload the same image twice they db wont let you.

14. Can we upload multiple images at the same time?
    Right now? No.

15. Why have the hash system?
    It'll save us computation resources because if somebody spams the same picture over and over it'll just show
    the past information from the database.
    Note: With the way hashes work I believe. It is "technically" a whole new picture of they change so much as one pixel on their image.
    However, that is not common knowledge.

## PERSONAL PARTS
1. When we get the prediction back its on a 1.0 scale therefor 1.0 implies it is 100% sure the image you sent has cancer
    that sounds so sketchy so instead I say on the JSX end we turn 1.0 into scales by having it say something like "confident"
2. Good news. When you upload the same image with the same hash to google buckets nothing happens.