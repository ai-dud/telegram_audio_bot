from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import discord
import time
from collections import deque
import pyperclip
import re

# Discord setup
DISCORD_TOKEN = "your discord token"
CHANNEL_ID = 1339913139096916010

# Setup all required intents
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

# Queue for storing emails
email_queue = deque()
is_processing = False

def enter_verification_code(driver, code):
    try:
        # Find all verification input boxes
        inputs = driver.find_elements(By.CSS_SELECTOR, "input.verify-input")
        
        # Enter each digit of the code
        for i, digit in enumerate(code):
            inputs[i].send_keys(digit)
            time.sleep(0.5)
            
        # Click Continue button after entering code
        continue_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.verify-email-button.default-btn"))
        )
        continue_button.click()
            
        print(f"✅ Verification code entered and continued")
        return True
    except Exception as e:
        print(f"❌ Error entering verification code: {str(e)}")
        return False

async def create_account(email, channel):
    global is_processing
    is_processing = True
    
    # Setup Chrome without headless mode
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')  # Just maximize window
    
    # Start browser
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # First get email from dropmail.me
        driver.get("https://dropmail.me/en/")
        wait = WebDriverWait(driver, 10)
        
        # Wait for 3 seconds for page to load properly
        time.sleep(2)
        
        # Copy email button
        copy_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.bi-clipboard.addr-tool.clipboard"))
        )
        copy_button.click()
        
        # Wait for clipboard to get email
        time.sleep(1)
        
        # Get email from clipboard
        temp_email = pyperclip.paste()
        
        # Open new tab for topmediai
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        
        # Go to topmediai website
        driver.get("https://www.topmediai.com/")
        
        # Wait for topmediai page to load properly
        time.sleep(3)
        wait = WebDriverWait(driver, 10)
        
        # Click login
        js_link = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='javascript:;']"))
        )
        js_link.click()
        
        # Click create account
        create_account = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.href-text"))
        )
        create_account.click()
        
        # Enter email
        email_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.sign-email"))
        )
        email_input.clear()
        email_input.send_keys(temp_email)  # Use the copied email
        
        # Enter password
        password_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.sign-password"))
        )
        password_input.clear()
        password_input.send_keys("xBymkE9u3wtSzfi")
        
        # Click create button
        create_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.creat-button.default-btn"))
        )
        create_button.click()
        
        # Switch back to dropmail tab
        driver.switch_to.window(driver.window_handles[0])
        
        # Wait for 9 seconds for email to arrive and load
        time.sleep(9)
        
        try:
            # Find pre element and get text
            pre_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "pre[data-bind*='linkifiedText']"))
            )
            email_text = pre_element.text
            
            # Send the text to Discord
            await channel.send(email_text)
            
            # Wait for verification code from Discord
            verification_code = None
            max_attempts = 60  # Wait up to 60 seconds
            
            while verification_code is None and max_attempts > 0:
                time.sleep(2)
                max_attempts -= 1
                
                async for message in channel.history(limit=5):
                    if message.author != client.user:  # Check if message is not from bot
                        content = message.content.strip()
                        if content.isdigit() and len(content) == 6:
                            verification_code = content
                            await channel.send(f"✅ Got verification code: {verification_code}")
                            break
            
            if verification_code is None:
                await channel.send("❌ Timeout waiting for verification code")
                return False
            
            # Switch back to topmediai tab
            driver.switch_to.window(driver.window_handles[1])
            
            # Enter verification code
            time.sleep(1)
            enter_verification_code(driver, verification_code)
            
            # Wait for 3 seconds after entering verification code
            time.sleep(3)
            
            # After verification code and continue button
            print(f"✅ Account created for: {email}")
            
            # Wait for 3 seconds after account creation
            time.sleep(3)
            
            # Click on API menu
            api_menu = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.menu-list.tts-api"))
            )
            api_menu.click()
            
            # Wait for 2 seconds for menu to open
            time.sleep(2)
            
            # Click on AI Music Generator API
            music_api = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.item-title.flexible a[href='/api/ai-music-generator-api/']"))
            )
            time.sleep(1)
            music_api.click()
            
            # Wait for new tab to open and switch to it
            time.sleep(2)
            new_tab = driver.window_handles[-1]
            driver.switch_to.window(new_tab)
            
            # Wait for page to load in new tab
            time.sleep(4)
            
            # Wait and click on Get API Key button
            get_api_key = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.base-bt.get-api-key[href='javascript:;']"))
            )
            time.sleep(2)
            get_api_key.click()
            
            # Wait for 2 seconds
            time.sleep(2)
            
            # Click on Copy API Key button
            copy_button = wait.until(
                EC.element_to_be_clickable((By.TAG_NAME, "button"))
            )
            copy_button.click()
            
            # Wait for clipboard content
            time.sleep(1)
            api_key = pyperclip.paste()
            
            # Send API key to Discord with specific format
            if api_key:
                clean_api_key = api_key.strip()
                formatted_message = f"API Key: {clean_api_key}"
                await channel.send(formatted_message)
            else:
                await channel.send("Could not get API key")
            
            is_processing = False
            
            # Process next email if any in queue
            if email_queue:
                next_email = email_queue.popleft()
                await create_account(next_email, channel)
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            await channel.send(f"❌ Error in process: {str(e)}")
            is_processing = False
            return False
    finally:
        time.sleep(2)
        driver.quit()

@client.event
async def on_ready():
    print(f'🤖 Bot is ready: {client.user}')
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🟢 Bot is online and waiting for emails...")

@client.event
async def on_message(message):
    global is_processing
    
    if message.author == client.user:
        return
        
    if message.channel.id != CHANNEL_ID:
        return
    
    content = message.content.strip().lower()  # Convert to lowercase for case-insensitive check
    
    # Only start process if message is "hello"
    if content == "hello":
        if not is_processing:
            try:
                # First get email from dropmail.me
                await create_account(None, message.channel)
            except Exception as e:
                await message.channel.send(f"❌ Error creating account: {str(e)}")
        else:
            await message.channel.send("⏳ Already processing, please wait...")

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
