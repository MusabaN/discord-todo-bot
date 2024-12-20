import re
import glob
import pytesseract
from PIL import Image
import urllib.parse
from datetime import datetime
from llama_cpp import Llama
import os

def image_to_text(image_path):
    """Extract text from an image using pytesseract."""
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, config='--oem 1')
    return text

def extract_event_details(prompt_text):

    llm = Llama.from_pretrained(
        repo_id="Qwen/Qwen2.5-3B-Instruct-GGUF",
        filename="qwen2.5-3b-instruct-q2_k.gguf",
        verbose=False
    )

    instruction = (
        "You are an assistant that extracts an event's date, start time, and end time from text. "
        "Ensure the output is a JSON object in exactly the following format:\n"
        "{'date': 'YYYY-MM-DD', 'start_time': 'HH:MM', 'end_time': 'HH:MM'}\n"
        "The 'date' must follow the ISO 8601 format (e.g., 'YYYY-MM-DD'). "
        "The 'start_time' and 'end_time' must use 24-hour notation (e.g., 'HH:MM'). "
        "The date in the text is formatted as 'DD.MM.YYYY and the times are formatted as 'HH.MM'."
        "Be sure the start_time and end_time use : to seperate hours and minutes.\n"
        "Do not include seconds or any additional information.\n"
        "Your response should consist solely of the JSON object, with no extra text or explanations."
        "An example of a valid response is {'date': '2022-12-31', 'start_time': '14:00', 'end_time': '16:00'}"
        "DO NOT convert the hours and minutes to any other timezone."
    )

    response = llm.create_chat_completion(
        messages = [
            {
                "role": "user",
                "content": f"{instruction}\n{prompt_text}"
            }
        ],
        response_format={"type": "json_object"},
    )

    print("-------------RESPONSE-------------------")
    print(response)
    print("----------------------------------------")


    return response['choices'][0]['message']['content']


def generate_google_cal_url_extension(event_details):
    """Generate a Google Calendar URL extension from event details, correcting potential format issues."""
    
    # Extract and clean date, start time, and end time
    date = event_details['date'].strip()
    start_time = event_details['start_time'].strip().replace('.', ':')
    end_time = event_details['end_time'].strip().replace('.', ':')

    # Convert date from DD.MM.YYYY to YYYY-MM-DD
    date_parts = date.split('.')
    iso_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"

    # Parse date and times into datetime objects
    start_dt = datetime.strptime(f"{iso_date} {start_time}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{iso_date} {end_time}", "%Y-%m-%d %H:%M")

    # Format for Google Calendar
    start_str = start_dt.strftime("%Y%m%dT%H%M%S")
    end_str = end_dt.strftime("%Y%m%dT%H%M%S")

    query_params = {
        'action': 'TEMPLATE',
        'text': 'Bandøving',  # Modify as needed for event titles
        'dates': f"{start_str}/{end_str}",
    }

    return urllib.parse.urlencode(query_params)

def get_participants():
    """Create a string of participants for the Google Calendar URL."""
    participants = os.getenv('PARTICIPANTS', None)
    return f"&add={participants}" if participants != None else ''

def create_event_url(image):
    """Extract text from an image, parse event details, and generate a Google Calendar URL."""
    text = image_to_text(image)
    event_details = regex_event_to_dictionary(text)
    event_url_extension = generate_google_cal_url_extension(event_details)
    base_url = "https://calendar.google.com/calendar/render?"
    participants = get_participants()
    return base_url + event_url_extension + participants


def regex_event_to_dictionary(text):
    """Extract event details from text using regex."""
    date = regex_date(text)
    times = regex_time(text).split('-')
    return {'date': date, 'start_time': times[0], 'end_time': times[1]}

def regex_date(text):
    """Extract date from text using regex."""
    date = re.search(r'\d{2}\.\d{2}\.\d{4}', text)
    return date.group() if date else None

def regex_time(text):
    """Extract time range from text using regex."""
    match = re.search(r'\b(\d{2}\.\d{2})\s*-\s*(\d{2}\.\d{2})\b', text)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None

def main():
    # for digit in range(8):
    #     image_path = glob.glob(f'./test/ovelse/skjermbilde{digit}.*')
    #     if image_path:
    #         text = image_to_text(image_path[0])
    #         print(f'\n\n---------- TEXT FROM IMAGE {digit} ------------')
    #         date = regex_date(text)
    #         time = regex_time(text)
    #         # print(text)
    #         print("---------- DATE ------------")
    #         print(date)
    #         print("---------- TIME ------------")
    #         print(time)
    #     else:
    #         print(f'No image found for digit {digit}')

    image_path = glob.glob(f'./test/ovelse/skjermbilde0.*')[0]
    text = image_to_text(image_path)

    # Extract event details from text
    event_details = regex_event_to_dictionary(text)

    print(event_details)
    
    # Generate the URL extension
    event_url_extension = generate_google_cal_url_extension(event_details)

    # Construct the full Google Calendar URL
    base_url = "https://calendar.google.com/calendar/render?"
    participants = get_participants()
    calendar_link = base_url + event_url_extension + participants

    print(calendar_link)

if __name__ == '__main__':
    main()