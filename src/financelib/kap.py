# Import necessary libraries
import time, os
import random
import requests

from financelib.settings import driver
from financelib.utils import today
class KAP:
  """
    KAP class to download PDF files and for many other services
    from the KAP website.
  """
  def __init__(self):
    """
      Initialize the KAP class
    """
  def download_pdfs_via_date_ranges(
      self, date_from = today, date_to = today, desired_path = ""):

    desired_path = desired_path + '/' if desired_path[-1] != '/' and desired_path != '' else desired_path
    randint = random.randint(10000000000, 99999999999)  # Random integer for the API URL
    api = f'https://www.kap.org.tr/tr/api/disclosures?ts={randint}&fromDate={date_from}&toDate={date_to}'  # API URL
    r = requests.get(api).json()  # Index should be adjusted according to the desired API URL

    # Extract necessary data from JSON
    basic = [item["basic"] for item in r]
    disclosure_indexes = [item["disclosureIndex"] for item in basic]
    company_codes = [item["stockCodes"] for item in basic]
    titles = [item["title"] for item in basic]

    # Create PDF URLs and download PDFs
    if not os.path.exists(desired_path):
      os.mkdir(desired_path)
      print(f"Directory {desired_path} created.")

    print("Downloading PDFs...")

    for i in range(0, len(basic)):
      pdf_url = f"https://www.kap.org.tr/tr/BildirimPdf/{disclosure_indexes[i]}"

      # Download the PDF file
      response = requests.get(pdf_url)
      if response.status_code == 200:

        pdf_file_path = f"{desired_path}{company_codes[i]}-{titles[i].replace('/', '-')}-{disclosure_indexes[i]}.pdf"

        # Write it to a PDF file
        with open(pdf_file_path, "wb") as pdf_file:
          pdf_file.write(response.content)

        print(f"PDF downloaded and saved to {pdf_file_path}")
      time.sleep(15)  # Wait for a while to avoid overloading the server

  def download_pdf_via_disclosure_no(self, disclosure_no: int, desired_path=''):
    """
      Download PDF files from the KAP website.
    """

    desired_path = desired_path + '/' if desired_path[-1] != '/' and desired_path != '' else desired_path
    # Go to the page URL
    time.sleep(5)  # Wait for the page to load

    pdf_url = f"https://www.kap.org.tr/tr/BildirimPdf/{disclosure_no}"

    response = requests.get(pdf_url)
    if response.status_code == 200:
      # Create desktop path and file name to save the file
      pdf_file_path = f"{desired_path}{disclosure_no}.pdf"

      # Write the PDF file
      with open(pdf_file_path, "wb") as pdf_file:
        pdf_file.write(response.content)

      print(f"PDF downloaded and saved to {pdf_file_path}")

      time.sleep(15)  # Wait to avoid overloading the server

    print("All PDFs have been downloaded.")

# Test the KAP class
if __name__ == "__main__":
  kap = KAP()
  kap.download_pdfs_via_date_ranges(date_from="2025-01-01", date_to="2025-01-21", desired_path="pdfs")
