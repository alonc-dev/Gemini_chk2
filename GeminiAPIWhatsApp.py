import google.generativeai as genai
import os
import apikey

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


###############################################
# ask gemini
###############################################
def generate_text(prompt: str):
    """Generates text using the Gemini API."""
    try:
         response = model.generate_content(prompt)
    except Exception as e:
        return f"An error occurred: {e}"
    return response.text

###############################################
# this module save the answer to avoid reask gemini
###############################################
def generate_text_with_cache(request: str) -> str:
    gemini_cache = None
    if request not in gemini_cache:
        try:
            response = model.generate_content(request)
        except Exception as e:
            return f"An error occurred: {e}"
        gemini_cache[request]=response.text
        # todo: save cache to file
    return gemini_cache[request]


###############################################
def generate_content_with_images(prompt, image_paths):
    """Generates content using text and images."""
    try:
        contents = [prompt]
        for image_path in image_paths:
            with open(image_path, "rb") as image_file:
                contents.append({"mime_type": "image/jpeg", "data": image_file.read()}) #Assuming jpeg images. you may need to change mime type.
        response = model.generate_content(contents)
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"




###############################################
def read_whatsapp_messages(contact_name):
    """
    Reads the latest messages from a specific contact on WhatsApp Web.

    Args:
        contact_name: The name of the contact to read messages from.

    Returns:
        A list of messages (strings), or None if an error occurred.
    """
    try:
        chrome_options = Options()
        #chrome_options.add_argument("--headless") # Uncomment for headless mode (no browser window)
        driver = webdriver.Chrome(options=chrome_options) # Ensure chromedriver is in your PATH

        driver.get("https://web.whatsapp.com/")

        # Wait for the QR code to be scanned and the page to load
        input("Scan the QR code and press Enter when WhatsApp Web is loaded...") # Replace with more robust wait if needed.

        # Find the search bar and search for the contact
        search_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        search_box.clear()
        search_box.send_keys(contact_name)

        # Wait for the contact to appear and click on it
        contact = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, f'//span[@title="{contact_name}"]'))
        )
        contact.click()

        # Wait for the chat to load
        time.sleep(2) # adjust as needed

        # Find all message elements
        message_elements = driver.find_elements(By.CSS_SELECTOR, 'div.message-in, div.message-out')

        messages = []
        for message_element in message_elements:
            try:
                message_text_element = message_element.find_element(By.CSS_SELECTOR, 'span.selectable-text')
                message_text = message_text_element.text
                messages.append(message_text)
            except:
                # Handle cases where messages have media, etc.
                pass

        return messages

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        try:
            driver.quit() #close the browser even on error.
        except:
            pass #if driver never existed.


###############################################
def check_for_activity():

    question = """ I am training at the gym. I just did a set of benchpress GYM_ACTIVITY,
    write the activity, weight as float number, unit as string, reps as integer, sets as integer values 
    for each of the follow activity seperate by comma.
    if the activity has multiple sets,duplicate the result per set.
    if there are multiple activities, split them to different results.
    result format each result different line: add_activity("activity", weight, "unit", reps, sets).
    """
   
    arr = ("I just did a set of benchpress, it was a personal record at 100 kilos, I managed to do only 2 though",
              "I just did 8 reps of leg curls at 120 lbs.",
              "Just completed 3 sets of lateral pull downs, each was 8 repetitions of 60 kg.",
              "Completed my superset squat at 100, 110 and 120kg. The first 2 sets I did 8 reps and only 6 in the last.")


    for txt in arr:
        prompt = f'{question}\n GYM_ACTIVITY: {txt}'
        #print(prompt)
        answer = generate_text(prompt)
        my_funs_arr = answer.split("\n")
        for my_fun in my_funs_arr:
            if my_fun.startswith("add_activity"):
                print(my_fun)
                eval(my_fun)


###############################################

def add_activity(activity, weight, unit, reps, sets):
    print(f"** add_activity('{activity}', {weight}, '{unit}', {reps}, {sets})")

###############################################

def main():
    print("----- generate_content ------")
    print("-- Start --")
    check_for_activity()
    #result_image = generate_content_with_images("Describe the images.", ["bonnie.jpg"])
    #print("\nImage Description:\n", result_image)
    print("-- End --")

    contact_name = "Test"  # Replace with the actual contact name
    messages = read_whatsapp_messages(contact_name)

    if messages:
        print(f"Messages from {contact_name}:")
        for message in messages:
            print(message)



###############################################
if __name__ == "__main__":
    genai.configure(api_key=apikey.GEMINI_API_KEY)
    print("----- get model ------")
    model_name = "gemini-1.5-flash"  # Or "gemini-pro-vision" for multimodal.
    safety_settings = [
        {
            "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        },
        {
            "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            "threshold": genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        },
    ]
    safety_settings=None
    model = genai.GenerativeModel(model_name, safety_settings=safety_settings)


    print("----- main ------")
    main()
