# Bandcamp.com Autocheckout

## Overview
This repository contains a program for harvesting sessions for the Bandcamp.com website. The program allows for the collection of session data from users accessing the Bandcamp.com website, facilitating further analysis or usage.

## Important Note
**The hashing algorithm used in mobile and generate mode needs to be updated. Please check the smali code in the APK for it.**

## Features
- Automatically collects session data from users visiting the Bandcamp.com website.
- Supports desktop mode with PayPal for payment processing.
- Supports desktop mode with card payments, although it may work very rarely due to security measures.

## Usage
To use the Bandcamp.com Session Harvester, follow these steps:

1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Edit `tasks-example.csv` to change your information.
4. Edit `config.json` to adjust the monitor delay and webhook settings.
5. Run the program to start harvesting sessions from the Bandcamp.com website.

## Note
Using this program to harvest sessions from the Bandcamp.com website may be subject to legal restrictions or terms of service agreements. Ensure that you have the necessary permissions or rights to collect session data from users.

## Maintenance
While 99% of the code still works, it's crucial to update the hashing algorithm used in mobile and generate mode. Failure to update this algorithm may result in inaccurate or unreliable results.

## Contributing
Contributions to the project are welcome! If you'd like to contribute, please fork the repository and submit a pull request with your changes. Be sure to follow the project's coding standards and guidelines.

## License
This project is licensed under the [MIT License](LICENSE).
