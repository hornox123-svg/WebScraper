import sys
import requests
import asyncio
from crawl import *
from json_report import write_json_report

async def main():
    arguments = sys.argv
    if len(arguments) < 4:
        print("no website provided")
        sys.exit(1)
    elif len(arguments) > 4:
        print("too many arguments provided")
        sys.exit(1)
    BASE_URL = sys.argv[1]
    max_conc = int(sys.argv[2])
    max_pages = int(sys.argv[3])

    print(f'starting crawl of: {BASE_URL}')
    page_data = await crawl_site_async(BASE_URL, max_conc, max_pages)
    pages = list(page_data.keys())

    write_json_report(page_data)

    '''print('\n#===========================#\n')
    print(f'\n# of pages: {len(pages)}\n')
    for page in pages:
        print('\n#===========================#\n')
        print(f'\nFirst Paragraph of {page}:\n\t{page_data[page]['first_paragraph']}\n')'''





if __name__ == "__main__":
    asyncio.run(main())
