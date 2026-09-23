| :warning: WARNING           |
|:----------------------------|
| This project was done with the help of AI coding agents.     |

# Simple Amazon Invoice Downloader

A Python script that automatically downloads Amazon.de invoices using browser automation. The script logs into your Amazon account, navigates through your order history, and downloads all available invoice PDFs for a specified time period.

## Features

- 🤖 **Automated Login**: Logs into Amazon.de using your credentials
- 🔑 **Manual Login**: Without credentials, you log in yourself in the browser window (works with 2FA)
- 📅 **Date Range Filtering**: Downloads invoices for a specific year (defaults to current year)
- 📄 **PDF Download**: Automatically downloads all available invoice PDFs
- 🗂️ **Organized Storage**: Saves files with descriptive names including date, amount, and order ID
- 🔒 **Secure**: Uses environment variables for credentials
- 🕐 **Human-like Behavior**: Includes random delays to avoid detection

## Prerequisites

- Python 3.7 or higher
- A German Amazon account (amazon.de)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/apvlv/simple-amazon-invoice-downloader.git
cd simple-amazon-invoice-downloader
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

4. Optional: create a `.env` file with your Amazon credentials. If you leave out `AMAZON_EMAIL` and `AMAZON_PASSWORD`, you log in manually in the browser window instead:
```env
AMAZON_EMAIL=your_email@example.com
AMAZON_PASSWORD=your_password
DOWNLOAD_DIR=./downloads
```

## Usage

Run the script, optionally with the year you want to download (defaults to the current year):

```bash
python az_dl.py        # current year
python az_dl.py 2023   # all invoices from 2023
```

The script will:
1. Open a browser window
2. Navigate to Amazon.de
3. Log in with your credentials, or wait until you have logged in manually
4. Go to your order history
5. Download all invoices from the selected year
6. Save them to the downloads directory

## Configuration

### Environment Variables

- `AMAZON_EMAIL`: Your Amazon login email
- `AMAZON_PASSWORD`: Your Amazon password
- `DOWNLOAD_DIR`: Directory to save downloaded invoices (default: `./downloads`)

### File Naming Convention

Downloaded files are named with the following pattern:
```
YYYYMMDD_amount_amazon_orderid_###.pdf
```

Example: `20250817_2469_amazon_123-4567890-1234567_001.pdf`

## Important Notes

### Security
- Never commit your `.env` file to version control
- Keep your Amazon credentials secure
- The script uses your actual Amazon account, so use responsibly

### Rate Limiting
- The script includes random delays between 2-5 seconds to mimic human behavior
- This helps avoid triggering Amazon's bot detection systems

### Browser Behavior
- The script runs in non-headless mode so you can see what's happening
- You may need to solve CAPTCHAs manually if they appear
- The browser window will close automatically when finished

## Troubleshooting

### Common Issues

**"Could not find orders page link"**
- Amazon's page structure may have changed
- Try manually navigating to your orders page when the browser opens

**"Keep me logged in checkbox not found"**
- This is normal and won't affect functionality
- The script continues without checking this box

**Login Issues**
- Verify your credentials in the `.env` file
- If two-factor authentication is enabled, use manual login: remove `AMAZON_EMAIL` and `AMAZON_PASSWORD` from `.env` and log in yourself in the browser window
- Ensure you're using the correct Amazon.de account

**No invoices downloaded**
- Check if you have orders in the selected year
- Some orders may not have invoices available for download
- Verify the date range in the console output

### Debug Mode

The script provides console output showing:
- Date range being processed
- Number of orders found on each page
- Download progress for each invoice
- Final count of downloaded invoices

## Legal Disclaimer

This tool is for personal use only. By using this script, you agree to:
- Use it only with your own Amazon account
- Comply with Amazon's Terms of Service
- Use downloaded invoices for legitimate purposes only
- Take responsibility for any consequences of its use

The authors are not responsible for any misuse of this tool or any consequences arising from its use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all prerequisites are installed correctly
3. Verify your `.env` file configuration
4. Open an issue on GitHub with detailed error information

---

**Note**: This script is designed for Amazon.de (German Amazon). It may not work with other Amazon regional sites without modifications.
