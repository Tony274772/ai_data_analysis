import pandas as pd
import io
import re

# This script cleans the malformed web-archive file into a proper CSV
with open('Nykaa Digital Marketing.csv', 'rb') as f:
    content = f.read().decode('utf-8', errors='ignore')

match = re.search(r'<pre[^>]*>(.*?)</pre>', content, re.DOTALL)
if match:
    csv_data = match.group(1).strip()
    df = pd.read_csv(io.StringIO(csv_data))
    # Save the proper version
    df.to_csv('cleaned_nykaa_data.csv', index=False)
    print("Success! Created cleaned_nykaa_data.csv")
else:
    print("Could not find CSV data in the file.")