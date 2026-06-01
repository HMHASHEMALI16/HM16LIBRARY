import json
import os
import urllib.parse

print("Starting JSON API generation...")
books_api_data = []

# ফোল্ডারের সব .epub ফাইল খুঁজে বের করা
for filename in os.listdir('.'):
    if filename.endswith('.epub'):
        # নাম থেকে .epub এক্সটেনশন বাদ দেওয়া
        name_without_ext = filename.replace('.epub', '')
        
        # _-_ দিয়ে বইয়ের নাম এবং লেখকের নাম আলাদা করা
        parts = name_without_ext.split('_-_')
        title = parts[0].replace('_', ' ')
        author = parts[1].replace('_', ' ') if len(parts) > 1 else "অজানা"
        
        # বাংলা নামের কারণে লিংক যেন ভেঙে না যায়, তাই URL Encode করা
        encoded_filename = urllib.parse.quote(filename)
        download_url = f"https://hmhashemali16.github.io/OPDS/{encoded_filename}"
        
        book_info = {
            "title": title,
            "author": author,
            "file_name": filename,
            "format": "epub",
            "download_link": download_url
        }
        books_api_data.append(book_info)

# api ফোল্ডার তৈরি করা
os.makedirs('api', exist_ok=True)

# books.json ফাইলে ডেটা সেভ করা
with open('api/books.json', 'w', encoding='utf-8') as json_file:
    json.dump(books_api_data, json_file, ensure_ascii=False, indent=4)

print("Success: JSON API created at api/books.json")
