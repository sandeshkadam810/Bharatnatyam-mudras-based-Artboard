# <script async src="https://cse.google.com/cse.js?cx=43a0ec294cd7645f4">
# </script>
# <div class="gcse-search"></div>

# cx-43a0ec294cd7645f4
# key-AIzaSyBBVV25lG55K6Sgu5Dm-7lb6qSUDfVuexk

from google_images_search import GoogleImagesSearch

# Your API key and CX (search engine ID)
api_key = 'AIzaSyBBVV25lG55K6Sgu5Dm-7lb6qSUDfVuexk'
cx = '43a0ec294cd7645f4'

# Initialize GoogleImagesSearch with your credentials
gis = GoogleImagesSearch(api_key, cx)

# Set search parameters
search_params = {
    'q': 'bharatanatyam rudra',
    'num': 50,  # Number of images to fetch
    'safe': 'off',  # Turn off SafeSearch
    'fileType': 'jpg',  # Only fetch jpg images
    'imgType': 'photo',  # Only fetch photos
    'imgSize': 'large',  # Large images
}

# Perform the search and check if results are returned
gis.search(search_params=search_params)

# Check if results are being fetched
if gis.results():
    print(f"Found {len(gis.results())} images")
    # Download images to a specific directory
    for index, image in enumerate(gis.results()):
        print(f"Downloading image {index + 1}: {image.url}")
        image.download(r'C:\Users\SANDESH\Desktop\ipcv_cp\folder')  # Adjust the folder path as per your OS
else:
    print("No images found")